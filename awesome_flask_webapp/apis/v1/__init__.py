from flask import Blueprint

from flask_cors import CORS

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

CORS(api_v1)

from awesome_flask_webapp.apis.v1 import resources

