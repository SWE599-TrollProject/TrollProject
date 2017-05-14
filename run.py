import json
from flask import (Flask, request, abort, jsonify, render_template)
from src.evaluator import Evaluator


class Err(Exception):
    def __init__(self, message, status_code, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


app = Flask('troll_tespit',
            template_folder='templates', static_folder='static')

@app.errorhandler(Err)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        screen_name = request.form['screen_name']
        evaluator = Evaluator(app.root_path)
        status, result = evaluator.evaluate(screen_name)
        if status != 200:
            raise Err(result, status_code=status)
        return json.dumps(result)
    else:
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
