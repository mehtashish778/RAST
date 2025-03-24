# -*- coding: utf-8 -*-
"""
HAZOP Analysis Tool - Scenario Management Page
"""
import streamlit as st
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from utils.data_access import ScenarioDAO, EquipmentDAO, ChemicalDAO
from typing import Dict, List, Any, Optional
from core.consequence import ConsequenceCalculator


def render_scenarios_page():
    """
    Render the scenario management page
    """
    st.header("HAZOP Scenario Management")
    
    # Create tabs for different actions
    tab1, tab2, tab3, tab4 = st.tabs([
        "View Scenarios", 
        "Create Scenario", 
        "Edit Scenario",
        "Scenario Analysis"
    ])
    
    with tab1:
        render_view_scenarios_tab()
    
    with tab2:
        render_create_scenario_tab()
    
    with tab3:
        render_edit_scenario_tab()
    
    with tab4:
        render_scenario_analysis_tab()


def render_view_scenarios_tab():
    """Render the view scenarios tab"""
    st.subheader("Scenario Database")
    
    # Add equipment filter
    equipment_list = EquipmentDAO.get_all_equipment()
    equipment_options = ["All Equipment"] + [f"{eq['tag']} - {eq['name']}" for eq in equipment_list]
    selected_equipment = st.selectbox("Filter by Equipment:", options=equipment_options)
    
    # Process filter selection
    scenarios = []
    if selected_equipment == "All Equipment":
        scenarios = ScenarioDAO.get_all_scenarios()
    else:
        # Extract equipment ID from the selection
        equipment_tag = selected_equipment.split(" - ")[0]
        for eq in equipment_list:
            if eq['tag'] == equipment_tag:
                scenarios = ScenarioDAO.get_scenarios_by_equipment(eq['id'])
                break
    
    if not scenarios:
        st.info("No scenarios found. Create new scenarios using the 'Create Scenario' tab.")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame(scenarios)
    
    # Format DataFrame for better display
    if 'attributes' in df.columns:
        try:
            df['attributes'] = df['attributes'].apply(lambda x: json.loads(x) if x else {})
        except Exception as e:
            st.error(f"Error parsing attributes: {e}")
    
    # Add equipment name for better readability
    if 'equipment_id' in df.columns:
        equipment_map = {eq['id']: f"{eq['tag']} - {eq['name']}" for eq in equipment_list}
        df['equipment'] = df['equipment_id'].apply(lambda x: equipment_map.get(x, "Unknown"))
    
    # Create an expander for each scenario
    for _, row in df.iterrows():
        with st.expander(f"Scenario {row['id']}: {row['node']} - {row['deviation']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Node:** " + row['node'])
                st.markdown("**Deviation:** " + row['deviation'])
                st.markdown("**Equipment:** " + row.get('equipment', "Unknown"))
                st.markdown("**Risk Category:** " + row.get('risk_category', "Not specified"))
            
            with col2:
                st.markdown("**Causes:**")
                st.markdown(row.get('causes', "Not specified"))
                st.markdown("**Consequences:**")
                st.markdown(row.get('consequences', "Not specified"))
                
            st.markdown("**Safeguards:**")
            st.markdown(row.get('safeguards', "Not specified"))
            st.markdown("**Recommendations:**")
            st.markdown(row.get('recommendations', "Not specified"))


def render_create_scenario_tab():
    """Render the create scenario tab"""
    st.subheader("Create New Scenario")
    
    # Get equipment list for selection
    equipment_list = EquipmentDAO.get_all_equipment()
    if not equipment_list:
        st.warning("No equipment found. Please add equipment in the Equipment Database before creating scenarios.")
        return
    
    # Add template selection
    use_template = st.checkbox("Use predefined template")
    
    if use_template:
        # Get template names
        templates = ScenarioDAO.get_available_templates()
        template_names = {
            "high_pressure": "High Pressure Scenario",
            "low_flow": "Low Flow Scenario",
            "high_temperature": "High Temperature Scenario"
        }
        
        template_options = [template_names.get(t, t) for t in templates]
        selected_template_idx = st.selectbox(
            "Select Template:",
            options=range(len(template_options)),
            format_func=lambda x: template_options[x]
        )
        
        # Get template data
        template_name = templates[selected_template_idx]
        template_data = ScenarioDAO.get_scenario_template(template_name)
        
        # Show template preview
        with st.expander("Template Preview", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Node:** {template_data.get('node', '')}")
                st.markdown(f"**Deviation:** {template_data.get('deviation', '')}")
                st.markdown(f"**Risk Category:** {template_data.get('risk_category', '')}")
            
            with col2:
                st.markdown("**Causes:**")
                st.markdown(template_data.get('causes', ''))
                st.markdown("**Consequences:**")
                st.markdown(template_data.get('consequences', ''))
    
    # Create form for scenario creation
    with st.form("create_scenario_form"):
        # Equipment selection
        equipment_options = [f"{eq['tag']} - {eq['name']}" for eq in equipment_list]
        selected_equipment = st.selectbox("Equipment:", options=equipment_options)
        
        # Extract equipment ID from selection
        equipment_id = None
        equipment_tag = selected_equipment.split(" - ")[0]
        for eq in equipment_list:
            if eq['tag'] == equipment_tag:
                equipment_id = eq['id']
                break
        
        # Initialize form fields with template data if selected
        if use_template and 'template_data' in locals():
            node_default = template_data.get('node', '')
            deviation_default = template_data.get('deviation', '')
            causes_default = template_data.get('causes', '')
            consequences_default = template_data.get('consequences', '')
            safeguards_default = template_data.get('safeguards', '')
            recommendations_default = template_data.get('recommendations', '')
            risk_category_default = template_data.get('risk_category', 'Low')
            attributes_default = json.dumps(template_data.get('attributes', {}))
        else:
            node_default = ''
            deviation_default = ''
            causes_default = ''
            consequences_default = ''
            safeguards_default = ''
            recommendations_default = ''
            risk_category_default = 'Low'
            attributes_default = '{}'
        
        # Basic scenario information
        node = st.text_input("Node:", value=node_default, placeholder="e.g., Reactor Feed")
        
        # Deviation input - either from template or using guide words
        if use_template and 'template_data' in locals():
            deviation = st.text_input("Deviation:", value=deviation_default)
        else:
            # Deviation selection - using standard HAZOP guide words
            guide_words = ["No/None", "More", "Less", "As Well As", "Part Of", "Reverse", "Other Than", "Too Early", "Too Late", "Before", "After"]
            parameters = ["Flow", "Pressure", "Temperature", "Level", "Composition", "Phase", "Reaction", "Maintenance", "Other"]
            
            col1, col2 = st.columns(2)
            with col1:
                guide_word = st.selectbox("Guide Word:", options=guide_words)
            with col2:
                parameter = st.selectbox("Parameter:", options=parameters)
            
            deviation = f"{guide_word} {parameter}"
            st.text_input("Deviation:", value=deviation, disabled=True)
        
        # Detailed scenario information
        causes = st.text_area("Causes:", value=causes_default, placeholder="List potential causes...")
        consequences = st.text_area("Consequences:", value=consequences_default, placeholder="List potential consequences...")
        safeguards = st.text_area("Safeguards:", value=safeguards_default, placeholder="List existing safeguards...")
        recommendations = st.text_area("Recommendations:", value=recommendations_default, placeholder="List recommendations...")
        
        # Risk assessment
        risk_categories = ["Low", "Medium", "High", "Very High"]
        risk_index = risk_categories.index(risk_category_default) if risk_category_default in risk_categories else 0
        risk_category = st.selectbox("Risk Category:", options=risk_categories, index=risk_index)
        
        # Additional attributes as JSON
        st.markdown("### Additional Attributes (Optional)")
        st.markdown("Enter any additional attributes in JSON format, e.g., `{\"severity\": 3, \"likelihood\": 2}`")
        attributes_json = st.text_area("Attributes (JSON):", value=attributes_default, placeholder="{}", height=100)
        
        # Submit button
        submitted = st.form_submit_button("Create Scenario")
        
        if submitted:
            try:
                # Parse attributes JSON
                attributes = {}
                if attributes_json:
                    attributes = json.loads(attributes_json)
                
                # Prepare scenario data
                scenario_data = {
                    "equipment_id": equipment_id,
                    "node": node,
                    "deviation": deviation,
                    "causes": causes,
                    "consequences": consequences,
                    "safeguards": safeguards,
                    "recommendations": recommendations,
                    "risk_category": risk_category,
                    "attributes": attributes
                }
                
                # Add scenario to database
                if ScenarioDAO.add_or_update_scenario(scenario_data):
                    st.success("Scenario created successfully!")
                else:
                    st.error("Failed to create scenario. Please check the inputs and try again.")
            except json.JSONDecodeError:
                st.error("Invalid JSON in attributes field. Please check the format.")
            except Exception as e:
                st.error(f"Error creating scenario: {e}")


def render_edit_scenario_tab():
    """Render the edit scenario tab"""
    st.subheader("Edit Existing Scenario")
    
    # Get all scenarios
    scenarios = ScenarioDAO.get_all_scenarios()
    if not scenarios:
        st.info("No scenarios found. Create new scenarios using the 'Create Scenario' tab.")
        return
    
    # Get equipment list for mapping
    equipment_list = EquipmentDAO.get_all_equipment()
    equipment_map = {eq['id']: f"{eq['tag']} - {eq['name']}" for eq in equipment_list}
    
    # Create selection options
    scenario_options = [f"Scenario {s['id']}: {s['node']} - {s['deviation']}" for s in scenarios]
    selected_scenario_idx = st.selectbox("Select Scenario to Edit:", options=range(len(scenario_options)), format_func=lambda x: scenario_options[x])
    
    # Get the selected scenario
    selected_scenario = scenarios[selected_scenario_idx]
    
    # Create form for scenario editing
    with st.form("edit_scenario_form"):
        # Equipment selection
        current_equipment = equipment_map.get(selected_scenario['equipment_id'], "Unknown")
        equipment_options = [f"{eq['tag']} - {eq['name']}" for eq in equipment_list]
        selected_equipment = st.selectbox("Equipment:", options=equipment_options, index=equipment_options.index(current_equipment) if current_equipment in equipment_options else 0)
        
        # Extract equipment ID from selection
        equipment_id = None
        equipment_tag = selected_equipment.split(" - ")[0]
        for eq in equipment_list:
            if eq['tag'] == equipment_tag:
                equipment_id = eq['id']
                break
        
        # Basic scenario information
        node = st.text_input("Node:", value=selected_scenario['node'])
        deviation = st.text_input("Deviation:", value=selected_scenario['deviation'])
        
        # Detailed scenario information
        causes = st.text_area("Causes:", value=selected_scenario.get('causes', ""))
        consequences = st.text_area("Consequences:", value=selected_scenario.get('consequences', ""))
        safeguards = st.text_area("Safeguards:", value=selected_scenario.get('safeguards', ""))
        recommendations = st.text_area("Recommendations:", value=selected_scenario.get('recommendations', ""))
        
        # Risk assessment
        risk_categories = ["Low", "Medium", "High", "Very High"]
        current_risk = selected_scenario.get('risk_category', "Low")
        risk_index = risk_categories.index(current_risk) if current_risk in risk_categories else 0
        risk_category = st.selectbox("Risk Category:", options=risk_categories, index=risk_index)
        
        # Additional attributes as JSON
        st.markdown("### Additional Attributes (Optional)")
        st.markdown("Enter any additional attributes in JSON format, e.g., `{\"severity\": 3, \"likelihood\": 2}`")
        
        # Parse existing attributes
        attributes_str = "{}"
        if 'attributes' in selected_scenario and selected_scenario['attributes']:
            if isinstance(selected_scenario['attributes'], str):
                attributes_str = selected_scenario['attributes']
            else:
                attributes_str = json.dumps(selected_scenario['attributes'])
        
        attributes_json = st.text_area("Attributes (JSON):", value=attributes_str, height=100)
        
        # Submit buttons
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Update Scenario")
        with col2:
            delete_button = st.form_submit_button("Delete Scenario", type="secondary")
        
        if submitted:
            try:
                # Parse attributes JSON
                attributes = {}
                if attributes_json:
                    attributes = json.loads(attributes_json)
                
                # Prepare scenario data
                scenario_data = {
                    "id": selected_scenario['id'],
                    "equipment_id": equipment_id,
                    "node": node,
                    "deviation": deviation,
                    "causes": causes,
                    "consequences": consequences,
                    "safeguards": safeguards,
                    "recommendations": recommendations,
                    "risk_category": risk_category,
                    "attributes": attributes
                }
                
                # Update scenario in database
                if ScenarioDAO.add_or_update_scenario(scenario_data):
                    st.success("Scenario updated successfully!")
                else:
                    st.error("Failed to update scenario. Please check the inputs and try again.")
            except json.JSONDecodeError:
                st.error("Invalid JSON in attributes field. Please check the format.")
            except Exception as e:
                st.error(f"Error updating scenario: {e}")
        
        if delete_button:
            if ScenarioDAO.delete_scenario(selected_scenario['id']):
                st.success("Scenario deleted successfully!")
            else:
                st.error("Failed to delete scenario.")


def render_scenario_analysis_tab():
    """Render the scenario analysis tab"""
    st.subheader("Scenario Analysis")
    
    # Create sub-tabs for different analysis views
    analysis_tab1, analysis_tab2, analysis_tab3 = st.tabs([
        "Overview", 
        "Risk Matrix", 
        "Consequence Analysis"
    ])
    
    # Get all scenarios
    scenarios = ScenarioDAO.get_all_scenarios()
    if not scenarios:
        with analysis_tab1, analysis_tab2, analysis_tab3:
            st.info("No scenarios found. Create new scenarios using the 'Create Scenario' tab.")
        return
    
    # Get equipment list for mapping
    equipment_list = EquipmentDAO.get_all_equipment()
    equipment_map = {eq['id']: f"{eq['tag']} - {eq['name']}" for eq in equipment_list}
    
    # Convert scenarios to DataFrame for analysis
    df = pd.DataFrame(scenarios)
    
    # Add equipment name for better readability
    if 'equipment_id' in df.columns:
        df['equipment'] = df['equipment_id'].apply(lambda x: equipment_map.get(x, "Unknown"))
    
    # Extract severity and likelihood from attributes if available
    if 'attributes' in df.columns:
        def extract_value(attr_str, key, default=0):
            try:
                if isinstance(attr_str, str):
                    attr = json.loads(attr_str)
                else:
                    attr = attr_str
                return attr.get(key, default)
            except:
                return default
                
        df['severity'] = df['attributes'].apply(lambda x: extract_value(x, 'severity', 1))
        df['likelihood'] = df['attributes'].apply(lambda x: extract_value(x, 'likelihood', 1))
        df['risk_score'] = df.apply(lambda row: ConsequenceCalculator.calculate_risk_score(row['severity'], row['likelihood']), axis=1)
    
    # OVERVIEW TAB
    with analysis_tab1:
        st.markdown("### Scenario Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Scenarios", len(scenarios))
        
        with col2:
            if 'risk_category' in df.columns:
                high_risk_count = len(df[df['risk_category'].isin(["High", "Very High"])])
                st.metric("High Risk Scenarios", high_risk_count)
        
        with col3:
            if 'equipment_id' in df.columns:
                equipment_count = df['equipment_id'].nunique()
                st.metric("Equipment with Scenarios", equipment_count)
        
        # Scenario distribution by equipment
        if 'equipment' in df.columns:
            st.markdown("### Scenarios by Equipment")
            equipment_counts = df['equipment'].value_counts()
            st.bar_chart(equipment_counts)
        
        # Risk category distribution
        if 'risk_category' in df.columns:
            st.markdown("### Scenarios by Risk Category")
            risk_counts = df['risk_category'].value_counts()
            st.bar_chart(risk_counts)
        
        # Advanced filtering
        st.markdown("### Advanced Filtering")
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            if 'equipment' in df.columns:
                equipment_filter = st.multiselect(
                    "Equipment:",
                    options=df['equipment'].unique(),
                    default=[]
                )
        
        with filter_col2:
            if 'risk_category' in df.columns:
                risk_filter = st.multiselect(
                    "Risk Category:",
                    options=df['risk_category'].unique(),
                    default=[]
                )
        
        # Apply filters
        filtered_df = df.copy()
        if equipment_filter:
            filtered_df = filtered_df[filtered_df['equipment'].isin(equipment_filter)]
        if risk_filter:
            filtered_df = filtered_df[filtered_df['risk_category'].isin(risk_filter)]
        
        # Display filtered scenarios
        if not filtered_df.empty:
            st.markdown("### Filtered Scenarios")
            st.dataframe(filtered_df[[
                'id', 'node', 'deviation', 'equipment', 'risk_category'
            ]])
        else:
            st.info("No scenarios match the selected filters.")
    
    # RISK MATRIX TAB
    with analysis_tab2:
        st.markdown("### Risk Assessment Matrix")
        
        if 'severity' in df.columns and 'likelihood' in df.columns:
            # Create risk matrix data
            matrix_data = np.zeros((5, 5))
            
            # Count scenarios in each cell
            for _, row in df.iterrows():
                sev = int(min(max(row['severity'], 1), 5))
                like = int(min(max(row['likelihood'], 1), 5))
                matrix_data[5-like, sev-1] += 1
            
            # Create figure and axis
            fig, ax = plt.figure(figsize=(10, 8)), plt.axes()
            
            # Define colors for risk levels
            cmap = plt.cm.RdYlGn_r
            
            # Create the heatmap
            im = ax.imshow(matrix_data, cmap=cmap)
            
            # Configure axes
            ax.set_xticks(np.arange(5))
            ax.set_yticks(np.arange(5))
            ax.set_xticklabels(['1', '2', '3', '4', '5'])
            ax.set_yticklabels(['5', '4', '3', '2', '1'])
            
            # Labels
            ax.set_xlabel('Severity')
            ax.set_ylabel('Likelihood')
            ax.set_title('Risk Matrix')
            
            # Add text annotations to each cell
            for i in range(5):
                for j in range(5):
                    if matrix_data[i, j] > 0:
                        text = ax.text(j, i, int(matrix_data[i, j]),
                                    ha="center", va="center", color="white", fontweight="bold")
            
            # Add colorbar
            plt.colorbar(im, ax=ax, label='Number of Scenarios')
            
            # Add risk level regions
            # Low risk (1-4)
            ax.add_patch(plt.Rectangle((-0.5, 3.5), 2, 2, fill=False, edgecolor='green', linewidth=2))
            # Medium risk (5-9)
            ax.add_patch(plt.Rectangle((1.5, 1.5), 2, 2, fill=False, edgecolor='yellow', linewidth=2))
            ax.add_patch(plt.Rectangle((-0.5, 1.5), 2, 2, fill=False, edgecolor='yellow', linewidth=2))
            ax.add_patch(plt.Rectangle((1.5, 3.5), 2, 2, fill=False, edgecolor='yellow', linewidth=2))
            # High risk (10-16)
            ax.add_patch(plt.Rectangle((3.5, -0.5), 1, 2, fill=False, edgecolor='orange', linewidth=2))
            ax.add_patch(plt.Rectangle((1.5, -0.5), 2, 2, fill=False, edgecolor='orange', linewidth=2))
            ax.add_patch(plt.Rectangle((3.5, 1.5), 1, 2, fill=False, edgecolor='orange', linewidth=2))
            # Very high risk (17-25)
            ax.add_patch(plt.Rectangle((3.5, 3.5), 1, 2, fill=False, edgecolor='red', linewidth=2))
            
            # Display the figure
            st.pyplot(fig)
            
            # Risk level legend
            st.markdown("### Risk Levels")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("🟢 **Low Risk** (1-4)")
                st.markdown("No immediate action needed")
            
            with col2:
                st.markdown("🟡 **Medium Risk** (5-9)")
                st.markdown("Action should be planned")
            
            with col3:
                st.markdown("🟠 **High Risk** (10-16)")
                st.markdown("Prompt action required")
            
            with col4:
                st.markdown("🔴 **Very High Risk** (17-25)")
                st.markdown("Immediate action required")
            
            # Display scenarios with highest risk
            high_risk = df.sort_values(by='risk_score', ascending=False).head(5)
            if not high_risk.empty:
                st.markdown("### Highest Risk Scenarios")
                for _, row in high_risk.iterrows():
                    with st.expander(f"Scenario {row['id']}: {row['node']} - {row['deviation']} (Risk Score: {row.get('risk_score', 'N/A')})"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Equipment:** {row.get('equipment', 'Unknown')}")
                            st.markdown(f"**Risk Category:** {row.get('risk_category', 'Unknown')}")
                            st.markdown(f"**Severity:** {row.get('severity', 'N/A')}")
                            st.markdown(f"**Likelihood:** {row.get('likelihood', 'N/A')}")
                        
                        with col2:
                            st.markdown("**Causes:**")
                            st.markdown(row.get('causes', 'Not specified'))
                            st.markdown("**Consequences:**")
                            st.markdown(row.get('consequences', 'Not specified'))
        else:
            st.warning("Risk matrix cannot be generated. Please add severity and likelihood attributes to your scenarios.")
    
    # CONSEQUENCE ANALYSIS TAB
    with analysis_tab3:
        st.markdown("### Consequence Analysis")
        
        # Select scenario for analysis
        scenario_options = [f"Scenario {s['id']}: {s['node']} - {s['deviation']}" for s in scenarios]
        selected_scenario_idx = st.selectbox(
            "Select Scenario:",
            options=range(len(scenario_options)),
            format_func=lambda x: scenario_options[x]
        )
        
        # Get the selected scenario
        selected_scenario = scenarios[selected_scenario_idx]
        
        # Create tabs for different consequence types
        consequence_tab1, consequence_tab2, consequence_tab3 = st.tabs([
            "Release & Dispersion", 
            "Fire & Explosion",
            "Risk Assessment"
        ])
        
        # RELEASE AND DISPERSION TAB
        with consequence_tab1:
            st.markdown("### Release and Dispersion Analysis")
            
            # Input parameters for release calculation
            st.markdown("#### Release Parameters")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                hole_size = st.number_input("Hole Size (mm)", min_value=1.0, max_value=1000.0, value=10.0, step=1.0)
            
            with col2:
                pressure = st.number_input("Pressure (kPa)", min_value=0.0, max_value=10000.0, value=500.0, step=100.0)
            
            with col3:
                density = st.number_input("Fluid Density (kg/m³)", min_value=1.0, max_value=20000.0, value=1000.0, step=100.0)
            
            # Calculate release rate
            release_rate = ConsequenceCalculator.estimate_release_rate(hole_size, pressure, density)
            
            st.markdown(f"**Estimated Release Rate: {release_rate:.2f} kg/s**")
            
            # Input parameters for dispersion calculation
            st.markdown("#### Dispersion Parameters")
            col1, col2 = st.columns(2)
            
            with col1:
                wind_speed = st.slider("Wind Speed (m/s)", min_value=1.0, max_value=20.0, value=5.0, step=0.5)
            
            with col2:
                stability_class = st.selectbox(
                    "Atmospheric Stability Class",
                    options=["A", "B", "C", "D", "E", "F"],
                    index=3,  # Default to D (neutral)
                    help="A: Very unstable, B: Unstable, C: Slightly unstable, D: Neutral, E: Stable, F: Very stable"
                )
            
            # Calculate dispersion distance
            dispersion_distance = ConsequenceCalculator.estimate_dispersion_distance(release_rate, wind_speed, stability_class)
            
            st.markdown(f"**Estimated Dispersion Distance: {dispersion_distance:.0f} meters**")
            
            # Get chemical properties if available
            st.markdown("#### Toxic Effects")
            
            chemicals = ChemicalDAO.get_all_chemicals()
            chemical_options = ["Select Chemical"] + [c['name'] for c in chemicals]
            selected_chemical = st.selectbox("Chemical:", options=chemical_options)
            
            if selected_chemical != "Select Chemical":
                # Get the chemical data
                chemical = ChemicalDAO.get_chemical_by_name(selected_chemical)
                
                if chemical:
                    # Extract needed properties
                    molecular_weight = 0
                    toxic_threshold = 0
                    
                    # Try to extract properties from JSON
                    if 'molecular_weight' in chemical:
                        molecular_weight = chemical['molecular_weight'] or 0
                    
                    if 'properties' in chemical and chemical['properties']:
                        try:
                            props = json.loads(chemical['properties']) if isinstance(chemical['properties'], str) else chemical['properties']
                            toxic_threshold = props.get('erpg_2', 0) or props.get('idlh', 0) or 100
                        except:
                            toxic_threshold = 100
                    
                    # Calculate toxic consequences
                    if molecular_weight > 0 and toxic_threshold > 0:
                        toxic_results = ConsequenceCalculator.estimate_toxic_consequence(
                            release_rate, toxic_threshold, molecular_weight, wind_speed
                        )
                        
                        # Display results
                        st.markdown("#### Toxic Release Consequence Estimates")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Affected Radius", f"{toxic_results['radius_m']:.0f} m")
                            st.metric("Affected Area", f"{toxic_results['affected_area_m2']/10000:.2f} ha")
                        
                        with col2:
                            st.metric("Release Duration", f"{toxic_results['release_duration_min']:.0f} min")
                            st.metric("Potential Population Affected", f"{toxic_results['potential_casualties']:.0f} people")
                    else:
                        st.warning("Insufficient chemical property data for toxic consequence analysis.")
                else:
                    st.warning("Chemical data not found.")
            else:
                st.info("Select a chemical to estimate toxic consequences.")
        
        # FIRE AND EXPLOSION TAB
        with consequence_tab2:
            st.markdown("### Fire and Explosion Analysis")
            
            # Choose analysis type
            analysis_type = st.radio("Analysis Type:", ["Fire Analysis", "Explosion Analysis"])
            
            if analysis_type == "Fire Analysis":
                st.markdown("#### Fire Parameters")
                col1, col2 = st.columns(2)
                
                with col1:
                    release_rate_fire = st.number_input("Release Rate (kg/s)", min_value=0.1, max_value=100.0, value=max(0.1, release_rate), step=0.1)
                
                with col2:
                    heat_of_combustion = st.number_input("Heat of Combustion (kJ/kg)", min_value=1000.0, max_value=100000.0, value=45000.0, step=1000.0)
                
                # Calculate fire consequences
                fire_results = ConsequenceCalculator.estimate_fire_consequence(release_rate_fire, heat_of_combustion)
                
                # Display results
                st.markdown("#### Fire Consequence Estimates")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Heat Release Rate", f"{fire_results['heat_release_rate_kw']/1000:.0f} MW")
                    st.metric("Flame Height", f"{fire_results['flame_height_m']:.1f} m")
                
                with col2:
                    st.metric("Radiation Distance (5 kW/m²)", f"{fire_results['radiation_distance_m']:.0f} m")
                    st.metric("Affected Area", f"{fire_results['affected_area_m2']/10000:.2f} ha")
                
            else:  # Explosion Analysis
                st.markdown("#### Explosion Parameters")
                col1, col2 = st.columns(2)
                
                with col1:
                    mass = st.number_input("Flammable Mass (kg)", min_value=1.0, max_value=10000.0, value=100.0, step=10.0)
                
                with col2:
                    tnt_factor = st.number_input("TNT Equivalency Factor", min_value=0.01, max_value=10.0, value=0.1, step=0.01)
                
                # Calculate explosion consequences
                explosion_results = ConsequenceCalculator.estimate_explosion_consequence(mass, tnt_factor)
                
                # Display results
                st.markdown("#### Explosion Consequence Estimates")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("TNT Equivalent", f"{explosion_results['tnt_equivalent_kg']:.1f} kg")
                    st.metric("Window Breakage Distance", f"{explosion_results['distance_window_breakage_m']:.0f} m")
                
                with col2:
                    st.metric("Structural Damage Distance", f"{explosion_results['distance_structural_damage_m']:.0f} m")
                    st.metric("Severe Structural Damage", f"{explosion_results['distance_severe_damage_m']:.0f} m")
        
        # RISK ASSESSMENT TAB
        with consequence_tab3:
            st.markdown("### Risk Assessment")
            
            # Get severity and likelihood from scenario attributes or allow user input
            attributes = {}
            if 'attributes' in selected_scenario and selected_scenario['attributes']:
                try:
                    if isinstance(selected_scenario['attributes'], str):
                        attributes = json.loads(selected_scenario['attributes'])
                    else:
                        attributes = selected_scenario['attributes']
                except:
                    pass
            
            # Input fields
            col1, col2 = st.columns(2)
            
            with col1:
                severity = st.slider("Severity (1-5):", min_value=1, max_value=5, value=attributes.get('severity', 3))
            
            with col2:
                likelihood = st.slider("Likelihood (1-5):", min_value=1, max_value=5, value=attributes.get('likelihood', 3))
            
            # Perform risk assessment
            risk_results = ConsequenceCalculator.assess_risk(severity, likelihood)
            
            # Display results
            st.markdown("#### Risk Assessment Results")
            
            # Create a custom risk meter
            risk_score = risk_results['risk_score']
            risk_category = risk_results['risk_category']
            
            # Define colors for risk levels
            color_map = {
                "Low": "green",
                "Medium": "yellow",
                "High": "orange",
                "Very High": "red"
            }
            
            # Calculate percentage for progress bar
            risk_percentage = (risk_score / 25) * 100
            
            # Display risk score with color
            st.markdown(f"<h3 style='text-align: center; color: {color_map[risk_category]};'>Risk Score: {risk_score}/25 ({risk_category})</h3>", unsafe_allow_html=True)
            
            # Create a progress bar for risk visualization
            st.progress(risk_percentage / 100)
            
            # Display risk assessment details
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Needs LOPA Analysis:** {'Yes' if risk_results['needs_lopa'] else 'No'}")
            
            with col2:
                st.markdown(f"**Recommended Action:**")
                st.markdown(risk_results['recommended_action'])
            
            # Option to update scenario with risk assessment
            if st.button("Update Scenario with Risk Assessment"):
                try:
                    # Update attributes with risk assessment
                    attributes.update({
                        'severity': severity,
                        'likelihood': likelihood,
                        'risk_score': risk_score,
                        'needs_lopa': risk_results['needs_lopa']
                    })
                    
                    # Update scenario data
                    scenario_data = {
                        'id': selected_scenario['id'],
                        'risk_category': risk_category,
                        'attributes': attributes
                    }
                    
                    # Update scenario in database
                    if ScenarioDAO.add_or_update_scenario(scenario_data):
                        st.success("Scenario updated with risk assessment!")
                    else:
                        st.error("Failed to update scenario.")
                except Exception as e:
                    st.error(f"Error updating scenario: {e}") 