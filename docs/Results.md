# Benchmarking Results

## Initial testing of concurrency

I wanted to initially test the the concurrency is working as I expect it to in both the Flask API server and the benchmarking script. So I ran the flask server with default configs (maximum of 10 concurrent requests): `make run`

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
Throughput: 9.779417011136857 requests per second
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
Throughput: 486.8680518378227 requests per second
Avg Output Tokens: 0.0600  |  Output Token Throughput: 29.2121 tokens per second
```
</details>

This was just to corroborate that if I sent more requests concurrently than what the Flask API server can handle at once, I was going to correctly get several `429` response codes.

## Modifying output tokens

I decided to do away with the concept of input tokens for this exercise and just focus on output_tokens to simplify the logic in the Flask API server. The benchmarking endpoint I used `/tokenizer` accepts just 1 integer parameter (`output_tokens`) and based on the size of the number, it will sleep for an associated amount of time and return the `output_token` value back to us.

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
Throughput: 9.786148945824198 requests per second
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
Throughput: 4.946042108191865 requests per second
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
Throughput: 3.319981494938044 requests per second
Avg Output Tokens: 300.0000  |  Output Token Throughput: 995.9944 tokens per second
```
</details>

<details>
<summary> 100 Requests, 10 concurrency, 3000 output tokens per request: 50.2s </summary>

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
Total time: 50.1952 seconds
Median latency: 5.0163  |  Average latency: 5.0187 seconds
Shortest request time: 5.0035 seconds  |  Longest request time: 5.0457 seconds
--- - --- - ---
Throughput: 1.9922219204762557 requests per second
Avg Output Tokens: 3000.0000  |  Output Token Throughput: 5976.6658 tokens per second
```
</details>

Obiously, as the ouput_token size gets larger (the return of the API also takes longer) and with fixed concurrency, the total time increases accordingly.

## Modifying concurrency

Where the benchmarking script really thrives, and async functions in general flourish, is being able to concurrently handle requests that involve waiting (mimicking high network IO wait time calls). I fixed the output tokes at 300 for all these tests.

`endpoints.txt`:
```
http://localhost:5000/tokenizer?output_tokens=300
```

<details>
<summary> 500 Requests, 10 concurrency, 300 ouput tokens per request: 152.3s </summary>

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
Throughput: 3.283567391348978 requests per second
Avg Output Tokens: 300.0000  |  Output Token Throughput: 985.0702 tokens per second
```
</details>

<details>
<summary> 500 Requests, 25 concurrency, 300 ouput tokens per request: 62.1s </summary>

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
Throughput: 8.049293076878389 requests per second
Avg Output Tokens: 300.0000  |  Output Token Throughput: 2414.7879 tokens per second
```
</details>

<details>
<summary> 500 Requests, 50 concurrency, 300 ouput tokens per request: 30.3s </summary>

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
Throughput: 16.459453736433314 requests per second
Avg Output Tokens: 300.0000  |  Output Token Throughput: 4937.8361 tokens per second
```
</details>

<details>
<summary> 500 Requests, 100 concurrency, 300 ouput tokens per request: 15.6s </summary>

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
Throughput: 32.045041825451555 requests per second
Avg Output Tokens: 300.0000  |  Output Token Throughput: 9613.5125 tokens per second
```
</details>

As we can see, keeping the ouput tokens the same, and only adjusting the concurrency, we can see that the higher the concurrency, the faster we finish and the higher the throughput, for the same number of similar requests
