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
                initiating_event TEXT,
                initiating_event_frequency REAL,
                enabling_conditions TEXT,
                enabling_condition_modifiers REAL,
                conditional_modifiers TEXT,
                conditional_modifier_values REAL,
                independent_protection_layers TEXT,
                ipl_pfd_values TEXT,
                target_mitigated_frequency REAL,
                calculated_mitigated_frequency REAL,
                status TEXT,
                FOREIGN KEY (scenario_id) REFERENCES scenarios (id)
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
        st.error(f"Database initialization error: {e}")
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