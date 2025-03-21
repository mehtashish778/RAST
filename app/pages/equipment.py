# -*- coding: utf-8 -*-
"""
HAZOP Analysis Tool - Equipment Database Page
"""
import streamlit as st
import pandas as pd
import json
import io
from utils.data_access import EquipmentDAO


def render_equipment_database_page():
    """
    Render the equipment database management page
    """
    st.header("Equipment Database")
    
    # Create tabs for different actions
    tab1, tab2, tab3, tab4 = st.tabs(["View Equipment", "Add Equipment", "Edit Equipment", "Import/Export"])
    
    with tab1:
        render_view_equipment_tab()
    
    with tab2:
        render_add_equipment_tab()
    
    with tab3:
        render_edit_equipment_tab()
    
    with tab4:
        render_import_export_tab()


def render_view_equipment_tab():
    """Render the view equipment tab"""
    st.subheader("Equipment Database")
    
    # Get all equipment from the database
    equipment_list = EquipmentDAO.get_all_equipment()
    
    if not equipment_list:
        st.info("No equipment found in the database. Add some equipment to get started.")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame(equipment_list)
    
    # Convert attributes from JSON string to dict
    if 'attributes' in df.columns:
        try:
            df['attributes'] = df['attributes'].apply(lambda x: json.loads(x) if x else {})
        except Exception as e:
            st.error(f"Error parsing attributes: {e}")
            df['attributes'] = '{}'
    
    # Display the equipment in a table
    st.dataframe(df)
    
    # Allow selecting an equipment for details
    if len(equipment_list) > 0:
        equipment_tags = [e['tag'] for e in equipment_list]
        selected_equipment = st.selectbox("Select equipment for details", equipment_tags)
        
        if selected_equipment:
            # Find the selected equipment
            equipment = next((e for e in equipment_list if e['tag'] == selected_equipment), None)
            if equipment:
                st.subheader(f"Details for {equipment['tag']} - {equipment['name']}")
                
                # Create columns for better layout
                col1, col2 = st.columns(2)
                
                # Display basic information in first column
                with col1:
                    st.write("**Basic Information**")
                    st.write(f"Tag: {equipment.get('tag', 'N/A')}")
                    st.write(f"Name: {equipment.get('name', 'N/A')}")
                    st.write(f"Type: {equipment.get('equipment_type', 'N/A')}")
                
                # Parse and display attributes
                with col2:
                    st.write("**Attributes**")
                    try:
                        attributes = json.loads(equipment.get('attributes', '{}'))
                        for key, value in attributes.items():
                            st.write(f"{key.replace('_', ' ').title()}: {value}")
                    except Exception as e:
                        st.error(f"Error parsing attributes: {e}")


def render_add_equipment_tab():
    """Render the add equipment tab"""
    st.subheader("Add New Equipment")
    
    with st.form("add_equipment_form"):
        # Basic information
        st.write("**Basic Information**")
        tag = st.text_input("Equipment Tag*", help="Unique identifier for the equipment (e.g., P-101)")
        name = st.text_input("Equipment Name*", help="Descriptive name for the equipment")
        
        # Equipment type selection
        equipment_type = st.selectbox(
            "Equipment Type*",
            ["Vessel", "Pump", "Heat Exchanger", "Pipe"],
            help="Type of equipment"
        )
        
        # Attributes based on equipment type
        st.write("**Equipment Attributes**")
        attributes = {}
        
        if equipment_type == "Vessel":
            col1, col2 = st.columns(2)
            with col1:
                volume = st.number_input("Volume (m³)", min_value=0.0, step=0.1)
                design_pressure = st.number_input("Design Pressure (bar)", min_value=0.0, step=0.1)
            with col2:
                design_temp = st.number_input("Design Temperature (°C)", step=0.1)
                material = st.text_input("Material of Construction")
            
            attributes = {
                "volume": volume,
                "design_pressure": design_pressure,
                "design_temperature": design_temp,
                "material": material
            }
        
        elif equipment_type == "Pump":
            col1, col2 = st.columns(2)
            with col1:
                flow_rate = st.number_input("Flow Rate (m³/h)", min_value=0.0, step=0.1)
                discharge_pressure = st.number_input("Discharge Pressure (bar)", min_value=0.0, step=0.1)
            with col2:
                motor_power = st.number_input("Motor Power (kW)", min_value=0.0, step=0.1)
                seal_type = st.text_input("Seal Type")
            
            attributes = {
                "flow_rate": flow_rate,
                "discharge_pressure": discharge_pressure,
                "motor_power": motor_power,
                "seal_type": seal_type
            }
        
        elif equipment_type == "Heat Exchanger":
            col1, col2 = st.columns(2)
            with col1:
                heat_duty = st.number_input("Heat Duty (MW)", min_value=0.0, step=0.1)
                tube_material = st.text_input("Tube Material")
            with col2:
                shell_material = st.text_input("Shell Material")
                design_pressure = st.number_input("Design Pressure (bar)", min_value=0.0, step=0.1)
                design_temp = st.number_input("Design Temperature (°C)", step=0.1)
            
            attributes = {
                "heat_duty": heat_duty,
                "tube_material": tube_material,
                "shell_material": shell_material,
                "design_pressure": design_pressure,
                "design_temperature": design_temp
            }
        
        elif equipment_type == "Pipe":
            col1, col2 = st.columns(2)
            with col1:
                diameter = st.number_input("Diameter (inches)", min_value=0.0, step=0.1)
                material = st.text_input("Material")
            with col2:
                design_pressure = st.number_input("Design Pressure (bar)", min_value=0.0, step=0.1)
                design_temp = st.number_input("Design Temperature (°C)", step=0.1)
                insulation = st.checkbox("Insulated")
            
            attributes = {
                "diameter": diameter,
                "material": material,
                "design_pressure": design_pressure,
                "design_temperature": design_temp,
                "insulation": insulation
            }
        
        # Submit button
        submitted = st.form_submit_button("Add Equipment")
        
        if submitted:
            if not tag or not name:
                st.error("Equipment Tag and Name are required")
            else:
                # Prepare data for database
                equipment_data = {
                    'tag': tag,
                    'name': name,
                    'equipment_type': equipment_type,
                    'attributes': json.dumps(attributes)
                }
                
                # Add the equipment to the database
                if EquipmentDAO.add_or_update_equipment(equipment_data):
                    st.success(f"Successfully added equipment: {tag} - {name}")
                else:
                    st.error("Failed to add equipment to the database")


def render_edit_equipment_tab():
    """Render the edit equipment tab"""
    st.subheader("Edit Equipment")
    
    # Get all equipment from the database
    equipment_list = EquipmentDAO.get_all_equipment()
    
    if not equipment_list:
        st.info("No equipment found in the database. Add some equipment first.")
        return
    
    # Allow selecting an equipment to edit
    equipment_tags = [e['tag'] for e in equipment_list]
    selected_equipment = st.selectbox("Select equipment to edit", equipment_tags)
    
    if selected_equipment:
        # Get the selected equipment
        equipment = EquipmentDAO.get_equipment_by_tag(selected_equipment)
        
        if equipment:
            # Parse attributes
            try:
                attributes = json.loads(equipment.get('attributes', '{}'))
            except:
                attributes = {}
            
            # Create form for editing
            with st.form("edit_equipment_form"):
                # Basic information
                st.write("**Basic Information**")
                tag = st.text_input("Equipment Tag*", value=equipment.get('tag', ''), disabled=True)
                name = st.text_input("Equipment Name*", value=equipment.get('name', ''))
                equipment_type = st.text_input("Equipment Type", value=equipment.get('equipment_type', ''), disabled=True)
                
                # Attributes based on equipment type
                st.write("**Equipment Attributes**")
                new_attributes = {}
                
                if equipment_type == "Vessel":
                    col1, col2 = st.columns(2)
                    with col1:
                        volume = st.number_input("Volume (m³)", 
                                               value=float(attributes.get('volume', 0) or 0),
                                               min_value=0.0, step=0.1)
                        design_pressure = st.number_input("Design Pressure (bar)", 
                                                       value=float(attributes.get('design_pressure', 0) or 0),
                                                       min_value=0.0, step=0.1)
                    with col2:
                        design_temp = st.number_input("Design Temperature (°C)", 
                                                   value=float(attributes.get('design_temperature', 0) or 0),
                                                   step=0.1)
                        material = st.text_input("Material of Construction", 
                                              value=attributes.get('material', ''))
                    
                    new_attributes = {
                        "volume": volume,
                        "design_pressure": design_pressure,
                        "design_temperature": design_temp,
                        "material": material
                    }
                
                elif equipment_type == "Pump":
                    col1, col2 = st.columns(2)
                    with col1:
                        flow_rate = st.number_input("Flow Rate (m³/h)", 
                                                value=float(attributes.get('flow_rate', 0) or 0),
                                                min_value=0.0, step=0.1)
                        discharge_pressure = st.number_input("Discharge Pressure (bar)", 
                                                         value=float(attributes.get('discharge_pressure', 0) or 0),
                                                         min_value=0.0, step=0.1)
                    with col2:
                        motor_power = st.number_input("Motor Power (kW)", 
                                                 value=float(attributes.get('motor_power', 0) or 0),
                                                 min_value=0.0, step=0.1)
                        seal_type = st.text_input("Seal Type", 
                                                value=attributes.get('seal_type', ''))
                    
                    new_attributes = {
                        "flow_rate": flow_rate,
                        "discharge_pressure": discharge_pressure,
                        "motor_power": motor_power,
                        "seal_type": seal_type
                    }
                
                elif equipment_type == "Heat Exchanger":
                    col1, col2 = st.columns(2)
                    with col1:
                        heat_duty = st.number_input("Heat Duty (MW)", 
                                                value=float(attributes.get('heat_duty', 0) or 0),
                                                min_value=0.0, step=0.1)
                        tube_material = st.text_input("Tube Material", 
                                                   value=attributes.get('tube_material', ''))
                    with col2:
                        shell_material = st.text_input("Shell Material", 
                                                    value=attributes.get('shell_material', ''))
                        design_pressure = st.number_input("Design Pressure (bar)", 
                                                       value=float(attributes.get('design_pressure', 0) or 0),
                                                       min_value=0.0, step=0.1)
                        design_temp = st.number_input("Design Temperature (°C)", 
                                                   value=float(attributes.get('design_temperature', 0) or 0),
                                                   step=0.1)
                    
                    new_attributes = {
                        "heat_duty": heat_duty,
                        "tube_material": tube_material,
                        "shell_material": shell_material,
                        "design_pressure": design_pressure,
                        "design_temperature": design_temp
                    }
                
                elif equipment_type == "Pipe":
                    col1, col2 = st.columns(2)
                    with col1:
                        diameter = st.number_input("Diameter (inches)", 
                                               value=float(attributes.get('diameter', 0) or 0),
                                               min_value=0.0, step=0.1)
                        material = st.text_input("Material", 
                                              value=attributes.get('material', ''))
                    with col2:
                        design_pressure = st.number_input("Design Pressure (bar)", 
                                                       value=float(attributes.get('design_pressure', 0) or 0),
                                                       min_value=0.0, step=0.1)
                        design_temp = st.number_input("Design Temperature (°C)", 
                                                   value=float(attributes.get('design_temperature', 0) or 0),
                                                   step=0.1)
                        insulation = st.checkbox("Insulated", 
                                              value=bool(attributes.get('insulation', False)))
                    
                    new_attributes = {
                        "diameter": diameter,
                        "material": material,
                        "design_pressure": design_pressure,
                        "design_temperature": design_temp,
                        "insulation": insulation
                    }
                
                # Submit button
                submitted = st.form_submit_button("Update Equipment")
                
                if submitted:
                    if not name:
                        st.error("Equipment Name is required")
                    else:
                        # Prepare data for database
                        equipment_data = {
                            'tag': tag,
                            'name': name,
                            'equipment_type': equipment_type,
                            'attributes': json.dumps(new_attributes)
                        }
                        
                        # Update the equipment in the database
                        if EquipmentDAO.add_or_update_equipment(equipment_data):
                            st.success(f"Successfully updated equipment: {tag} - {name}")
                        else:
                            st.error("Failed to update equipment in the database")


def render_import_export_tab():
    """Render the import/export tab"""
    st.subheader("Import/Export Equipment Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Export Equipment Data**")
        if st.button("Export to CSV"):
            equipment_list = EquipmentDAO.get_all_equipment()
            if equipment_list:
                df = pd.DataFrame(equipment_list)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="equipment_export.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No equipment data to export")
    
    with col2:
        st.write("**Import Equipment Data**")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                if st.button("Import Data"):
                    success = EquipmentDAO.import_equipment_from_dataframe(df)
                    if success:
                        st.success("Equipment data imported successfully")
                    else:
                        st.error("Failed to import equipment data")
            except Exception as e:
                st.error(f"Error processing CSV file: {e}")


if __name__ == "__main__":
    render_equipment_database_page() 