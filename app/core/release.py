# -*- coding: utf-8 -*-
"""
HAZOP Analysis Tool - Release Rate Calculation Module
Provides comprehensive models for estimating release rates for various scenarios
"""
import math
from enum import Enum
from typing import Dict, Any, Tuple, Optional, List, Union


class FluidPhase(Enum):
    """Enumeration of fluid phases"""
    LIQUID = "liquid"
    GAS = "gas"
    TWO_PHASE = "two-phase"


class ReleaseType(Enum):
    """Enumeration of release types"""
    HOLE = "hole"
    PIPE = "pipe"
    RELIEF_VALVE = "relief_valve"
    VENT = "vent"
    FLANGE_LEAK = "flange_leak"


class ReleaseCalculator:
    """Calculator for release rates in various scenarios"""
    
    # Constants
    GRAVITY = 9.81  # m/s²
    UNIVERSAL_GAS_CONSTANT = 8.31446  # J/(mol·K)
    
    @staticmethod
    def calculate_discharge_coefficient(reynolds_number: float, orifice_type: str = "sharp") -> float:
        """
        Calculate discharge coefficient based on Reynolds number and orifice type
        
        Args:
            reynolds_number: Reynolds number of the flow
            orifice_type: Type of orifice (sharp, rounded, pipe)
            
        Returns:
            Discharge coefficient (dimensionless)
        """
        # Default coefficients for different orifice types
        if orifice_type == "rounded":
            cd = 0.98  # Rounded entrance
        elif orifice_type == "pipe":
            cd = 0.82  # Pipe entrance
        else:  # sharp
            # Sharp orifice - coefficient varies with Reynolds number
            if reynolds_number < 10:
                cd = 0.5  # Very low Reynolds number
            elif reynolds_number < 1000:
                # Interpolate for transitional flow
                cd = 0.5 + 0.11 * (math.log10(reynolds_number) - 1) / 2
            else:
                cd = 0.61  # Fully turbulent flow
        
        return cd
    
    @staticmethod
    def calculate_reynolds_number(velocity: float, diameter: float, 
                                  density: float, viscosity: float) -> float:
        """
        Calculate Reynolds number
        
        Args:
            velocity: Flow velocity in m/s
            diameter: Characteristic diameter in m
            density: Fluid density in kg/m³
            viscosity: Fluid dynamic viscosity in Pa·s
            
        Returns:
            Reynolds number (dimensionless)
        """
        return density * velocity * diameter / viscosity
    
    @staticmethod
    def liquid_release_rate(hole_diameter_mm: float, pressure_differential_kpa: float,
                           density_kgm3: float, height_differential_m: float = 0.0,
                           discharge_coef: float = 0.61) -> Dict[str, Any]:
        """
        Calculate liquid release rate through a hole or orifice
        
        Args:
            hole_diameter_mm: Hole diameter in mm
            pressure_differential_kpa: Pressure differential in kPa
            density_kgm3: Liquid density in kg/m³
            height_differential_m: Height difference between liquid level and hole in m
            discharge_coef: Discharge coefficient (dimensionless)
            
        Returns:
            Dictionary with release rate results
        """
        # Convert units
        hole_diameter_m = hole_diameter_mm / 1000
        pressure_differential_pa = pressure_differential_kpa * 1000
        
        # Calculate hole area
        hole_area_m2 = math.pi * (hole_diameter_m ** 2) / 4
        
        # Calculate total pressure including hydrostatic head
        hydrostatic_pressure_pa = density_kgm3 * ReleaseCalculator.GRAVITY * height_differential_m
        total_pressure_pa = pressure_differential_pa + hydrostatic_pressure_pa
        
        # Calculate velocity using Bernoulli's equation
        velocity = discharge_coef * math.sqrt(2 * total_pressure_pa / density_kgm3)
        
        # Calculate mass flow rate
        mass_flow_rate = hole_area_m2 * velocity * density_kgm3
        
        # Calculate volumetric flow rate
        volumetric_flow_rate = mass_flow_rate / density_kgm3
        
        return {
            "mass_flow_rate_kgs": mass_flow_rate,
            "volumetric_flow_rate_m3s": volumetric_flow_rate,
            "velocity_ms": velocity,
            "hole_area_m2": hole_area_m2,
            "discharge_coefficient": discharge_coef
        }
    
    @staticmethod
    def gas_release_rate(hole_diameter_mm: float, upstream_pressure_kpa: float,
                        downstream_pressure_kpa: float, temperature_k: float,
                        molecular_weight: float, k: float = 1.4,
                        discharge_coef: float = 0.61) -> Dict[str, Any]:
        """
        Calculate gas release rate through a hole or orifice
        
        Args:
            hole_diameter_mm: Hole diameter in mm
            upstream_pressure_kpa: Upstream pressure in kPa
            downstream_pressure_kpa: Downstream pressure in kPa
            temperature_k: Gas temperature in K
            molecular_weight: Gas molecular weight in g/mol
            k: Specific heat ratio (Cp/Cv)
            discharge_coef: Discharge coefficient (dimensionless)
            
        Returns:
            Dictionary with release rate results
        """
        # Convert units
        hole_diameter_m = hole_diameter_mm / 1000
        upstream_pressure_pa = upstream_pressure_kpa * 1000
        downstream_pressure_pa = downstream_pressure_kpa * 1000
        molecular_weight_kg = molecular_weight / 1000  # Convert g/mol to kg/mol
        
        # Calculate hole area
        hole_area_m2 = math.pi * (hole_diameter_m ** 2) / 4
        
        # Calculate pressure ratio
        pressure_ratio = downstream_pressure_pa / upstream_pressure_pa
        
        # Calculate critical pressure ratio
        critical_pressure_ratio = (2 / (k + 1)) ** (k / (k - 1))
        
        # Check if flow is choked (sonic)
        is_choked = pressure_ratio <= critical_pressure_ratio
        
        # Calculate gas density at upstream conditions
        gas_density = (upstream_pressure_pa * molecular_weight_kg) / (ReleaseCalculator.UNIVERSAL_GAS_CONSTANT * temperature_k)
        
        # Calculate mass flow rate
        if is_choked:
            # Sonic flow
            flow_function = (k * (2 / (k + 1)) ** ((k + 1) / (k - 1))) ** 0.5
            mass_flow_rate = discharge_coef * hole_area_m2 * upstream_pressure_pa * flow_function * \
                            (molecular_weight_kg / (ReleaseCalculator.UNIVERSAL_GAS_CONSTANT * temperature_k)) ** 0.5
        else:
            # Subsonic flow
            # Using a simplified gas discharge equation where flow increases as pressure_ratio decreases
            flow_parameter = math.sqrt((2 * k) / (k - 1)) * \
                            math.sqrt(pressure_ratio ** (2/k) * (1 - pressure_ratio ** ((k-1)/k)))
            
            mass_flow_rate = discharge_coef * hole_area_m2 * flow_parameter * \
                           upstream_pressure_pa * math.sqrt(gas_density / upstream_pressure_pa)
        
        # Calculate volumetric flow rate at standard conditions (1 atm, 15°C)
        std_temperature = 288.15  # K (15°C)
        std_pressure = 101325  # Pa (1 atm)
        std_density = (std_pressure * molecular_weight_kg) / (ReleaseCalculator.UNIVERSAL_GAS_CONSTANT * std_temperature)
        volumetric_flow_rate_std = mass_flow_rate / std_density
        
        return {
            "mass_flow_rate_kgs": mass_flow_rate,
            "volumetric_flow_rate_std_m3s": volumetric_flow_rate_std,
            "is_choked": is_choked,
            "hole_area_m2": hole_area_m2,
            "discharge_coefficient": discharge_coef,
            "gas_density_kgm3": gas_density,
            "pressure_ratio": pressure_ratio,
            "critical_pressure_ratio": critical_pressure_ratio
        }
    
    @staticmethod
    def two_phase_release_rate(hole_diameter_mm: float, upstream_pressure_kpa: float,
                              downstream_pressure_kpa: float, temperature_k: float,
                              liquid_fraction: float, liquid_density_kgm3: float,
                              vapor_density_kgm3: float, discharge_coef: float = 0.61) -> Dict[str, Any]:
        """
        Calculate two-phase release rate through a hole or orifice using homogeneous equilibrium model
        
        Args:
            hole_diameter_mm: Hole diameter in mm
            upstream_pressure_kpa: Upstream pressure in kPa
            downstream_pressure_kpa: Downstream pressure in kPa
            temperature_k: Fluid temperature in K
            liquid_fraction: Liquid mass fraction (0-1)
            liquid_density_kgm3: Liquid phase density in kg/m³
            vapor_density_kgm3: Vapor phase density in kg/m³
            discharge_coef: Discharge coefficient (dimensionless)
            
        Returns:
            Dictionary with release rate results
        """
        # Convert units
        hole_diameter_m = hole_diameter_mm / 1000
        upstream_pressure_pa = upstream_pressure_kpa * 1000
        downstream_pressure_pa = downstream_pressure_kpa * 1000
        
        # Calculate hole area
        hole_area_m2 = math.pi * (hole_diameter_m ** 2) / 4
        
        # Calculate mixture density
        if liquid_fraction >= 1.0:
            # Pure liquid
            mixture_density = liquid_density_kgm3
        elif liquid_fraction <= 0.0:
            # Pure vapor
            mixture_density = vapor_density_kgm3
        else:
            # Two-phase mixture
            mixture_density = 1.0 / ((liquid_fraction / liquid_density_kgm3) + 
                                    ((1 - liquid_fraction) / vapor_density_kgm3))
        
        # Calculate pressure differential
        pressure_differential_pa = upstream_pressure_pa - downstream_pressure_pa
        
        # Use a simplified approach based on the homogeneous equilibrium model
        velocity = discharge_coef * math.sqrt(2 * pressure_differential_pa / mixture_density)
        
        # Calculate mass flow rate
        mass_flow_rate = hole_area_m2 * velocity * mixture_density
        
        # Calculate volumetric flow rates for each phase
        liquid_mass_flow = mass_flow_rate * liquid_fraction
        vapor_mass_flow = mass_flow_rate * (1 - liquid_fraction)
        
        liquid_volumetric_flow = liquid_mass_flow / liquid_density_kgm3
        vapor_volumetric_flow = vapor_mass_flow / vapor_density_kgm3
        
        return {
            "mass_flow_rate_kgs": mass_flow_rate,
            "liquid_mass_flow_rate_kgs": liquid_mass_flow,
            "vapor_mass_flow_rate_kgs": vapor_mass_flow,
            "liquid_volumetric_flow_rate_m3s": liquid_volumetric_flow,
            "vapor_volumetric_flow_rate_m3s": vapor_volumetric_flow,
            "total_volumetric_flow_rate_m3s": liquid_volumetric_flow + vapor_volumetric_flow,
            "mixture_density_kgm3": mixture_density,
            "velocity_ms": velocity,
            "hole_area_m2": hole_area_m2,
            "discharge_coefficient": discharge_coef
        }
    
    @staticmethod
    def pipe_release_rate(pipe_diameter_mm: float, pipe_length_m: float,
                         pressure_differential_kpa: float, fluid_density_kgm3: float,
                         fluid_viscosity_pas: float, friction_factor: float = None,
                         pipe_roughness_mm: float = 0.045) -> Dict[str, Any]:
        """
        Calculate release rate through a pipe segment
        
        Args:
            pipe_diameter_mm: Pipe inner diameter in mm
            pipe_length_m: Pipe length in m
            pressure_differential_kpa: Pressure differential in kPa
            fluid_density_kgm3: Fluid density in kg/m³
            fluid_viscosity_pas: Fluid dynamic viscosity in Pa·s
            friction_factor: Darcy friction factor (if None, calculated from roughness)
            pipe_roughness_mm: Pipe roughness in mm
            
        Returns:
            Dictionary with release rate results
        """
        # Convert units
        pipe_diameter_m = pipe_diameter_mm / 1000
        pipe_roughness_m = pipe_roughness_mm / 1000
        pressure_differential_pa = pressure_differential_kpa * 1000
        
        # Calculate pipe area
        pipe_area_m2 = math.pi * (pipe_diameter_m ** 2) / 4
        
        # Iterative solution for friction factor if not provided
        if friction_factor is None:
            # Initial guess using Haaland equation
            relative_roughness = pipe_roughness_m / pipe_diameter_m
            friction_factor = 0.3  # Initial guess
            
            # Estimate initial velocity
            velocity_guess = math.sqrt(2 * pressure_differential_pa / (fluid_density_kgm3 * (1 + 4 * friction_factor * pipe_length_m / pipe_diameter_m)))
            
            # Calculate initial Reynolds number
            reynolds = ReleaseCalculator.calculate_reynolds_number(
                velocity_guess, pipe_diameter_m, fluid_density_kgm3, fluid_viscosity_pas
            )
            
            # Determine flow regime
            if reynolds < 2300:
                # Laminar flow
                friction_factor = 64 / reynolds
            else:
                # Turbulent flow - use Colebrook equation iteratively
                for _ in range(10):  # Limit iterations
                    # Haaland equation (explicit approximation of Colebrook)
                    friction_factor = (-1.8 * math.log10(((relative_roughness/3.7)**1.11) + (6.9/reynolds)))**(-2)
                    
                    # Recalculate velocity
                    velocity = math.sqrt(2 * pressure_differential_pa / (fluid_density_kgm3 * (1 + 4 * friction_factor * pipe_length_m / pipe_diameter_m)))
                    
                    # Recalculate Reynolds number
                    new_reynolds = ReleaseCalculator.calculate_reynolds_number(
                        velocity, pipe_diameter_m, fluid_density_kgm3, fluid_viscosity_pas
                    )
                    
                    # Check convergence
                    if abs(new_reynolds - reynolds) / reynolds < 0.01:
                        reynolds = new_reynolds
                        break
                    
                    reynolds = new_reynolds
        
        # Calculate velocity and flow rates
        velocity = math.sqrt(2 * pressure_differential_pa / (fluid_density_kgm3 * (1 + 4 * friction_factor * pipe_length_m / pipe_diameter_m)))
        mass_flow_rate = pipe_area_m2 * velocity * fluid_density_kgm3
        volumetric_flow_rate = mass_flow_rate / fluid_density_kgm3
        
        # Calculate Reynolds number for final velocity
        reynolds = ReleaseCalculator.calculate_reynolds_number(
            velocity, pipe_diameter_m, fluid_density_kgm3, fluid_viscosity_pas
        )
        
        return {
            "mass_flow_rate_kgs": mass_flow_rate,
            "volumetric_flow_rate_m3s": volumetric_flow_rate,
            "velocity_ms": velocity,
            "pipe_area_m2": pipe_area_m2,
            "friction_factor": friction_factor,
            "reynolds_number": reynolds
        }
    
    @staticmethod
    def calculate_release_duration(inventory_kg: float, mass_flow_rate_kgs: float) -> float:
        """
        Calculate release duration based on inventory and flow rate
        
        Args:
            inventory_kg: Total inventory in kg
            mass_flow_rate_kgs: Mass flow rate in kg/s
            
        Returns:
            Release duration in seconds
        """
        if mass_flow_rate_kgs <= 0:
            return float('inf')  # Infinite duration for zero flow rate
        
        return inventory_kg / mass_flow_rate_kgs
    
    @staticmethod
    def calculate_release_quantity(mass_flow_rate_kgs: float, duration_s: float) -> float:
        """
        Calculate release quantity based on flow rate and duration
        
        Args:
            mass_flow_rate_kgs: Mass flow rate in kg/s
            duration_s: Duration in seconds
            
        Returns:
            Release quantity in kg
        """
        return mass_flow_rate_kgs * duration_s
    
    @staticmethod
    def flange_leak_rate(pressure_kpa: float, flange_size_mm: float, 
                        fluid_density_kgm3: float, leak_type: str = "small") -> Dict[str, Any]:
        """
        Estimate leak rate from a flange connection
        
        Args:
            pressure_kpa: Pressure in kPa
            flange_size_mm: Flange diameter in mm
            fluid_density_kgm3: Fluid density in kg/m³
            leak_type: Size of leak (small, medium, large)
            
        Returns:
            Dictionary with leak rate results
        """
        # Convert units
        pressure_pa = pressure_kpa * 1000
        flange_size_m = flange_size_mm / 1000
        flange_circumference = math.pi * flange_size_m
        
        # Leak area as a function of flange size and leak type
        leak_areas = {
            "small": 1e-7 * flange_circumference,  # 0.1 mm² per meter of circumference
            "medium": 1e-6 * flange_circumference,  # 1 mm² per meter of circumference
            "large": 1e-5 * flange_circumference   # 10 mm² per meter of circumference
        }
        
        leak_area = leak_areas.get(leak_type, leak_areas["small"])
        
        # Discharge coefficient based on leak type
        discharge_coefficients = {
            "small": 0.5,
            "medium": 0.6,
            "large": 0.65
        }
        
        discharge_coef = discharge_coefficients.get(leak_type, 0.6)
        
        # Calculate velocity
        velocity = discharge_coef * math.sqrt(2 * pressure_pa / fluid_density_kgm3)
        
        # Calculate flow rates
        mass_flow_rate = leak_area * velocity * fluid_density_kgm3
        volumetric_flow_rate = mass_flow_rate / fluid_density_kgm3
        
        return {
            "mass_flow_rate_kgs": mass_flow_rate,
            "volumetric_flow_rate_m3s": volumetric_flow_rate,
            "leak_area_m2": leak_area,
            "velocity_ms": velocity,
            "discharge_coefficient": discharge_coef
        } 