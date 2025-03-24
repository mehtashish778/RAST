import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the app directory to the path for imports
app_dir = Path(__file__).parent.parent.absolute() / "app"
sys.path.append(str(app_dir))

# Import the module directly
from app.utils.data_access import IPLDAO


@pytest.fixture
def mock_db_manager():
    """Fixture to create a mock database manager"""
    mock_db = MagicMock()
    mock_db.execute_query.return_value = MagicMock()
    mock_db.get_session.return_value = MagicMock()
    return mock_db


class TestIPLDAO:
    """Tests for IPLDAO class"""
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_all_ipls(self, mock_get_db):
        """Test getting all IPLs"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_ipls = [
            {"id": 1, "name": "BPCS Control", "ipl_type": "BPCS", "pfd": 0.1},
            {"id": 2, "name": "Relief Valve", "ipl_type": "RELIEF", "pfd": 0.01}
        ]
        
        mock_result.__iter__.return_value = [
            MagicMock(_mapping=ipl) for ipl in sample_ipls
        ]
        
        # Call the method
        result = IPLDAO.get_all_ipls()
        
        # Verify the result
        assert mock_db.execute_query.called
        assert len(result) == 2
        assert result[0]["name"] == "BPCS Control"
        assert result[1]["name"] == "Relief Valve"
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_ipl_by_id(self, mock_get_db):
        """Test getting an IPL by ID"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_ipl = {"id": 1, "name": "BPCS Control", "ipl_type": "BPCS", "pfd": 0.1}
        
        mock_result.rowcount = 1
        mock_result.fetchone.return_value = MagicMock(_mapping=sample_ipl)
        
        # Call the method
        result = IPLDAO.get_ipl_by_id(1)
        
        # Verify the result
        assert mock_db.execute_query.called
        assert result["name"] == "BPCS Control"
        assert result["pfd"] == 0.1
    
    @patch('app.utils.data_access.get_db_manager')
    def test_get_ipls_by_scenario(self, mock_get_db):
        """Test getting IPLs by scenario ID"""
        # Setup mock
        mock_db = mock_get_db.return_value
        mock_result = MagicMock()
        mock_db.execute_query.return_value = mock_result
        
        # Create sample data
        sample_ipls = [
            {"id": 1, "name": "BPCS Control", "ipl_type": "BPCS", "pfd": 0.1, "scenario_id": 100},
            {"id": 3, "name": "Alarm", "ipl_type": "ALARM", "pfd": 0.1, "scenario_id": 100}
        ]
        
        mock_result.__iter__.return_value = [
            MagicMock(_mapping=ipl) for ipl in sample_ipls
        ]
        
        # Call the method
        result = IPLDAO.get_ipls_by_scenario(100)
        
        # Verify the result
        assert mock_db.execute_query.called
        assert len(result) == 2
        assert all(ipl["scenario_id"] == 100 for ipl in result)
    
    @patch('app.utils.data_access.get_db_manager')
    def test_add_or_update_ipl_add(self, mock_get_db):
        """Test adding a new IPL"""
        # Setup mock
        mock_db = mock_get_db.return_value
        
        # Create sample data
        new_ipl = {
            "name": "New IPL", 
            "description": "Test Description",
            "ipl_type": "SIS", 
            "pfd": 0.01, 
            "scenario_id": 100
        }
        
        # Call the method
        result = IPLDAO.add_or_update_ipl(new_ipl)
        
        # Verify the result
        assert result is True
        mock_db.execute_query.assert_called_once()
        
        # Check that the first arg contains INSERT
        args, _ = mock_db.execute_query.call_args
        assert "INSERT INTO ipls" in str(args[0])
    
    @patch('app.utils.data_access.get_db_manager')
    def test_add_or_update_ipl_update(self, mock_get_db):
        """Test updating an existing IPL"""
        # Setup mock
        mock_db = mock_get_db.return_value
        
        # Create sample data
        update_ipl = {
            "id": 1,
            "name": "Updated IPL", 
            "description": "Updated Description",
            "ipl_type": "SIS", 
            "pfd": 0.001, 
            "scenario_id": 100
        }
        
        # Call the method
        result = IPLDAO.add_or_update_ipl(update_ipl)
        
        # Verify the result
        assert result is True
        mock_db.execute_query.assert_called_once()
        
        # Check that the first arg contains UPDATE
        args, _ = mock_db.execute_query.call_args
        assert "UPDATE ipls SET" in str(args[0])
    
    @patch('app.utils.data_access.get_db_manager')
    def test_delete_ipl(self, mock_get_db):
        """Test deleting an IPL"""
        # Setup mock
        mock_db = mock_get_db.return_value
        
        # Call the method
        result = IPLDAO.delete_ipl(1)
        
        # Verify the result
        assert result is True
        mock_db.execute_query.assert_called_once()
        
        # Check that the first arg contains DELETE
        args, _ = mock_db.execute_query.call_args
        assert "DELETE FROM ipls" in str(args[0]) 