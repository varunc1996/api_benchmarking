# api_benchmarking
API benchmarking system

## Setup

I used python version `3.12.2`. To setup virtual environment in which to run flask server and benchmarking scripts you can run:

```
python -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
```

## Running Flask API server

To run the flask server, you can either run it with python directly or through the `make` target.

```
# Directly with python
python server_app/routes.py --max-concurrent-requests 10

# Through make. It has a default max concurrency of 10 in the Makefile
make run

# If you want a higher max concurrency
make run CONCURRENCY=100
```

## Running Benchmarking Script

The benchmarking script takes 3 parameters: `requests`, `concurrency` & `targets`

<details>
<summary>Parameters</summary>

| Parameter | Type Type | Default | Description |
| --- | --- | ---- | --- |
| `requests` | `int` | 10 | Total number of requests to execute |
| `concurrency` | `int` | 5 | Maximum number of parallel requests allowed |
| `targets` | `string` | `endpoints.txt` | Path to the file containing endpoints to randomly hit |
</details>

```
# Example
python benchmarking/async_benchmarking.py --requests 10 --concurrency 5 --targets endpoints.txt
```

[Benchmarking Results](docs/Results.md)
