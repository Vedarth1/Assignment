from flask import Blueprint
from src.controllers.processing_controller import processing

api=Blueprint('api',__name__)

api.register_blueprint(processing)