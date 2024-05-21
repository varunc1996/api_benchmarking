# Default value for MAX_CONCURRENT_REQUESTS
DEFAULT_MAX_CONCURRENT_REQUESTS := 10

# Allow overriding of MAX_CONCURRENT_REQUESTS via command-line argument
MAX_CONCURRENT_REQUESTS := $(if $(value CONCURRENCY),$(value CONCURRENCY),$(DEFAULT_MAX_CONCURRENT_REQUESTS))

# Run the Flask API server with the specified or default max concurrent requests
run:
	@echo "Running Flask server with max-concurrent-requests=$(MAX_CONCURRENT_REQUESTS)"
	@python server_app/routes.py --max-concurrent-requests=$(MAX_CONCURRENT_REQUESTS)

# .PHONY: run
