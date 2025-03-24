import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import sqlite3
import tempfile
import sqlalchemy as sa
from sqlalchemy import text

# Add the app directory to the path for imports
app_dir = Path(__file__).parent.parent.absolute() / "app"
sys.path.append(str(app_dir))

from app.utils.database import DatabaseManager


class TestDatabaseManager:
    """Test the DatabaseManager class"""
    
    @pytest.fixture(autouse=True)
    def setup_mocks(self, monkeypatch):
        """Set up a test database path and mock os.makedirs"""
        # Create a temporary file path for testing
        self.test_db_path = os.path.join(tempfile.gettempdir(), 'test_db.sqlite')
        
        # Mock os.makedirs to prevent directory creation
        monkeypatch.setattr(os, 'makedirs', MagicMock())
        
    def test_initialization(self):
        """Test database manager initialization"""
        db_manager = DatabaseManager(self.test_db_path)
        assert db_manager.db_path == self.test_db_path
        assert db_manager.connection_string == f"sqlite:///{self.test_db_path}"
        
    @patch('sqlalchemy.create_engine')
    def test_connect(self, mock_create_engine):
        """Test database connection"""
        # Setup mock
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        # Create instance and connect
        db_manager = DatabaseManager(self.test_db_path)
        result = db_manager.connect()
        
        # Verify connection
        assert result is True
        mock_create_engine.assert_any_call(f"sqlite:///{self.test_db_path}")
        
    @patch('sqlalchemy.create_engine')
    def test_connect_exception(self, mock_create_engine):
        """Test database connection failure"""
        # Setup mock to raise exception
        mock_create_engine.side_effect = Exception("Connection failed")
        
        # Create instance and try to connect
        db_manager = DatabaseManager(self.test_db_path)
        # Reset the engine since connect is called in __init__
        db_manager.engine = None
        result = db_manager.connect()
        
        # Verify connection failure
        assert result is False
        
    @patch('sqlalchemy.create_engine')
    def test_execute_query(self, mock_create_engine):
        """Test executing a query"""
        # Setup mocks
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        # Mock session
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        
        # Create instance
        db_manager = DatabaseManager(self.test_db_path)
        db_manager.get_session = MagicMock(return_value=mock_session)
        
        # Execute query
        result = db_manager.execute_query("SELECT * FROM test")
        
        # Verify query execution
        assert result is mock_result
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
        
    @patch('sqlalchemy.create_engine')
    def test_execute_query_with_params(self, mock_create_engine):
        """Test executing a query with parameters"""
        # Setup mocks
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        # Mock session
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        
        # Create instance
        db_manager = DatabaseManager(self.test_db_path)
        db_manager.get_session = MagicMock(return_value=mock_session)
        
        # Execute query with parameters
        params = {"id": 1}
        result = db_manager.execute_query("SELECT * FROM test WHERE id = :id", params)
        
        # Verify query execution
        assert result is mock_result
        mock_session.execute.assert_called_once_with("SELECT * FROM test WHERE id = :id", params)
        mock_session.commit.assert_called_once()
        
    @patch('sqlalchemy.create_engine')
    def test_execute_query_exception(self, mock_create_engine):
        """Test handling exception during query execution"""
        # Setup mocks
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        # Mock session
        mock_session = MagicMock()
        mock_session.execute.side_effect = Exception("Query failed")
        
        # Create instance
        db_manager = DatabaseManager(self.test_db_path)
        db_manager.get_session = MagicMock(return_value=mock_session)
        
        # Execute query should handle exception
        result = db_manager.execute_query("SELECT * FROM test")
        
        # Verify exception handling
        assert result is None
        mock_session.rollback.assert_called_once()
        
    @patch('sqlalchemy.create_engine')
    def test_close_session(self, mock_create_engine):
        """Test closing database session"""
        # Setup mocks
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        # Create instance
        db_manager = DatabaseManager(self.test_db_path)
        
        # Mock session
        mock_session = MagicMock()
        
        # Close session
        db_manager.close_session(mock_session)
        
        # Verify connection closed
        mock_session.close.assert_called_once()
        
    @patch('sqlalchemy.create_engine')
    def test_get_session(self, mock_create_engine):
        """Test getting a database session"""
        # Setup mocks
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        # Mock session factory
        mock_session = MagicMock()
        mock_session_factory = MagicMock(return_value=mock_session)
        
        # Create instance
        db_manager = DatabaseManager(self.test_db_path)
        db_manager.Session = mock_session_factory
        
        # Get session
        session = db_manager.get_session()
        
        # Verify session
        assert session is mock_session
        mock_session_factory.assert_called_once() 