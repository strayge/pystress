# PyStress
Script for generating http requests by templates.  
Used as simple replacements for Yandex.Tank.  

### Usage
```
usage: stress.py [-h] [-n 10] [-p] [--no-shuffle] [--head] [--output] [-j]
                 [-t 20] [-f stress.json]

optional arguments:
  -h, --help      show this help message and exit
  -n 10           threads/processes count
  -p              use processes in pool (default - threads)
  --no-shuffle    do not shuffle all jobs
  --head          show head of each response
  --output        show full response
  -t 20           read timeout for requests
  -f stress.json  config filename
```

### Config
```json
[
    {
        "method": "GET",
        "url": "http://ya.ru/",
        "headers": {"Content-Type": "application/json"},
        "filename": "external_payload.txt",
        "count": 2
    },
    {
        "method": "GET",
        "url": "http://127.1:9200/",
        "headers": {"Content-Type": "application/json"},
        "data": "embedded payload (can be string or dictionary)",
        "count": 2
    },
    {
        "method": "GET",
        "url": "https://ggstats.strayge.com/viewers",
        "count": 2
    },
    {
        "method": "GET",
        "url": "http://api2.goodgame.ru/info/test",
        "count": 1
    }
]
```

### Result
```
$ python3 stress.py
2019-11-28 01:19:13 MainProcess        INFO     init
2019-11-28 01:19:13 MainProcess        INFO     starting
2019-11-28 01:19:13 MainProcess        ERROR    ERR  ConnectionError  <http://127.1:9200/>
2019-11-28 01:19:13 MainProcess        ERROR    ERR  ConnectionError  <http://127.1:9200/>
2019-11-28 01:19:13 MainProcess        INFO     404  0.21s  <http://api2.goodgame.ru/info/test>
2019-11-28 01:19:13 MainProcess        INFO     200  0.24s  <http://ya.ru/>
2019-11-28 01:19:13 MainProcess        INFO     200  0.29s  <http://ya.ru/>
2019-11-28 01:19:16 MainProcess        INFO     200  2.53s  <https://ggstats.strayge.com/viewers>
2019-11-28 01:19:16 MainProcess        INFO     200  2.60s  <https://ggstats.strayge.com/viewers>
2019-11-28 01:19:16 MainProcess        INFO     done
-----------------------------------------------------------------
total 7 requests in 2.598 seconds
min: 0.209, max: 2.596, avg: 1.172
P50: 0.292, P90: 2.596, P95: 2.596, P99: 2.596

============================ statuses ===========================
200                       4    (57.14%)
404                       1    (14.29%)
ConnectionError           2    (28.57%)
-----------------------------------------------------------------
```