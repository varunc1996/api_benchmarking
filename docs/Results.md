# Benchmarking Results

## Initial testing of concurrency

I wanted to initially test the the concurrency is working as I expect it to. So I ran the flask server with default configurations and the benchmarking script with 100 requests at concurreny of 10, then 100 requests with concurrency of 100, with an output token request of 300000 for each request.

<details>
<summary> `endpoints.txt` </summary>

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

## Testing on small number of tokens

