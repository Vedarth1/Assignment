class InvalidQueryError(Exception):
    def __init__(self, message: str, query: str = None, details: dict = None):
        self.message = message
        self.query = query
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        base = f"InvalidQueryError: {self.message}"
        if self.query:
            base += f"\nQuery: {self.query}"
        if self.details:
            base += f"\nDetails: {self.details}"
        return base

    def to_dict(self) -> dict:
        return {
            'error': 'InvalidQueryError',
            'message': self.message,
            'query': self.query,
            'details': self.details
        }


class DatabaseError(Exception):
    def __init__(self, message: str, operation: str = None, table: str = None, details: dict = None):
        self.message = message
        self.operation = operation
        self.table = table
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        base = f"DatabaseError: {self.message}"
        if self.operation:
            base += f"\nOperation: {self.operation}"
        if self.table:
            base += f"\nTable: {self.table}"
        if self.details:
            base += f"\nDetails: {self.details}"
        return base

    def to_dict(self) -> dict:
        return {
            'error': 'DatabaseError',
            'message': self.message,
            'operation': self.operation,
            'table': self.table,
            'details': self.details
        }