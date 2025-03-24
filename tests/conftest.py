import pytest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pandas as pd

# Add the app directory to the path for imports
app_dir = Path(__file__).parent.parent.absolute() / "app"
sys.path.append(str(app_dir))


@pytest.fixture
def sample_chemical_data():
    """Fixture providing sample chemical data"""
    return {
        "name": "Test Chemical",
        "formula": "C2H6O",
        "cas_number": "64-17-5",
        "molecular_weight": 46.07,
        "boiling_point": 78.37,
        "flash_point": 13,
        "properties": '{"erpg_2": 3000, "idlh": 3300}'
    }


@pytest.fixture
def sample_equipment_data():
    """Fixture providing sample equipment data"""
    return {
        "tag": "R-101",
        "name": "Reactor",
        "type": "CSTR",
        "description": "Main reaction vessel",
        "design_pressure": 10.0,
        "design_temperature": 150.0,
        "design_code": "ASME VIII",
        "materials": "Carbon Steel",
        "notes": "Sample reactor data"
    }


@pytest.fixture
def sample_scenario_data():
    """Fixture providing sample scenario data"""
    return {
        "equipment_id": 1,
        "node": "Reactor Feed",
        "deviation": "High Temperature",
        "causes": "Control valve failure\nExothermic reaction",
        "consequences": "Runaway reaction\nPressure increase",
        "safeguards": "High temperature alarm\nPressure relief valve",
        "recommendations": "Add high temperature interlock\nReview relief valve sizing",
        "risk_category": "High",
        "attributes": {"severity": 4, "likelihood": 3}
    }


@pytest.fixture
def sample_dataframe():
    """Fixture providing a sample pandas DataFrame"""
    return pd.DataFrame([
        {"name": "Methane", "formula": "CH4", "molecular_weight": 16.04},
        {"name": "Ethane", "formula": "C2H6", "molecular_weight": 30.07},
        {"name": "Propane", "formula": "C3H8", "molecular_weight": 44.10}
    ])


@pytest.fixture
def mock_db_connection():
    """Fixture providing a mock database connection"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.isolation_level = None
    return mock_conn


@pytest.fixture
def mock_db_session():
    """Fixture providing a mock database session"""
    mock_session = MagicMock()
    return mock_session


# Set up test environment variables
def pytest_configure(config):
    """Configure pytest environment"""
    os.environ["TESTING"] = "True"
    os.environ["DB_PATH"] = ":memory:"  # Use in-memory SQLite for testing 