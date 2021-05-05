from flask import Flask, Response, request
from flask_cors import CORS
import json

from class_name_suggester import ClassNameSuggester
from data_classes import FilterCriteria
from query_handler import QueryHandler

app = Flask(__name__)
CORS(app)

suggester = ClassNameSuggester()
query_handler = QueryHandler()

@app.route('/execute_query', methods=['POST'])
def execute_query():
    filter_criteria_canvas: FilterCriteria = FilterCriteria.from_json(request.get_data().decode("utf-8"))
    #filter_criteria_nasnet = request.args.get("query")
    return Response(json.dumps(query_handler.handle_query(filter_criteria_canvas)),
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
