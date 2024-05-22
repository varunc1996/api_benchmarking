from flask import Flask, jsonify, request
from functools import wraps

import argparse
import math
import random
import threading
import time

app = Flask(__name__)
concurrent_requests = 0
lock = threading.Lock()


def increment_concurrent_requests():
    """
    Increment number of ongoing requests using lock
    """
    global concurrent_requests
    with lock:
        concurrent_requests += 1


def decrement_concurrent_requests():
    """
    Decrement number of ongoing requests using lock
    """
    global concurrent_requests
    with lock:
        concurrent_requests -= 1


def check_concurrent_requests(func):
    """
    Wrapper function to handle concurrency of the flask API server
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f'concurrent requests: {concurrent_requests}')
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


# For testing purposes
@app.route('/hello')
@check_concurrent_requests
def hello():
    return "Hello World"


# For testing concurrency purposes
@app.route('/sleeper')
@check_concurrent_requests
def sleeper():
    sleep_length = int(request.args.get('sleep_length'))

    if not sleep_length:
        sleep_length = 1

    time.sleep(sleep_length)
    return f"slept for {sleep_length} second"


# The endpoint to use for benchmarking
@app.route('/tokenizer', methods=['GET'])
@check_concurrent_requests
def tokenizer():
    output_tokens = int(request.args.get('output_tokens'))

    if not output_tokens:
        return "Invalid input", 400

    # To mimic different amounts of output tokens configurations,
    # just sleep to represent a request taking longer for more output tokens
    if output_tokens < 10:  # Few output tokens takes less time
        time.sleep(1)
    elif output_tokens < 100:
        time.sleep(2)
    elif output_tokens < 1000:
        time.sleep(3)
    else:
        time.sleep(5)

    return jsonify({
        'output_tokens': output_tokens,
    })


# To update app config
@app.route('/update_config', methods=['POST'])
def update_config():
    data = request.json
    if 'max_concurrent_requests' in data:
        app.config['MAX_CONCURRENT_REQUESTS'] = data['max_concurrent_requests']
        return jsonify(message="Max concurrent requests updated successfully")
    else:  # 'max_concurrent_requests' not in data:
        return jsonify(error="max_concurrent_requests field is required in the request"), 400


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Simple python flask server')
    parser.add_argument('--max-concurrent-requests', type=int, default=1,
                        help='Maximum number of concurrent requests allowed')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    app.config['MAX_CONCURRENT_REQUESTS'] = args.max_concurrent_requests
    app.run()
