from flask import Blueprint, Flask, Response, json
from flask_cors import CORS

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
