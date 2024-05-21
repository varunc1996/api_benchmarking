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
        # print(f'concurrent requests: {concurrent_requests}')
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
    input_text = request.args.get('input_text')
    output_tokens = int(request.args.get('output_tokens'))

    if not input_text or not output_tokens:
        return "Invalid input", 400

    output_text, input_tokens = generate_response(input_text, output_tokens)

    # Just return both input and output tokens, so it's easier to
    # benchmarks and it's easy to use the target file without doing a bunch of string parsing
    return jsonify({
        'input_text': input_text, 'ouput_text': output_text,
        'input_tokens': input_tokens, 'output_tokens': output_tokens,
    })


def generate_response(input_text, output_tokens):
    """
    Generate a response text of length based on output_tokens & determine the number of input tokens
    Token length is between 1 & 26

    Args:
        input_text (string): The inputted string
        output_tokens (int): the length in tokens of the response

    Returns:
        string: some response string
        int: the number of tokens in the input string

    For reference, I assumed that 1 token == 4 characters 
    when figuring out how many tokens were in the input string (from OpenAI tokenizer website)
    Reference: https://platform.openai.com/tokenizer
    """

    output_text = ' '.join([generate_random_word() for _ in range(output_tokens)])

    input_tokens = math.ceil(len(input_text) / 4)
    return output_text, input_tokens


def generate_random_word():
    """
    Return a random word from the list
    """
    word_list = [
        "apple", "banana", "cherry", 
        "date", "elderberry", "fig", 
        "grape", "honeydew", "iron", 
        "jewel" "kiwi", "lemon"
        "melon", "night", "outside",
        "pencil", "quality", "rose", "steel",
        "torn", "under", "violet",
        "white", "xerox", "yellow", "zoo"]
    return random.choice(word_list)


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
