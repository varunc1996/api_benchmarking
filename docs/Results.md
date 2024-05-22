# Benchmarking Results

I decided to do away with the concept of input tokens for this exercise and just focus on output_tokens to simplify the logic in the Flask API server. The benchmarking endpoint I used `/tokenizer` accepts just 1 integer parameter (`output_tokens`) and based on the size of the number, it will sleep for an associated amount of time and return the `output_token` value back to us. I designed it this way to mimic an API request with high netowrk IO wait time, like an LLM HTTP request might take. It also allows us to more easily accentuate the benefits of the asynchronous aspects of the benchmarking script. In reality, an LLM HTTP request's latency would actually be a function of both the number of input tokens and output tokens, but in this example, having just 1 lever to pull was a simpler way to higlight that behavior.

## Initial testing of concurrency

I wanted to initially test that the concurrency is working as I expect it to in both the Flask API server and the benchmarking script. So I ran the flask server with default configs (maximum of 10 concurrent requests): `make run`

`endpoints.txt`:
```
http://localhost:5000/tokenizer?output_tokens=3
```

<details>
<summary> 500 Requests, 10 concurrency </summary>

```
$ python benchmarking/async_benchmarking.py --requests 500 --concurrency 10 --targets endpoints.txt
*** Results ***
Status codes:
  200: 500 times
Success ratio: 100.00%
--- - --- - ---
Total time: 51.1278 seconds
Median latency: 1.0119  |  Average latency: 1.0216 seconds
Shortest request time: 1.0014 seconds  |  Longest request time: 1.2117 seconds
--- - --- - ---
Throughput: 9.7794 requests per second
Avg Output Tokens: 3.0000  |  Output Token Throughput: 29.3383 tokens per second
```
</details>

<details>
<summary> 500 Requests, 25 concurrency </summary>

```
$ python benchmarking/async_benchmarking.py --requests 500 --concurrency 25 --targets endpoints.txt
*** Results ***
Status codes:
  200: 10 times
  429: 490 times
Success ratio: 2.00%
--- - --- - ---
Total time: 1.0270 seconds
Median latency: 0.0097  |  Average latency: 0.0310 seconds
Shortest request time: 0.0046 seconds  |  Longest request time: 1.0248 seconds
--- - --- - ---
Throughput: 486.8681 requests per second
Avg Output Tokens: 0.0600  |  Output Token Throughput: 29.2121 tokens per second
```
</details>

This was just to corroborate that if I sent more requests concurrently than what the Flask API server could handle at once, I was going to correctly get several `429` response codes.

## Modifying output tokens

For the rest of the testing, I ran the flask server with concurrency of 100: `make run CONCURRENCY=100`

For this stage of testing, I wanted to display how the number of output tokens would affect the latency/throughput.

<details>
<summary> 100 Requests, 10 concurrency, 3 output tokens per request: 10.2s </summary>

`endpoints.txt`:
```
http://localhost:5000/tokenizer?output_tokens=3
```

Results:
```
$ python benchmarking/async_benchmarking.py --requests 100 --concurrency 10 --targets endpoints.txt
*** Results ***
Status codes:
  200: 100 times
Success ratio: 100.00%
--- - --- - ---
Total time: 10.2185 seconds
Median latency: 1.0189  |  Average latency: 1.0206 seconds
Shortest request time: 1.0052 seconds  |  Longest request time: 1.0411 seconds
--- - --- - ---
Throughput: 9.7861 requests per second
Avg Output Tokens: 3.0000  |  Output Token Throughput: 29.3584 tokens per second
```
</details>

<details>
<summary> 100 Requests, 10 concurrency, 30 output tokens per request: 20.2s </summary>

`endpoints.txt`:
```
http://localhost:5000/tokenizer?output_tokens=30
```

Results:
```
$ python benchmarking/async_benchmarking.py --requests 100 --concurrency 10 --targets endpoints.txt
*** Results ***
Status codes:
  200: 100 times
Success ratio: 100.00%
--- - --- - ---
Total time: 20.2182 seconds
Median latency: 2.0171  |  Average latency: 2.0202 seconds
Shortest request time: 2.0045 seconds  |  Longest request time: 2.0479 seconds
--- - --- - ---
Throughput: 4.9461 requests per second
Avg Output Tokens: 30.0000  |  Output Token Throughput: 148.3813 tokens per second
```
</details>

<details>
<summary> 100 Requests, 10 concurrency, 300 output tokens per request: 30.1s </summary>

`endpoints.txt`:
```
http://localhost:5000/tokenizer?output_tokens=300
```

Results:
```
$ python benchmarking/async_benchmarking.py --requests 100 --concurrency 10 --targets endpoints.txt
*** Results ***
Status codes:
  200: 100 times
Success ratio: 100.00%
--- - --- - ---
Total time: 30.1206 seconds
Median latency: 3.0110  |  Average latency: 3.0115 seconds
Shortest request time: 3.0024 seconds  |  Longest request time: 3.0266 seconds
--- - --- - ---
Throughput: 3.3199 requests per second
Avg Output Tokens: 300.0000  |  Output Token Throughput: 995.9944 tokens per second
```
</details>

<details>
<summary> 100 Requests, 10 concurrency, 3000 output tokens per request: 50.2s </summary>

`endpoints.txt`:
```
http://localhost:5000/tokenizer?output_tokens=3000
```

Results:
```
$ python benchmarking/async_benchmarking.py --requests 100 --concurrency 10 --targets endpoints.txt
*** Results ***
Status codes:
  200: 100 times
Success ratio: 100.00%
--- - --- - ---
Total time: 50.1952 seconds
Median latency: 5.0163  |  Average latency: 5.0187 seconds
Shortest request time: 5.0035 seconds  |  Longest request time: 5.0457 seconds
--- - --- - ---
Throughput: 1.9922 requests per second
Avg Output Tokens: 3000.0000  |  Output Token Throughput: 5976.6658 tokens per second
```
</details>

Obviously, as the ouput_token size gets larger (the return of the API also takes longer) with fixed concurrency, the total time increases accordingly.

## Modifying concurrency

Where the benchmarking script really thrives, and async functions in general flourish, is being able to concurrently handle requests that involve waiting (mimicking high network IO wait time calls). I fixed the output tokens to 300 for all these tests.

`endpoints.txt`:
```
http://localhost:5000/tokenizer?output_tokens=300
```

<details>
<summary> 500 Requests, 10 concurrency: 152.3s </summary>

```
$ python benchmarking/async_benchmarking.py --requests 500 --concurrency 10 --targets endpoints.txt
*** Results ***
Status codes:
  200: 500 times
Success ratio: 100.00%
--- - --- - ---
Total time: 152.2734 seconds
Median latency: 3.0377  |  Average latency: 3.0423 seconds
Shortest request time: 3.0107 seconds  |  Longest request time: 3.1984 seconds
--- - --- - ---
Throughput: 3.2835 requests per second
Avg Output Tokens: 300.0000  |  Output Token Throughput: 985.0702 tokens per second
```
</details>

<details>
<summary> 500 Requests, 25 concurrency: 62.1s </summary>

```
$ python benchmarking/async_benchmarking.py --requests 500 --concurrency 25 --targets endpoints.txt
*** Results ***
Status codes:
  200: 500 times
Success ratio: 100.00%
--- - --- - ---
Total time: 62.1173 seconds
Median latency: 3.0468  |  Average latency: 3.0813 seconds
Shortest request time: 3.0028 seconds  |  Longest request time: 3.5544 seconds
--- - --- - ---
Throughput: 8.0492 requests per second
Avg Output Tokens: 300.0000  |  Output Token Throughput: 2414.7879 tokens per second
```
</details>

<details>
<summary> 500 Requests, 50 concurrency: 30.3s </summary>

```
$ python benchmarking/async_benchmarking.py --requests 500 --concurrency 50 --targets endpoints.txt
*** Results ***
Status codes:
  200: 500 times
Success ratio: 100.00%
--- - --- - ---
Total time: 30.3777 seconds
Median latency: 3.0358  |  Average latency: 3.0365 seconds
Shortest request time: 3.0064 seconds  |  Longest request time: 3.0660 seconds
--- - --- - ---
Throughput: 16.4594 requests per second
Avg Output Tokens: 300.0000  |  Output Token Throughput: 4937.8361 tokens per second
```
</details>

<details>
<summary> 500 Requests, 100 concurrency: 15.6s </summary>

```
$ python benchmarking/async_benchmarking.py --requests 500 --concurrency 100 --targets endpoints.txt
*** Results ***
Status codes:
  200: 500 times
Success ratio: 100.00%
--- - --- - ---
Total time: 15.6030 seconds
Median latency: 3.0525  |  Average latency: 3.1036 seconds
Shortest request time: 3.0015 seconds  |  Longest request time: 3.4362 seconds
--- - --- - ---
Throughput: 32.0451 requests per second
Avg Output Tokens: 300.0000  |  Output Token Throughput: 9613.5125 tokens per second
```
</details>

As we can see, keeping the ouput tokens the same, and only adjusting the concurrency, we can see that the higher the concurrency, the faster we finish and the higher the throughput, for the same number of similar requests

## Variable number of output tokens

In this set of tests I wanted to now have several types of requests with different numbers of output_tokens (similar to what an actual LLM's HTTP endpoint would see), and wanted to test the throughputs/latencies as I adjusted the concurrency

`endpoints.txt`:
```
http://localhost:5000/tokenizer?output_tokens=3
http://localhost:5000/tokenizer?output_tokens=30
http://localhost:5000/tokenizer?output_tokens=300
http://localhost:5000/tokenizer?output_tokens=3000
http://localhost:5000/tokenizer?output_tokens=30000
```

<details>
<summary> 500 Requests, 10 concurrency: 163.5s </summary>

```
$ python benchmarking/async_benchmarking.py --requests 500 --concurrency 10 --targets endpoints.txt
*** Results ***
Status codes:
  200: 500 times
Success ratio: 100.00%
--- - --- - ---
Total time: 163.4575 seconds
Median latency: 3.0084  |  Average latency: 3.2145 seconds
Shortest request time: 1.0020 seconds  |  Longest request time: 5.0286 seconds
--- - --- - ---
Throughput: 3.0588 requests per second
Avg Output Tokens: 7497.9300  |  Output Token Throughput: 22935.4101 tokens per second
```
</details>

<details>
<summary> 500 Requests, 25 concurrency: 67.1s </summary>

```
$ python benchmarking/async_benchmarking.py --requests 500 --concurrency 25 --targets endpoints.txt
*** Results ***
Status codes:
  200: 500 times
Success ratio: 100.00%
--- - --- - ---
Total time: 67.1320 seconds
Median latency: 3.0068  |  Average latency: 3.2163 seconds
Shortest request time: 1.0016 seconds  |  Longest request time: 5.0296 seconds
--- - --- - ---
Throughput: 7.4481 requests per second
Avg Output Tokens: 7237.5960  |  Output Token Throughput: 53905.7356 tokens per second
```
</details>

<details>
<summary> 500 Requests, 50 concurrency: 35.2s </summary>

```
$ python benchmarking/async_benchmarking.py --requests 500 --concurrency 50 --targets endpoints.txt
*** Results ***
Status codes:
  200: 500 times
Success ratio: 100.00%
--- - --- - ---
Total time: 35.1906 seconds
Median latency: 3.0071  |  Average latency: 3.2033 seconds
Shortest request time: 1.0022 seconds  |  Longest request time: 5.0915 seconds
--- - --- - ---
Throughput: 14.2083 requests per second
Avg Output Tokens: 6562.5420  |  Output Token Throughput: 93242.8397 tokens per second
```
</details>

<details>
<summary> 500 Requests, 100 concurrency: 19.1s </summary>

```
$ python benchmarking/async_benchmarking.py --requests 500 --concurrency 100 --targets endpoints.txt
*** Results ***
Status codes:
  200: 500 times
Success ratio: 100.00%
--- - --- - ---
Total time: 19.1005 seconds
Median latency: 3.0125  |  Average latency: 3.2725 seconds
Shortest request time: 1.0020 seconds  |  Longest request time: 5.0529 seconds
--- - --- - ---
Throughput: 26.1772 requests per second
Avg Output Tokens: 7131.4320  |  Output Token Throughput: 186681.4221 tokens per second
```
</details>

Again, as expected, over the same set of requests that are randomly picked each time, as we increased the concurrency of our benchmarking tests, we were able to achieve higher request and output token throughput and were able to finish the same set of random requests in less time.

## Conclusion & Thoughts

Not all that ground breaking, was the fact that as we increased concurrency of our API benchmarking system, we were able to sustain a higher throughput and make the same number of requests in less time.

In order to better mimic an LLM's HTTP endpoint, I actually initially created a random word generator function, and the `/tokenizer` endpoint was returning a corresponding number of words based on the number of `output_tokens` the request asked for. However, when stress testing that endpoint, especially with higher concurrency, the flask API server was bottlenecked at the random word generator function because I had several HTTP requests making several additional calls to that word generator function; therefore, increased concurrency wasn't actually translating to higher throughput, so I decided to abandon that idea and not overcomplicate the flask server.

I could have made the API server more resilient using `gunicorn` along with Flask, and therefore could have had several workers/threads. That may have ameliorated the bottleneck I mentioned above, however, then this would have become an exercise focused on optimizing the API server's work capacity instead.

In the past I've usually used golang when trying to write more concurrent code, as I've found that it's generally optimized around and promoting of goroutines. This was my first time using python's coroutines for a similar goal.
