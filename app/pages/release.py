# -*- coding: utf-8 -*-
"""
HAZOP Analysis Tool - Release Rate Calculation Page
Provides a Streamlit interface for various release rate calculations
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import json
import os
from typing import Dict, List, Any, Tuple

# Fix the import to use a relative path
import sys
from pathlib import Path

# Add parent directory to path (just in case)
sys.path.append(str(Path(__file__).parent.parent.parent))

# Use relative import
from core.release import ReleaseCalculator, FluidPhase, ReleaseType
from utils.data_access import ChemicalDAO


def render_release_calculation_page():
    """
    Render the release rate calculation page
    """
    st.title("Release Rate Calculations")
    st.markdown("""
    This tool calculates release rates for various scenarios encountered in process safety analysis,
    including leak through holes, pipe segments, and flange connections. 
    
    Select the release scenario type and enter the required parameters to calculate the release rates.
    """)
    
    # Create tabs for different release types
    release_tabs = st.tabs([
        "Liquid Release",
        "Gas Release",
        "Two-Phase Release",
        "Pipe Release",
        "Flange Leak"
    ])
    
    # LIQUID RELEASE TAB
    with release_tabs[0]:
        render_liquid_release_tab()
    
    # GAS RELEASE TAB
    with release_tabs[1]:
        render_gas_release_tab()
    
    # TWO-PHASE RELEASE TAB
    with release_tabs[2]:
        render_two_phase_release_tab()
    
    # PIPE RELEASE TAB
    with release_tabs[3]:
        render_pipe_release_tab()
    
    # FLANGE LEAK TAB
    with release_tabs[4]:
        render_flange_leak_tab()


def render_liquid_release_tab():
    """
    Render the liquid release rate calculation tab
    """
    st.header("Liquid Release Rate Calculation")
    st.markdown("""
    Calculate the release rate of a liquid through a hole or orifice using Bernoulli's equation.
    """)
    
    # Create input form
    with st.form("liquid_release_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            hole_diameter = st.number_input(
                "Hole Diameter (mm)",
                min_value=0.1,
                max_value=1000.0,
                value=10.0,
                step=1.0,
                help="Diameter of the hole or orifice through which the liquid is released"
            )
            
            pressure_differential = st.number_input(
                "Pressure Differential (kPa)",
                min_value=0.0,
                max_value=50000.0,
                value=500.0,
                step=10.0,
                help="Pressure difference between inside and outside of the container"
            )
            
            density = st.number_input(
                "Liquid Density (kg/m³)",
                min_value=1.0,
                max_value=20000.0,
                value=1000.0,
                step=10.0,
                help="Density of the liquid"
            )
        
        with col2:
            height_differential = st.number_input(
                "Height Differential (m)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                help="Height difference between liquid level and hole"
            )
            
            discharge_coefficient = st.number_input(
                "Discharge Coefficient",
                min_value=0.1,
                max_value=1.0,
                value=0.61,
                step=0.01,
                help="Coefficient accounting for viscous effects and turbulence"
            )
            
            inventory = st.number_input(
                "Total Inventory (kg)",
                min_value=0.0,
                max_value=1000000.0,
                value=1000.0,
                step=100.0,
                help="Total amount of liquid in the container"
            )
        
        # Submit button
        submitted = st.form_submit_button("Calculate")
    
    # Calculate and display results when form is submitted
    if submitted:
        # Calculate release rate
        results = ReleaseCalculator.liquid_release_rate(
            hole_diameter, pressure_differential, density,
            height_differential, discharge_coefficient
        )
        
        # Calculate release duration and total quantity
        release_duration = ReleaseCalculator.calculate_release_duration(
            inventory, results["mass_flow_rate_kgs"]
        )
        
        # Display results
        st.subheader("Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Mass Flow Rate", f"{results['mass_flow_rate_kgs']:.3f} kg/s")
            st.metric("Volumetric Flow Rate", f"{results['volumetric_flow_rate_m3s'] * 3600:.1f} m³/h")
            st.metric("Exit Velocity", f"{results['velocity_ms']:.1f} m/s")
        
        with col2:
            st.metric("Hole Area", f"{results['hole_area_m2'] * 1e6:.2f} mm²")
            if release_duration < 3600:
                st.metric("Release Duration", f"{release_duration:.1f} seconds")
            else:
                st.metric("Release Duration", f"{release_duration / 60:.1f} minutes")
            total_quantity = results["mass_flow_rate_kgs"] * min(release_duration, 3600)
            st.metric("Quantity Released in 1 hour", f"{total_quantity:.1f} kg")
        
        # Plot Flow Rate vs Hole Size
        st.subheader("Sensitivity Analysis")
        
        hole_sizes = np.linspace(1, hole_diameter * 3, 20)
        flow_rates = []
        
        for size in hole_sizes:
            result = ReleaseCalculator.liquid_release_rate(
                size, pressure_differential, density,
                height_differential, discharge_coefficient
            )
            flow_rates.append(result["mass_flow_rate_kgs"])
        
        fig = px.line(
            x=hole_sizes,
            y=flow_rates,
            labels={"x": "Hole Diameter (mm)", "y": "Mass Flow Rate (kg/s)"},
            title="Mass Flow Rate vs. Hole Size"
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_gas_release_tab():
    """
    Render the gas release rate calculation tab
    """
    st.header("Gas Release Rate Calculation")
    st.markdown("""
    Calculate the release rate of a gas through a hole or orifice, accounting for choked flow conditions.
    """)
    
    # Get chemical data for molecular weight and specific heat ratio
    chemicals = ChemicalDAO.get_all_chemicals()
    chemical_options = ["Select Chemical"] + [c['name'] for c in chemicals if c.get('phase', '').lower() == 'gas']
    
    # Use columns for layout
    col1, col2 = st.columns(2)
    
    with col1:
        selected_chemical = st.selectbox(
            "Chemical:",
            options=chemical_options,
            help="Select a chemical to automatically populate properties"
        )
    
    # Initialize properties
    molecular_weight = 0.0
    specific_heat_ratio = 1.4  # Default for diatomic gases
    
    # Get chemical properties if selected
    if selected_chemical != "Select Chemical":
        chemical = ChemicalDAO.get_chemical_by_name(selected_chemical)
        if chemical:
            if 'molecular_weight' in chemical and chemical['molecular_weight']:
                molecular_weight = float(chemical['molecular_weight'])
            
            if 'properties' in chemical and chemical['properties']:
                try:
                    props = json.loads(chemical['properties']) if isinstance(chemical['properties'], str) else chemical['properties']
                    if 'specific_heat_ratio' in props and props['specific_heat_ratio']:
                        specific_heat_ratio = float(props['specific_heat_ratio'])
                except:
                    pass
    
    # Create input form
    with st.form("gas_release_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            hole_diameter = st.number_input(
                "Hole Diameter (mm)",
                min_value=0.1,
                max_value=1000.0,
                value=10.0,
                step=1.0,
                help="Diameter of the hole or orifice"
            )
            
            upstream_pressure = st.number_input(
                "Upstream Pressure (kPa)",
                min_value=0.0,
                max_value=50000.0,
                value=1000.0,
                step=10.0,
                help="Pressure inside the container"
            )
            
            downstream_pressure = st.number_input(
                "Downstream Pressure (kPa)",
                min_value=0.0,
                max_value=50000.0,
                value=101.3,
                step=10.0,
                help="Pressure outside the container (usually atmospheric)"
            )
        
        with col2:
            temperature = st.number_input(
                "Temperature (°C)",
                min_value=-273.0,
                max_value=1000.0,
                value=25.0,
                step=5.0,
                help="Gas temperature"
            )
            
            molecular_weight_input = st.number_input(
                "Molecular Weight (g/mol)",
                min_value=1.0,
                max_value=500.0,
                value=molecular_weight if molecular_weight > 0 else 28.97,
                step=1.0,
                help="Molecular weight of the gas"
            )
            
            specific_heat_ratio_input = st.number_input(
                "Specific Heat Ratio (Cp/Cv)",
                min_value=1.0,
                max_value=2.0,
                value=specific_heat_ratio,
                step=0.01,
                help="Ratio of specific heats at constant pressure and volume"
            )
            
            discharge_coefficient = st.number_input(
                "Discharge Coefficient",
                min_value=0.1,
                max_value=1.0,
                value=0.61,
                step=0.01,
                help="Coefficient accounting for viscous effects and turbulence"
            )
        
        # Submit button
        submitted = st.form_submit_button("Calculate")
    
    # Calculate and display results when form is submitted
    if submitted:
        # Convert temperature to Kelvin
        temperature_k = temperature + 273.15
        
        # Calculate release rate
        results = ReleaseCalculator.gas_release_rate(
            hole_diameter, upstream_pressure, downstream_pressure,
            temperature_k, molecular_weight_input, specific_heat_ratio_input,
            discharge_coefficient
        )
        
        # Display results
        st.subheader("Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Mass Flow Rate", f"{results['mass_flow_rate_kgs']:.3f} kg/s")
            st.metric("Volumetric Flow Rate (std)", f"{results['volumetric_flow_rate_std_m3s'] * 3600:.1f} Nm³/h")
            if results['is_choked']:
                st.metric("Flow Condition", "Choked (Sonic) Flow")
            else:
                st.metric("Flow Condition", "Subsonic Flow")
        
        with col2:
            st.metric("Hole Area", f"{results['hole_area_m2'] * 1e6:.2f} mm²")
            st.metric("Gas Density", f"{results['gas_density_kgm3']:.2f} kg/m³")
            st.metric("Pressure Ratio", f"{results['pressure_ratio']:.4f} (Critical: {results['critical_pressure_ratio']:.4f})")
        
        # Plot Flow Rate vs Pressure
        st.subheader("Sensitivity Analysis")
        
        pressures = np.linspace(downstream_pressure * 1.1, upstream_pressure * 1.5, 20)
        flow_rates = []
        
        for pressure in pressures:
            result = ReleaseCalculator.gas_release_rate(
                hole_diameter, pressure, downstream_pressure,
                temperature_k, molecular_weight_input, specific_heat_ratio_input,
                discharge_coefficient
            )
            flow_rates.append(result["mass_flow_rate_kgs"])
        
        fig = px.line(
            x=pressures,
            y=flow_rates,
            labels={"x": "Upstream Pressure (kPa)", "y": "Mass Flow Rate (kg/s)"},
            title="Mass Flow Rate vs. Upstream Pressure"
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_two_phase_release_tab():
    """
    Render the two-phase release rate calculation tab
    """
    st.header("Two-Phase Release Rate Calculation")
    st.markdown("""
    Calculate the release rate of a two-phase mixture (liquid and gas) using the homogeneous equilibrium model.
    """)
    
    # Create input form
    with st.form("two_phase_release_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            hole_diameter = st.number_input(
                "Hole Diameter (mm)",
                min_value=0.1,
                max_value=1000.0,
                value=10.0,
                step=1.0,
                help="Diameter of the hole or orifice"
            )
            
            upstream_pressure = st.number_input(
                "Upstream Pressure (kPa)",
                min_value=0.0,
                max_value=50000.0,
                value=1000.0,
                step=10.0,
                help="Pressure inside the container"
            )
            
            downstream_pressure = st.number_input(
                "Downstream Pressure (kPa)",
                min_value=0.0,
                max_value=50000.0,
                value=101.3,
                step=10.0,
                help="Pressure outside the container (usually atmospheric)"
            )
        
        with col2:
            temperature = st.number_input(
                "Temperature (°C)",
                min_value=-273.0,
                max_value=1000.0,
                value=25.0,
                step=5.0,
                help="Fluid temperature"
            )
            
            liquid_fraction = st.slider(
                "Liquid Mass Fraction",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.01,
                help="Mass fraction of liquid in the mixture (0 = all gas, 1 = all liquid)"
            )
            
            liquid_density = st.number_input(
                "Liquid Density (kg/m³)",
                min_value=1.0,
                max_value=20000.0,
                value=800.0,
                step=10.0,
                help="Density of the liquid phase"
            )
            
            vapor_density = st.number_input(
                "Vapor Density (kg/m³)",
                min_value=0.1,
                max_value=100.0,
                value=5.0,
                step=0.1,
                help="Density of the vapor phase"
            )
            
            discharge_coefficient = st.number_input(
                "Discharge Coefficient",
                min_value=0.1,
                max_value=1.0,
                value=0.61,
                step=0.01,
                help="Coefficient accounting for viscous effects and turbulence"
            )
        
        # Submit button
        submitted = st.form_submit_button("Calculate")
    
    # Calculate and display results when form is submitted
    if submitted:
        # Convert temperature to Kelvin
        temperature_k = temperature + 273.15
        
        # Calculate release rate
        results = ReleaseCalculator.two_phase_release_rate(
            hole_diameter, upstream_pressure, downstream_pressure,
            temperature_k, liquid_fraction, liquid_density,
            vapor_density, discharge_coefficient
        )
        
        # Display results
        st.subheader("Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Mass Flow Rate", f"{results['mass_flow_rate_kgs']:.3f} kg/s")
            st.metric("Liquid Mass Flow Rate", f"{results['liquid_mass_flow_rate_kgs']:.3f} kg/s")
            st.metric("Vapor Mass Flow Rate", f"{results['vapor_mass_flow_rate_kgs']:.3f} kg/s")
        
        with col2:
            st.metric("Total Volumetric Flow Rate", f"{results['total_volumetric_flow_rate_m3s'] * 3600:.1f} m³/h")
            st.metric("Liquid Volumetric Flow Rate", f"{results['liquid_volumetric_flow_rate_m3s'] * 3600:.1f} m³/h")
            st.metric("Vapor Volumetric Flow Rate", f"{results['vapor_volumetric_flow_rate_m3s'] * 3600:.1f} m³/h")
        
        with col3:
            st.metric("Mixture Density", f"{results['mixture_density_kgm3']:.2f} kg/m³")
            st.metric("Exit Velocity", f"{results['velocity_ms']:.1f} m/s")
            st.metric("Hole Area", f"{results['hole_area_m2'] * 1e6:.2f} mm²")
        
        # Plot Flow Rate vs Liquid Fraction
        st.subheader("Sensitivity Analysis")
        
        liquid_fractions = np.linspace(0, 1, 21)
        flow_rates = []
        
        for fraction in liquid_fractions:
            result = ReleaseCalculator.two_phase_release_rate(
                hole_diameter, upstream_pressure, downstream_pressure,
                temperature_k, fraction, liquid_density,
                vapor_density, discharge_coefficient
            )
            flow_rates.append(result["mass_flow_rate_kgs"])
        
        fig = px.line(
            x=liquid_fractions,
            y=flow_rates,
            labels={"x": "Liquid Mass Fraction", "y": "Mass Flow Rate (kg/s)"},
            title="Mass Flow Rate vs. Liquid Mass Fraction"
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_pipe_release_tab():
    """
    Render the pipe release rate calculation tab
    """
    st.header("Pipe Release Rate Calculation")
    st.markdown("""
    Calculate the release rate through a pipe segment, accounting for friction losses.
    """)
    
    # Create input form
    with st.form("pipe_release_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            pipe_diameter = st.number_input(
                "Pipe Inner Diameter (mm)",
                min_value=1.0,
                max_value=1000.0,
                value=50.0,
                step=1.0,
                help="Inner diameter of the pipe"
            )
            
            pipe_length = st.number_input(
                "Pipe Length (m)",
                min_value=0.1,
                max_value=1000.0,
                value=10.0,
                step=1.0,
                help="Length of the pipe segment"
            )
            
            pressure_differential = st.number_input(
                "Pressure Differential (kPa)",
                min_value=0.0,
                max_value=50000.0,
                value=100.0,
                step=10.0,
                help="Pressure difference between pipe inlet and outlet"
            )
        
        with col2:
            density = st.number_input(
                "Fluid Density (kg/m³)",
                min_value=1.0,
                max_value=20000.0,
                value=1000.0,
                step=10.0,
                help="Density of the fluid"
            )
            
            viscosity = st.number_input(
                "Fluid Viscosity (cP)",
                min_value=0.01,
                max_value=10000.0,
                value=1.0,
                step=0.1,
                help="Dynamic viscosity of the fluid in centipoise"
            )
            
            pipe_roughness = st.number_input(
                "Pipe Roughness (mm)",
                min_value=0.0,
                max_value=10.0,
                value=0.045,
                step=0.005,
                help="Pipe wall roughness"
            )
        
        # Submit button
        submitted = st.form_submit_button("Calculate")
    
    # Calculate and display results when form is submitted
    if submitted:
        # Convert viscosity from cP to Pa·s
        viscosity_pas = viscosity / 1000.0
        
        # Calculate release rate
        results = ReleaseCalculator.pipe_release_rate(
            pipe_diameter, pipe_length, pressure_differential,
            density, viscosity_pas, pipe_roughness_mm=pipe_roughness
        )
        
        # Display results
        st.subheader("Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Mass Flow Rate", f"{results['mass_flow_rate_kgs']:.3f} kg/s")
            st.metric("Volumetric Flow Rate", f"{results['volumetric_flow_rate_m3s'] * 3600:.1f} m³/h")
            st.metric("Flow Velocity", f"{results['velocity_ms']:.2f} m/s")
        
        with col2:
            st.metric("Pipe Cross-sectional Area", f"{results['pipe_area_m2'] * 1e6:.0f} mm²")
            st.metric("Friction Factor", f"{results['friction_factor']:.4f}")
            st.metric("Reynolds Number", f"{results['reynolds_number']:.0f}")
            
            # Show flow regime
            if results['reynolds_number'] < 2300:
                st.metric("Flow Regime", "Laminar")
            elif results['reynolds_number'] < 4000:
                st.metric("Flow Regime", "Transitional")
            else:
                st.metric("Flow Regime", "Turbulent")
        
        # Plot Flow Rate vs Pipe Diameter
        st.subheader("Sensitivity Analysis")
        
        diameters = np.linspace(pipe_diameter * 0.5, pipe_diameter * 2, 10)
        flow_rates = []
        
        for diameter in diameters:
            result = ReleaseCalculator.pipe_release_rate(
                diameter, pipe_length, pressure_differential,
                density, viscosity_pas, pipe_roughness_mm=pipe_roughness
            )
            flow_rates.append(result["mass_flow_rate_kgs"])
        
        fig = px.line(
            x=diameters,
            y=flow_rates,
            labels={"x": "Pipe Diameter (mm)", "y": "Mass Flow Rate (kg/s)"},
            title="Mass Flow Rate vs. Pipe Diameter"
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_flange_leak_tab():
    """
    Render the flange leak rate calculation tab
    """
    st.header("Flange Leak Rate Calculation")
    st.markdown("""
    Estimate the leak rate from a flange connection at various leak sizes.
    """)
    
    # Create input form
    with st.form("flange_leak_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            pressure = st.number_input(
                "Pressure (kPa)",
                min_value=0.0,
                max_value=50000.0,
                value=1000.0,
                step=10.0,
                help="Internal pressure at the flange"
            )
            
            flange_size = st.number_input(
                "Flange Size (mm)",
                min_value=10.0,
                max_value=1000.0,
                value=100.0,
                step=10.0,
                help="Flange diameter"
            )
        
        with col2:
            density = st.number_input(
                "Fluid Density (kg/m³)",
                min_value=1.0,
                max_value=20000.0,
                value=1000.0,
                step=10.0,
                help="Density of the fluid"
            )
            
            leak_type = st.selectbox(
                "Leak Type",
                options=["small", "medium", "large"],
                help="Size of the leak"
            )
        
        # Submit button
        submitted = st.form_submit_button("Calculate")
    
    # Calculate and display results when form is submitted
    if submitted:
        # Calculate leak rate
        results = ReleaseCalculator.flange_leak_rate(
            pressure, flange_size, density, leak_type
        )
        
        # Display results
        st.subheader("Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Mass Leak Rate", f"{results['mass_flow_rate_kgs'] * 3600:.3f} kg/h")
            st.metric("Volumetric Leak Rate", f"{results['volumetric_flow_rate_m3s'] * 3600 * 1000:.1f} L/h")
        
        with col2:
            st.metric("Leak Area", f"{results['leak_area_m2'] * 1e6:.2f} mm²")
            st.metric("Leak Velocity", f"{results['velocity_ms']:.1f} m/s")
        
        # Calculate leak rates for all types
        leak_types = ["small", "medium", "large"]
        leak_rates = []
        
        for lt in leak_types:
            result = ReleaseCalculator.flange_leak_rate(
                pressure, flange_size, density, lt
            )
            leak_rates.append(result["mass_flow_rate_kgs"] * 3600)  # kg/h
        
        # Create bar chart
        st.subheader("Leak Rate Comparison")
        
        fig = px.bar(
            x=leak_types,
            y=leak_rates,
            labels={"x": "Leak Type", "y": "Mass Leak Rate (kg/h)"},
            title="Leak Rate by Leak Type",
            color=leak_rates,
            color_continuous_scale="Reds"
        )
        
        st.plotly_chart(fig, use_container_width=True) 