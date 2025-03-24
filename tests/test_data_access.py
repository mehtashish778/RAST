import pytest
import sys
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd

# Add the app directory to the path for imports
app_dir = Path(__file__).parent.parent.absolute() / "app"
sys.path.append(str(app_dir))

# Import the module directly
import app.utils.data_access  
from app.utils.data_access import ChemicalDAO, EquipmentDAO, ScenarioDAO


@pytest.fixture
def mock_db_manager():
    """Fixture to create a mock database manager"""
    mock_db = MagicMock()
    mock_db.execute_query.return_value = MagicMock()
    mock_db.get_session.return_value = MagicMock()
    return mock_db


class TestChemicalDAO:
    """Tests for ChemicalDAO class"""
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_all_chemicals(self, mock_get_db):
        """Test getting all chemicals"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_chemicals = [
            {"id": 1, "name": "Methane", "formula": "CH4", "molecular_weight": 16.04},
            {"id": 2, "name": "Ethane", "formula": "C2H6", "molecular_weight": 30.07}
        ]
        
        mock_result.__iter__.return_value = [
            MagicMock(_mapping=chemical) for chemical in sample_chemicals
        ]
        
        # Call the method
        result = ChemicalDAO.get_all_chemicals()
        
        # Verify the result
        assert mock_db.execute_query.called
        assert len(result) == 2
        assert result[0]["name"] == "Methane"
        assert result[1]["name"] == "Ethane"
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_chemical_by_name(self, mock_get_db):
        """Test getting a chemical by name"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_chemical = {"id": 1, "name": "Methane", "formula": "CH4", "molecular_weight": 16.04}
        
        mock_result.rowcount = 1
        mock_result.fetchone.return_value = MagicMock(_mapping=sample_chemical)
        
        # Call the method
        result = ChemicalDAO.get_chemical_by_name("Methane")
        
        # Verify the result
        assert mock_db.execute_query.called
        assert result["name"] == "Methane"
        assert result["formula"] == "CH4"
    
    @patch('app.utils.data_access.get_db_manager')
    def test_add_or_update_chemical_new(self, mock_get_db):
        """Test adding a new chemical"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_existing = MagicMock()
        mock_existing.rowcount = 0
        mock_db.execute_query.return_value = mock_existing
        
        # Create sample data
        new_chemical = {"name": "Propane", "formula": "C3H8", "molecular_weight": 44.1}
        
        # Call the method
        result = ChemicalDAO.add_or_update_chemical(new_chemical)
        
        # Verify the result
        assert result is True
        assert mock_db.execute_query.call_count == 2  # One for check, one for insert
    
    @patch('app.utils.data_access.get_db_manager')
    def test_delete_chemical(self, mock_get_db):
        """Test deleting a chemical"""
        # Setup mock
        mock_db = mock_get_db.return_value
        
        # Call the method
        result = ChemicalDAO.delete_chemical("Methane")
        
        # Verify the result
        assert result is True
        mock_db.execute_query.assert_called_once()


class TestEquipmentDAO:
    """Tests for EquipmentDAO class"""
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_all_equipment(self, mock_get_db):
        """Test getting all equipment"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_equipment = [
            {"id": 1, "tag": "P-101", "name": "Feed Pump", "type": "Centrifugal Pump"},
            {"id": 2, "tag": "E-201", "name": "Heat Exchanger", "type": "Shell and Tube"}
        ]
        
        mock_result.__iter__.return_value = [
            MagicMock(_mapping=equipment) for equipment in sample_equipment
        ]
        
        # Call the method
        result = EquipmentDAO.get_all_equipment()
        
        # Verify the result
        assert mock_db.execute_query.called
        assert len(result) == 2
        assert result[0]["tag"] == "P-101"
        assert result[1]["tag"] == "E-201"
    
    @patch('app.utils.data_access.get_db_manager')
    def test_add_or_update_equipment_update(self, mock_get_db):
        """Test updating an existing equipment"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_existing = MagicMock()
        mock_existing.rowcount = 1
        mock_existing.fetchone.return_value = MagicMock(_mapping={"id": 1})
        mock_db.execute_query.return_value = mock_existing
        
        # Create sample data
        update_equipment = {"tag": "P-101", "name": "Feed Pump Updated", "type": "Centrifugal Pump"}
        
        # Call the method
        result = EquipmentDAO.add_or_update_equipment(update_equipment)
        
        # Verify the result
        assert result is True
        assert mock_db.execute_query.call_count == 2  # One for check, one for update


class TestScenarioDAO:
    """Tests for ScenarioDAO class"""
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_all_scenarios(self, mock_get_db):
        """Test getting all scenarios"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_scenarios = [
            {"id": 1, "node": "Pump Discharge", "deviation": "High Pressure", "equipment_id": 1},
            {"id": 2, "node": "Reactor Feed", "deviation": "Low Flow", "equipment_id": 2}
        ]
        
        mock_result.__iter__.return_value = [
            MagicMock(_mapping=scenario) for scenario in sample_scenarios
        ]
        
        # Call the method
        result = ScenarioDAO.get_all_scenarios()
        
        # Verify the result
        assert mock_db.execute_query.called
        assert len(result) == 2
        assert result[0]["node"] == "Pump Discharge"
        assert result[1]["node"] == "Reactor Feed"
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_scenarios_by_equipment(self, mock_get_db):
        """Test getting scenarios by equipment"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_scenarios = [
            {"id": 1, "node": "Pump Discharge", "deviation": "High Pressure", "equipment_id": 1},
            {"id": 3, "node": "Pump Suction", "deviation": "Low Pressure", "equipment_id": 1}
        ]
        
        mock_result.__iter__.return_value = [
            MagicMock(_mapping=scenario) for scenario in sample_scenarios
        ]
        
        # Call the method
        result = ScenarioDAO.get_scenarios_by_equipment(1)
        
        # Verify the result
        assert mock_db.execute_query.called
        assert len(result) == 2
        assert all(scenario["equipment_id"] == 1 for scenario in result)
    
    @patch('app.utils.data_access.ScenarioDAO.get_available_templates')
    @patch('app.utils.data_access.json.loads')
    def test_get_scenario_template(self, mock_json_loads, mock_get_templates):
        """Test getting a scenario template"""
        # Setup mocks
        mock_get_templates.return_value = ["high_pressure", "low_flow", "high_temperature"]
        mock_json_loads.return_value = {"severity": 3, "likelihood": 3}
        
        # Mock template data 
        app.utils.data_access.ScenarioDAO.TEMPLATES = {
            "high_pressure": {
                "node": "Equipment Discharge",
                "deviation": "More Pressure",
                "attributes": '{"severity": 3, "likelihood": 3}'
            }
        }
        
        # Call the method
        result = ScenarioDAO.get_scenario_template("high_pressure")
        
        # Verify the result
        assert isinstance(result, dict)
        assert "node" in result
        assert "deviation" in result
        assert "attributes" in result
        assert result["deviation"] == "More Pressure"
    
    @patch('app.utils.data_access.ScenarioDAO.TEMPLATES', {
        "high_pressure": {"node": "Equipment Discharge", "deviation": "More Pressure"},
        "low_flow": {"node": "Equipment Inlet", "deviation": "Less Flow"},
        "high_temperature": {"node": "Heat Exchanger", "deviation": "More Temperature"}
    })
    def test_get_available_templates(self):
        """Test getting available templates"""
        # Call the method
        result = ScenarioDAO.get_available_templates()
        
        # Verify the result
        assert isinstance(result, list)
        assert "high_pressure" in result
        assert "low_flow" in result
        assert "high_temperature" in result
        assert len(result) == 3
        
    @patch('app.utils.data_access.get_db_manager')
    def test_add_or_update_scenario(self, mock_get_db):
        """Test adding a new scenario"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_session = MagicMock()
        mock_db.get_session.return_value = mock_session
        
        # Create sample data with attributes
        new_scenario = {
            "equipment_id": 1,
            "node": "Test Node",
            "deviation": "Test Deviation",
            "causes": "Test Causes",
            "consequences": "Test Consequences",
            "attributes": {"severity": 3, "likelihood": 2}
        }
        
        # Call the method
        result = ScenarioDAO.add_or_update_scenario(new_scenario)
        
        # Verify the result
        assert result is True
        assert mock_session.execute.called
        assert mock_session.commit.called 