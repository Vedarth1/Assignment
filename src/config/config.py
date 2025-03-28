from src.config.devconfig import DevConfig

class Config:
    def __init__(self):
        self.dev_config = DevConfig()

    API_KEYS = {
        "demo-key": "ved",
        "test-key": "ved"
    }
    
    DATABASE_SCHEMA = {
        "sales": {
            "columns": ["id", "product", "amount", "date", "region"],
            "sample_data": [
                [1, "Laptop", 1200, "2023-01-15", "North"],
                [2, "Phone", 800, "2023-01-16", "South"],
                [3, "Tablet", 450, "2023-01-17", "East"],
                [4, "Laptop", 1200, "2023-01-18", "West"],
                [5, "Phone", 800, "2023-01-19", "North"]
            ]
        },
        "customers": {
            "columns": ["id", "name", "email", "join_date"],
            "sample_data": [
                [1, "Alice", "alice@example.com", "2022-05-10"],
                [2, "Bob", "bob@example.com", "2022-06-15"],
                [3, "Charlie", "charlie@example.com", "2022-07-20"]
            ]
        },
        "products": {
            "columns": ["id", "name", "category", "price"],
            "sample_data": [
                [1, "Laptop", "Electronics", 1200],
                [2, "Phone", "Electronics", 800],
                [3, "Tablet", "Electronics", 450]
            ]
        }
    }