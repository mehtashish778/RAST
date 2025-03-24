# -*- coding: utf-8 -*-
"""
HAZOP Analysis Tool - Consequence Analysis Module
Provides calculation methods for estimating consequences of scenarios
"""
import math
from typing import Dict, Any, Tuple, Optional, List


class ConsequenceCalculator:
    """Calculator for scenario consequences"""
    
    @staticmethod
    def calculate_risk_score(severity: int, likelihood: int) -> int:
        """
        Calculate risk score based on severity and likelihood
        
        Args:
            severity: Severity rating (1-5)
            likelihood: Likelihood rating (1-5)
            
        Returns:
            Risk score (1-25)
        """
        # Ensure values are within range
        sev = max(1, min(5, severity))
        like = max(1, min(5, likelihood))
        
        # Calculate score
        return sev * like
    
    @staticmethod
    def get_risk_category(risk_score: int) -> str:
        """
        Get risk category based on risk score
        
        Args:
            risk_score: Risk score (1-25)
            
        Returns:
            Risk category (Low, Medium, High, Very High)
        """
        if risk_score <= 4:
            return "Low"
        elif risk_score <= 9:
            return "Medium"
        elif risk_score <= 16:
            return "High"
        else:
            return "Very High"
    
    @staticmethod
    def estimate_release_rate(hole_size_mm: float, pressure_kpa: float, density_kgm3: float) -> float:
        """
        Estimate liquid release rate through a hole
        
        Args:
            hole_size_mm: Hole diameter in mm
            pressure_kpa: Pressure differential in kPa
            density_kgm3: Fluid density in kg/m³
            
        Returns:
            Release rate in kg/s
        """
        # Convert hole size to m²
        hole_area = math.pi * (hole_size_mm / 1000) ** 2 / 4
        
        # Discharge coefficient
        discharge_coef = 0.61
        
        # Convert pressure to Pa
        pressure_pa = pressure_kpa * 1000
        
        # Calculate flow rate
        flow_rate = discharge_coef * hole_area * math.sqrt(2 * pressure_pa / density_kgm3)
        
        return flow_rate
    
    @staticmethod
    def estimate_dispersion_distance(release_rate_kgs: float, wind_speed_ms: float, 
                                    stability_class: str) -> float:
        """
        Estimate dispersion distance for hazardous concentration
        
        Args:
            release_rate_kgs: Release rate in kg/s
            wind_speed_ms: Wind speed in m/s
            stability_class: Pasquill-Gifford stability class (A-F)
            
        Returns:
            Dispersion distance in meters
        """
        # Simple correlation based on release rate and wind speed
        # This is a simplified model - real dispersion modeling is much more complex
        stability_factor = {
            "A": 0.5,  # Very unstable
            "B": 0.7,
            "C": 1.0,
            "D": 1.5,
            "E": 2.0,
            "F": 3.0   # Very stable
        }.get(stability_class, 1.0)
        
        # Basic dispersion calculation
        distance = ((release_rate_kgs ** 0.6) * stability_factor) / (wind_speed_ms ** 0.3)
        
        return max(10, min(10000, distance * 100))  # Limit to reasonable range
    
    @staticmethod
    def estimate_toxic_consequence(release_rate_kgs: float, toxic_threshold_ppm: float,
                                   molecular_weight: float, wind_speed_ms: float) -> Dict[str, Any]:
        """
        Estimate consequences for toxic release
        
        Args:
            release_rate_kgs: Release rate in kg/s
            toxic_threshold_ppm: Toxic concentration threshold in ppm
            molecular_weight: Molecular weight of the substance
            wind_speed_ms: Wind speed in m/s
            
        Returns:
            Dictionary with consequence estimates
        """
        # Convert toxic threshold to kg/m³
        toxic_threshold_kgm3 = (toxic_threshold_ppm / 1e6) * (molecular_weight / 24.45)
        
        # Simple correlation for affected radius
        radius = 50 * math.sqrt(release_rate_kgs / (wind_speed_ms * toxic_threshold_kgm3))
        
        # Limit to reasonable range
        radius = max(10, min(5000, radius))
        
        # Estimate affected area
        affected_area = math.pi * radius ** 2
        
        # Estimate population density (people per km²) - default to suburban
        population_density = 1000
        
        # Calculate potential casualties (very rough estimate)
        potential_casualties = (affected_area / 1e6) * population_density
        
        return {
            "radius_m": radius,
            "affected_area_m2": affected_area,
            "potential_casualties": potential_casualties,
            "release_duration_min": 10  # Assuming 10 minutes release
        }
    
    @staticmethod
    def estimate_fire_consequence(release_rate_kgs: float, heat_of_combustion_kjkg: float) -> Dict[str, Any]:
        """
        Estimate consequences for fire scenario
        
        Args:
            release_rate_kgs: Release rate in kg/s
            heat_of_combustion_kjkg: Heat of combustion in kJ/kg
            
        Returns:
            Dictionary with consequence estimates
        """
        # Calculate heat release rate
        heat_release_rate = release_rate_kgs * heat_of_combustion_kjkg
        
        # Simple correlation for flame height
        flame_height = 0.235 * (heat_release_rate ** 0.4)
        
        # Simple correlation for radiation distance (to 5 kW/m²)
        radiation_distance = 0.1 * math.sqrt(heat_release_rate)
        
        # Simple correlation for affected radius
        radius = max(radiation_distance, 10)
        
        # Estimate affected area
        affected_area = math.pi * radius ** 2
        
        return {
            "heat_release_rate_kw": heat_release_rate,
            "flame_height_m": flame_height,
            "radiation_distance_m": radiation_distance,
            "affected_area_m2": affected_area
        }
    
    @staticmethod
    def estimate_explosion_consequence(mass_kg: float, tnt_equiv_factor: float) -> Dict[str, Any]:
        """
        Estimate consequences for explosion scenario using TNT equivalency
        
        Args:
            mass_kg: Mass of explosive material in kg
            tnt_equiv_factor: TNT equivalency factor
            
        Returns:
            Dictionary with consequence estimates
        """
        # Calculate TNT equivalent mass
        tnt_equiv_mass = mass_kg * tnt_equiv_factor
        
        # Calculate scaled distances for different overpressures
        # 0.02 bar (window breakage)
        distance_002bar = 50 * (tnt_equiv_mass ** (1/3))
        
        # 0.1 bar (structural damage)
        distance_01bar = 18 * (tnt_equiv_mass ** (1/3))
        
        # 0.3 bar (severe structural damage)
        distance_03bar = 9 * (tnt_equiv_mass ** (1/3))
        
        return {
            "tnt_equivalent_kg": tnt_equiv_mass,
            "distance_window_breakage_m": distance_002bar,
            "distance_structural_damage_m": distance_01bar,
            "distance_severe_damage_m": distance_03bar
        }
    
    @staticmethod
    def assess_risk(severity: int, likelihood: int) -> Dict[str, Any]:
        """
        Perform full risk assessment for a scenario
        
        Args:
            severity: Severity rating (1-5)
            likelihood: Likelihood rating (1-5)
            
        Returns:
            Dictionary with risk assessment results
        """
        # Calculate risk score
        risk_score = ConsequenceCalculator.calculate_risk_score(severity, likelihood)
        
        # Determine risk category
        risk_category = ConsequenceCalculator.get_risk_category(risk_score)
        
        # Determine if additional analysis is needed
        needs_lopa = risk_category in ["High", "Very High"]
        
        # Determine recommended actions
        if risk_category == "Very High":
            recommended_action = "Immediate action required to reduce risk"
        elif risk_category == "High":
            recommended_action = "Prompt action required to reduce risk"
        elif risk_category == "Medium":
            recommended_action = "Action should be planned to reduce risk"
        else:
            recommended_action = "No immediate action required"
        
        return {
            "severity": severity,
            "likelihood": likelihood,
            "risk_score": risk_score,
            "risk_category": risk_category,
            "needs_lopa": needs_lopa,
            "recommended_action": recommended_action
        } 