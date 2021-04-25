from flask import Flask, Response, request
from flask_cors import CORS
import json

from class_name_suggester import ClassNameSuggester

app = Flask(__name__)
CORS(app)

suggester = ClassNameSuggester()


@app.route('/execute_filter', methods=['POST'])
def execute_filter():
    request_body = json.loads(request.get_data().decode("utf-8"))
    return Response(json.dumps({request: request_body}),
                    mimetype="application/json")


@app.route('/suggest_imagenet_class', methods=['GET'])
def suggest_imagenet_class():
    query_string = request.args.get("query")
    return Response(json.dumps({"classes": suggester.predict_class(query_string)}), mimetype="application/json")


@app.route('/', methods=['GET'])
def sample():
    return "Hello from our api!"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000')
