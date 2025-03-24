# -*- coding: utf-8 -*-
"""
HAZOP Analysis Tool - Layer of Protection Analysis (LOPA) Worksheet
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

# Add the application directory to path for imports
app_dir = Path(__file__).parent.parent.absolute()
if str(app_dir) not in sys.path:
    sys.path.append(str(app_dir))

from core.ipl import (
    IPL, IPLType, IPLCategory, SIL, 
    LOPACalculator, LOPAScenario
)
from utils.database import get_db_manager
from utils.data_access import ScenarioDAO

def render_lopa_page():
    """Render the LOPA worksheet page"""
    st.title("Layer of Protection Analysis (LOPA)")
    
    # Add tabs for the different aspects of LOPA
    tabs = st.tabs(["LOPA Scenarios", "IPL Management", "SIF Assessment"])
    
    with tabs[0]:
        render_lopa_scenarios_tab()
    
    with tabs[1]:
        render_ipl_management_tab()
    
    with tabs[2]:
        render_sif_assessment_tab()

def render_lopa_scenarios_tab():
    """Render the LOPA scenarios tab"""
    st.header("LOPA Scenarios")
    
    # Load existing scenarios if available
    hazop_scenarios = ScenarioDAO.get_all_scenarios()
    
    # UI for selecting a HAZOP scenario to analyze
    st.subheader("Select HAZOP Scenario")
    
    if not hazop_scenarios:
        st.warning("No HAZOP scenarios available. Create scenarios in the Scenarios page first.")
        return
    
    scenario_options = {f"{s['id']}: {s['deviation'][:50]}...": s for s in hazop_scenarios}
    selected_scenario_key = st.selectbox(
        "Select a scenario to analyze:",
        options=list(scenario_options.keys()),
        index=0
    )
    
    if selected_scenario_key:
        selected_scenario = scenario_options[selected_scenario_key]
        
        # Display selected scenario details
        with st.expander("Scenario Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**ID:** {selected_scenario['id']}")
                st.write(f"**Node:** {selected_scenario.get('node', 'Not specified')}")
                st.write(f"**Deviation:** {selected_scenario.get('deviation', 'Not specified')}")
            with col2:
                st.write(f"**Causes:** {selected_scenario.get('causes', 'Not specified')}")
                st.write(f"**Consequences:** {selected_scenario.get('consequences', 'Not specified')}")
                st.write(f"**Risk Category:** {selected_scenario.get('risk_category', 'Not specified')}")
        
        # LOPA scenario creation/editing
        st.subheader("LOPA Scenario Definition")
        
        # Check if LOPA scenario already exists for this HAZOP scenario
        # In a real implementation, this would query the database
        
        # For demonstration, create a new LOPA scenario
        with st.form("lopa_scenario_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                initiating_event = st.text_input(
                    "Initiating Event",
                    value=selected_scenario.get('causes', 'Equipment failure')
                )
                
                initiating_freq = st.number_input(
                    "Initiating Event Frequency (per year)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.1,
                    format="%.4f",
                    help="Frequency of the initiating event in events per year"
                )
                
                initiating_basis = st.text_area(
                    "Frequency Basis",
                    value="Industry standard values",
                    help="Source or basis for the initiating event frequency"
                )
            
            with col2:
                consequence_desc = st.text_area(
                    "Consequence Description",
                    value=selected_scenario.get('consequences', 'Potential release')
                )
                
                consequence_category = st.selectbox(
                    "Consequence Category",
                    options=["Personnel Safety", "Environmental", "Asset Damage", "Business Interruption", "Reputation"],
                    index=0
                )
                
                consequence_severity = st.slider(
                    "Consequence Severity",
                    min_value=1,
                    max_value=5,
                    value=3,
                    help="Severity level from 1 (minor) to 5 (catastrophic)"
                )
                
                target_frequency = st.number_input(
                    "Target Mitigated Frequency (per year)",
                    min_value=1e-7,
                    max_value=1.0,
                    value=1e-5,
                    format="%.7f",
                    help="Target frequency after applying protection layers"
                )
            
            notes = st.text_area(
                "Notes",
                value="",
                help="Additional notes or comments about this LOPA scenario"
            )
            
            save_button = st.form_submit_button("Save LOPA Scenario")
            
            if save_button:
                # In a real implementation, save the scenario to the database
                st.success("LOPA scenario saved successfully!")
                
                # Create a temporary LOPA scenario object for demonstration
                lopa_scenario = LOPAScenario(
                    id=None,
                    scenario_id=selected_scenario['id'],
                    description=f"LOPA for {selected_scenario['deviation'][:50]}...",
                    node_id=selected_scenario.get('equipment_id'),
                    consequence_description=consequence_desc,
                    consequence_category=consequence_category,
                    consequence_severity=consequence_severity,
                    initiating_event=initiating_event,
                    initiating_event_frequency=initiating_freq,
                    initiating_event_basis=initiating_basis,
                    ipls=[],  # Empty list for now
                    conditional_modifiers={},
                    target_mitigated_frequency=target_frequency,
                    notes=notes
                )
                
                # Store in session state for use in other tabs
                if 'lopa_scenarios' not in st.session_state:
                    st.session_state.lopa_scenarios = {}
                
                st.session_state.lopa_scenarios[selected_scenario['id']] = lopa_scenario
        
        # Display IPL section if scenario exists
        if 'lopa_scenarios' in st.session_state and selected_scenario['id'] in st.session_state.lopa_scenarios:
            lopa_scenario = st.session_state.lopa_scenarios[selected_scenario['id']]
            
            st.subheader("Independent Protection Layers (IPLs)")
            
            # Add IPL button
            if st.button("Add New IPL", key="add_ipl_button"):
                st.session_state.show_add_ipl = True
            
            # IPL adding interface
            if st.session_state.get('show_add_ipl', False):
                with st.form("add_ipl_form"):
                    st.subheader("Add New IPL")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        ipl_name = st.text_input(
                            "IPL Name",
                            value="New IPL"
                        )
                        
                        ipl_description = st.text_area(
                            "Description",
                            value="Description of protection layer"
                        )
                        
                        ipl_type = st.selectbox(
                            "IPL Type",
                            options=[t.value for t in IPLType],
                            index=0
                        )
                        
                        ipl_category = st.selectbox(
                            "Category",
                            options=[c.value for c in IPLCategory],
                            index=0
                        )
                    
                    with col2:
                        # Get recommended PFD based on selected type
                        selected_type = next((t for t in IPLType if t.value == ipl_type), IPLType.OTHER)
                        recommended_pfd = IPL.recommended_pfd(selected_type)
                        
                        pfd = st.number_input(
                            "Probability of Failure on Demand (PFD)",
                            min_value=0.0,
                            max_value=1.0,
                            value=recommended_pfd,
                            format="%.4f",
                            help=f"Recommended PFD for {ipl_type}: {recommended_pfd}"
                        )
                        
                        # Calculate RRF (Risk Reduction Factor)
                        rrf = 1.0 / pfd if pfd > 0 else float('inf')
                        st.metric("Risk Reduction Factor (RRF)", f"{rrf:.1f}")
                        
                        is_enabled = st.checkbox(
                            "Enable IPL",
                            value=True,
                            help="Include this IPL in LOPA calculations"
                        )
                        
                        sil_options = [f"SIL {s.value}" if s.value > 0 else "None" for s in SIL]
                        sil_index = 0
                        
                        # Recommend SIL based on PFD
                        if pfd <= 0.00001:
                            sil_index = 4  # SIL 4
                        elif pfd <= 0.0001:
                            sil_index = 3  # SIL 3
                        elif pfd <= 0.001:
                            sil_index = 2  # SIL 2
                        elif pfd <= 0.01:
                            sil_index = 1  # SIL 1
                        
                        sil_value = st.selectbox(
                            "Safety Integrity Level (SIL)",
                            options=sil_options,
                            index=sil_index
                        )
                    
                    add_ipl_button = st.form_submit_button("Add IPL")
                    
                    if add_ipl_button:
                        # Create new IPL object
                        new_ipl = IPL(
                            name=ipl_name,
                            description=ipl_description,
                            ipl_type=ipl_type,
                            category=ipl_category,
                            pfd=pfd,
                            is_enabled=is_enabled,
                            sil=SIL(sil_index),  # Convert from index to SIL enum
                            scenario_id=selected_scenario['id']
                        )
                        
                        # Add to scenario
                        lopa_scenario.ipls.append(new_ipl)
                        st.session_state.show_add_ipl = False
                        st.success("IPL added successfully!")
                        st.rerun()
            
            # Display existing IPLs
            if lopa_scenario.ipls:
                display_ipls_table(lopa_scenario.ipls)
                
                # Calculate and display results
                st.subheader("LOPA Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Initiating Event Frequency",
                        f"{lopa_scenario.initiating_event_frequency:.4e} per year"
                    )
                
                with col2:
                    st.metric(
                        "Mitigated Frequency",
                        f"{lopa_scenario.mitigated_frequency:.4e} per year"
                    )
                
                with col3:
                    st.metric(
                        "Risk Reduction Factor",
                        f"{lopa_scenario.risk_reduction_factor:.1f}"
                    )
                
                # Display traffic light for target
                st.subheader("Target Assessment")
                
                if lopa_scenario.meets_target:
                    st.success(f"✅ Target frequency of {lopa_scenario.target_mitigated_frequency:.4e} per year is met.")
                else:
                    st.error(f"❌ Target frequency of {lopa_scenario.target_mitigated_frequency:.4e} per year is NOT met.")
                    st.warning("Consider adding additional IPLs or improving existing ones.")
                
                # Add conditional modifiers
                st.subheader("Conditional Modifiers")
                
                with st.expander("Add Conditional Modifier", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        modifier_name = st.text_input("Modifier Name", value="Ignition Probability")
                    
                    with col2:
                        modifier_value = st.slider(
                            "Probability",
                            min_value=0.0,
                            max_value=1.0,
                            value=0.1,
                            step=0.01,
                            format="%.2f"
                        )
                    
                    if st.button("Add Modifier"):
                        lopa_scenario.conditional_modifiers[modifier_name] = modifier_value
                        st.success(f"Added {modifier_name} with probability {modifier_value}")
                        st.rerun()
                
                # Display modifiers table
                if lopa_scenario.conditional_modifiers:
                    modifiers_df = pd.DataFrame([
                        {"Modifier": k, "Probability": v}
                        for k, v in lopa_scenario.conditional_modifiers.items()
                    ])
                    st.table(modifiers_df)

def display_ipls_table(ipls: List[IPL]):
    """Display IPLs in a table format"""
    if not ipls:
        st.info("No IPLs defined for this scenario yet.")
        return
    
    # Convert IPLs to DataFrame for display
    ipls_data = []
    for ipl in ipls:
        ipls_data.append({
            "Name": ipl.name,
            "Type": ipl.ipl_type.value if hasattr(ipl.ipl_type, 'value') else str(ipl.ipl_type),
            "PFD": f"{ipl.pfd:.4f}",
            "RRF": f"{ipl.rrF:.1f}",
            "Status": "Enabled" if ipl.is_enabled else "Disabled",
            "SIL": f"SIL {ipl.sil.value}" if ipl.sil and hasattr(ipl.sil, 'value') else "None"
        })
    
    ipls_df = pd.DataFrame(ipls_data)
    st.dataframe(ipls_df)
    
    # Show total risk reduction
    total_rrf = 1.0
    for ipl in ipls:
        if ipl.is_enabled:
            total_rrf *= ipl.rrF
    
    st.metric("Combined Risk Reduction Factor", f"{total_rrf:.1f}")

def render_ipl_management_tab():
    """Render the IPL management tab"""
    st.header("IPL Management")
    
    # Display IPL library
    st.subheader("IPL Library")
    
    # Create a table of standard IPLs with their typical PFD values
    ipl_library = []
    
    for ipl_type in IPLType:
        pfd = IPL.recommended_pfd(ipl_type)
        rrf = 1.0 / pfd if pfd > 0 else float('inf')
        
        # Determine typical SIL level
        sil_level = "None"
        if pfd <= 0.00001:
            sil_level = "SIL 4"
        elif pfd <= 0.0001:
            sil_level = "SIL 3"
        elif pfd <= 0.001:
            sil_level = "SIL 2"
        elif pfd <= 0.01:
            sil_level = "SIL 1"
        
        ipl_library.append({
            "IPL Type": ipl_type.value,
            "Typical PFD": f"{pfd:.4f}",
            "Typical RRF": f"{rrf:.1f}",
            "SIL Equivalent": sil_level,
            "Category": "Prevention" if ipl_type in [IPLType.BPCS, IPLType.SIS, IPLType.MECHANICAL] else "Mitigation"
        })
    
    st.table(pd.DataFrame(ipl_library))
    
    # IPL design guidance
    with st.expander("IPL Design Guidance", expanded=False):
        st.markdown("""
        ### IPL Design Principles
        
        Independent Protection Layers must meet these criteria:
        
        1. **Specificity**: The IPL is designed to prevent or mitigate the specific consequence of concern.
        2. **Independence**: The IPL is independent of the initiating event and all other layers of protection.
        3. **Dependability**: The IPL can be relied upon to perform its function.
        4. **Auditability**: The IPL is designed to facilitate confirmation of the protective functions.
        
        ### IPL Documentation Requirements
        
        For each IPL, document:
        - Design basis and assumptions
        - Testing and maintenance requirements
        - Proof test procedures and frequencies
        - Failure history and common cause failures
        - Management of change procedures
        """)

def render_sif_assessment_tab():
    """Render the SIF assessment tab"""
    st.header("Safety Instrumented Function (SIF) Assessment")
    
    # SIF assessment guidance
    st.info("Select a scenario in the LOPA tab to perform SIF assessment.")
    
    # Only show SIF assessment if scenario is selected
    if 'lopa_scenarios' in st.session_state and st.session_state.lopa_scenarios:
        # For simplicity, use the first scenario in the session state
        scenario_id = list(st.session_state.lopa_scenarios.keys())[0]
        lopa_scenario = st.session_state.lopa_scenarios[scenario_id]
        
        st.subheader(f"SIF Assessment for Scenario {scenario_id}")
        
        # Calculate required SIL
        st.subheader("SIL Determination")
        
        # Extract non-SIS IPLs for calculation
        non_sis_ipls = [ipl for ipl in lopa_scenario.ipls 
                        if ipl.is_enabled and ipl.ipl_type != IPLType.SIS]
        
        required_sil, required_pfd = LOPACalculator.calculate_required_sil(
            lopa_scenario.initiating_event_frequency,
            lopa_scenario.target_mitigated_frequency,
            non_sis_ipls,
            list(lopa_scenario.conditional_modifiers.values()) if lopa_scenario.conditional_modifiers else None
        )
        
        # Display required SIL
        st.markdown(f"### Required Safety Integrity Level: **SIL {required_sil.value}**")
        st.markdown(f"Required PFD: **{required_pfd:.5f}**")
        
        # SIL verification section
        st.subheader("SIF Architecture")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Sensor Subsystem")
            sensor_config = st.selectbox(
                "Sensor Configuration",
                options=["1oo1", "1oo2", "2oo2", "2oo3", "2oo4"],
                index=0,
                help="1oo1 = 1 out of 1 (single), 1oo2 = 1 out of 2 (redundant), etc."
            )
            
            sensor_pfd = st.number_input(
                "Sensor PFD",
                min_value=0.0,
                max_value=1.0,
                value=0.01,
                format="%.4f"
            )
        
        with col2:
            st.markdown("#### Logic Solver Subsystem")
            logic_config = st.selectbox(
                "Logic Solver Configuration",
                options=["1oo1", "1oo2", "2oo2", "2oo3"],
                index=0
            )
            
            logic_pfd = st.number_input(
                "Logic Solver PFD",
                min_value=0.0,
                max_value=1.0,
                value=0.001,
                format="%.4f"
            )
        
        with col3:
            st.markdown("#### Final Element Subsystem")
            fe_config = st.selectbox(
                "Final Element Configuration",
                options=["1oo1", "1oo2", "2oo2", "2oo3"],
                index=0
            )
            
            fe_pfd = st.number_input(
                "Final Element PFD",
                min_value=0.0,
                max_value=1.0,
                value=0.01,
                format="%.4f"
            )
        
        # Calculate overall PFD
        overall_pfd = sensor_pfd + logic_pfd + fe_pfd
        overall_rrf = 1.0 / overall_pfd if overall_pfd > 0 else float('inf')
        
        # Determine actual SIL level
        actual_sil = "None"
        if overall_pfd <= 0.00001:
            actual_sil = "SIL 4"
        elif overall_pfd <= 0.0001:
            actual_sil = "SIL 3"
        elif overall_pfd <= 0.001:
            actual_sil = "SIL 2"
        elif overall_pfd <= 0.01:
            actual_sil = "SIL 1"
        
        # Display results
        st.subheader("SIF Performance")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Overall PFD", f"{overall_pfd:.5f}")
        
        with col2:
            st.metric("Risk Reduction Factor", f"{overall_rrf:.1f}")
        
        with col3:
            st.metric("Achieved SIL", actual_sil)
        
        # Check if SIF meets requirements
        if overall_pfd <= required_pfd:
            st.success(f"✅ SIF design meets the required SIL {required_sil.value}")
        else:
            st.error(f"❌ SIF design does NOT meet the required SIL {required_sil.value}")
            st.warning("Consider improving sensor, logic solver, or final element reliability, or adding redundancy.")
        
        # SIL verification documentation
        with st.expander("SIL Verification Documentation", expanded=False):
            st.markdown("""
            ### SIL Verification Documentation
            
            Complete SIL verification requires documentation of:
            
            1. **Safety Requirements Specification (SRS)**
               - Safety function description
               - Required SIL
               - Process safety time
               - Response time requirements
               - Safe state definition
            
            2. **Hardware Fault Tolerance (HFT)**
               - Architectural constraints
               - Redundancy requirements
               - Common cause failure analysis
            
            3. **Proof Test Intervals**
               - Test procedures
               - Test coverage
               - Test frequency
            
            4. **Systematic Capability**
               - Development process assessment
               - Quality management
               - Functional safety management
            """)

# Initialize session state variables on first run
if 'show_add_ipl' not in st.session_state:
    st.session_state.show_add_ipl = False

if 'lopa_scenarios' not in st.session_state:
    st.session_state.lopa_scenarios = {} 