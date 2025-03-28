from typing import Dict, Any, Optional, Tuple
import re
from src.utils.database import db_instance
from src.utils.errors import InvalidQueryError, DatabaseError

class QueryProcessor:
    @staticmethod
    def process_query(natural_query: str) -> Dict[str, Any]:
        """Process a natural language query and return results with comprehensive error handling"""
        if not natural_query or not isinstance(natural_query, str):
            raise InvalidQueryError(
                "Query must be a non-empty string",
                details={
                    "input_received": natural_query,
                    "input_type": type(natural_query).__name__
                }
            )

        query = natural_query.lower()
        
        try:
            if QueryProcessor._is_filter(query):
                return QueryProcessor._process_filter(query)
            elif QueryProcessor._is_select_all(query):
                return QueryProcessor._process_select_all(query)
            elif QueryProcessor._is_count(query):
                return QueryProcessor._process_count(query)
            elif QueryProcessor._is_sum(query):
                return QueryProcessor._process_sum(query)
            elif QueryProcessor._is_avg(query):
                return QueryProcessor._process_avg(query)
            else:
                raise InvalidQueryError(
                    "Could not determine query type",
                    query=natural_query,
                    details={
                        "supported_query_types": [
                            "select all", "count", "sum", "average", "filter"
                        ],
                        "example_queries": [
                            "Show me all sales",
                            "How many customers do we have?",
                            "What is the total amount of sales",
                            "Show me sales where region is North"
                        ]
                    }
                )
        except DatabaseError:
            raise
        except Exception as e:
            raise InvalidQueryError(
                f"Unexpected error processing query: {str(e)}",
                query=natural_query,
                details={
                    "internal_error": str(e),
                    "type": type(e).__name__
                }
            ) from e

    @staticmethod
    def explain_query(natural_query: str) -> Dict[str, Any]:
        """Explain how a query would be processed with proper error handling"""
        try:
            if not natural_query or not isinstance(natural_query, str):
                raise InvalidQueryError("Query must be a non-empty string")

            query = natural_query.lower()
            
            if QueryProcessor._is_filter(query):
                table, column, value = QueryProcessor._extract_filter_condition(query)
                return {
                    "status": "success",
                    "explanation": f"Will filter {table} table where {column} equals {value}",
                    "query_type": "filter",
                    "table": table,
                    "filter_column": column,
                    "filter_value": value
                }
            elif QueryProcessor._is_select_all(query):
                table = QueryProcessor._extract_table_name(query)
                return {
                    "status": "success",
                    "explanation": f"Will return all records from {table} table",
                    "query_type": "select_all",
                    "table": table
                }
            elif QueryProcessor._is_count(query):
                table = QueryProcessor._extract_table_name(query)
                return {
                    "status": "success",
                    "explanation": f"Will count records in {table} table",
                    "query_type": "count",
                    "table": table
                }
            elif QueryProcessor._is_sum(query):
                table, column = QueryProcessor._extract_table_and_column(
                    query, ["amount", "price"]
                )
                return {
                    "status": "success",
                    "explanation": f"Will sum {column} values from {table} table",
                    "query_type": "sum",
                    "table": table,
                    "column": column
                }
            elif QueryProcessor._is_avg(query):
                table, column = QueryProcessor._extract_table_and_column(
                    query, ["amount", "price"]
                )
                return {
                    "status": "success",
                    "explanation": f"Will average {column} values from {table} table",
                    "query_type": "average",
                    "table": table,
                    "column": column
                }
            else:
                return {
                    "status": "error",
                    "explanation": "Query type not recognized",
                    "query": natural_query,
                    "supported_query_types": [
                        "select all", "count", "sum", "average", "filter"
                    ]
                }
        except InvalidQueryError as e:
            return {
                "status": "error",
                "error": "InvalidQueryError",
                "explanation": str(e),
                "details": getattr(e, "details", None),
                "query": natural_query
            }
        except Exception as e:
            return {
                "status": "error",
                "error": "ExplanationError",
                "explanation": f"Could not explain query: {str(e)}",
                "query": natural_query,
                "details": {
                    "type": type(e).__name__,
                    "message": str(e)
                }
            }

    @staticmethod
    def validate_query(natural_query: str) -> Dict[str, Any]:
        """Validate if a query can be processed with proper error handling"""
        try:
            if not natural_query or not isinstance(natural_query, str):
                raise InvalidQueryError("Query must be a non-empty string")

            query = natural_query.lower()
            validation_result = {
                "status": "error",
                "query": natural_query
            }

            # Check table exists
            table = QueryProcessor._extract_table_name(query)
            if not db_instance.table_exists(table):
                validation_result.update({
                    "reason": f"Table '{table}' does not exist",
                    "available_tables": list(db_instance.tables.keys())
                })
                return validation_result
            
            # Check columns if needed
            if QueryProcessor._is_sum(query) or QueryProcessor._is_avg(query) or QueryProcessor._is_filter(query):
                if QueryProcessor._is_filter(query):
                    _, column, _ = QueryProcessor._extract_filter_condition(query)
                else:
                    _, column = QueryProcessor._extract_table_and_column(query, ["amount", "price"])
                
                columns = db_instance.get_table_columns(table)
                if column not in columns:
                    validation_result.update({
                        "reason": f"Column '{column}' not found in table '{table}'",
                        "available_columns": columns
                    })
                    return validation_result
            
            return {
                "status": "success",
                "valid": True,
                "reason": "Query is valid",
                "query": natural_query,
                "table": table
            }
        except InvalidQueryError as e:
            return {
                "status": "error",
                "valid": False,
                "reason": str(e),
                "query": natural_query,
                "details": getattr(e, "details", None)
            }
        except Exception as e:
            return {
                "status": "error",
                "valid": False,
                "reason": f"Validation failed: {str(e)}",
                "query": natural_query,
                "details": {
                    "type": type(e).__name__,
                    "message": str(e)
                }
            }

    # Helper methods
    @staticmethod
    def _extract_table_name(query: str) -> str:
        """Extract table name with detailed error reporting"""
        tables = db_instance.tables.keys()
        for table in tables:
            if table in query:
                return table
        
        raise InvalidQueryError(
            "Could not determine table name from query",
            query=query,
            details={
                "available_tables": list(tables),
                "suggestion": "Include one of the available table names in your query"
            }
        )
    
    @staticmethod
    def _extract_table_and_column(query: str, possible_columns: list) -> Tuple[str, str]:
        """Extract table and column with detailed error reporting"""
        try:
            table = QueryProcessor._extract_table_name(query)
            for col in possible_columns:
                if col in query:
                    return table, col
            
            raise InvalidQueryError(
                f"Could not find any of the required columns in query",
                query=query,
                details={
                    "required_columns": possible_columns,
                    "available_columns": db_instance.get_table_columns(table),
                    "suggestion": f"Include one of {possible_columns} in your query"
                }
            )
        except Exception as e:
            raise InvalidQueryError(
                f"Failed to extract table and column: {str(e)}",
                query=query
            ) from e
    
    @staticmethod
    def _extract_filter_condition(query: str) -> Tuple[str, str, str]:
        """Extract filter condition with detailed error reporting"""
        patterns = [
            # Pattern for "Show me all X where Y is Z"
            r"show me all (\w+)\s+where\s+(\w+)\s+is\s+(\w+)",
            r"show me all (\w+)\s+where\s+(\w+)\s+equals\s+(\w+)",
            # Pattern for "Filter X where Y is Z"
            r"filter\s+(\w+)\s+where\s+(\w+)\s+is\s+(\w+)",
            r"filter\s+(\w+)\s+where\s+(\w+)\s+=\s+'?(\w+)'?",
            # Pattern for "Show me X where Y equals Z"
            r"show me\s+(\w+)\s+where\s+(\w+)\s+equals\s+'?(\w+)'?",
            # Pattern for "Get X with Y = Z"
            r"get\s+(\w+)\s+with\s+(\w+)\s+=\s+'?(\w+)'?"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match and len(match.groups()) == 3:
                return match.group(1), match.group(2), match.group(3).lower()
        
        # Fallback: Try to extract components separately
        try:
            table = QueryProcessor._extract_table_name(query)
            where_match = re.search(r"where\s+(\w+)\s+(is|equals|=)\s+'?(\w+)'?", query, re.IGNORECASE)
            if where_match:
                return table, where_match.group(1), where_match.group(3).lower()
            
            raise InvalidQueryError(
                "Could not parse filter condition from query",
                query=query,
                details={
                    "expected_patterns": [
                        "Show me all <table> where <column> is <value>",
                        "Filter <table> where <column> = <value>",
                        "Show me <table> where <column> equals <value>"
                    ],
                    "suggestion": "Use one of the supported filter patterns"
                }
            )
        except Exception as e:
            raise InvalidQueryError(
                f"Failed to extract filter condition: {str(e)}",
                query=query
            ) from e

    # Processing methods
    @staticmethod
    def _process_select_all(query: str) -> Dict[str, Any]:
        """Process select all query with proper error handling"""
        try:
            table = QueryProcessor._extract_table_name(query)
            data = db_instance.get_table(table)
            return {
                "status": "success",
                "query_type": "select_all",
                "table": table,
                "results": data,
                "count": len(data)
            }
        except Exception as e:
            raise DatabaseError(
                f"Failed to retrieve data from table '{table}'",
                operation="select_all",
                table=table,
                details={"internal_error": str(e)}
            ) from e
    
    @staticmethod
    def _process_count(query: str) -> Dict[str, Any]:
        """Process count query with proper error handling"""
        try:
            table = QueryProcessor._extract_table_name(query)
            data = db_instance.get_table(table)
            return {
                "status": "success",
                "query_type": "count",
                "table": table,
                "count": len(data)
            }
        except Exception as e:
            raise DatabaseError(
                f"Failed to count records in table '{table}'",
                operation="count",
                table=table,
                details={"internal_error": str(e)}
            ) from e
    
    @staticmethod
    def _process_sum(query: str) -> Dict[str, Any]:
        """Process sum query with proper error handling"""
        try:
            table, column = QueryProcessor._extract_table_and_column(query, ["amount", "price"])
            data = db_instance.get_table(table)
            
            if not all(isinstance(item.get(column), (int, float)) for item in data):
                raise InvalidQueryError(
                    f"Cannot calculate sum of non-numeric column '{column}'",
                    query=query,
                    details={
                        "column_type": "non-numeric",
                        "suggestion": "Use a numeric column for sum operations"
                    }
                )
            
            total = sum(float(item[column]) for item in data)
            return {
                "status": "success",
                "query_type": "sum",
                "table": table,
                "column": column,
                "total": total
            }
        except Exception as e:
            raise DatabaseError(
                f"Failed to calculate sum for column '{column}' in table '{table}'",
                operation="sum",
                table=table,
                details={
                    "column": column,
                    "internal_error": str(e)
                }
            ) from e
    
    @staticmethod
    def _process_avg(query: str) -> Dict[str, Any]:
        """Process average query with proper error handling"""
        try:
            table, column = QueryProcessor._extract_table_and_column(query, ["amount", "price"])
            data = db_instance.get_table(table)
            
            if not data:
                return {
                    "status": "success",
                    "query_type": "average",
                    "table": table,
                    "column": column,
                    "average": 0,
                    "count": 0,
                    "warning": "Table is empty"
                }
            
            if not all(isinstance(item.get(column), (int, float)) for item in data):
                raise InvalidQueryError(
                    f"Cannot calculate average of non-numeric column '{column}'",
                    query=query,
                    details={
                        "column_type": "non-numeric",
                        "suggestion": "Use a numeric column for average operations"
                    }
                )
            
            total = sum(float(item[column]) for item in data)
            avg = total / len(data)
            return {
                "status": "success",
                "query_type": "average",
                "table": table,
                "column": column,
                "average": avg,
                "count": len(data)
            }
        except Exception as e:
            raise DatabaseError(
                f"Failed to calculate average for column '{column}' in table '{table}'",
                operation="average",
                table=table,
                details={
                    "column": column,
                    "internal_error": str(e)
                }
            ) from e
    
    @staticmethod
    def _process_filter(query: str) -> Dict[str, Any]:
        """Process filter query with proper error handling"""
        try:
            table, column, value = QueryProcessor._extract_filter_condition(query)
            data = db_instance.get_table(table)
            
            filtered = [
                item for item in data 
                if str(item.get(column, "")).lower() == value.lower()
            ]
            
            return {
                "status": "success",
                "query_type": "filter",
                "table": table,
                "filter_column": column,
                "filter_value": value,
                "results": filtered,
                "count": len(filtered)
            }
        except Exception as e:
            raise DatabaseError(
                f"Failed to filter table '{table}' by column '{column}'",
                operation="filter",
                table=table,
                details={
                    "column": column,
                    "filter_value": value,
                    "internal_error": str(e)
                }
            ) from e

    # Query type detection methods
    @staticmethod
    def _is_select_all(query: str) -> bool:
        return any(phrase in query for phrase in ["show me all", "list all", "get all", "display all"])
    
    @staticmethod
    def _is_count(query: str) -> bool:
        return "how many" in query or "count" in query
    
    @staticmethod
    def _is_sum(query: str) -> bool:
        return "sum of" in query or "total" in query
    
    @staticmethod
    def _is_avg(query: str) -> bool:
        return "average" in query or "avg" in query
    
    @staticmethod
    def _is_filter(query: str) -> bool:
        return any(
            phrase in query 
            for phrase in ["where", "filter", "with", "equals", "is", "region is", "product is"]
        )