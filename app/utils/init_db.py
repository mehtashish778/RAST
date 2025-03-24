# -*- coding: utf-8 -*-
"""
HAZOP Analysis Tool - Database Initialization Module
Creates and initializes the database schema and loads sample data
"""
import os
import json
import sqlite3
import streamlit as st
from pathlib import Path
import sys

# Add the parent directory to the path to resolve imports
current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from utils.database import get_db_manager
from sqlalchemy import text


def init_database():
    """Initialize database schema and load sample data"""
    db = get_db_manager()
    session = db.get_session()
    
    try:
        # Create chemicals table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS chemicals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                cas_number TEXT,
                molecular_weight REAL,
                boiling_point REAL,
                melting_point REAL,
                flash_point REAL,
                auto_ignition_temp REAL,
                lower_flammability_limit REAL,
                upper_flammability_limit REAL,
                erpg_2 REAL,
                erpg_3 REAL,
                nfpa_health INTEGER,
                nfpa_flammability INTEGER,
                nfpa_reactivity INTEGER,
                nfpa_special TEXT,
                properties TEXT
            )
        """))
        
        # Create equipment table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag TEXT UNIQUE,
                name TEXT,
                equipment_type TEXT,
                attributes TEXT
            )
        """))
        
        # Create scenarios table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_id INTEGER,
                node TEXT,
                deviation TEXT,
                causes TEXT,
                consequences TEXT,
                safeguards TEXT,
                recommendations TEXT,
                risk_category TEXT,
                attributes TEXT,
                FOREIGN KEY (equipment_id) REFERENCES equipment (id)
            )
        """))
        
        # Create lopa_scenarios table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS lopa_scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id INTEGER,
                description TEXT,
                node_id INTEGER,
                consequence_description TEXT,
                consequence_category TEXT,
                consequence_severity INTEGER,
                initiating_event TEXT,
                initiating_event_frequency REAL,
                initiating_event_basis TEXT,
                target_mitigated_frequency REAL,
                conditional_modifiers TEXT,
                notes TEXT,
                FOREIGN KEY (scenario_id) REFERENCES scenarios (id)
            )
        """))
        
        # Create ipls table for independent protection layers
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS ipls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id INTEGER,
                lopa_scenario_id INTEGER,
                name TEXT,
                description TEXT,
                ipl_type TEXT,
                category TEXT,
                pfd REAL,
                is_enabled INTEGER,
                sil INTEGER,
                FOREIGN KEY (scenario_id) REFERENCES scenarios (id),
                FOREIGN KEY (lopa_scenario_id) REFERENCES lopa_scenarios (id)
            )
        """))
        
        # Create sifs table for safety instrumented functions
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS sifs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                scenario_id INTEGER,
                required_sil INTEGER,
                process_safety_time REAL,
                sif_response_time REAL,
                safety_function TEXT,
                safe_state TEXT,
                verification_status TEXT,
                notes TEXT,
                FOREIGN KEY (scenario_id) REFERENCES scenarios (id)
            )
        """))
        
        # Create sif_subsystems table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS sif_subsystems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sif_id INTEGER,
                name TEXT,
                architecture TEXT,
                pfd_per_component REAL,
                beta REAL,
                test_interval_months INTEGER,
                dc REAL,
                mttr_hours REAL,
                subsystem_type TEXT,
                FOREIGN KEY (sif_id) REFERENCES sifs (id)
            )
        """))
        
        session.commit()
        print("Database schema created successfully")
        
        # Load sample data if it exists
        load_sample_data()
        
        return True
    except Exception as e:
        if session:
            session.rollback()
        print(f"Database initialization error: {e}")
        return False
    finally:
        db.close_session(session)


def load_sample_data():
    """Load sample data from JSON files if they exist"""
    data_dir = Path(__file__).parent.parent / 'data'
    
    # Check if tables are empty before loading sample data
    db = get_db_manager()
    session = db.get_session()
    
    try:
        # Check if chemicals table is empty
        chemical_count = session.execute(text("SELECT COUNT(*) FROM chemicals")).scalar()
        if chemical_count == 0:
            # Load sample chemicals
            chemical_file = data_dir / 'sample_chemicals.json'
            if chemical_file.exists():
                with open(chemical_file, 'r') as f:
                    chemicals_data = json.load(f)
                    
                for chemical in chemicals_data:
                    # Prepare columns and values for the INSERT query
                    columns = ", ".join(chemical.keys())
                    placeholders = ", ".join(f":{key}" for key in chemical.keys())
                    
                    # Execute the INSERT query
                    session.execute(text(f"INSERT INTO chemicals ({columns}) VALUES ({placeholders})"), chemical)
                
                print(f"Loaded {len(chemicals_data)} sample chemicals")
        
        # Check if equipment table is empty
        equipment_count = session.execute(text("SELECT COUNT(*) FROM equipment")).scalar()
        if equipment_count == 0:
            # Load sample equipment
            equipment_file = data_dir / 'sample_equipment.json'
            if equipment_file.exists():
                with open(equipment_file, 'r') as f:
                    equipment_data = json.load(f)
                    
                for equipment in equipment_data:
                    # Prepare columns and values for the INSERT query
                    columns = ", ".join(equipment.keys())
                    placeholders = ", ".join(f":{key}" for key in equipment.keys())
                    
                    # Execute the INSERT query
                    session.execute(text(f"INSERT INTO equipment ({columns}) VALUES ({placeholders})"), equipment)
                
                print(f"Loaded {len(equipment_data)} sample equipment items")
        
        # Check if scenarios table is empty
        scenario_count = session.execute(text("SELECT COUNT(*) FROM scenarios")).scalar()
        if scenario_count == 0:
            # Load sample scenarios
            scenario_file = data_dir / 'sample_scenarios.json'
            if scenario_file.exists():
                with open(scenario_file, 'r') as f:
                    scenarios_data = json.load(f)
                    
                for scenario in scenarios_data:
                    # Prepare columns and values for the INSERT query
                    columns = ", ".join(scenario.keys())
                    placeholders = ", ".join(f":{key}" for key in scenario.keys())
                    
                    # Execute the INSERT query
                    session.execute(text(f"INSERT INTO scenarios ({columns}) VALUES ({placeholders})"), scenario)
                
                print(f"Loaded {len(scenarios_data)} sample scenarios")
        
        # Check if lopa_scenarios table is empty
        lopa_count = session.execute(text("SELECT COUNT(*) FROM lopa_scenarios")).scalar()
        if lopa_count == 0:
            # Load sample LOPA scenarios
            lopa_file = data_dir / 'sample_lopa.json'
            if lopa_file.exists():
                with open(lopa_file, 'r') as f:
                    lopa_data = json.load(f)
                    
                for lopa in lopa_data:
                    # Prepare columns and values for the INSERT query
                    columns = ", ".join(lopa.keys())
                    placeholders = ", ".join(f":{key}" for key in lopa.keys())
                    
                    # Execute the INSERT query
                    session.execute(text(f"INSERT INTO lopa_scenarios ({columns}) VALUES ({placeholders})"), lopa)
                
                print(f"Loaded {len(lopa_data)} sample LOPA scenarios")
        
        # Check if ipls table is empty
        ipl_count = session.execute(text("SELECT COUNT(*) FROM ipls")).scalar()
        if ipl_count == 0:
            # Load sample IPLs
            ipl_file = data_dir / 'sample_ipls.json'
            if ipl_file.exists():
                with open(ipl_file, 'r') as f:
                    ipls_data = json.load(f)
                    
                for ipl in ipls_data:
                    # Prepare columns and values for the INSERT query
                    columns = ", ".join(ipl.keys())
                    placeholders = ", ".join(f":{key}" for key in ipl.keys())
                    
                    # Execute the INSERT query
                    session.execute(text(f"INSERT INTO ipls ({columns}) VALUES ({placeholders})"), ipl)
                
                print(f"Loaded {len(ipls_data)} sample IPLs")
        
        # Check if sifs table is empty
        sif_count = session.execute(text("SELECT COUNT(*) FROM sifs")).scalar()
        if sif_count == 0:
            # Load sample SIFs
            sif_file = data_dir / 'sample_sifs.json'
            if sif_file.exists():
                with open(sif_file, 'r') as f:
                    sifs_data = json.load(f)
                    
                for sif in sifs_data:
                    # Store subsystems separately and remove from SIF data
                    subsystems = None
                    if 'subsystems' in sif:
                        subsystems = sif.pop('subsystems')
                    
                    # Prepare columns and values for the INSERT query
                    columns = ", ".join(sif.keys())
                    placeholders = ", ".join(f":{key}" for key in sif.keys())
                    
                    # Execute the INSERT query
                    session.execute(text(f"INSERT INTO sifs ({columns}) VALUES ({placeholders})"), sif)
                    
                    # Add subsystems if available
                    if subsystems:
                        sif_id = sif['id']
                        for subsystem in subsystems:
                            # Add sif_id to subsystem data
                            subsystem['sif_id'] = sif_id
                            
                            # Prepare columns and values for the INSERT query
                            columns = ", ".join(subsystem.keys())
                            placeholders = ", ".join(f":{key}" for key in subsystem.keys())
                            
                            # Execute the INSERT query
                            session.execute(text(f"INSERT INTO sif_subsystems ({columns}) VALUES ({placeholders})"), subsystem)
                
                print(f"Loaded {len(sifs_data)} sample SIFs")
        
        session.commit()
    except Exception as e:
        if session:
            session.rollback()
        print(f"Error loading sample data: {e}")
    finally:
        db.close_session(session)


if __name__ == "__main__":
    print("Initializing HAZOP Analysis Tool database...")
    if init_database():
        print("Database initialization complete") 