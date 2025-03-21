# -*- coding: utf-8 -*-
"""
Database utility for the HAZOP Analysis Tool
Provides SQLAlchemy-based database connection and session management
"""
import os
import json
from pathlib import Path
import streamlit as st
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import text
from typing import Optional, Dict, Any, Union, List

# Database file paths
DEFAULT_DB_PATH = os.path.join(Path(__file__).parent.parent, 'data', 'hazop.db')


class DatabaseManager:
    """
    Manages database connections and operations for the HAZOP Analysis Tool
    Provides a unified interface for data persistence
    """
    def __init__(self, db_path: str = None):
        """Initialize database manager with connection to SQLite database"""
        self.db_path = db_path or DEFAULT_DB_PATH
        self.engine = None
        self.session_factory = None
        self.Session = None
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Create connection string
        self.connection_string = f"sqlite:///{self.db_path}"
        
        # Connect to database
        self.connect()
        
    def connect(self) -> bool:
        """
        Establish database connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Create engine
            self.engine = sa.create_engine(self.connection_string)
            
            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)
            self.Session = scoped_session(self.session_factory)
            
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def get_session(self):
        """
        Get a new database session
        
        Returns:
            Session object
        """
        return self.Session()
    
    def close_session(self, session):
        """
        Close a database session
        
        Args:
            session: Session to close
        """
        if session:
            session.close()
    
    def execute_query(self, query, params=None):
        """
        Execute a SQL query and return the results
        
        Args:
            query: SQL query (should be a SQLAlchemy text object)
            params: Query parameters
            
        Returns:
            Query result
        """
        session = self.get_session()
        try:
            if params:
                result = session.execute(query, params)
            else:
                result = session.execute(query)
            
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            print(f"Query execution error: {e}")
            return None
        finally:
            self.close_session(session)
    
    def export_to_json(self, table_name: str, file_path: str, key_field: str = None) -> bool:
        """
        Export a table to a JSON file
        
        Args:
            table_name: Name of the table to export
            file_path: Path to save the JSON file
            key_field: Field to use as the key in the JSON object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Query all records from the table
            query = text(f"SELECT * FROM {table_name}")
            result = self.execute_query(query)
            
            if not result:
                return False
            
            # Convert result to list of dictionaries
            records = [dict(row._mapping) for row in result]
            
            # If key field specified, convert to dict with key field as the key
            if key_field and records:
                data = {}
                for record in records:
                    if key_field in record:
                        data[record[key_field]] = record
                    else:
                        # Fall back to list if key field not found
                        data = records
                        break
            else:
                data = records
            
            # Write to JSON file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    def import_from_json(self, table_name: str, file_path: str, key_field: str = None) -> bool:
        """
        Import data from a JSON file to a table
        
        Args:
            table_name: Name of the table to import into
            file_path: Path to the JSON file
            key_field: Field used as the key in the JSON object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Convert dict to list if needed
            if isinstance(data, dict):
                records = []
                for key, value in data.items():
                    if isinstance(value, dict):
                        if key_field and key_field not in value:
                            value[key_field] = key
                        records.append(value)
                    else:
                        # Not a valid format
                        return False
            else:
                records = data
            
            # Insert or update records
            for record in records:
                if key_field and key_field in record:
                    # Check if record exists
                    check_query = text(f"SELECT COUNT(*) FROM {table_name} WHERE {key_field} = :{key_field}")
                    result = self.execute_query(check_query, {key_field: record[key_field]})
                    row = result.fetchone()
                    
                    if row and row[0] > 0:
                        # Update existing record
                        set_items = []
                        for key in record:
                            if key != key_field:  # Skip the key field in SET clause
                                set_items.append(f"{key} = :{key}")
                        
                        set_clause = ", ".join(set_items)
                        update_query = text(f"UPDATE {table_name} SET {set_clause} WHERE {key_field} = :{key_field}")
                        self.execute_query(update_query, record)
                    else:
                        # Insert new record
                        columns = ", ".join(record.keys())
                        placeholders = ", ".join(f":{key}" for key in record.keys())
                        insert_query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")
                        self.execute_query(insert_query, record)
                else:
                    # No key field, just insert
                    columns = ", ".join(record.keys())
                    placeholders = ", ".join(f":{key}" for key in record.keys())
                    insert_query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")
                    self.execute_query(insert_query, record)
            
            return True
        except Exception as e:
            print(f"Error importing from JSON: {e}")
            return False


# Singleton instance
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """
    Get or create the database manager singleton
    
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    
    return _db_manager 