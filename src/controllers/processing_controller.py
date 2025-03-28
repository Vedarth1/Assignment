from flask import Blueprint, Flask, Response, json,request, jsonify
from flask_cors import CORS
from src.services.query import QueryProcessor
from src.utils.errors import InvalidQueryError

app = Flask(__name__)
CORS(app,supports_credentials=True)

processing = Blueprint("processing", __name__)

@processing.route('/hello', methods=["GET"])
def hello():
    return Response(
        response=json.dumps({'status': "success", "message": "Hello"}),
        status=200,
        mimetype='application/json'
    )

@processing.route('/query', methods=['POST'])
# @authenticate
def query():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Query parameter is required"}), 400
    
    try:
        result = QueryProcessor.process_query(data['query'])
        return jsonify(result)
    except InvalidQueryError as e:
        return jsonify({"error": str(e)}), 400

@processing.route('/explain', methods=['POST'])
# @authenticate
def explain():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Query parameter is required"}), 400
    
    explanation = QueryProcessor.explain_query(data['query'])
    return jsonify(explanation)

@processing.route('/validate', methods=['POST'])
# @authenticate
def validate():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Query parameter is required"}), 400
    
    validation = QueryProcessor.validate_query(data['query'])
    return jsonify(validation)