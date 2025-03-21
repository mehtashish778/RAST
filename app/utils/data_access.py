# -*- coding: utf-8 -*-
"""
Data Access Layer for the HAZOP Analysis Tool
Provides database access methods for application data
"""
import json
from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd
from sqlalchemy import text
from utils.database import get_db_manager


class ChemicalDAO:
    """Data Access Object for Chemical data"""
    
    @staticmethod
    def get_all_chemicals() -> List[Dict[str, Any]]:
        """
        Get all chemicals from the database
        
        Returns:
            List of chemical dictionaries
        """
        db = get_db_manager()
        result = db.execute_query(text("SELECT * FROM chemicals ORDER BY name"))
        if result:
            return [dict(row._mapping) for row in result]
        return []
    
    @staticmethod
    def get_chemical_by_name(name: str) -> Optional[Dict[str, Any]]:
        """
        Get a chemical by name
        
        Args:
            name: Name of the chemical
            
        Returns:
            Chemical dictionary or None if not found
        """
        db = get_db_manager()
        result = db.execute_query(text("SELECT * FROM chemicals WHERE name = :name"), {"name": name})
        if result and result.rowcount > 0:
            row = result.fetchone()
            if row:
                return dict(row._mapping)
        return None
    
    @staticmethod
    def add_or_update_chemical(chemical_data: Dict[str, Any]) -> bool:
        """
        Add or update a chemical in the database
        
        Args:
            chemical_data: Chemical data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db_manager()
        
        # Check if chemical exists
        name = chemical_data.get('name')
        if not name:
            return False
        
        # Check if the chemical already exists
        existing = db.execute_query(
            text("SELECT id FROM chemicals WHERE name = :name"), 
            {"name": name}
        )
        
        try:
            if existing and existing.rowcount > 0:
                # Update existing chemical
                row = existing.fetchone()
                if row:
                    chemical_id = row._mapping['id']
                    
                    # Remove id from data if present (to avoid trying to update primary key)
                    if 'id' in chemical_data:
                        del chemical_data['id']
                    
                    # Prepare SET clause
                    set_items = []
                    for key in chemical_data:
                        set_items.append(f"{key} = :{key}")
                    
                    set_clause = ", ".join(set_items)
                    
                    # Execute update
                    db.execute_query(
                        text(f"UPDATE chemicals SET {set_clause} WHERE id = :id"),
                        {**chemical_data, "id": chemical_id}
                    )
            else:
                # Insert new chemical
                columns = ", ".join(chemical_data.keys())
                placeholders = ", ".join(f":{key}" for key in chemical_data.keys())
                
                db.execute_query(
                    text(f"INSERT INTO chemicals ({columns}) VALUES ({placeholders})"),
                    chemical_data
                )
            
            return True
        except Exception as e:
            print(f"Error adding/updating chemical: {e}")
            return False
    
    @staticmethod
    def delete_chemical(name: str) -> bool:
        """
        Delete a chemical by name
        
        Args:
            name: Name of the chemical
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db_manager()
        try:
            db.execute_query(text("DELETE FROM chemicals WHERE name = :name"), {"name": name})
            return True
        except Exception as e:
            print(f"Error deleting chemical: {e}")
            return False
    
    @staticmethod
    def import_chemicals_from_dataframe(df: pd.DataFrame) -> bool:
        """
        Import chemicals from a pandas DataFrame
        
        Args:
            df: DataFrame containing chemical data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert DataFrame to list of dictionaries
            chemicals = df.to_dict(orient='records')
            
            # Add or update each chemical
            for chemical in chemicals:
                ChemicalDAO.add_or_update_chemical(chemical)
            
            return True
        except Exception as e:
            print(f"Error importing chemicals: {e}")
            return False


class EquipmentDAO:
    """Data Access Object for Equipment data"""
    
    @staticmethod
    def get_all_equipment() -> List[Dict[str, Any]]:
        """
        Get all equipment from the database
        
        Returns:
            List of equipment dictionaries
        """
        db = get_db_manager()
        result = db.execute_query(text("SELECT * FROM equipment ORDER BY tag"))
        if result:
            return [dict(row._mapping) for row in result]
        return []
    
    @staticmethod
    def get_equipment_by_tag(tag: str) -> Optional[Dict[str, Any]]:
        """
        Get equipment by tag
        
        Args:
            tag: Equipment tag
            
        Returns:
            Equipment dictionary or None if not found
        """
        db = get_db_manager()
        result = db.execute_query(text("SELECT * FROM equipment WHERE tag = :tag"), {"tag": tag})
        if result and result.rowcount > 0:
            row = result.fetchone()
            if row:
                return dict(row._mapping)
        return None
    
    @staticmethod
    def add_or_update_equipment(equipment_data: Dict[str, Any]) -> bool:
        """
        Add or update equipment in the database
        
        Args:
            equipment_data: Equipment data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db_manager()
        
        # Check if tag exists
        tag = equipment_data.get('tag')
        if not tag:
            return False
        
        # Check if the equipment already exists
        existing = db.execute_query(
            text("SELECT id FROM equipment WHERE tag = :tag"), 
            {"tag": tag}
        )
        
        try:
            if existing and existing.rowcount > 0:
                # Update existing equipment
                row = existing.fetchone()
                if row:
                    equipment_id = row._mapping['id']
                    
                    # Remove id from data if present (to avoid trying to update primary key)
                    if 'id' in equipment_data:
                        del equipment_data['id']
                    
                    # Prepare SET clause
                    set_items = []
                    for key in equipment_data:
                        set_items.append(f"{key} = :{key}")
                    
                    set_clause = ", ".join(set_items)
                    
                    # Execute update
                    db.execute_query(
                        text(f"UPDATE equipment SET {set_clause} WHERE id = :id"),
                        {**equipment_data, "id": equipment_id}
                    )
            else:
                # Insert new equipment
                columns = ", ".join(equipment_data.keys())
                placeholders = ", ".join(f":{key}" for key in equipment_data.keys())
                
                db.execute_query(
                    text(f"INSERT INTO equipment ({columns}) VALUES ({placeholders})"),
                    equipment_data
                )
            
            return True
        except Exception as e:
            print(f"Error adding/updating equipment: {e}")
            return False
    
    @staticmethod
    def delete_equipment(tag: str) -> bool:
        """
        Delete equipment by tag
        
        Args:
            tag: Equipment tag
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db_manager()
        try:
            db.execute_query(text("DELETE FROM equipment WHERE tag = :tag"), {"tag": tag})
            return True
        except Exception as e:
            print(f"Error deleting equipment: {e}")
            return False
    
    @staticmethod
    def import_equipment_from_dataframe(df: pd.DataFrame) -> bool:
        """
        Import equipment from a pandas DataFrame
        
        Args:
            df: DataFrame containing equipment data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert DataFrame to list of dictionaries
            equipment_list = df.to_dict(orient='records')
            
            # Add or update each equipment
            for equipment in equipment_list:
                EquipmentDAO.add_or_update_equipment(equipment)
            
            return True
        except Exception as e:
            print(f"Error importing equipment: {e}")
            return False


class ScenarioDAO:
    """Data Access Object for HAZOP Scenario data"""
    
    @staticmethod
    def get_scenarios_by_equipment(equipment_id: str) -> List[Dict[str, Any]]:
        """
        Get all scenarios for a specific piece of equipment
        
        Args:
            equipment_id: ID of the equipment
            
        Returns:
            List of scenario dictionaries
        """
        db = get_db_manager()
        result = db.execute_query(
            "SELECT * FROM scenarios WHERE equipment_id = :equipment_id ORDER BY id",
            {"equipment_id": equipment_id}
        )
        if result:
            return [dict(row) for row in result]
        return []
    
    @staticmethod
    def add_or_update_scenario(scenario_data: Dict[str, Any]) -> bool:
        """
        Add or update a scenario in the database
        
        Args:
            scenario_data: Dictionary containing scenario data
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db_manager()
        session = db.get_session()
        
        try:
            # Extract attributes that don't match direct columns
            attributes = scenario_data.pop('attributes', {})
            
            # Convert attributes to JSON string
            scenario_data['attributes'] = json.dumps(attributes)
            
            # Check if scenario exists
            if 'id' in scenario_data and scenario_data['id']:
                scenario_id = scenario_data['id']
                existing = session.execute(
                    "SELECT 1 FROM scenarios WHERE id = :id",
                    {"id": scenario_id}
                ).fetchone()
                
                if existing:
                    # Build update query
                    set_clause = ", ".join([f"{k} = :{k}" for k in scenario_data.keys()])
                    session.execute(
                        f"UPDATE scenarios SET {set_clause} WHERE id = :id",
                        scenario_data
                    )
                else:
                    # Insert new scenario
                    columns = ", ".join(scenario_data.keys())
                    values = ", ".join([f":{k}" for k in scenario_data.keys()])
                    session.execute(
                        f"INSERT INTO scenarios ({columns}) VALUES ({values})",
                        scenario_data
                    )
            else:
                # Remove id if it's None
                if 'id' in scenario_data:
                    scenario_data.pop('id')
                    
                # Insert new scenario
                columns = ", ".join(scenario_data.keys())
                values = ", ".join([f":{k}" for k in scenario_data.keys()])
                session.execute(
                    f"INSERT INTO scenarios ({columns}) VALUES ({values})",
                    scenario_data
                )
            
            session.commit()
            return True
        except Exception as e:
            if session:
                session.rollback()
            print(f"Error adding/updating scenario: {e}")
            return False
        finally:
            db.close_session(session)
    
    @staticmethod
    def delete_scenario(scenario_id: int) -> bool:
        """
        Delete a scenario from the database
        
        Args:
            scenario_id: ID of the scenario to delete
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db_manager()
        session = db.get_session()
        
        try:
            session.execute("DELETE FROM scenarios WHERE id = :id", {"id": scenario_id})
            session.commit()
            return True
        except Exception as e:
            if session:
                session.rollback()
            print(f"Error deleting scenario: {e}")
            return False
        finally:
            db.close_session(session) 