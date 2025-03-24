import pytest
import sys
import os
import math
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the app directory to the path for imports
app_dir = Path(__file__).parent.parent.absolute() / "app"
sys.path.append(str(app_dir))

# Import the module directly to avoid path issues
import app.core.release
from app.core.release import ReleaseCalculator, FluidPhase, ReleaseType


class TestReleaseCalculator:
    """Tests for ReleaseCalculator class"""
    
    def test_calculate_discharge_coefficient(self):
        """Test discharge coefficient calculation"""
        # Test different orifice types
        assert ReleaseCalculator.calculate_discharge_coefficient(5000, "sharp") == 0.61
        assert ReleaseCalculator.calculate_discharge_coefficient(5000, "rounded") == 0.98
        assert ReleaseCalculator.calculate_discharge_coefficient(5000, "pipe") == 0.82
        
        # Test Reynolds number dependence for sharp orifice
        assert ReleaseCalculator.calculate_discharge_coefficient(5, "sharp") == 0.5
        assert 0.5 < ReleaseCalculator.calculate_discharge_coefficient(500, "sharp") < 0.61
    
    def test_calculate_reynolds_number(self):
        """Test Reynolds number calculation"""
        # Test typical values
        assert ReleaseCalculator.calculate_reynolds_number(1.0, 0.01, 1000.0, 0.001) == 10000.0
        assert ReleaseCalculator.calculate_reynolds_number(2.0, 0.05, 800.0, 0.002) == 40000.0
        
        # Test zero case
        assert ReleaseCalculator.calculate_reynolds_number(0.0, 0.01, 1000.0, 0.001) == 0.0
    
    @patch('app.core.release.math')
    def test_liquid_release_rate(self, mock_math):
        """Test liquid release rate calculation"""
        # Setup math mock
        mock_math.pi = math.pi
        mock_math.sqrt.side_effect = lambda x: math.sqrt(x)
        
        # Test with typical values
        results = ReleaseCalculator.liquid_release_rate(10.0, 500.0, 1000.0)
        assert isinstance(results, dict)
        assert "mass_flow_rate_kgs" in results
        assert "volumetric_flow_rate_m3s" in results
        assert "velocity_ms" in results
        assert "hole_area_m2" in results
        assert results["mass_flow_rate_kgs"] > 0
        
        # Test with height differential
        results_with_height = ReleaseCalculator.liquid_release_rate(10.0, 500.0, 1000.0, 5.0)
        # Higher head should give higher flow rate
        assert results_with_height["mass_flow_rate_kgs"] > results["mass_flow_rate_kgs"]
        
        # Test different hole sizes
        results_small = ReleaseCalculator.liquid_release_rate(5.0, 500.0, 1000.0)
        results_large = ReleaseCalculator.liquid_release_rate(20.0, 500.0, 1000.0)
        assert results_large["mass_flow_rate_kgs"] > results["mass_flow_rate_kgs"] > results_small["mass_flow_rate_kgs"]
    
    @patch('app.core.release.math')
    def test_gas_release_rate(self, mock_math):
        """Test gas release rate calculation"""
        # Setup math mock
        mock_math.pi = math.pi
        mock_math.sqrt.side_effect = lambda x: math.sqrt(x)
        
        # Constants for testing
        hole_size = 10.0  # mm
        upstream_pressure = 1000.0  # kPa
        downstream_pressure = 100.0  # kPa
        temperature = 300.0  # K
        molecular_weight = 28.0  # g/mol
        k = 1.4  # Specific heat ratio
        
        # Test with typical values - choked flow
        results = ReleaseCalculator.gas_release_rate(
            hole_size, upstream_pressure, downstream_pressure,
            temperature, molecular_weight, k
        )
        assert isinstance(results, dict)
        assert "mass_flow_rate_kgs" in results
        assert "volumetric_flow_rate_std_m3s" in results
        assert "is_choked" in results
        assert results["mass_flow_rate_kgs"] > 0
        assert results["is_choked"] is True  # Should be choked with this pressure ratio
        
        # Test with high downstream pressure - subsonic flow
        high_downstream = 800.0  # kPa
        results_subsonic = ReleaseCalculator.gas_release_rate(
            hole_size, upstream_pressure, high_downstream,
            temperature, molecular_weight, k
        )
        assert results_subsonic["is_choked"] is False
        
        # Lower downstream pressure should give higher flow rate for subsonic flow
        if not results_subsonic["is_choked"]:
            lower_downstream = 500.0  # kPa
            results_lower = ReleaseCalculator.gas_release_rate(
                hole_size, upstream_pressure, lower_downstream,
                temperature, molecular_weight, k
            )
            assert results_lower["mass_flow_rate_kgs"] > results_subsonic["mass_flow_rate_kgs"]
    
    @patch('app.core.release.math')
    def test_two_phase_release_rate(self, mock_math):
        """Test two-phase release rate calculation"""
        # Setup math mock
        mock_math.pi = math.pi
        mock_math.sqrt.side_effect = lambda x: math.sqrt(x)
        
        # Constants for testing
        hole_size = 10.0  # mm
        upstream_pressure = 1000.0  # kPa
        downstream_pressure = 100.0  # kPa
        temperature = 300.0  # K
        liquid_density = 800.0  # kg/m³
        vapor_density = 5.0  # kg/m³
        
        # Test with different liquid fractions
        for liquid_fraction in [0.0, 0.2, 0.5, 0.8, 1.0]:
            results = ReleaseCalculator.two_phase_release_rate(
                hole_size, upstream_pressure, downstream_pressure,
                temperature, liquid_fraction, liquid_density, vapor_density
            )
            assert isinstance(results, dict)
            assert "mass_flow_rate_kgs" in results
            assert "liquid_mass_flow_rate_kgs" in results
            assert "vapor_mass_flow_rate_kgs" in results
            assert "mixture_density_kgm3" in results
            assert results["mass_flow_rate_kgs"] > 0
            
            # Check that phase distribution is correct
            assert abs(results["liquid_mass_flow_rate_kgs"] - liquid_fraction * results["mass_flow_rate_kgs"]) < 1e-10
            assert abs(results["vapor_mass_flow_rate_kgs"] - (1 - liquid_fraction) * results["mass_flow_rate_kgs"]) < 1e-10
            
            # Check that volumetric flow calculations are correct
            assert abs(results["liquid_volumetric_flow_rate_m3s"] - results["liquid_mass_flow_rate_kgs"] / liquid_density) < 1e-10
            if liquid_fraction < 1.0:  # Avoid division by zero
                assert abs(results["vapor_volumetric_flow_rate_m3s"] - results["vapor_mass_flow_rate_kgs"] / vapor_density) < 1e-10
        
        # Density checks
        assert abs(ReleaseCalculator.two_phase_release_rate(
            hole_size, upstream_pressure, downstream_pressure,
            temperature, 1.0, liquid_density, vapor_density
        )["mixture_density_kgm3"] - liquid_density) < 1e-10
        
        assert abs(ReleaseCalculator.two_phase_release_rate(
            hole_size, upstream_pressure, downstream_pressure,
            temperature, 0.0, liquid_density, vapor_density
        )["mixture_density_kgm3"] - vapor_density) < 1e-10
    
    @patch('app.core.release.math')
    def test_pipe_release_rate(self, mock_math):
        """Test pipe release rate calculation"""
        # Setup math mock
        mock_math.pi = math.pi
        mock_math.sqrt.side_effect = lambda x: math.sqrt(x)
        mock_math.log10.side_effect = lambda x: math.log10(x)
        
        # Constants for testing
        pipe_diameter = 50.0  # mm
        pipe_length = 10.0  # m
        pressure_differential = 100.0  # kPa
        density = 1000.0  # kg/m³
        viscosity = 0.001  # Pa·s
        
        # Test with fixed friction factor
        results_fixed = ReleaseCalculator.pipe_release_rate(
            pipe_diameter, pipe_length, pressure_differential,
            density, viscosity, friction_factor=0.02
        )
        assert isinstance(results_fixed, dict)
        assert "mass_flow_rate_kgs" in results_fixed
        assert "volumetric_flow_rate_m3s" in results_fixed
        assert "velocity_ms" in results_fixed
        assert "friction_factor" in results_fixed
        assert results_fixed["mass_flow_rate_kgs"] > 0
        assert results_fixed["friction_factor"] == 0.02
        
        # Test with calculated friction factor
        results_calc = ReleaseCalculator.pipe_release_rate(
            pipe_diameter, pipe_length, pressure_differential,
            density, viscosity
        )
        assert results_calc["friction_factor"] > 0
        
        # Test with different pipe diameters
        results_small = ReleaseCalculator.pipe_release_rate(
            25.0, pipe_length, pressure_differential,
            density, viscosity, friction_factor=0.02
        )
        results_large = ReleaseCalculator.pipe_release_rate(
            100.0, pipe_length, pressure_differential,
            density, viscosity, friction_factor=0.02
        )
        assert results_large["mass_flow_rate_kgs"] > results_fixed["mass_flow_rate_kgs"] > results_small["mass_flow_rate_kgs"]
    
    def test_calculate_release_duration(self):
        """Test release duration calculation"""
        # Test normal case
        assert ReleaseCalculator.calculate_release_duration(1000.0, 10.0) == 100.0
        
        # Test edge cases
        assert ReleaseCalculator.calculate_release_duration(0.0, 10.0) == 0.0
        assert math.isinf(ReleaseCalculator.calculate_release_duration(1000.0, 0.0))
    
    def test_calculate_release_quantity(self):
        """Test release quantity calculation"""
        # Test normal case
        assert ReleaseCalculator.calculate_release_quantity(10.0, 100.0) == 1000.0
        
        # Test edge cases
        assert ReleaseCalculator.calculate_release_quantity(0.0, 100.0) == 0.0
        assert ReleaseCalculator.calculate_release_quantity(10.0, 0.0) == 0.0
    
    @patch('app.core.release.math')
    def test_flange_leak_rate(self, mock_math):
        """Test flange leak rate calculation"""
        # Setup math mock
        mock_math.pi = math.pi
        mock_math.sqrt.side_effect = lambda x: math.sqrt(x)
        
        # Constants for testing
        pressure = 1000.0  # kPa
        flange_size = 100.0  # mm
        density = 1000.0  # kg/m³
        
        # Test different leak types
        results_small = ReleaseCalculator.flange_leak_rate(pressure, flange_size, density, "small")
        results_medium = ReleaseCalculator.flange_leak_rate(pressure, flange_size, density, "medium")
        results_large = ReleaseCalculator.flange_leak_rate(pressure, flange_size, density, "large")
        
        assert isinstance(results_small, dict)
        assert "mass_flow_rate_kgs" in results_small
        assert "leak_area_m2" in results_small
        assert results_small["mass_flow_rate_kgs"] > 0
        
        # Check relative leak sizes
        assert results_large["mass_flow_rate_kgs"] > results_medium["mass_flow_rate_kgs"] > results_small["mass_flow_rate_kgs"]
        assert results_large["leak_area_m2"] > results_medium["leak_area_m2"] > results_small["leak_area_m2"]
        
        # Check that leak area scales with flange size
        large_flange_results = ReleaseCalculator.flange_leak_rate(pressure, flange_size * 2, density, "small")
        assert large_flange_results["leak_area_m2"] > results_small["leak_area_m2"] 