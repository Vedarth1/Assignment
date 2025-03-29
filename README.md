
# Natural Language Query API

A REST API that processes natural language queries and converts them into database operations.


## Features

✨ **Query Processing**
- Convert natural language to database queries
- Support for SUM, COUNT, AVG, FILTER, and SELECT ALL operations
- Intelligent column and table detection

🔍 **Query Analysis**
- `/explain` endpoint shows how queries will be processed
- `/validate` endpoint checks query validity before execution
- `/query` endpoint process the query

🛡️ **Error Handling**
- Clear error messages with suggestions
- Validation for tables and columns
- Type checking for numeric operations



## Tech Stack

- Language: Python
- Framework: Flask
- Database: SQLite (or in-memory solution)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/Vedarth1/Assignment
   cd Assignment
   ```

2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Run the Flask app:
   ```sh
   python app.py
   ```
## API Reference

## Demo queries
- What is the total amount of sales
- How many customers do we have?
- total sales amount last quarter
- average sales amount in west region
- list all customers

#### Query Processing Routes

```http
  GET /api/protected
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Your API key |

Response:
```sh
{
    "message": "You have access to this protected resource!",
    "status": "success"
}   
   ```

#### For Processing query

```http
  POST /api/query
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `query`      | `string` | **Required**. write query here |
| `api_key` | `string` | **Required**. Your API key |


Response:
```sh
{
    "column": "amount",
    "query_type": "sum",
    "status": "success",
    "table": "sales",
    "total": 4450.0
}
   ```

#### For Validating query

```http
  POST /api/validate
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `query`      | `string` | **Required**. write query here |
| `api_key` | `string` | **Required**. Your API key |


Response:
```sh
{
    "components": {
        "columns": [
            "amount"
        ],
        "conditions": [],
        "table": "sales"
    },
    "issues": [],
    "query": "What is the total amount of sales",
    "status": "success",
    "valid": true
}
   ```

#### For explaining query

```http
  POST /api/validate
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `query`      | `string` | **Required**. write query here |
| `api_key` | `string` | **Required**. Your API key |


Response:
```sh
{
    "column": "amount",
    "processing_steps": [
        "Identified as sum query",
        "Extracted table name: sales",
        "Selected column for summation: amount",
        "Will calculate sum of amount values from sales table"
    ],
    "query": "What is the total amount of sales",
    "query_type": "sum",
    "status": "success",
    "table": "sales"
}
   ```


## Assumptions 

- A data set is taken as a reference for implementation 
- Refer /config/config.py for data schema
- api_key = demo-key or test-key


## Deployment

To access this project api go to 

```bash
  https://assignment-muec.onrender.com
```
