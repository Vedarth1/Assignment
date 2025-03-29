import re
from typing import Dict, Any, Optional, Tuple, List
from src.utils.database import db_instance
from src.utils.errors import InvalidQueryError, DatabaseError

class QueryProcessor:
    # Constants for column mappings
    COLUMN_MAPPINGS = {
        'amount': ['amount', 'total', 'sum', 'value', 'price', 'sales', 'revenue'],
        'price': ['price', 'cost', 'value', 'amount', 'rate']
    }

    @staticmethod
    def process_query(natural_query: str) -> Dict[str, Any]:
        try:
            if not natural_query or not isinstance(natural_query, str):
                raise InvalidQueryError("Query must be a non-empty string")

            query = natural_query.lower()
            
            if QueryProcessor._is_sum(query):
                return QueryProcessor._process_sum(query)
            elif QueryProcessor._is_filter(query):
                return QueryProcessor._process_filter(query)
            elif QueryProcessor._is_select_all(query):
                return QueryProcessor._process_select_all(query)
            elif QueryProcessor._is_count(query):
                return QueryProcessor._process_count(query)
            elif QueryProcessor._is_avg(query):
                return QueryProcessor._process_avg(query)
            else:
                raise InvalidQueryError(
                    "Could not determine query intent",
                    details={"supported_intents": ["select_all", "count", "sum", "avg", "filter"]}
                )

        except DatabaseError:
            raise
        except Exception as e:
            raise InvalidQueryError(f"Error processing query: {str(e)}") from e

    @staticmethod
    def _is_sum(query: str) -> bool:
        sum_phrases = [
            "sum of", "total", "add up", 
            "what is the total", "calculate the total",
            "total amount of", "sum amount of"
        ]
        return any(phrase in query for phrase in sum_phrases)

    @staticmethod
    def _is_filter(query: str) -> bool:
        filter_keywords = ["where", "filter", "with", "equals", "=", "is"]
        table = QueryProcessor._find_table_in_query(query)
        return (any(kw in query for kw in filter_keywords) and 
                table is not None and
                any(re.search(rf"{kw}\s+\w+\s*=\s*'?\w+'?", query) for kw in filter_keywords))

    @staticmethod
    def _is_select_all(query: str) -> bool:
        return any(phrase in query for phrase in ["show me all", "list all", "get all", "display all"])

    @staticmethod
    def _is_count(query: str) -> bool:
        return "how many" in query or "count" in query

    @staticmethod
    def _is_avg(query: str) -> bool:
        return "average" in query or "avg" in query

    @staticmethod
    def _process_sum(query: str) -> Dict[str, Any]:
        """Process sum query"""
        try:
            table, column = QueryProcessor._extract_table_and_column(query, ["amount", "price"])
            data = db_instance.get_table(table)
            
            # Validate column is numeric
            if not all(isinstance(item.get(column), (int, float)) for item in data):
                raise InvalidQueryError(f"Column '{column}' is not numeric")
            
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
                f"Failed to calculate sum for {column or 'unknown'} in {table or 'unknown'}",
                details={"error": str(e)}
            )

    @staticmethod
    def _process_filter(query: str) -> Dict[str, Any]:
        """Process filter query"""
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
            raise DatabaseError(f"Failed to filter records: {str(e)}")

    @staticmethod
    def _process_select_all(query: str) -> Dict[str, Any]:
        """Process select all query"""
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
            raise DatabaseError(f"Failed to retrieve data: {str(e)}")

    @staticmethod
    def _process_count(query: str) -> Dict[str, Any]:
        """Process count query"""
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
            raise DatabaseError(f"Failed to count records: {str(e)}")

    @staticmethod
    def _process_avg(query: str) -> Dict[str, Any]:
        """Process average query"""
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
                raise InvalidQueryError(f"Column '{column}' is not numeric")
            
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
            raise DatabaseError(f"Failed to calculate average: {str(e)}")

    @staticmethod
    def _extract_table_name(query: str) -> str:
        """Extract table name from query"""
        available_tables = db_instance.get_table_names()
        for table in available_tables:
            if table in query:
                return table
        
        raise InvalidQueryError(
            "Could not determine table name",
            details={"available_tables": available_tables}
        )

    @staticmethod
    def _find_table_in_query(query: str) -> Optional[str]:
        """Find table name in query without raising error"""
        available_tables = db_instance.get_table_names()
        for table in available_tables:
            if table in query:
                return table
        return None

    @staticmethod
    def _extract_table_and_column(query: str, possible_columns: list) -> Tuple[str, str]:
        """Extract table and column from query"""
        try:
            table = QueryProcessor._extract_table_name(query)
            
            if "total amount of" in query or "sum of amount" in query:
                return table, "amount"
            if "total price of" in query or "sum of price" in query:
                return table, "price"
            
            for col in possible_columns:
                if col in query:
                    return table, col
            
            for col, synonyms in QueryProcessor.COLUMN_MAPPINGS.items():
                if any(synonym in query for synonym in synonyms):
                    if col in db_instance.get_table_columns(table):
                        return table, col
            
            raise InvalidQueryError(
                "Could not determine column to process",
                details={"available_columns": db_instance.get_table_columns(table)}
            )
        except Exception as e:
            raise InvalidQueryError(f"Failed to extract table/column: {str(e)}")

    @staticmethod
    def _extract_filter_condition(query: str) -> Tuple[str, str, str]:
        """Extract filter condition from query"""
        patterns = [
            r"show me all (\w+)\s+where\s+(\w+)\s+is\s+(\w+)",
            r"filter\s+(\w+)\s+where\s+(\w+)\s+=\s+'?(\w+)'?",
            r"get\s+(\w+)\s+with\s+(\w+)\s+=\s+'?(\w+)'?"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match and len(match.groups()) == 3:
                return match.group(1), match.group(2), match.group(3).lower()
        
        try:
            table = QueryProcessor._extract_table_name(query)
            where_match = re.search(r"where\s+(\w+)\s+(is|equals|=)\s+'?(\w+)'?", query, re.IGNORECASE)
            if where_match:
                return table, where_match.group(1), where_match.group(3).lower()
            
            raise InvalidQueryError(
                "Could not parse filter condition",
                details={
                    "expected_patterns": [
                        "Show me all <table> where <column> is <value>",
                        "Filter <table> where <column> = <value>"
                    ]
                }
            )
        except Exception as e:
            raise InvalidQueryError(f"Failed to extract filter condition: {str(e)}")
        
    @staticmethod
    def explain_query(natural_query: str) -> Dict[str, Any]:
        """Explain how a query would be processed"""
        try:
            if not natural_query or not isinstance(natural_query, str):
                raise InvalidQueryError("Query must be a non-empty string")

            query = natural_query.lower()
            explanation = {
                "status": "success",
                "query": natural_query,
                "processing_steps": [],
                "query_type": None,
                "table": None,
                "column": None
            }

            # Determine query type and build explanation
            if QueryProcessor._is_sum(query):
                explanation["query_type"] = "sum"
                table, column = QueryProcessor._extract_table_and_column(query, ["amount", "price"])
                explanation.update({
                    "table": table,
                    "column": column,
                    "processing_steps": [
                        f"Identified as sum query",
                        f"Extracted table name: {table}",
                        f"Selected column for summation: {column}",
                        f"Will calculate sum of {column} values from {table} table"
                    ]
                })
            elif QueryProcessor._is_filter(query):
                explanation["query_type"] = "filter"
                table, column, value = QueryProcessor._extract_filter_condition(query)
                explanation.update({
                    "table": table,
                    "filter_column": column,
                    "filter_value": value,
                    "processing_steps": [
                        f"Identified as filter query",
                        f"Extracted table name: {table}",
                        f"Identified filter condition: {column} = {value}",
                        f"Will retrieve records from {table} where {column} matches {value}"
                    ]
                })
            elif QueryProcessor._is_select_all(query):
                explanation["query_type"] = "select_all"
                table = QueryProcessor._extract_table_name(query)
                explanation.update({
                    "table": table,
                    "processing_steps": [
                        f"Identified as select all query",
                        f"Extracted table name: {table}",
                        f"Will retrieve all records from {table} without filtering"
                    ]
                })
            elif QueryProcessor._is_count(query):
                explanation["query_type"] = "count"
                table = QueryProcessor._extract_table_name(query)
                explanation.update({
                    "table": table,
                    "processing_steps": [
                        f"Identified as count query",
                        f"Extracted table name: {table}",
                        f"Will count all records in {table} table"
                    ]
                })
            elif QueryProcessor._is_avg(query):
                explanation["query_type"] = "average"
                table, column = QueryProcessor._extract_table_and_column(query, ["amount", "price"])
                explanation.update({
                    "table": table,
                    "column": column,
                    "processing_steps": [
                        f"Identified as average query",
                        f"Extracted table name: {table}",
                        f"Selected column for averaging: {column}",
                        f"Will calculate average of {column} values from {table} table"
                    ]
                })
            else:
                raise InvalidQueryError(
                    "Could not determine query intent",
                    details={"supported_intents": ["select_all", "count", "sum", "avg", "filter"]}
                )

            return explanation

        except InvalidQueryError as e:
            return {
                "status": "error",
                "error": "InvalidQueryError",
                "message": str(e),
                "query": natural_query,
                "details": getattr(e, "details", None),
                "suggestion": "Try rephrasing your query using one of the supported patterns"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": "ExplanationError",
                "message": f"Could not explain query: {str(e)}",
                "query": natural_query,
                "details": {
                    "type": type(e).__name__,
                    "suggestion": "Check your query syntax and try again"
                }
            }
    @staticmethod
    def validate_query(natural_query: str) -> Dict[str, Any]:
        """Validate if a query can be processed"""
        try:
            if not natural_query or not isinstance(natural_query, str):
                raise InvalidQueryError("Query must be a non-empty string")

            query = natural_query.lower()
            validation_result = {
                "status": "success",
                "valid": True,
                "query": natural_query,
                "components": {
                    "table": None,
                    "columns": [],
                    "conditions": []
                },
                "issues": []
            }

            # Extract components based on query type
            if QueryProcessor._is_sum(query):
                try:
                    table, column = QueryProcessor._extract_table_and_column(query, ["amount", "price"])
                    validation_result["components"]["table"] = table
                    validation_result["components"]["columns"].append(column)
                except Exception as e:
                    validation_result["valid"] = False
                    validation_result["issues"].append(str(e))
            
            elif QueryProcessor._is_filter(query):
                try:
                    table, column, value = QueryProcessor._extract_filter_condition(query)
                    validation_result["components"]["table"] = table
                    validation_result["components"]["columns"].append(column)
                    validation_result["components"]["conditions"].append({
                        "column": column,
                        "operator": "=",
                        "value": value
                    })
                except Exception as e:
                    validation_result["valid"] = False
                    validation_result["issues"].append(str(e))
            
            # Add similar blocks for other query types...
            else:
                validation_result["valid"] = False
                validation_result["issues"].append("Could not determine query type")

            # Validate the extracted components
            if validation_result["valid"]:
                table = validation_result["components"]["table"]
                
                # Check table exists
                if not table or table not in db_instance.get_table_names():
                    validation_result["valid"] = False
                    validation_result["issues"].append(
                        f"Table '{table}' not found. Available tables: {db_instance.get_table_names()}"
                    )
                
                # Check columns exist in table
                for col in validation_result["components"]["columns"]:
                    if col not in db_instance.get_table_columns(table):
                        validation_result["valid"] = False
                        validation_result["issues"].append(
                            f"Column '{col}' not found in table '{table}'. "
                            f"Available columns: {db_instance.get_table_columns(table)}"
                        )
                
                # For sum/avg queries, check column is numeric
                if QueryProcessor._is_sum(query) or QueryProcessor._is_avg(query):
                    column = validation_result["components"]["columns"][0]
                    sample_data = db_instance.get_table(table)[0] if db_instance.get_table(table) else {}
                    if not isinstance(sample_data.get(column), (int, float)):
                        validation_result["valid"] = False
                        validation_result["issues"].append(
                            f"Column '{column}' is not numeric and cannot be used for sum/average"
                        )

            return validation_result

        except Exception as e:
            return {
                "status": "error",
                "valid": False,
                "query": natural_query,
                "error": str(e),
                "suggestion": "Check your query syntax and try again"
            }