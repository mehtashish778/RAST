# -*- coding: utf-8 -*-
"""
HAZOP Analysis Tool - Chemical Database Page
"""
import streamlit as st
import pandas as pd
import io
from utils.data_access import ChemicalDAO


def render_chemical_database_page():
    """
    Render the chemical database management page
    """
    st.header("Chemical Database")
    st.write("Chemical database management feature is currently under development.")
    
    # Create tabs for different actions
    tab1, tab2, tab3, tab4 = st.tabs(["View Chemicals", "Add Chemical", "Edit Chemical", "Import/Export"])
    
    with tab1:
        render_view_chemicals_tab()
    
    with tab2:
        render_add_chemical_tab()
    
    with tab3:
        render_edit_chemical_tab()
    
    with tab4:
        render_import_export_tab()


def render_view_chemicals_tab():
    """Render the view chemicals tab"""
    st.subheader("Chemical Database")
    
    # Get all chemicals from the database
    chemicals = ChemicalDAO.get_all_chemicals()
    
    if not chemicals:
        st.info("No chemicals found in the database. Add some chemicals to get started.")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame(chemicals)
    
    # Convert properties from JSON string to dict
    if 'properties' in df.columns:
        try:
            import json
            df['properties'] = df['properties'].apply(lambda x: json.loads(x) if x else {})
        except Exception as e:
            st.error(f"Error parsing properties: {e}")
            df['properties'] = '{}'
    
    # Display the chemicals in a table
    st.dataframe(df)
    
    # Allow selecting a chemical for details
    if len(chemicals) > 0:
        chemical_names = [c['name'] for c in chemicals]
        selected_chemical = st.selectbox("Select a chemical for details", chemical_names)
        
        if selected_chemical:
            # Find the selected chemical
            chemical = next((c for c in chemicals if c['name'] == selected_chemical), None)
            if chemical:
                st.subheader(f"Details for {chemical['name']}")
                
                # Create columns for better layout
                col1, col2 = st.columns(2)
                
                # Display basic properties in first column
                with col1:
                    st.write("**Basic Information**")
                    st.write(f"CAS Number: {chemical.get('cas_number', 'N/A')}")
                    st.write(f"Molecular Weight: {chemical.get('molecular_weight', 'N/A')} g/mol")
                    st.write(f"Boiling Point: {chemical.get('boiling_point', 'N/A')} °C")
                    st.write(f"Melting Point: {chemical.get('melting_point', 'N/A')} °C")
                
                # Display safety properties in second column
                with col2:
                    st.write("**Safety Properties**")
                    st.write(f"Flash Point: {chemical.get('flash_point', 'N/A')} °C")
                    st.write(f"Auto-ignition Temperature: {chemical.get('auto_ignition_temp', 'N/A')} °C")
                    st.write(f"Lower Flammability Limit: {chemical.get('lower_flammability_limit', 'N/A')} %")
                    st.write(f"Upper Flammability Limit: {chemical.get('upper_flammability_limit', 'N/A')} %")
                
                # Display NFPA ratings
                st.write("**NFPA Ratings**")
                nfpa_col1, nfpa_col2, nfpa_col3, nfpa_col4 = st.columns(4)
                
                with nfpa_col1:
                    st.metric("Health", chemical.get('nfpa_health', 'N/A'))
                with nfpa_col2:
                    st.metric("Flammability", chemical.get('nfpa_flammability', 'N/A'))
                with nfpa_col3:
                    st.metric("Reactivity", chemical.get('nfpa_reactivity', 'N/A'))
                with nfpa_col4:
                    st.metric("Special", chemical.get('nfpa_special', 'N/A'))
                
                # Display additional properties
                st.write("**Additional Properties**")
                try:
                    import json
                    properties = json.loads(chemical.get('properties', '{}'))
                    if properties:
                        for key, value in properties.items():
                            st.write(f"{key}: {value}")
                    else:
                        st.write("No additional properties")
                except Exception as e:
                    st.error(f"Error parsing properties: {e}")


def render_add_chemical_tab():
    """Render the add chemical tab"""
    st.subheader("Add New Chemical")
    
    # Create form for adding a new chemical
    with st.form("add_chemical_form"):
        # Basic information
        st.write("**Basic Information**")
        name = st.text_input("Chemical Name*", help="The full name of the chemical")
        cas = st.text_input("CAS Number", help="Chemical Abstracts Service registry number")
        mol_weight = st.number_input("Molecular Weight (g/mol)", min_value=0.0, step=0.1)
        
        # Physical properties
        st.write("**Physical Properties**")
        col1, col2 = st.columns(2)
        with col1:
            boiling_point = st.number_input("Boiling Point (°C)", step=0.1)
            melting_point = st.number_input("Melting Point (°C)", step=0.1)
        with col2:
            flash_point = st.number_input("Flash Point (°C)", step=0.1)
            auto_ignition = st.number_input("Auto-ignition Temperature (°C)", step=0.1)
        
        # Flammability
        st.write("**Flammability**")
        col3, col4 = st.columns(2)
        with col3:
            lfl = st.number_input("Lower Flammability Limit (%)", min_value=0.0, max_value=100.0, step=0.1)
        with col4:
            ufl = st.number_input("Upper Flammability Limit (%)", min_value=0.0, max_value=100.0, step=0.1)
        
        # Emergency Response Planning Guidelines
        st.write("**Emergency Response Planning Guidelines**")
        col5, col6 = st.columns(2)
        with col5:
            erpg_2 = st.number_input("ERPG-2 (ppm)", min_value=0.0, step=0.1, 
                                    help="Concentration below which individuals could be exposed for up to 1 hour without experiencing irreversible health effects")
        with col6:
            erpg_3 = st.number_input("ERPG-3 (ppm)", min_value=0.0, step=0.1,
                                    help="Concentration below which individuals could be exposed for up to 1 hour without experiencing life-threatening health effects")
        
        # NFPA Ratings
        st.write("**NFPA Ratings**")
        col7, col8, col9, col10 = st.columns(4)
        with col7:
            nfpa_health = st.number_input("Health", min_value=0, max_value=4, step=1)
        with col8:
            nfpa_flammability = st.number_input("Flammability", min_value=0, max_value=4, step=1)
        with col9:
            nfpa_reactivity = st.number_input("Reactivity", min_value=0, max_value=4, step=1)
        with col10:
            nfpa_special = st.text_input("Special", max_chars=3, help="Special notice, like OX (oxidizer), W (water reactive)")
        
        # Additional properties
        st.write("**Additional Properties (Optional)**")
        st.text_area("Additional Properties", 
                    help="Enter additional properties in 'key: value' format, one per line")
        
        # Submit button
        submitted = st.form_submit_button("Add Chemical")
        
        if submitted:
            if not name:
                st.error("Chemical Name is required")
            else:
                # Prepare data for database
                chemical_data = {
                    'name': name,
                    'cas_number': cas if cas else None,
                    'molecular_weight': mol_weight if mol_weight > 0 else None,
                    'boiling_point': boiling_point,
                    'melting_point': melting_point,
                    'flash_point': flash_point,
                    'auto_ignition_temp': auto_ignition,
                    'lower_flammability_limit': lfl if lfl > 0 else None,
                    'upper_flammability_limit': ufl if ufl > 0 else None,
                    'erpg_2': erpg_2 if erpg_2 > 0 else None,
                    'erpg_3': erpg_3 if erpg_3 > 0 else None,
                    'nfpa_health': nfpa_health,
                    'nfpa_flammability': nfpa_flammability,
                    'nfpa_reactivity': nfpa_reactivity,
                    'nfpa_special': nfpa_special if nfpa_special else None
                }
                
                # Add the chemical to the database
                if ChemicalDAO.add_or_update_chemical(chemical_data):
                    st.success(f"Successfully added chemical: {name}")
                else:
                    st.error("Failed to add chemical to the database")


def render_edit_chemical_tab():
    """Render the edit chemical tab"""
    st.subheader("Edit Chemical")
    
    # Get all chemicals from the database
    chemicals = ChemicalDAO.get_all_chemicals()
    
    if not chemicals:
        st.info("No chemicals found in the database. Add some chemicals first.")
        return
    
    # Allow selecting a chemical to edit
    chemical_names = [c['name'] for c in chemicals]
    selected_chemical = st.selectbox("Select a chemical to edit", chemical_names)
    
    if selected_chemical:
        # Get the selected chemical
        chemical = ChemicalDAO.get_chemical_by_name(selected_chemical)
        
        if chemical:
            # Create form for editing
            with st.form("edit_chemical_form"):
                # Basic information
                st.write("**Basic Information**")
                name = st.text_input("Chemical Name*", value=chemical.get('name', ''), help="The full name of the chemical")
                cas = st.text_input("CAS Number", value=chemical.get('cas_number', ''), help="Chemical Abstracts Service registry number")
                mol_weight = st.number_input("Molecular Weight (g/mol)", 
                                            value=float(chemical.get('molecular_weight', 0.0) or 0.0),
                                            min_value=0.0, step=0.1)
                
                # Physical properties
                st.write("**Physical Properties**")
                col1, col2 = st.columns(2)
                with col1:
                    boiling_point = st.number_input("Boiling Point (°C)", 
                                                  value=float(chemical.get('boiling_point', 0.0) or 0.0),
                                                  step=0.1)
                    melting_point = st.number_input("Melting Point (°C)", 
                                                   value=float(chemical.get('melting_point', 0.0) or 0.0),
                                                   step=0.1)
                with col2:
                    flash_point = st.number_input("Flash Point (°C)", 
                                                value=float(chemical.get('flash_point', 0.0) or 0.0),
                                                step=0.1)
                    auto_ignition = st.number_input("Auto-ignition Temperature (°C)", 
                                                   value=float(chemical.get('auto_ignition_temp', 0.0) or 0.0),
                                                   step=0.1)
                
                # Flammability
                st.write("**Flammability**")
                col3, col4 = st.columns(2)
                with col3:
                    lfl = st.number_input("Lower Flammability Limit (%)", 
                                        value=float(chemical.get('lower_flammability_limit', 0.0) or 0.0),
                                        min_value=0.0, max_value=100.0, step=0.1)
                with col4:
                    ufl = st.number_input("Upper Flammability Limit (%)", 
                                        value=float(chemical.get('upper_flammability_limit', 0.0) or 0.0),
                                        min_value=0.0, max_value=100.0, step=0.1)
                
                # Emergency Response Planning Guidelines
                st.write("**Emergency Response Planning Guidelines**")
                col5, col6 = st.columns(2)
                with col5:
                    erpg_2 = st.number_input("ERPG-2 (ppm)", 
                                            value=float(chemical.get('erpg_2', 0.0) or 0.0),
                                            min_value=0.0, step=0.1)
                with col6:
                    erpg_3 = st.number_input("ERPG-3 (ppm)", 
                                            value=float(chemical.get('erpg_3', 0.0) or 0.0),
                                            min_value=0.0, step=0.1)
                
                # NFPA Ratings
                st.write("**NFPA Ratings**")
                col7, col8, col9, col10 = st.columns(4)
                with col7:
                    nfpa_health = st.number_input("Health", 
                                                value=int(chemical.get('nfpa_health', 0) or 0),
                                                min_value=0, max_value=4, step=1)
                with col8:
                    nfpa_flammability = st.number_input("Flammability", 
                                                      value=int(chemical.get('nfpa_flammability', 0) or 0),
                                                      min_value=0, max_value=4, step=1)
                with col9:
                    nfpa_reactivity = st.number_input("Reactivity", 
                                                     value=int(chemical.get('nfpa_reactivity', 0) or 0),
                                                     min_value=0, max_value=4, step=1)
                with col10:
                    nfpa_special = st.text_input("Special", 
                                               value=chemical.get('nfpa_special', ''),
                                               max_chars=3, help="Special notice, like OX (oxidizer), W (water reactive)")
                
                # Submit button
                submitted = st.form_submit_button("Update Chemical")
                
                if submitted:
                    if not name:
                        st.error("Chemical Name is required")
                    else:
                        # Prepare data for database
                        chemical_data = {
                            'id': chemical.get('id'),
                            'name': name,
                            'cas_number': cas if cas else None,
                            'molecular_weight': mol_weight if mol_weight > 0 else None,
                            'boiling_point': boiling_point,
                            'melting_point': melting_point,
                            'flash_point': flash_point,
                            'auto_ignition_temp': auto_ignition,
                            'lower_flammability_limit': lfl if lfl > 0 else None,
                            'upper_flammability_limit': ufl if ufl > 0 else None,
                            'erpg_2': erpg_2 if erpg_2 > 0 else None,
                            'erpg_3': erpg_3 if erpg_3 > 0 else None,
                            'nfpa_health': nfpa_health,
                            'nfpa_flammability': nfpa_flammability,
                            'nfpa_reactivity': nfpa_reactivity,
                            'nfpa_special': nfpa_special if nfpa_special else None
                        }
                        
                        # Update the chemical in the database
                        if ChemicalDAO.add_or_update_chemical(chemical_data):
                            st.success(f"Successfully updated chemical: {name}")
                        else:
                            st.error("Failed to update chemical in the database")
            
            # Add delete button outside the form
            if st.button(f"Delete {selected_chemical}", key="delete_chemical"):
                if st.session_state.get('confirm_delete') != selected_chemical:
                    st.session_state.confirm_delete = selected_chemical
                    st.warning(f"Are you sure you want to delete {selected_chemical}? Click again to confirm.")
                else:
                    if ChemicalDAO.delete_chemical(selected_chemical):
                        st.success(f"Successfully deleted chemical: {selected_chemical}")
                        st.session_state.confirm_delete = None
                        st.experimental_rerun()
                    else:
                        st.error(f"Failed to delete chemical: {selected_chemical}")


def render_import_export_tab():
    """Render the import/export tab"""
    st.subheader("Import/Export Chemicals")
    
    # Create tabs for import and export
    import_tab, export_tab = st.tabs(["Import", "Export"])
    
    with import_tab:
        st.write("Import chemicals from Excel or CSV file")
        
        # File uploader
        uploaded_file = st.file_uploader("Choose a file", type=["xlsx", "csv"])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.write("Preview of data to be imported:")
                st.dataframe(df.head())
                
                required_columns = ['name']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"Missing required columns: {', '.join(missing_columns)}")
                else:
                    if st.button("Import Chemicals"):
                        # Import the chemicals
                        success_count, error_count = ChemicalDAO.import_chemicals_from_dataframe(df)
                        
                        if success_count > 0:
                            st.success(f"Successfully imported {success_count} chemicals")
                        
                        if error_count > 0:
                            st.warning(f"Failed to import {error_count} chemicals")
            
            except Exception as e:
                st.error(f"Error importing file: {e}")
    
    with export_tab:
        st.write("Export chemicals to Excel or CSV file")
        
        # Get all chemicals from the database
        chemicals = ChemicalDAO.get_all_chemicals()
        
        if not chemicals:
            st.info("No chemicals to export")
        else:
            # Convert to DataFrame for export
            df = pd.DataFrame(chemicals)
            
            # Exclude ID column for export
            if 'id' in df.columns:
                df = df.drop(columns=['id'])
            
            # Convert properties from JSON string to dict
            if 'properties' in df.columns:
                try:
                    import json
                    df['properties'] = df['properties'].apply(lambda x: json.loads(x) if x else {})
                except Exception as e:
                    st.error(f"Error parsing properties: {e}")
                    df['properties'] = '{}'
            
            # Export options
            export_format = st.radio("Select export format", ["Excel", "CSV"])
            
            if st.button("Export Chemicals"):
                try:
                    if export_format == "Excel":
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, index=False, sheet_name='Chemicals')
                        
                        data = output.getvalue()
                        st.download_button(
                            label="Download Excel file",
                            data=data,
                            file_name="chemicals.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:  # CSV
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV file",
                            data=csv,
                            file_name="chemicals.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"Error exporting chemicals: {e}")


if __name__ == "__main__":
    render_chemical_database_page() 