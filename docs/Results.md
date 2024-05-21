# Benchmarking Results

## Initial testing of concurrency

I wanted to initially test the the concurrency is working as I expect it to. So I ran the flask server with default configurations and the benchmarking script with 100 requests at concurreny of 10, then 100 requests with concurrency of 100, with an output token request of 300000 for each request.

<details>
<summary> endpoints.txt </summary>

```
http://localhost:5000/tokenizer?output_tokens=300000&input_text=abcdefgh
```
</details>

<details>
<summary> 100 Requests, 10 concurrency </summary>

```
$ python benchmarking/async_benchmarking.py --requests 100 --concurrency 10 --targets endpoints.txt
*** Results ***
Status codes:
  200: 100 times
Success ratio: 100.00%
--- - --- - ---
Total time: 9.1415 seconds
Median latency: 0.8848  |  Average latency: 0.8865 seconds
Shortest request time: 0.4683 seconds  |  Longest request time: 1.4985 seconds
--- - --- - ---
Throughput: 10.939075850185478 requests per second
Avg Input Tokens: 2.0000  |  Avg Output Tokens: 300000.0000
Input Token Throughput: 21.8782 tokens per second  |  Output Token Throughput: 3281722.7551 tokens per second
```
</details>

<details>
<summary> 100 Requests, 100 concurrency </summary>

```
$ python benchmarking/async_benchmarking.py --requests 100 --concurrency 100 --targets endpoints.txt
*** Results ***
Status codes:
  200: 45 times
  429: 55 times
Success ratio: 45.00%
--- - --- - ---
Total time: 4.2960 seconds
Median latency: 3.2156  |  Average latency: 2.9817 seconds
Shortest request time: 0.2459 seconds  |  Longest request time: 4.2917 seconds
--- - --- - ---
Throughput: 23.277331747585237 requests per second
Avg Input Tokens: 0.9000  |  Avg Output Tokens: 135000.0000
Input Token Throughput: 20.9496 tokens per second  |  Output Token Throughput: 3142439.7859 tokens per second
```
</details>

This was just to corroborate that if I sent more requests concurrently than what the Flask API server can handle at once, I was going to correctly get some `429` response codes.

## Modifying concurrency

For the rest of the testing, I ran the flask server with concurrency of 100: `make run CONCURRENCY=100`

<details>
<summary> endpoints.txt </summary>

```
http://localhost:5000/tokenizer?output_tokens=3000&input_text=abcdefgh
```
</details>

<details>
<summary> 10K Requests, 5 concurrency, 3K ouput tokens per request: 29.2s </summary>

```
$ python benchmarking/async_benchmarking.py --requests 10000 --concurrency 5 --targets endpoints.txt
*** Results ***
Status codes:
  200: 10000 times
Success ratio: 100.00%
--- - --- - ---
Total time: 29.1562 seconds
Median latency: 0.0065  |  Average latency: 0.0145 seconds
Shortest request time: 0.0016 seconds  |  Longest request time: 13.1148 seconds
--- - --- - ---
Throughput: 342.98051624263013 requests per second
Avg Input Tokens: 2.0000  |  Avg Output Tokens: 3000.0000
Input Token Throughput: 685.9610 tokens per second  |  Output Token Throughput: 1028941.5487 tokens per second
```
</details>

<details>
<summary> 10K Requests, 10 concurrency, 3K ouput tokens per request: 17.3s </summary>

```
$ python benchmarking/async_benchmarking.py --requests 10000 --concurrency 10 --targets endpoints.txt
*** Results ***
Status codes:
  200: 10000 times
Success ratio: 100.00%
--- - --- - ---
Total time: 17.3026 seconds
Median latency: 0.0150  |  Average latency: 0.0171 seconds
Shortest request time: 0.0045 seconds  |  Longest request time: 0.1030 seconds
--- - --- - ---
Throughput: 577.9483276959896 requests per second
Avg Input Tokens: 2.0000  |  Avg Output Tokens: 3000.0000
Input Token Throughput: 1155.8967 tokens per second  |  Output Token Throughput: 1733844.9831 tokens per second
```
</details>

<details>
<summary> 10K Requests, 15 concurrency, 3K ouput tokens per request: 15.7s </summary>

```
$ python benchmarking/async_benchmarking.py --requests 10000 --concurrency 15 --targets endpoints.txt
*** Results ***
Status codes:
  200: 10000 times
Success ratio: 100.00%
--- - --- - ---
Total time: 15.7279 seconds
Median latency: 0.0205  |  Average latency: 0.0234 seconds
Shortest request time: 0.0039 seconds  |  Longest request time: 0.3286 seconds
--- - --- - ---
Throughput: 635.8147659899045 requests per second
Avg Input Tokens: 2.0000  |  Avg Output Tokens: 3000.0000
Input Token Throughput: 1271.6295 tokens per second  |  Output Token Throughput: 1907444.2980 tokens per second
```
</details>

<details>
<summary> 10K Requests, 20 concurrency, 3K ouput tokens per request: 13.5s </summary>

```
$  python benchmarking/async_benchmarking.py --requests 10000 --concurrency 20 --targets endpoints.txt
*** Results ***
Status codes:
  200: 10000 times
Success ratio: 100.00%
--- - --- - ---
Total time: 13.5230 seconds
Median latency: 0.0260  |  Average latency: 0.0269 seconds
Shortest request time: 0.0115 seconds  |  Longest request time: 0.0730 seconds
--- - --- - ---
Throughput: 739.4807800149299 requests per second
Avg Input Tokens: 2.0000  |  Avg Output Tokens: 3000.0000
Input Token Throughput: 1478.9616 tokens per second  |  Output Token Throughput: 2218442.3400 tokens per second
```
</details>

As we can see, keeping the ouput tokens the same, and only adjusting the concurrency, we can see that the higher the concurrency, the faster we finish and the higher the throughput, for the same number of similar requests

## Modifying output tokens

For this stage of testing, I wanted to see how the number of output tokens would affect the latency/throughput.

<details>
<summary> 10K Requests, 10 concurrency, 30 output tokens per request: 4.5s </summary>

endpoints.txt:
```
http://localhost:5000/tokenizer?output_tokens=30&input_text=abcdefgh
```

Results:
```
$ python benchmarking/async_benchmarking.py --requests 10000 --concurrency 10 --targets endpoints.txt
*** Results ***
Status codes:
  200: 10000 times
Success ratio: 100.00%
--- - --- - ---
Total time: 4.4980 seconds
Median latency: 0.0039  |  Average latency: 0.0044 seconds
Shortest request time: 0.0019 seconds  |  Longest request time: 0.0512 seconds
--- - --- - ---
Throughput: 2223.217314607504 requests per second
Avg Input Tokens: 2.0000  |  Avg Output Tokens: 30.0000
Input Token Throughput: 4446.4346 tokens per second  |  Output Token Throughput: 66696.5194 tokens per second
```
</details>

<details>
<summary> 10K Requests, 10 concurrency, 3K output tokens per request: 20.3s </summary>

endpoints.txt:
```
http://localhost:5000/tokenizer?output_tokens=3000&input_text=abcdefgh
```

Results:
```
$ python benchmarking/async_benchmarking.py --requests 10000 --concurrency 10 --targets endpoints.txt
*** Results ***
Status codes:
  200: 10000 times
Success ratio: 100.00%
--- - --- - ---
Total time: 20.2512 seconds
Median latency: 0.0082  |  Average latency: 0.0202 seconds
Shortest request time: 0.0014 seconds  |  Longest request time: 13.1212 seconds
--- - --- - ---
Throughput: 493.7991143812041 requests per second
Avg Input Tokens: 2.0000  |  Avg Output Tokens: 3000.0000
Input Token Throughput: 987.5982 tokens per second  |  Output Token Throughput: 1481397.3431 tokens per second
```
</details>

<details>
<summary> 10K Requests, 10 concurrency, 300K output tokens per request: 918.4s </summary>

endpoints.txt:
```
http://localhost:5000/tokenizer?output_tokens=300000&input_text=abcdefgh
```

Results:
```
$ python benchmarking/async_benchmarking.py --requests 10000 --concurrency 10 --targets endpoints.txt
*** Results ***
Status codes:
  200: 10000 times
Success ratio: 100.00%
--- - --- - ---
Total time: 918.4218 seconds
Median latency: 0.9027  |  Average latency: 0.9180 seconds
Shortest request time: 0.3070 seconds  |  Longest request time: 4.4582 seconds
--- - --- - ---
Throughput: 10.888243337908905 requests per second
Avg Input Tokens: 2.0000  |  Avg Output Tokens: 300000.0000
Input Token Throughput: 21.7765 tokens per second  |  Output Token Throughput: 3266473.0014 tokens per second
```
</details>
