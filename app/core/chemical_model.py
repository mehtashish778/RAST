"""
Chemical Data Model for HAZOP Analysis Tool
"""
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
import json
import os


@dataclass
class Chemical:
    """Chemical data class representing physical and safety properties"""
    
    name: str
    cas_number: str = ""
    molecular_weight: float = 0.0
    
    # Physical properties
    boiling_point: Optional[float] = None  # degrees C
    melting_point: Optional[float] = None  # degrees C
    flash_point: Optional[float] = None    # degrees C
    auto_ignition_temp: Optional[float] = None  # degrees C
    
    # Safety properties
    lower_flammability_limit: Optional[float] = None  # % volume in air
    upper_flammability_limit: Optional[float] = None  # % volume in air
    erpg_2: Optional[float] = None  # ppm or mg/m3
    erpg_3: Optional[float] = None  # ppm or mg/m3
    
    # NFPA ratings
    nfpa_health: int = 0
    nfpa_flammability: int = 0
    nfpa_reactivity: int = 0
    nfpa_special: str = ""
    
    # Vapor pressure constants (Antoine equation)
    vp_a: Optional[float] = None
    vp_b: Optional[float] = None
    vp_c: Optional[float] = None
    
    # Heat capacity constants
    cp_a: Optional[float] = None
    cp_b: Optional[float] = None
    
    # Heat of vaporization constants
    hv_a: Optional[float] = None
    hv_b: Optional[float] = None
    hv_c: Optional[float] = None
    
    # Vapor pressure calculation
    def vapor_pressure(self, temperature_c: float) -> Optional[float]:
        """Calculate vapor pressure in bar at specified temperature (C)"""
        if None in (self.vp_a, self.vp_b, self.vp_c):
            return None
        
        try:
            # Antoine equation: log10(P) = A - B/(T + C)
            temperature_k = temperature_c + 273.15
            log_pressure = self.vp_a - (self.vp_b / (temperature_k + self.vp_c))
            return 10 ** log_pressure
        except (ValueError, ZeroDivisionError):
            return None
    
    # Heat of vaporization calculation
    def heat_of_vaporization(self, temperature_c: float) -> Optional[float]:
        """Calculate heat of vaporization in kJ/mol at specified temperature (C)"""
        if None in (self.hv_a, self.hv_b, self.hv_c):
            return None
        
        try:
            temperature_k = temperature_c + 273.15
            return self.hv_a + self.hv_b * temperature_k + self.hv_c * temperature_k**2
        except ValueError:
            return None
    
    def to_dict(self) -> Dict:
        """Convert the chemical to a dictionary"""
        return {
            "name": self.name,
            "cas_number": self.cas_number,
            "molecular_weight": self.molecular_weight,
            "boiling_point": self.boiling_point,
            "melting_point": self.melting_point,
            "flash_point": self.flash_point,
            "auto_ignition_temp": self.auto_ignition_temp,
            "lower_flammability_limit": self.lower_flammability_limit,
            "upper_flammability_limit": self.upper_flammability_limit,
            "erpg_2": self.erpg_2,
            "erpg_3": self.erpg_3,
            "nfpa_health": self.nfpa_health,
            "nfpa_flammability": self.nfpa_flammability,
            "nfpa_reactivity": self.nfpa_reactivity,
            "nfpa_special": self.nfpa_special,
            "vp_a": self.vp_a,
            "vp_b": self.vp_b,
            "vp_c": self.vp_c,
            "cp_a": self.cp_a,
            "cp_b": self.cp_b,
            "hv_a": self.hv_a,
            "hv_b": self.hv_b,
            "hv_c": self.hv_c,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Chemical':
        """Create a Chemical instance from a dictionary"""
        return cls(**data)


class ChemicalDatabase:
    """Manager for chemical database operations"""
    
    def __init__(self, data_directory: str = None):
        self.chemicals: Dict[str, Chemical] = {}
        self.data_directory = data_directory or os.path.join(os.path.dirname(__file__), '../data')
        self.default_db_path = os.path.join(self.data_directory, 'chemicals.json')
        
    def add_chemical(self, chemical: Chemical) -> None:
        """Add a chemical to the database"""
        self.chemicals[chemical.name] = chemical
    
    def get_chemical(self, name: str) -> Optional[Chemical]:
        """Get a chemical by name"""
        return self.chemicals.get(name)
    
    def list_chemicals(self) -> List[str]:
        """List all chemical names in the database"""
        return list(self.chemicals.keys())
    
    def import_from_excel(self, file_path: str, sheet_name: str = 'Chemical Data') -> int:
        """Import chemicals from Excel file"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            count = 0
            
            for _, row in df.iterrows():
                # Convert row to dictionary, handling NaN values
                row_dict = row.to_dict()
                cleaned_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
                
                # Create chemical and add to database
                chemical = Chemical.from_dict(cleaned_dict)
                self.add_chemical(chemical)
                count += 1
                
            return count
        except Exception as e:
            print(f"Error importing from Excel: {e}")
            return 0
    
    def save_database(self, file_path: str = None) -> bool:
        """Save the chemical database to a JSON file"""
        file_path = file_path or self.default_db_path
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Convert chemicals to dictionaries
            chemicals_dict = {name: chem.to_dict() for name, chem in self.chemicals.items()}
            
            with open(file_path, 'w') as f:
                json.dump(chemicals_dict, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False
    
    def load_database(self, file_path: str = None) -> bool:
        """Load the chemical database from a JSON file"""
        file_path = file_path or self.default_db_path
        
        try:
            if not os.path.exists(file_path):
                return False
                
            with open(file_path, 'r') as f:
                chemicals_dict = json.load(f)
            
            for name, chem_dict in chemicals_dict.items():
                self.chemicals[name] = Chemical.from_dict(chem_dict)
            
            return True
        except Exception as e:
            print(f"Error loading database: {e}")
            return False 