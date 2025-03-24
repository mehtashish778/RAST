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
    """Data Access Object for Scenario data"""
    
    @staticmethod
    def get_all_scenarios() -> List[Dict[str, Any]]:
        """
        Get all scenarios from the database
        
        Returns:
            List of scenario dictionaries
        """
        db = get_db_manager()
        result = db.execute_query(text("SELECT * FROM scenarios ORDER BY id"))
        if result:
            return [dict(row._mapping) for row in result]
        return []
    
    @staticmethod
    def get_scenario_by_id(scenario_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a scenario by ID
        
        Args:
            scenario_id: ID of the scenario
            
        Returns:
            Scenario dictionary or None if not found
        """
        db = get_db_manager()
        result = db.execute_query(
            text("SELECT * FROM scenarios WHERE id = :id"),
            {"id": scenario_id}
        )
        if result and result.rowcount > 0:
            row = result.fetchone()
            if row:
                return dict(row._mapping)
        return None
    
    @staticmethod
    def get_scenarios_by_equipment(equipment_id: int) -> List[Dict[str, Any]]:
        """
        Get all scenarios for a specific piece of equipment
        
        Args:
            equipment_id: ID of the equipment
            
        Returns:
            List of scenario dictionaries
        """
        db = get_db_manager()
        result = db.execute_query(
            text("SELECT * FROM scenarios WHERE equipment_id = :equipment_id ORDER BY id"),
            {"equipment_id": equipment_id}
        )
        if result:
            return [dict(row._mapping) for row in result]
        return []
    
    @staticmethod
    def get_scenarios_by_risk_category(risk_category: str) -> List[Dict[str, Any]]:
        """
        Get all scenarios with a specific risk category
        
        Args:
            risk_category: Risk category to filter by
            
        Returns:
            List of scenario dictionaries
        """
        db = get_db_manager()
        result = db.execute_query(
            text("SELECT * FROM scenarios WHERE risk_category = :risk_category ORDER BY id"),
            {"risk_category": risk_category}
        )
        if result:
            return [dict(row._mapping) for row in result]
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
            # Extract attributes that should be stored as JSON
            attributes = scenario_data.pop('attributes', {})
            
            # Convert attributes to JSON string
            scenario_data['attributes'] = json.dumps(attributes)
            
            # Check if scenario exists
            if 'id' in scenario_data and scenario_data['id']:
                scenario_id = scenario_data['id']
                existing = session.execute(
                    text("SELECT 1 FROM scenarios WHERE id = :id"),
                    {"id": scenario_id}
                ).fetchone()
                
                if existing:
                    # Build update query
                    set_clause = ", ".join([f"{k} = :{k}" for k in scenario_data.keys()])
                    session.execute(
                        text(f"UPDATE scenarios SET {set_clause} WHERE id = :id"),
                        scenario_data
                    )
                else:
                    # Insert new scenario
                    columns = ", ".join(scenario_data.keys())
                    placeholders = ", ".join([f":{k}" for k in scenario_data.keys()])
                    session.execute(
                        text(f"INSERT INTO scenarios ({columns}) VALUES ({placeholders})"),
                        scenario_data
                    )
            else:
                # Remove id if it's None
                if 'id' in scenario_data:
                    scenario_data.pop('id')
                    
                # Insert new scenario
                columns = ", ".join(scenario_data.keys())
                placeholders = ", ".join([f":{k}" for k in scenario_data.keys()])
                session.execute(
                    text(f"INSERT INTO scenarios ({columns}) VALUES ({placeholders})"),
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
            session.execute(
                text("DELETE FROM scenarios WHERE id = :id"),
                {"id": scenario_id}
            )
            session.commit()
            return True
        except Exception as e:
            if session:
                session.rollback()
            print(f"Error deleting scenario: {e}")
            return False
        finally:
            db.close_session(session)
            
    @staticmethod
    def get_scenario_template(template_name: str) -> Dict[str, Any]:
        """
        Get a predefined scenario template
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template dictionary with predefined values
        """
        templates = {
            "high_pressure": {
                "node": "Pressure System",
                "deviation": "More Pressure",
                "causes": "- Control valve failure\n- External fire\n- Blocked outlet\n- Thermal expansion",
                "consequences": "- Equipment rupture\n- Release of material\n- Potential injury to personnel",
                "safeguards": "- Pressure safety valve\n- High pressure alarm\n- Rupture disc",
                "recommendations": "- Review PSV sizing\n- Add high pressure interlock",
                "risk_category": "High",
                "attributes": {"severity": 4, "likelihood": 2}
            },
            "low_flow": {
                "node": "Flow System",
                "deviation": "Less Flow",
                "causes": "- Pump failure\n- Valve closed\n- Line blockage\n- Instrument failure",
                "consequences": "- Process upset\n- Potential equipment damage\n- Product quality issues",
                "safeguards": "- Low flow alarm\n- Standby pump\n- Flow indication",
                "recommendations": "- Add auto-switching to standby pump\n- Review maintenance procedures",
                "risk_category": "Medium",
                "attributes": {"severity": 2, "likelihood": 3}
            },
            "high_temperature": {
                "node": "Temperature System",
                "deviation": "More Temperature",
                "causes": "- Cooling failure\n- Control system failure\n- Exothermic reaction\n- External fire",
                "consequences": "- Equipment damage\n- Product degradation\n- Potential runaway reaction",
                "safeguards": "- High temperature alarm\n- Emergency cooling\n- Temperature indication",
                "recommendations": "- Add independent high temperature shutdown\n- Review cooling system capacity",
                "risk_category": "High",
                "attributes": {"severity": 3, "likelihood": 3}
            }
        }
        
        return templates.get(template_name, {})
    
    @staticmethod
    def get_available_templates() -> List[str]:
        """
        Get a list of available scenario templates
        
        Returns:
            List of template names
        """
        return ["high_pressure", "low_flow", "high_temperature"]


class IPLDAO:
    """Data Access Object for Independent Protection Layer data"""
    
    @staticmethod
    def get_all_ipls() -> List[Dict[str, Any]]:
        """
        Get all IPLs from the database
        
        Returns:
            List of IPL dictionaries
        """
        db = get_db_manager()
        result = db.execute_query(text("SELECT * FROM ipls ORDER BY id"))
        if result:
            return [dict(row._mapping) for row in result]
        return []
    
    @staticmethod
    def get_ipl_by_id(ipl_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an IPL by ID
        
        Args:
            ipl_id: ID of the IPL
            
        Returns:
            IPL dictionary or None if not found
        """
        db = get_db_manager()
        result = db.execute_query(text("SELECT * FROM ipls WHERE id = :id"), {"id": ipl_id})
        if result and result.rowcount > 0:
            row = result.fetchone()
            if row:
                return dict(row._mapping)
        return None
    
    @staticmethod
    def get_ipls_by_scenario(scenario_id: int) -> List[Dict[str, Any]]:
        """
        Get all IPLs for a specific scenario
        
        Args:
            scenario_id: ID of the scenario
            
        Returns:
            List of IPL dictionaries
        """
        db = get_db_manager()
        result = db.execute_query(
            text("SELECT * FROM ipls WHERE scenario_id = :scenario_id ORDER BY id"),
            {"scenario_id": scenario_id}
        )
        if result:
            return [dict(row._mapping) for row in result]
        return []
    
    @staticmethod
    def get_ipls_by_lopa_scenario(lopa_scenario_id: int) -> List[Dict[str, Any]]:
        """
        Get all IPLs for a specific LOPA scenario
        
        Args:
            lopa_scenario_id: ID of the LOPA scenario
            
        Returns:
            List of IPL dictionaries
        """
        db = get_db_manager()
        result = db.execute_query(
            text("SELECT * FROM ipls WHERE lopa_scenario_id = :lopa_scenario_id ORDER BY id"),
            {"lopa_scenario_id": lopa_scenario_id}
        )
        if result:
            return [dict(row._mapping) for row in result]
        return []
    
    @staticmethod
    def add_or_update_ipl(ipl_data: Dict[str, Any]) -> bool:
        """
        Add or update an IPL in the database
        
        Args:
            ipl_data: Dictionary containing IPL data
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db_manager()
        
        # Check if IPL exists
        ipl_id = ipl_data.get('id')
        
        try:
            if ipl_id:
                # Update existing IPL
                # Remove id from data if present (to avoid trying to update primary key)
                update_data = {k: v for k, v in ipl_data.items() if k != 'id'}
                
                # Prepare SET clause
                set_items = []
                for key in update_data:
                    set_items.append(f"{key} = :{key}")
                
                set_clause = ", ".join(set_items)
                
                # Execute update
                db.execute_query(
                    text(f"UPDATE ipls SET {set_clause} WHERE id = :id"),
                    {**update_data, "id": ipl_id}
                )
            else:
                # Add new IPL
                # Prepare columns and values for INSERT
                columns = ", ".join(ipl_data.keys())
                placeholders = ", ".join(f":{key}" for key in ipl_data.keys())
                
                # Execute insert
                db.execute_query(
                    text(f"INSERT INTO ipls ({columns}) VALUES ({placeholders})"),
                    ipl_data
                )
            
            return True
        except Exception as e:
            print(f"Error adding/updating IPL: {e}")
            return False
    
    @staticmethod
    def delete_ipl(ipl_id: int) -> bool:
        """
        Delete an IPL from the database
        
        Args:
            ipl_id: ID of the IPL to delete
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db_manager()
        
        try:
            db.execute_query(
                text("DELETE FROM ipls WHERE id = :id"),
                {"id": ipl_id}
            )
            return True
        except Exception as e:
            print(f"Error deleting IPL: {e}")
            return False


class SIFDAO:
    """Data Access Object for Safety Instrumented Function data"""
    
    @staticmethod
    def get_all_sifs() -> List[Dict[str, Any]]:
        """
        Get all SIFs from the database
        
        Returns:
            List of SIF dictionaries
        """
        db = get_db_manager()
        result = db.execute_query(text("SELECT * FROM sifs ORDER BY id"))
        if result:
            return [dict(row._mapping) for row in result]
        return []
    
    @staticmethod
    def get_sif_by_id(sif_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a SIF by ID
        
        Args:
            sif_id: ID of the SIF
            
        Returns:
            SIF dictionary or None if not found
        """
        db = get_db_manager()
        result = db.execute_query(text("SELECT * FROM sifs WHERE id = :id"), {"id": sif_id})
        if result and result.rowcount > 0:
            row = result.fetchone()
            if row:
                return dict(row._mapping)
        return None
    
    @staticmethod
    def get_sifs_by_scenario(scenario_id: int) -> List[Dict[str, Any]]:
        """
        Get all SIFs for a specific scenario
        
        Args:
            scenario_id: ID of the scenario
            
        Returns:
            List of SIF dictionaries
        """
        db = get_db_manager()
        result = db.execute_query(
            text("SELECT * FROM sifs WHERE scenario_id = :scenario_id ORDER BY id"),
            {"scenario_id": scenario_id}
        )
        if result:
            return [dict(row._mapping) for row in result]
        return []
    
    @staticmethod
    def add_or_update_sif(sif_data: Dict[str, Any]) -> bool:
        """
        Add or update a SIF in the database
        
        Args:
            sif_data: Dictionary containing SIF data
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db_manager()
        
        # Check if SIF exists
        sif_id = sif_data.get('id')
        
        try:
            if sif_id:
                # Update existing SIF
                # Remove id from data if present (to avoid trying to update primary key)
                update_data = {k: v for k, v in sif_data.items() if k != 'id'}
                
                # Prepare SET clause
                set_items = []
                for key in update_data:
                    set_items.append(f"{key} = :{key}")
                
                set_clause = ", ".join(set_items)
                
                # Execute update
                db.execute_query(
                    text(f"UPDATE sifs SET {set_clause} WHERE id = :id"),
                    {**update_data, "id": sif_id}
                )
            else:
                # Add new SIF
                # Prepare columns and values for INSERT
                columns = ", ".join(sif_data.keys())
                placeholders = ", ".join(f":{key}" for key in sif_data.keys())
                
                # Execute insert
                db.execute_query(
                    text(f"INSERT INTO sifs ({columns}) VALUES ({placeholders})"),
                    sif_data
                )
            
            return True
        except Exception as e:
            print(f"Error adding/updating SIF: {e}")
            return False
    
    @staticmethod
    def delete_sif(sif_id: int) -> bool:
        """
        Delete a SIF from the database
        
        Args:
            sif_id: ID of the SIF to delete
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db_manager()
        
        try:
            # First delete any associated subsystems
            db.execute_query(
                text("DELETE FROM sif_subsystems WHERE sif_id = :sif_id"),
                {"sif_id": sif_id}
            )
            
            # Then delete the SIF
            db.execute_query(
                text("DELETE FROM sifs WHERE id = :id"),
                {"id": sif_id}
            )
            return True
        except Exception as e:
            print(f"Error deleting SIF: {e}")
            return False
    
    @staticmethod
    def get_subsystems_by_sif(sif_id: int) -> List[Dict[str, Any]]:
        """
        Get all subsystems for a specific SIF
        
        Args:
            sif_id: ID of the SIF
            
        Returns:
            List of subsystem dictionaries
        """
        db = get_db_manager()
        result = db.execute_query(
            text("SELECT * FROM sif_subsystems WHERE sif_id = :sif_id ORDER BY id"),
            {"sif_id": sif_id}
        )
        if result:
            return [dict(row._mapping) for row in result]
        return []
    
    @staticmethod
    def add_or_update_subsystem(subsystem_data: Dict[str, Any]) -> bool:
        """
        Add or update a SIF subsystem in the database
        
        Args:
            subsystem_data: Dictionary containing subsystem data
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db_manager()
        
        # Check if subsystem exists
        subsystem_id = subsystem_data.get('id')
        
        try:
            if subsystem_id:
                # Update existing subsystem
                # Remove id from data if present (to avoid trying to update primary key)
                update_data = {k: v for k, v in subsystem_data.items() if k != 'id'}
                
                # Prepare SET clause
                set_items = []
                for key in update_data:
                    set_items.append(f"{key} = :{key}")
                
                set_clause = ", ".join(set_items)
                
                # Execute update
                db.execute_query(
                    text(f"UPDATE sif_subsystems SET {set_clause} WHERE id = :id"),
                    {**update_data, "id": subsystem_id}
                )
            else:
                # Add new subsystem
                # Prepare columns and values for INSERT
                columns = ", ".join(subsystem_data.keys())
                placeholders = ", ".join(f":{key}" for key in subsystem_data.keys())
                
                # Execute insert
                db.execute_query(
                    text(f"INSERT INTO sif_subsystems ({columns}) VALUES ({placeholders})"),
                    subsystem_data
                )
            
            return True
        except Exception as e:
            print(f"Error adding/updating SIF subsystem: {e}")
            return False
    
    @staticmethod
    def delete_subsystem(subsystem_id: int) -> bool:
        """
        Delete a SIF subsystem from the database
        
        Args:
            subsystem_id: ID of the subsystem to delete
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db_manager()
        
        try:
            db.execute_query(
                text("DELETE FROM sif_subsystems WHERE id = :id"),
                {"id": subsystem_id}
            )
            return True
        except Exception as e:
            print(f"Error deleting SIF subsystem: {e}")
            return False


class LOPAScenarioDAO:
    """Data Access Object for LOPA Scenario data"""
    
    @staticmethod
    def get_all_lopa_scenarios() -> List[Dict[str, Any]]:
        """
        Get all LOPA scenarios from the database
        
        Returns:
            List of LOPA scenario dictionaries
        """
        db = get_db_manager()
        result = db.execute_query(text("SELECT * FROM lopa_scenarios ORDER BY id"))
        if result:
            return [dict(row._mapping) for row in result]
        return []
    
    @staticmethod
    def get_lopa_scenario_by_id(lopa_scenario_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a LOPA scenario by ID
        
        Args:
            lopa_scenario_id: ID of the LOPA scenario
            
        Returns:
            LOPA scenario dictionary or None if not found
        """
        db = get_db_manager()
        result = db.execute_query(
            text("SELECT * FROM lopa_scenarios WHERE id = :id"),
            {"id": lopa_scenario_id}
        )
        if result and result.rowcount > 0:
            row = result.fetchone()
            if row:
                return dict(row._mapping)
        return None
    
    @staticmethod
    def get_lopa_scenarios_by_scenario(scenario_id: int) -> List[Dict[str, Any]]:
        """
        Get all LOPA scenarios for a specific HAZOP scenario
        
        Args:
            scenario_id: ID of the HAZOP scenario
            
        Returns:
            List of LOPA scenario dictionaries
        """
        db = get_db_manager()
        result = db.execute_query(
            text("SELECT * FROM lopa_scenarios WHERE scenario_id = :scenario_id ORDER BY id"),
            {"scenario_id": scenario_id}
        )
        if result:
            return [dict(row._mapping) for row in result]
        return []
    
    @staticmethod
    def add_or_update_lopa_scenario(lopa_data: Dict[str, Any]) -> bool:
        """
        Add or update a LOPA scenario in the database
        
        Args:
            lopa_data: Dictionary containing LOPA scenario data
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db_manager()
        
        # Check if LOPA scenario exists
        lopa_id = lopa_data.get('id')
        
        try:
            if lopa_id:
                # Update existing LOPA scenario
                # Remove id from data if present (to avoid trying to update primary key)
                update_data = {k: v for k, v in lopa_data.items() if k != 'id'}
                
                # Prepare SET clause
                set_items = []
                for key in update_data:
                    set_items.append(f"{key} = :{key}")
                
                set_clause = ", ".join(set_items)
                
                # Execute update
                db.execute_query(
                    text(f"UPDATE lopa_scenarios SET {set_clause} WHERE id = :id"),
                    {**update_data, "id": lopa_id}
                )
            else:
                # Add new LOPA scenario
                # Prepare columns and values for INSERT
                columns = ", ".join(lopa_data.keys())
                placeholders = ", ".join(f":{key}" for key in lopa_data.keys())
                
                # Execute insert
                db.execute_query(
                    text(f"INSERT INTO lopa_scenarios ({columns}) VALUES ({placeholders})"),
                    lopa_data
                )
            
            return True
        except Exception as e:
            print(f"Error adding/updating LOPA scenario: {e}")
            return False
    
    @staticmethod
    def delete_lopa_scenario(lopa_scenario_id: int) -> bool:
        """
        Delete a LOPA scenario from the database
        
        Args:
            lopa_scenario_id: ID of the LOPA scenario to delete
            
        Returns:
            True if successful, False otherwise
        """
        db = get_db_manager()
        
        try:
            # Delete associated IPLs first
            db.execute_query(
                text("DELETE FROM ipls WHERE lopa_scenario_id = :lopa_scenario_id"),
                {"lopa_scenario_id": lopa_scenario_id}
            )
            
            # Delete the LOPA scenario
            db.execute_query(
                text("DELETE FROM lopa_scenarios WHERE id = :id"),
                {"id": lopa_scenario_id}
            )
            return True
        except Exception as e:
            print(f"Error deleting LOPA scenario: {e}")
            return False
    
    @staticmethod
    def get_lopa_summary() -> pd.DataFrame:
        """
        Get a summary of all LOPA scenarios with their associated IPLs
        
        Returns:
            Pandas DataFrame with LOPA summary data
        """
        db = get_db_manager()
        
        query = text("""
            SELECT 
                l.id, 
                l.scenario_id,
                l.description,
                l.consequence_category,
                l.consequence_severity,
                l.initiating_event,
                l.initiating_event_frequency,
                l.target_mitigated_frequency,
                COUNT(i.id) as ipl_count,
                s.node,
                s.deviation
            FROM 
                lopa_scenarios l
            LEFT JOIN 
                ipls i ON l.id = i.lopa_scenario_id
            LEFT JOIN
                scenarios s ON l.scenario_id = s.id
            GROUP BY 
                l.id
            ORDER BY 
                l.id
        """)
        
        result = db.execute_query(query)
        
        if result:
            data = [dict(row._mapping) for row in result]
            return pd.DataFrame(data)
        
        return pd.DataFrame() 