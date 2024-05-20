from flask import Flask, jsonify, request
from functools import wraps

import argparse
import threading

app = Flask(__name__)
concurrent_requests = 0
lock = threading.Lock()


def increment_concurrent_requests():
    global concurrent_requests
    with lock:
        concurrent_requests += 1


def decrement_concurrent_requests():
    global concurrent_requests
    with lock:
        concurrent_requests -= 1


def check_concurrent_requests(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if concurrent_requests >= app.config['MAX_CONCURRENT_REQUESTS']:
            return jsonify(error="Too many concurrent requests"), 429
        else:
            increment_concurrent_requests()
            try:
                response = func(*args, **kwargs)
                return response
            finally:
                decrement_concurrent_requests()
    return wrapper


@app.route('/hello')
@check_concurrent_requests
def hello():
    return "Hello"


@app.route('/world')
@check_concurrent_requests
def world():
    return "World"


@check_concurrent_requests
@app.route('/test3')
def test3():
    return "Test3"


@app.route('/config', methods=['POST'])
def set_config():
    data = request.json
    if 'max_concurrent_requests' in data:
        app.config['MAX_CONCURRENT_REQUESTS'] = data['max_concurrent_requests']
        return jsonify(message="Max concurrent requests updated successfully")
    else:
        return jsonify(error="max_concurrent_requests field is required in the request"), 400


def parse_arguments():
    parser = argparse.ArgumentParser(description='Run the Flask server')
    parser.add_argument('--max-concurrent-requests', type=int, default=1,
                        help='Maximum number of concurrent requests allowed')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    app.config['MAX_CONCURRENT_REQUESTS'] = args.max_concurrent_requests
    app.run(debug=True)
