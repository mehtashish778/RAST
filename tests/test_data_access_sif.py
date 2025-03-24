import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the app directory to the path for imports
app_dir = Path(__file__).parent.parent.absolute() / "app"
sys.path.append(str(app_dir))

# Import the module directly
from app.utils.data_access import SIFDAO


@pytest.fixture
def mock_db_manager():
    """Fixture to create a mock database manager"""
    mock_db = MagicMock()
    mock_db.execute_query.return_value = MagicMock()
    mock_db.get_session.return_value = MagicMock()
    return mock_db


class TestSIFDAO:
    """Tests for SIFDAO class"""
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_all_sifs(self, mock_get_db):
        """Test getting all SIFs"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_sifs = [
            {"id": 1, "name": "High Pressure Shutdown", "required_sil": 2, "scenario_id": 100},
            {"id": 2, "name": "Low Level Trip", "required_sil": 1, "scenario_id": 101}
        ]
        
        mock_result.__iter__.return_value = [
            MagicMock(_mapping=sif) for sif in sample_sifs
        ]
        
        # Call the method
        result = SIFDAO.get_all_sifs()
        
        # Verify the result
        assert mock_db.execute_query.called
        assert len(result) == 2
        assert result[0]["name"] == "High Pressure Shutdown"
        assert result[1]["name"] == "Low Level Trip"
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_sif_by_id(self, mock_get_db):
        """Test getting a SIF by ID"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_sif = {"id": 1, "name": "High Pressure Shutdown", "required_sil": 2, "scenario_id": 100}
        
        mock_result.rowcount = 1
        mock_result.fetchone.return_value = MagicMock(_mapping=sample_sif)
        
        # Call the method
        result = SIFDAO.get_sif_by_id(1)
        
        # Verify the result
        assert mock_db.execute_query.called
        assert result["name"] == "High Pressure Shutdown"
        assert result["required_sil"] == 2
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_sifs_by_scenario(self, mock_get_db):
        """Test getting SIFs by scenario ID"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_sifs = [
            {"id": 1, "name": "High Pressure Shutdown", "required_sil": 2, "scenario_id": 100},
            {"id": 3, "name": "High Temperature Shutdown", "required_sil": 2, "scenario_id": 100}
        ]
        
        mock_result.__iter__.return_value = [
            MagicMock(_mapping=sif) for sif in sample_sifs
        ]
        
        # Call the method
        result = SIFDAO.get_sifs_by_scenario(100)
        
        # Verify the result
        assert mock_db.execute_query.called
        assert len(result) == 2
        assert all(sif["scenario_id"] == 100 for sif in result)
    
    @patch('app.utils.data_access.get_db_manager')
    def test_add_or_update_sif_add(self, mock_get_db):
        """Test adding a new SIF"""
        # Setup mock
        mock_db = mock_get_db.return_value
        
        # Create sample data
        new_sif = {
            "name": "New SIF", 
            "description": "Test Description",
            "required_sil": 3,
            "process_safety_time": 30,
            "scenario_id": 100
        }
        
        # Call the method
        result = SIFDAO.add_or_update_sif(new_sif)
        
        # Verify the result
        assert result is True
        mock_db.execute_query.assert_called_once()
        
        # Check that the first arg contains INSERT
        args, _ = mock_db.execute_query.call_args
        assert "INSERT INTO sifs" in str(args[0])
    
    @patch('app.utils.data_access.get_db_manager')
    def test_add_or_update_sif_update(self, mock_get_db):
        """Test updating an existing SIF"""
        # Setup mock
        mock_db = mock_get_db.return_value
        
        # Create sample data
        update_sif = {
            "id": 1,
            "name": "Updated SIF", 
            "description": "Updated Description",
            "required_sil": 3,
            "process_safety_time": 30,
            "scenario_id": 100
        }
        
        # Call the method
        result = SIFDAO.add_or_update_sif(update_sif)
        
        # Verify the result
        assert result is True
        mock_db.execute_query.assert_called_once()
        
        # Check that the first arg contains UPDATE
        args, _ = mock_db.execute_query.call_args
        assert "UPDATE sifs SET" in str(args[0])
    
    @patch('app.utils.data_access.get_db_manager')
    def test_delete_sif(self, mock_get_db):
        """Test deleting a SIF"""
        # Setup mock
        mock_db = mock_get_db.return_value
        
        # Call the method
        result = SIFDAO.delete_sif(1)
        
        # Verify the result
        assert result is True
        assert mock_db.execute_query.call_count == 2  # One for subsystems, one for SIF
        
        # Check that the last call contains DELETE FROM sifs
        calls = mock_db.execute_query.call_args_list
        assert "DELETE FROM sifs" in str(calls[1][0][0])
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_subsystems_by_sif(self, mock_get_db):
        """Test getting subsystems by SIF ID"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_subsystems = [
            {"id": 1, "sif_id": 1, "name": "Sensor Subsystem", "architecture": "1oo2"},
            {"id": 2, "sif_id": 1, "name": "Logic Solver", "architecture": "1oo1"},
            {"id": 3, "sif_id": 1, "name": "Final Element", "architecture": "1oo2"}
        ]
        
        mock_result.__iter__.return_value = [
            MagicMock(_mapping=subsystem) for subsystem in sample_subsystems
        ]
        
        # Call the method
        result = SIFDAO.get_subsystems_by_sif(1)
        
        # Verify the result
        assert mock_db.execute_query.called
        assert len(result) == 3
        assert all(subsystem["sif_id"] == 1 for subsystem in result)
    
    @patch('app.utils.data_access.get_db_manager')
    def test_add_or_update_subsystem(self, mock_get_db):
        """Test adding a new subsystem"""
        # Setup mock
        mock_db = mock_get_db.return_value
        
        # Create sample data
        new_subsystem = {
            "sif_id": 1,
            "name": "Sensor Subsystem", 
            "architecture": "1oo2",
            "pfd_per_component": 0.01,
            "test_interval_months": 12
        }
        
        # Call the method
        result = SIFDAO.add_or_update_subsystem(new_subsystem)
        
        # Verify the result
        assert result is True
        mock_db.execute_query.assert_called_once()
        
        # Check that the first arg contains INSERT
        args, _ = mock_db.execute_query.call_args
        assert "INSERT INTO sif_subsystems" in str(args[0]) 