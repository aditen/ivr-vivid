import json

from flask import Flask, Response, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from class_name_suggester import ClassNameSuggester
from data_classes import FilterCriteria
from query_handler import QueryHandler

app = Flask(__name__)
CORS(app)

query_handler = QueryHandler()
suggester = ClassNameSuggester()

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
# TODO: write one that is correct
API_URL = 'http://petstore.swagger.io/v2/swagger.json'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "ViViD REST Documentation"
    },
)

app.register_blueprint(swaggerui_blueprint)


@app.route('/execute_query', methods=['POST'])
def execute_query():
    filter_criteria: FilterCriteria = FilterCriteria.from_json(request.get_data().decode("utf-8"))
    return Response(json.dumps(query_handler.handle_query(filter_criteria)),
                    mimetype="application/json")


@app.route('/suggest_imagenet_class', methods=['GET'])
def suggest_imagenet_class():
    query_string = request.args.get("query")
    return Response(json.dumps(suggester.predict_class(query_string)), mimetype="application/json")


@app.route('/', methods=['GET'])
def sample():
    return "Hello from our api!"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000')
