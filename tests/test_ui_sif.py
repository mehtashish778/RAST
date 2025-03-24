import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
import sys
import os
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.pages.lopa import LOPAPage
from app.core.sif import SIF, SIFSubsystem, SIL

# Create QApplication instance for testing
app = None
def setup_module():
    global app
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

class TestSIFUI:
    @pytest.fixture
    def mock_db(self):
        """Create a mock database with required methods"""
        mock = MagicMock()
        # Setup the mock to return test data
        mock.get_sif_by_id.return_value = SIF(
            name="Test SIF",
            subsystems=[
                SIFSubsystem(
                    name="Test Sensor",
                    architecture="1oo2",
                    pfd_per_component=0.01,
                    beta=0.1,
                    test_interval_months=12,
                    dc=0.9,
                    mttr_hours=8,
                    subsystem_type="Sensor"
                ),
                SIFSubsystem(
                    name="Test Logic",
                    architecture="1oo1",
                    pfd_per_component=0.001,
                    beta=0.1,
                    test_interval_months=12,
                    dc=0.99,
                    mttr_hours=8,
                    subsystem_type="Logic Solver"
                ),
                SIFSubsystem(
                    name="Test Final Element",
                    architecture="1oo1",
                    pfd_per_component=0.01,
                    beta=0.1,
                    test_interval_months=12,
                    dc=0.9,
                    mttr_hours=8,
                    subsystem_type="Final Element"
                )
            ],
            target_sil=SIL(3)
        )
        mock.get_all_sifs.return_value = [
            SIF(
                name="Test SIF 1",
                subsystems=[
                    SIFSubsystem(
                        name="Test Sensor",
                        architecture="1oo2",
                        pfd_per_component=0.01,
                        beta=0.1,
                        test_interval_months=12,
                        dc=0.9,
                        mttr_hours=8,
                        subsystem_type="Sensor"
                    ),
                    SIFSubsystem(
                        name="Test Logic",
                        architecture="1oo1",
                        pfd_per_component=0.001,
                        beta=0.1,
                        test_interval_months=12,
                        dc=0.99,
                        mttr_hours=8,
                        subsystem_type="Logic Solver"
                    ),
                    SIFSubsystem(
                        name="Test Final Element",
                        architecture="1oo1",
                        pfd_per_component=0.01,
                        beta=0.1,
                        test_interval_months=12,
                        dc=0.9,
                        mttr_hours=8,
                        subsystem_type="Final Element"
                    )
                ],
                target_sil=SIL(3)
            ),
            SIF(
                name="Test SIF 2",
                subsystems=[
                    SIFSubsystem(
                        name="Test Sensor 2",
                        architecture="1oo1",
                        pfd_per_component=0.01,
                        beta=0.1,
                        test_interval_months=12,
                        dc=0.9,
                        mttr_hours=8,
                        subsystem_type="Sensor"
                    ),
                    SIFSubsystem(
                        name="Test Logic 2",
                        architecture="1oo1",
                        pfd_per_component=0.001,
                        beta=0.1,
                        test_interval_months=12,
                        dc=0.99,
                        mttr_hours=8,
                        subsystem_type="Logic Solver"
                    ),
                    SIFSubsystem(
                        name="Test Final Element 2",
                        architecture="1oo1",
                        pfd_per_component=0.01,
                        beta=0.1,
                        test_interval_months=12,
                        dc=0.9,
                        mttr_hours=8,
                        subsystem_type="Final Element"
                    )
                ],
                target_sil=SIL(2)
            )
        ]
        return mock

    @pytest.fixture
    def lopa_page(self, mock_db):
        """Create a LOPA page with a mocked database"""
        with patch('app.pages.lopa.SIFDAO', return_value=mock_db):
            page = LOPAPage()
            # Initialize the SIF tab
            page.init_sif_tab()
            return page

    def test_sif_tab_initialization(self, lopa_page):
        """Test that the SIF tab is properly initialized"""
        # Check that the SIF tab exists
        assert lopa_page.tabWidget.count() >= 2  # Should have at least 2 tabs
        assert lopa_page.tabWidget.tabText(1) == "SIF Assessment"  # Second tab should be SIF Assessment
        
        # Check that the SIF table is populated
        assert lopa_page.sif_table.rowCount() > 0
        
    def test_add_sif_button(self, lopa_page, mock_db):
        """Test that clicking the Add SIF button opens the dialog"""
        with patch('app.pages.lopa.SIFDialog') as mock_dialog:
            # Setup the mock dialog
            mock_instance = MagicMock()
            mock_dialog.return_value = mock_instance
            mock_instance.exec_.return_value = True
            mock_instance.get_sif.return_value = SIF(
                name="New Test SIF",
                subsystems=[
                    SIFSubsystem(
                        name="New Sensor",
                        architecture="1oo1",
                        pfd_per_component=0.01,
                        beta=0.1,
                        test_interval_months=12,
                        dc=0.9,
                        mttr_hours=8,
                        subsystem_type="Sensor"
                    ),
                    SIFSubsystem(
                        name="New Logic",
                        architecture="1oo1",
                        pfd_per_component=0.001,
                        beta=0.1,
                        test_interval_months=12,
                        dc=0.99,
                        mttr_hours=8,
                        subsystem_type="Logic Solver"
                    ),
                    SIFSubsystem(
                        name="New Final Element",
                        architecture="1oo1",
                        pfd_per_component=0.01,
                        beta=0.1,
                        test_interval_months=12,
                        dc=0.9,
                        mttr_hours=8,
                        subsystem_type="Final Element"
                    )
                ],
                target_sil=SIL(3)
            )
            
            # Click the add button
            lopa_page.btn_add_sif.click()
            
            # Check that the dialog was shown
            mock_dialog.assert_called_once()
            mock_instance.exec_.assert_called_once()
            
            # Check that the SIF was added to the database
            mock_db.add_or_update_sif.assert_called_once()
    
    def test_edit_sif_button(self, lopa_page, mock_db):
        """Test that clicking the Edit SIF button opens the dialog with the selected SIF"""
        with patch('app.pages.lopa.SIFDialog') as mock_dialog:
            # Setup the mock dialog
            mock_instance = MagicMock()
            mock_dialog.return_value = mock_instance
            mock_instance.exec_.return_value = True
            mock_instance.get_sif.return_value = SIF(
                name="Updated Test SIF",
                subsystems=[
                    SIFSubsystem(
                        name="Updated Sensor",
                        architecture="1oo1",
                        pfd_per_component=0.01,
                        beta=0.1,
                        test_interval_months=12,
                        dc=0.9,
                        mttr_hours=8,
                        subsystem_type="Sensor"
                    ),
                    SIFSubsystem(
                        name="Updated Logic",
                        architecture="1oo1",
                        pfd_per_component=0.001,
                        beta=0.1,
                        test_interval_months=12,
                        dc=0.99,
                        mttr_hours=8,
                        subsystem_type="Logic Solver"
                    ),
                    SIFSubsystem(
                        name="Updated Final Element",
                        architecture="1oo1",
                        pfd_per_component=0.01,
                        beta=0.1,
                        test_interval_months=12,
                        dc=0.9,
                        mttr_hours=8,
                        subsystem_type="Final Element"
                    )
                ],
                target_sil=SIL(3)
            )
            
            # Select the first row in the SIF table
            lopa_page.sif_table.selectRow(0)
            
            # Click the edit button
            lopa_page.btn_edit_sif.click()
            
            # Check that the dialog was shown with the correct SIF
            mock_dialog.assert_called_once()
            mock_dialog.assert_called_with(existing_sif=mock_db.get_sif_by_id())
            mock_instance.exec_.assert_called_once()
            
            # Check that the SIF was updated in the database
            mock_db.add_or_update_sif.assert_called_once()
    
    def test_delete_sif_button(self, lopa_page, mock_db):
        """Test that clicking the Delete SIF button deletes the selected SIF"""
        with patch('PyQt5.QtWidgets.QMessageBox.question') as mock_question:
            # Setup the mock question dialog to return "Yes"
            mock_question.return_value = QApplication.instance().style().standardIcon(QApplication.instance().style().SP_DialogOkButton)
            
            # Select the first row in the SIF table
            lopa_page.sif_table.selectRow(0)
            
            # Get the ID of the selected SIF
            sif_id = lopa_page.sif_table.item(0, 0).data(Qt.UserRole)
            
            # Click the delete button
            lopa_page.btn_delete_sif.click()
            
            # Check that the confirmation dialog was shown
            mock_question.assert_called_once()
            
            # Check that the SIF was deleted from the database
            mock_db.delete_sif.assert_called_once_with(sif_id)
    
    def test_verify_sif_button(self, lopa_page, mock_db):
        """Test that clicking the Verify SIF button shows the verification results"""
        with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
            # Select the first row in the SIF table
            lopa_page.sif_table.selectRow(0)
            
            # Click the verify button
            lopa_page.btn_verify_sif.click()
            
            # Check that the information dialog was shown with verification results
            mock_info.assert_called_once()
            
    def test_sif_details_view(self, lopa_page, mock_db):
        """Test that selecting a SIF shows its details"""
        # Select the first row in the SIF table
        lopa_page.sif_table.selectRow(0)
        
        # Get the ID of the selected SIF
        sif_id = lopa_page.sif_table.item(0, 0).data(Qt.UserRole)
        
        # Check that the SIF details were loaded
        mock_db.get_sif_by_id.assert_called_with(sif_id)
        
        # Check that the subsystems table is populated
        assert lopa_page.subsystem_table.rowCount() > 0 