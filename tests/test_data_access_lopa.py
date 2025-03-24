import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd

# Add the app directory to the path for imports
app_dir = Path(__file__).parent.parent.absolute() / "app"
sys.path.append(str(app_dir))

# Import the module directly
from app.utils.data_access import LOPAScenarioDAO


@pytest.fixture
def mock_db_manager():
    """Fixture to create a mock database manager"""
    mock_db = MagicMock()
    mock_db.execute_query.return_value = MagicMock()
    mock_db.get_session.return_value = MagicMock()
    return mock_db


class TestLOPAScenarioDAO:
    """Tests for LOPAScenarioDAO class"""
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_all_lopa_scenarios(self, mock_get_db):
        """Test getting all LOPA scenarios"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_scenarios = [
            {"id": 1, "scenario_id": 100, "description": "Scenario 1", "consequence_severity": 3},
            {"id": 2, "scenario_id": 101, "description": "Scenario 2", "consequence_severity": 4}
        ]
        
        mock_result.__iter__.return_value = [
            MagicMock(_mapping=scenario) for scenario in sample_scenarios
        ]
        
        # Call the method
        result = LOPAScenarioDAO.get_all_lopa_scenarios()
        
        # Verify the result
        assert mock_db.execute_query.called
        assert len(result) == 2
        assert result[0]["description"] == "Scenario 1"
        assert result[1]["description"] == "Scenario 2"
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_lopa_scenario_by_id(self, mock_get_db):
        """Test getting a LOPA scenario by ID"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_scenario = {"id": 1, "scenario_id": 100, "description": "Scenario 1", "consequence_severity": 3}
        
        mock_result.rowcount = 1
        mock_result.fetchone.return_value = MagicMock(_mapping=sample_scenario)
        
        # Call the method
        result = LOPAScenarioDAO.get_lopa_scenario_by_id(1)
        
        # Verify the result
        assert mock_db.execute_query.called
        assert result["description"] == "Scenario 1"
        assert result["consequence_severity"] == 3
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_lopa_scenarios_by_scenario(self, mock_get_db):
        """Test getting LOPA scenarios by base scenario ID"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_scenarios = [
            {"id": 1, "scenario_id": 100, "description": "LOPA 1 for Scenario 100", "consequence_severity": 3},
            {"id": 3, "scenario_id": 100, "description": "LOPA 2 for Scenario 100", "consequence_severity": 4}
        ]
        
        mock_result.__iter__.return_value = [
            MagicMock(_mapping=scenario) for scenario in sample_scenarios
        ]
        
        # Call the method
        result = LOPAScenarioDAO.get_lopa_scenarios_by_scenario(100)
        
        # Verify the result
        assert mock_db.execute_query.called
        assert len(result) == 2
        assert all(scenario["scenario_id"] == 100 for scenario in result)
    
    @patch('app.utils.data_access.get_db_manager')
    def test_add_or_update_lopa_scenario_add(self, mock_get_db):
        """Test adding a new LOPA scenario"""
        # Setup mock
        mock_db = mock_get_db.return_value
        
        # Create sample data
        new_scenario = {
            "scenario_id": 100,
            "description": "New LOPA Scenario", 
            "consequence_description": "Fire potential",
            "consequence_category": "Fire",
            "consequence_severity": 3,
            "initiating_event": "Pump seal failure",
            "initiating_event_frequency": 0.1,
            "target_mitigated_frequency": 1e-5
        }
        
        # Call the method
        result = LOPAScenarioDAO.add_or_update_lopa_scenario(new_scenario)
        
        # Verify the result
        assert result is True
        mock_db.execute_query.assert_called_once()
        
        # Check that the first arg contains INSERT
        args, _ = mock_db.execute_query.call_args
        assert "INSERT INTO lopa_scenarios" in str(args[0])
    
    @patch('app.utils.data_access.get_db_manager')
    def test_add_or_update_lopa_scenario_update(self, mock_get_db):
        """Test updating an existing LOPA scenario"""
        # Setup mock
        mock_db = mock_get_db.return_value
        
        # Create sample data
        update_scenario = {
            "id": 1,
            "scenario_id": 100,
            "description": "Updated LOPA Scenario", 
            "consequence_description": "Updated consequence",
            "consequence_category": "Fire",
            "consequence_severity": 4,
            "initiating_event": "Updated event",
            "initiating_event_frequency": 0.2,
            "target_mitigated_frequency": 1e-6
        }
        
        # Call the method
        result = LOPAScenarioDAO.add_or_update_lopa_scenario(update_scenario)
        
        # Verify the result
        assert result is True
        mock_db.execute_query.assert_called_once()
        
        # Check that the first arg contains UPDATE
        args, _ = mock_db.execute_query.call_args
        assert "UPDATE lopa_scenarios SET" in str(args[0])
    
    @patch('app.utils.data_access.get_db_manager')
    def test_delete_lopa_scenario(self, mock_get_db):
        """Test deleting a LOPA scenario"""
        # Setup mock
        mock_db = mock_get_db.return_value
        
        # Call the method
        result = LOPAScenarioDAO.delete_lopa_scenario(1)
        
        # Verify the result
        assert result is True
        assert mock_db.execute_query.call_count == 2  # One for IPLs, one for LOPA scenario
        
        # Check that the last call contains DELETE FROM lopa_scenarios
        calls = mock_db.execute_query.call_args_list
        assert "DELETE FROM lopa_scenarios" in str(calls[1][0][0])
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_lopa_summary(self, mock_get_db):
        """Test getting a summary of all LOPA scenarios"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_summary = [
            {
                "id": 1, 
                "scenario_id": 100,
                "description": "LOPA 1",
                "consequence_category": "Fire",
                "consequence_severity": 3,
                "initiating_event": "Pump seal failure",
                "initiating_event_frequency": 0.1,
                "target_mitigated_frequency": 1e-5,
                "ipl_count": 2,
                "node": "Node 1",
                "deviation": "High Pressure"
            },
            {
                "id": 2, 
                "scenario_id": 101,
                "description": "LOPA 2",
                "consequence_category": "Toxic Release",
                "consequence_severity": 4,
                "initiating_event": "Valve failure",
                "initiating_event_frequency": 0.05,
                "target_mitigated_frequency": 1e-6,
                "ipl_count": 3,
                "node": "Node 2",
                "deviation": "Low Flow"
            }
        ]
        
        mock_result.__iter__.return_value = [
            MagicMock(_mapping=row) for row in sample_summary
        ]
        
        # Call the method
        result = LOPAScenarioDAO.get_lopa_summary()
        
        # Verify the result
        assert mock_db.execute_query.called
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "ipl_count" in result.columns
        assert "description" in result.columns 