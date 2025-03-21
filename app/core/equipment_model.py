"""
Equipment Data Model for HAZOP Analysis Tool
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
import pandas as pd
import json
import os
import uuid


@dataclass
class Equipment:
    """Base Equipment class representing common properties"""
    
    tag: str  # Unique equipment identifier
    name: str  # Descriptive name
    equipment_type: str  # Type identifier (vessel, heat exchanger, etc.)
    service: str = ""  # Equipment service description
    
    # Physical properties
    volume: Optional[float] = None  # Volume in liters
    material: str = "Carbon Steel"  # Construction material
    
    # Design conditions
    max_allowable_working_pressure: Optional[float] = None  # MAWP in bar
    design_temperature: Optional[float] = None  # Design temp in C
    
    # Location information
    plant_area: str = ""
    elevation: Optional[float] = None  # Height in meters
    
    # Additional attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Generate unique ID if not provided
        if not hasattr(self, 'id') or not self.id:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict:
        """Convert equipment to dictionary"""
        return {
            "id": getattr(self, 'id', str(uuid.uuid4())),
            "tag": self.tag,
            "name": self.name,
            "equipment_type": self.equipment_type,
            "service": self.service,
            "volume": self.volume,
            "material": self.material,
            "max_allowable_working_pressure": self.max_allowable_working_pressure,
            "design_temperature": self.design_temperature,
            "plant_area": self.plant_area,
            "elevation": self.elevation,
            "attributes": self.attributes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Equipment':
        """Create equipment instance from dictionary"""
        # Extract attributes dictionary
        attributes = data.pop('attributes', {})
        
        # Create equipment instance
        instance = cls(**{k: v for k, v in data.items() if k != 'attributes'})
        instance.attributes = attributes
        
        return instance


@dataclass
class Vessel(Equipment):
    """Vessel equipment class (tanks, reactors, columns)"""
    
    def __post_init__(self):
        super().__post_init__()
        self.equipment_type = "Vessel"
        
        # Vessel-specific attributes
        self.attributes.setdefault("diameter", None)  # mm
        self.attributes.setdefault("height", None)  # mm
        self.attributes.setdefault("orientation", "Vertical")  # Vertical/Horizontal
        self.attributes.setdefault("heads", "2:1 Elliptical")  # Head type


@dataclass
class HeatExchanger(Equipment):
    """Heat exchanger equipment class"""
    
    def __post_init__(self):
        super().__post_init__()
        self.equipment_type = "Heat Exchanger"
        
        # Heat exchanger-specific attributes
        self.attributes.setdefault("heat_transfer_area", None)  # sq m
        self.attributes.setdefault("shell_side_fluid", "")
        self.attributes.setdefault("tube_side_fluid", "")
        self.attributes.setdefault("overall_heat_transfer_coefficient", None)  # kW/sq m-K


@dataclass
class Pump(Equipment):
    """Pump equipment class"""
    
    def __post_init__(self):
        super().__post_init__()
        self.equipment_type = "Pump"
        
        # Pump-specific attributes
        self.attributes.setdefault("design_flow", None)  # m3/hr
        self.attributes.setdefault("design_head", None)  # m
        self.attributes.setdefault("motor_power", None)  # kW


@dataclass
class Pipe(Equipment):
    """Pipe equipment class"""
    
    def __post_init__(self):
        super().__post_init__()
        self.equipment_type = "Pipe"
        
        # Pipe-specific attributes
        self.attributes.setdefault("diameter", None)  # mm
        self.attributes.setdefault("length", None)  # m
        self.attributes.setdefault("schedule", "")
        self.attributes.setdefault("from_equipment", "")
        self.attributes.setdefault("to_equipment", "")


class EquipmentFactory:
    """Factory for creating equipment instances"""
    
    @staticmethod
    def create_equipment(equipment_type: str, data: Dict) -> Equipment:
        """Create appropriate equipment instance based on type"""
        equipment_classes = {
            "Vessel": Vessel,
            "Heat Exchanger": HeatExchanger,
            "Pump": Pump,
            "Pipe": Pipe
        }
        
        equipment_class = equipment_classes.get(equipment_type, Equipment)
        return equipment_class(**data)


class EquipmentDatabase:
    """Manager for equipment database operations"""
    
    def __init__(self, data_directory: str = None):
        self.equipment: Dict[str, Equipment] = {}
        self.data_directory = data_directory or os.path.join(os.path.dirname(__file__), '../data')
        self.default_db_path = os.path.join(self.data_directory, 'equipment.json')
    
    def add_equipment(self, equipment: Equipment) -> None:
        """Add equipment to database"""
        self.equipment[equipment.tag] = equipment
    
    def get_equipment(self, tag: str) -> Optional[Equipment]:
        """Get equipment by tag"""
        return self.equipment.get(tag)
    
    def list_equipment(self) -> List[str]:
        """List all equipment tags"""
        return list(self.equipment.keys())
    
    def import_from_excel(self, file_path: str, sheet_name: str = 'Equipment Table') -> int:
        """Import equipment from Excel file"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            count = 0
            
            for _, row in df.iterrows():
                # Skip rows without tags
                if pd.isna(row.get('tag', '')):
                    continue
                    
                # Convert row to dictionary, handling NaN values
                row_dict = row.to_dict()
                equipment_type = row_dict.get('equipment_type', 'Equipment')
                
                # Clean the dictionary
                cleaned_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
                
                # Process attributes
                attributes = {}
                for key in list(cleaned_dict.keys()):
                    if key not in ['id', 'tag', 'name', 'equipment_type', 'service', 
                                  'volume', 'material', 'max_allowable_working_pressure', 
                                  'design_temperature', 'plant_area', 'elevation']:
                        attributes[key] = cleaned_dict.pop(key)
                
                cleaned_dict['attributes'] = attributes
                
                # Create equipment and add to database
                equipment = EquipmentFactory.create_equipment(equipment_type, cleaned_dict)
                self.add_equipment(equipment)
                count += 1
                
            return count
        except Exception as e:
            print(f"Error importing from Excel: {e}")
            return 0
    
    def save_database(self, file_path: str = None) -> bool:
        """Save equipment database to JSON file"""
        file_path = file_path or self.default_db_path
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Convert equipment to dictionaries
            equipment_dict = {tag: equip.to_dict() for tag, equip in self.equipment.items()}
            
            with open(file_path, 'w') as f:
                json.dump(equipment_dict, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False
    
    def load_database(self, file_path: str = None) -> bool:
        """Load equipment database from JSON file"""
        file_path = file_path or self.default_db_path
        
        try:
            if not os.path.exists(file_path):
                return False
                
            with open(file_path, 'r') as f:
                equipment_dict = json.load(f)
            
            for tag, equip_dict in equipment_dict.items():
                equipment_type = equip_dict.get('equipment_type', 'Equipment')
                equipment = EquipmentFactory.create_equipment(equipment_type, equip_dict)
                self.equipment[tag] = equipment
            
            return True
        except Exception as e:
            print(f"Error loading database: {e}")
            return False 