import pytest
import os
import sys
import sqlite3
import tempfile
from unittest.mock import patch

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.data_access import SIFDAO, create_tables
from app.core.sif import SIF, SIFSubsystem, SIL, SIFVerifier
from app.utils.database import get_db_connection

class TestSIFIntegration:
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        # Create a temporary file for the database
        db_file = tempfile.NamedTemporaryFile(delete=False)
        db_path = db_file.name
        db_file.close()
        
        # Create a connection to the database
        conn = sqlite3.connect(db_path)
        
        # Create the necessary tables
        create_tables(conn)
        
        # Patch the get_db_connection function to return our test connection
        with patch('app.utils.data_access.get_db_connection', return_value=conn):
            yield conn
            
        # Close the connection and remove the database file
        conn.close()
        os.unlink(db_path)
        
    def test_complete_sif_workflow(self, temp_db):
        """Test the complete SIF assessment workflow"""
        # Initialize the DAO
        sif_dao = SIFDAO()
        
        # 1. Create SIF with subsystems
        sensor = SIFSubsystem(
            name="Pressure Sensor",
            architecture="1oo2",
            pfd_per_component=0.01,
            beta=0.1,
            test_interval_months=12,
            dc=0.9,
            mttr_hours=8,
            subsystem_type="Sensor"
        )
        
        logic = SIFSubsystem(
            name="PLC Controller",
            architecture="1oo1",
            pfd_per_component=0.001,
            beta=0.1,
            test_interval_months=12,
            dc=0.99,
            mttr_hours=8,
            subsystem_type="Logic Solver"
        )
        
        final_element = SIFSubsystem(
            name="Shutdown Valve",
            architecture="1oo2",
            pfd_per_component=0.01,
            beta=0.1,
            test_interval_months=12,
            dc=0.9,
            mttr_hours=8,
            subsystem_type="Final Element"
        )
        
        subsystems = [sensor, logic, final_element]
        
        sif = SIF(
            name="High Pressure Protection",
            subsystems=subsystems,
            target_sil=SIL(3)
        )
        
        # 2. Add SIF to database
        sif_id = sif_dao.add_or_update_sif(sif)
        assert sif_id is not None, "SIF ID should not be None"
        
        # 3. Retrieve SIF from database
        retrieved_sif = sif_dao.get_sif_by_id(sif_id)
        assert retrieved_sif is not None, "Retrieved SIF should not be None"
        assert retrieved_sif.name == "High Pressure Protection", "SIF name should match"
        assert retrieved_sif.target_sil.value == 3, "Target SIL should match"
        assert len(retrieved_sif.subsystems) == 3, "SIF should have 3 subsystems"
        
        # Check subsystem details
        subsystem_types = [s.subsystem_type for s in retrieved_sif.subsystems]
        assert "Sensor" in subsystem_types, "SIF should have a Sensor subsystem"
        assert "Logic Solver" in subsystem_types, "SIF should have a Logic Solver subsystem"
        assert "Final Element" in subsystem_types, "SIF should have a Final Element subsystem"
        
        # 4. Calculate and verify PFD
        overall_pfd = retrieved_sif.calculate_overall_pfd()
        assert 0 < overall_pfd < 1, f"Overall PFD should be between 0 and 1, got {overall_pfd}"
        
        # 5. Verify SIL
        verification_result = retrieved_sif.verify()
        assert isinstance(verification_result, bool), "Verification result should be a boolean"
        
        # 6. Update SIF (modify a subsystem)
        retrieved_sif.subsystems[0].architecture = "2oo3"
        retrieved_sif.subsystems[0].pfd_per_component = 0.005
        
        # 7. Save the updated SIF
        updated_id = sif_dao.add_or_update_sif(retrieved_sif)
        assert updated_id == sif_id, "Updated SIF ID should match original ID"
        
        # 8. Retrieve updated SIF
        updated_sif = sif_dao.get_sif_by_id(sif_id)
        assert updated_sif.subsystems[0].architecture == "2oo3", "Architecture should be updated"
        assert updated_sif.subsystems[0].pfd_per_component == 0.005, "PFD per component should be updated"
        
        # 9. Calculate new PFD and compare
        new_overall_pfd = updated_sif.calculate_overall_pfd()
        # The PFD should be different after the update
        assert new_overall_pfd != overall_pfd, "New PFD should be different from original PFD"
        
        # 10. Verify SIL again
        new_verification_result = updated_sif.verify()
        assert isinstance(new_verification_result, bool), "New verification result should be a boolean"
        
        # 11. Delete the SIF
        sif_dao.delete_sif(sif_id)
        
        # 12. Verify SIF was deleted
        deleted_sif = sif_dao.get_sif_by_id(sif_id)
        assert deleted_sif is None, "SIF should be deleted"
        
    def test_multiple_sifs_workflow(self, temp_db):
        """Test workflow with multiple SIFs"""
        # Initialize the DAO
        sif_dao = SIFDAO()
        
        # Create and add multiple SIFs
        sif_ids = []
        
        # Create SIF 1
        subsystems1 = [
            SIFSubsystem(
                name="Temperature Sensor",
                architecture="1oo2",
                pfd_per_component=0.01,
                beta=0.1,
                test_interval_months=12,
                dc=0.9,
                mttr_hours=8,
                subsystem_type="Sensor"
            ),
            SIFSubsystem(
                name="PLC Controller",
                architecture="1oo1",
                pfd_per_component=0.001,
                beta=0.1,
                test_interval_months=12,
                dc=0.99,
                mttr_hours=8,
                subsystem_type="Logic Solver"
            ),
            SIFSubsystem(
                name="Cooling Valve",
                architecture="1oo2",
                pfd_per_component=0.01,
                beta=0.1,
                test_interval_months=12,
                dc=0.9,
                mttr_hours=8,
                subsystem_type="Final Element"
            )
        ]
        
        sif1 = SIF(
            name="High Temperature Protection",
            subsystems=subsystems1,
            target_sil=SIL(2)
        )
        
        # Create SIF 2
        subsystems2 = [
            SIFSubsystem(
                name="Level Sensor",
                architecture="1oo1",
                pfd_per_component=0.01,
                beta=0.1,
                test_interval_months=12,
                dc=0.9,
                mttr_hours=8,
                subsystem_type="Sensor"
            ),
            SIFSubsystem(
                name="Safety PLC",
                architecture="1oo1",
                pfd_per_component=0.001,
                beta=0.1,
                test_interval_months=12,
                dc=0.99,
                mttr_hours=8,
                subsystem_type="Logic Solver"
            ),
            SIFSubsystem(
                name="Drain Valve",
                architecture="1oo1",
                pfd_per_component=0.01,
                beta=0.1,
                test_interval_months=12,
                dc=0.9,
                mttr_hours=8,
                subsystem_type="Final Element"
            )
        ]
        
        sif2 = SIF(
            name="High Level Protection",
            subsystems=subsystems2,
            target_sil=SIL(1)
        )
        
        # Add SIFs to database
        sif_id1 = sif_dao.add_or_update_sif(sif1)
        sif_id2 = sif_dao.add_or_update_sif(sif2)
        
        sif_ids = [sif_id1, sif_id2]
        
        # Get all SIFs
        all_sifs = sif_dao.get_all_sifs()
        assert len(all_sifs) == 2, "Should have 2 SIFs in the database"
        
        # Verify SIFs
        verifier = SIFVerifier()
        
        # Get SIF 1
        sif1_retrieved = sif_dao.get_sif_by_id(sif_id1)
        pfd1 = sif1_retrieved.calculate_overall_pfd()
        result1, _ = verifier.verify_sil(sif1_retrieved.target_sil.value, pfd1)
        
        # Get SIF 2
        sif2_retrieved = sif_dao.get_sif_by_id(sif_id2)
        pfd2 = sif2_retrieved.calculate_overall_pfd()
        result2, _ = verifier.verify_sil(sif2_retrieved.target_sil.value, pfd2)
        
        # Assert results
        assert isinstance(result1, bool), "Verification result for SIF 1 should be a boolean"
        assert isinstance(result2, bool), "Verification result for SIF 2 should be a boolean"
        
        # Delete SIFs
        for sif_id in sif_ids:
            sif_dao.delete_sif(sif_id)
            
        # Verify SIFs are deleted
        all_sifs_after_delete = sif_dao.get_all_sifs()
        assert len(all_sifs_after_delete) == 0, "All SIFs should be deleted"
    
    def test_boundary_conditions(self, temp_db):
        """Test SIF assessment at boundary conditions"""
        # Initialize the DAO
        sif_dao = SIFDAO()
        
        # Create subsystems at SIL boundary conditions
        sensor = SIFSubsystem(
            name="Boundary Sensor",
            architecture="1oo1",
            pfd_per_component=0.01,  # At SIL 1 boundary
            beta=0.1,
            test_interval_months=12,
            dc=0.0,  # No diagnostic coverage
            mttr_hours=8,
            subsystem_type="Sensor"
        )
        
        logic = SIFSubsystem(
            name="Boundary Logic",
            architecture="1oo1",
            pfd_per_component=0.01,  # At SIL 1 boundary
            beta=0.1,
            test_interval_months=12,
            dc=0.0,  # No diagnostic coverage
            mttr_hours=8,
            subsystem_type="Logic Solver"
        )
        
        final_element = SIFSubsystem(
            name="Boundary Final Element",
            architecture="1oo1",
            pfd_per_component=0.01,  # At SIL 1 boundary
            beta=0.1,
            test_interval_months=12,
            dc=0.0,  # No diagnostic coverage
            mttr_hours=8,
            subsystem_type="Final Element"
        )
        
        subsystems = [sensor, logic, final_element]
        
        # Create SIF with target SIL 1
        sif = SIF(
            name="Boundary Test SIF",
            subsystems=subsystems,
            target_sil=SIL(1)
        )
        
        # Add SIF to database
        sif_id = sif_dao.add_or_update_sif(sif)
        
        # Retrieve SIF
        retrieved_sif = sif_dao.get_sif_by_id(sif_id)
        
        # Calculate PFD
        overall_pfd = retrieved_sif.calculate_overall_pfd()
        
        # PFD will be higher than 0.1 due to multiple subsystems at 0.01 PFD
        assert overall_pfd > 0.01, "Overall PFD should be greater than 0.01"
        
        # Verify SIL - should not meet SIL 1 requirements
        verification_result = retrieved_sif.verify()
        assert verification_result is False, "SIF should not meet SIL 1 requirements"
        
        # Update subsystems for improved PFD
        retrieved_sif.subsystems[0].architecture = "1oo2"
        retrieved_sif.subsystems[1].architecture = "1oo2"
        retrieved_sif.subsystems[2].architecture = "1oo2"
        
        # Add updated SIF
        sif_dao.add_or_update_sif(retrieved_sif)
        
        # Retrieve updated SIF
        updated_sif = sif_dao.get_sif_by_id(sif_id)
        
        # Calculate new PFD
        new_overall_pfd = updated_sif.calculate_overall_pfd()
        
        # PFD should be better now
        assert new_overall_pfd < overall_pfd, "New PFD should be lower than original PFD"
        
        # Verify SIL - should now meet SIL 1 requirements
        new_verification_result = updated_sif.verify()
        assert new_verification_result is True, "Updated SIF should meet SIL 1 requirements" 