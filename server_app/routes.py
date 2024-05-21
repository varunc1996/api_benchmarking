from flask import Flask, jsonify, request
from functools import wraps

import argparse
import math
import threading
import time

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


@app.route('/hello')
@check_concurrent_requests
def hello():
    return "Hello World"


@app.route('/sleeper')
@check_concurrent_requests
def sleeper():
    sleep_length = int(request.args.get('sleep_length'))

    if not sleep_length:
        sleep_length = 1

    time.sleep(sleep_length)
    return f"slept for {sleep_length} second"


@app.route('/tokenizer', methods=['GET'])
@check_concurrent_requests
def tokenizer():
    input_text = request.args.get('input_text')
    output_tokens = int(request.args.get('output_tokens'))

    if not input_text or not output_tokens:
        return "Invalid input", 400

    output_text, input_tokens = generate_response(input_text, output_tokens)
    return jsonify({'ouput_text': output_text, 'input_tokens': input_tokens})


def generate_response(input_text, output_tokens):
    """
    Generate a response text of length based on output_tokens & determine the number of input tokens
    Max token length is 26

    Args:
        input_text (string): The inputted string
        output_tokens (int): the length in tokens of the response

    Returns:
        string: some response string
        int: the number of tokens in the input string
    """

    base_token = 'abcdefghijklmnopqrstuvwxyz'  # Max token length is 26
    output_text = base_token[:app.config['TOKEN_LENGTH']] * output_tokens

    input_tokens = math.ceil(len(input_text) / app.config['TOKEN_LENGTH'])
    return output_text, input_tokens


@app.route('/update_config', methods=['POST'])
def update_config():
    data = request.json
    if 'max_concurrent_requests' in data:
        app.config['MAX_CONCURRENT_REQUESTS'] = data['max_concurrent_requests']
        return jsonify(message="Max concurrent requests updated successfully")
    if 'token_length' in data:
        if data['token_length'] < 1:
            data['token_length'] = 1
        elif data['token_length'] > 26:
            data['token_length'] = 26

        app.config['TOKEN_LENGTH'] = data['token_length']
        return jsonify(message=f"Token length updated successfully to {data['token_length']}")

    if 'max_concurrent_requests' not in data and 'token_length' not in data:
        return jsonify(error="max_concurrent_requests/token_length field is required in the request"), 400


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments

    For reference, I assumed that 1 token == 4 characters (from OpenAI tokenizer website)
    Reference: https://platform.openai.com/tokenizer
    """
    parser = argparse.ArgumentParser(description='Simple python flask server')
    parser.add_argument('--max-concurrent-requests', type=int, default=1,
                        help='Maximum number of concurrent requests allowed')
    parser.add_argument('--token-length', type=int, default=4,
                        help='The number of characters that constitute a token. Between 1-26')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    app.config['MAX_CONCURRENT_REQUESTS'] = args.max_concurrent_requests
    app.config['TOKEN_LENGTH'] = args.token_length
    app.run()
