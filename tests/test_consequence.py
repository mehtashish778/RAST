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
import app.core.consequence
from app.core.consequence import ConsequenceCalculator


class TestConsequenceCalculator:
    """Tests for ConsequenceCalculator class"""
    
    def test_calculate_risk_score(self):
        """Test risk score calculation"""
        # Test normal cases
        assert ConsequenceCalculator.calculate_risk_score(3, 4) == 12
        assert ConsequenceCalculator.calculate_risk_score(1, 1) == 1
        assert ConsequenceCalculator.calculate_risk_score(5, 5) == 25
        
        # Test edge cases
        assert ConsequenceCalculator.calculate_risk_score(0, 4) == 4  # Should clamp to minimum 1
        assert ConsequenceCalculator.calculate_risk_score(3, 0) == 3  # Should clamp to minimum 1
        assert ConsequenceCalculator.calculate_risk_score(6, 4) == 20  # Should clamp to maximum 5
    
    def test_get_risk_category(self):
        """Test risk category determination"""
        # Test category boundaries
        assert ConsequenceCalculator.get_risk_category(1) == "Low"
        assert ConsequenceCalculator.get_risk_category(4) == "Low"
        assert ConsequenceCalculator.get_risk_category(5) == "Medium"
        assert ConsequenceCalculator.get_risk_category(9) == "Medium"
        assert ConsequenceCalculator.get_risk_category(10) == "High"
        assert ConsequenceCalculator.get_risk_category(16) == "High"
        assert ConsequenceCalculator.get_risk_category(17) == "Very High"
        assert ConsequenceCalculator.get_risk_category(25) == "Very High"
    
    @patch('app.core.consequence.math')
    def test_estimate_release_rate(self, mock_math):
        """Test release rate estimation"""
        # Setup math mock
        mock_math.sqrt.side_effect = lambda x: math.sqrt(x)
        mock_math.pi = math.pi
        
        # Test with typical values
        release_rate = ConsequenceCalculator.estimate_release_rate(10.0, 500.0, 1000.0)
        assert release_rate > 0
        assert isinstance(release_rate, float)
        
        # Test proportionality
        release_rate1 = ConsequenceCalculator.estimate_release_rate(10.0, 500.0, 1000.0)
        release_rate2 = ConsequenceCalculator.estimate_release_rate(20.0, 500.0, 1000.0)
        assert release_rate2 > release_rate1  # Bigger hole, higher rate
        
        # Test zero case
        release_rate_zero = ConsequenceCalculator.estimate_release_rate(0.0, 500.0, 1000.0)
        assert release_rate_zero == 0
    
    @patch('app.core.consequence.math')
    def test_estimate_dispersion_distance(self, mock_math):
        """Test dispersion distance estimation"""
        # Setup math mock
        mock_math.sqrt.side_effect = lambda x: math.sqrt(x)
        mock_math.pow.side_effect = lambda x, y: math.pow(x, y)
        
        # Test basic functionality
        distance = ConsequenceCalculator.estimate_dispersion_distance(1.0, 5.0, "D")
        assert distance > 0
        assert isinstance(distance, float)
        
        # Test different stability classes
        distance_unstable = ConsequenceCalculator.estimate_dispersion_distance(1.0, 5.0, "A")
        distance_stable = ConsequenceCalculator.estimate_dispersion_distance(1.0, 5.0, "F")
        assert distance_stable > distance_unstable  # Stable atmosphere leads to greater distances
    
    def test_assess_risk(self):
        """Test risk assessment function"""
        # Test low risk case
        low_risk = ConsequenceCalculator.assess_risk(1, 2)
        assert low_risk["risk_score"] == 2
        assert low_risk["risk_category"] == "Low"
        assert low_risk["needs_lopa"] is False
        
        # Test high risk case
        high_risk = ConsequenceCalculator.assess_risk(4, 4)
        assert high_risk["risk_score"] == 16
        assert high_risk["risk_category"] == "High"
        assert high_risk["needs_lopa"] is True
        
        # Test very high risk case
        very_high_risk = ConsequenceCalculator.assess_risk(5, 5)
        assert very_high_risk["risk_score"] == 25
        assert very_high_risk["risk_category"] == "Very High"
        assert very_high_risk["needs_lopa"] is True
    
    @patch('app.core.consequence.math')
    def test_fire_consequence(self, mock_math):
        """Test fire consequence estimation"""
        # Setup math mock
        mock_math.pow.side_effect = lambda x, y: math.pow(x, y)
        mock_math.sqrt.side_effect = lambda x: math.sqrt(x)
        
        # Test with typical values
        fire_results = ConsequenceCalculator.estimate_fire_consequence(2.0, 45000.0)
        assert isinstance(fire_results, dict)
        assert "heat_release_rate_kw" in fire_results
        assert "flame_height_m" in fire_results
        assert "radiation_distance_m" in fire_results
        assert fire_results["heat_release_rate_kw"] == 2.0 * 45000.0
        
        # Test zero case
        zero_results = ConsequenceCalculator.estimate_fire_consequence(0.0, 45000.0)
        assert zero_results["heat_release_rate_kw"] == 0
    
    @patch('app.core.consequence.math')
    def test_explosion_consequence(self, mock_math):
        """Test explosion consequence estimation"""
        # Setup math mock
        mock_math.pow.side_effect = lambda x, y: math.pow(x, y)
        mock_math.cbrt = lambda x: x ** (1/3)
        
        # Test with typical values
        explosion_results = ConsequenceCalculator.estimate_explosion_consequence(100.0, 0.1)
        assert isinstance(explosion_results, dict)
        assert "tnt_equivalent_kg" in explosion_results
        assert "distance_window_breakage_m" in explosion_results
        assert "distance_structural_damage_m" in explosion_results
        assert "distance_severe_damage_m" in explosion_results
        assert explosion_results["tnt_equivalent_kg"] == 10.0  # 100 * 0.1
        
        # Test proportionality
        small_explosion = ConsequenceCalculator.estimate_explosion_consequence(50.0, 0.1)
        large_explosion = ConsequenceCalculator.estimate_explosion_consequence(100.0, 0.1)
        assert large_explosion["distance_window_breakage_m"] > small_explosion["distance_window_breakage_m"] 