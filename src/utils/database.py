from typing import Dict, List, Optional, Any
from src.config.config import Config

class Database:
    def __init__(self):
        self.tables = {}
        self._initialize_database()
    
    def _initialize_database(self):
        for table_name, table_def in Config.DATABASE_SCHEMA.items():
            columns = table_def["columns"]
            sample_data = table_def["sample_data"]
            
            self.tables[table_name] = [
                dict(zip(columns, row)) for row in sample_data
            ]

    def get_table_names(self) -> List[str]:
        """Returns a list of all table names."""
        return list(self.tables.keys())

    def get_table(self, table_name: str) -> List[Dict[str, Any]]:
        return self.tables.get(table_name, [])

    def get_table_columns(self, table_name: str) -> Optional[List[str]]:
        if table_name not in self.tables or not self.tables[table_name]:
            return None
        return list(self.tables[table_name][0].keys())

    def table_exists(self, table_name: str) -> bool:
        return table_name in self.tables

db_instance = Database()