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
  -j              parse json response
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
        "count": 20
    },
    {
        "method": "GET",
        "url": "http://127.1:9200/",
        "headers": {"Content-Type": "application/json"},
        "data": "embedded payload (can be string or dictionary)",
        "count": 2
    }
]
```