import argparse
import json
import logging
import math
import random
import time
from collections import Counter

import requests

logging.basicConfig(
    format='%(asctime)-15s %(processName)-18s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", help="threads/processes count", type=int, default=10, metavar='10')
    parser.add_argument("-p", help="use processes in pool (default - threads)", action="store_true")
    parser.add_argument("--no-shuffle", help="do not shuffle all jobs", action="store_true")
    parser.add_argument("--head", help="show head of each response", action="store_true")
    parser.add_argument("--output", help="show full response", action="store_true")
    parser.add_argument("-j", help="parse json response", action="store_true")
    parser.add_argument("-t", help="read timeout for requests", type=int, default=20, metavar='20')
    parser.add_argument("-f", help="config filename", type=str, default='stress.json', metavar='stress.json')
    return parser.parse_args()


def shorter(line):
    if len(line) > 80:
        if '(' in line[:60]:
            return line.split('(', 1)[0]
        return line[:35] + '...' + line[-35:]
    return line


def percentile(values, percent):
    size = len(values)
    position = int(math.ceil((size * percent) / 100)) - 1
    return sorted(values)[position] if len(values) >= position else -1.0


def make_request(params):
    result = {'status': None, 'time': None}

    settings = params.get('settings', {})
    timeout = settings.get('t')
    head = settings.get('head')
    output = settings.get('output')
    read_json = settings.get('j')

    method = params.get('method', 'GET')
    url = params.get('url')
    headers = params.get('headers')
    data = params.get('data')
    if isinstance(data, dict):
        data = json.dumps(data)

    try:
        req_start_time = time.time()
        resp = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            timeout=timeout,
        )
        req_end_time = time.time()
        result['status'] = resp.status_code
        result['time'] = req_end_time - req_start_time

        hits = None
        if read_json:
            try:
                if resp.status_code < 300:
                    resp_json = json.loads(resp.content)
                    hits = resp_json['hits']['total']
                else:
                    hits = 'ERR'
            except Exception as e:
                hits = repr(e)

        if read_json:
            log = f'{resp.status_code} {result["time"]:5.2f}s  [{hits}]  <{url}>'
        else:
            log = f'{resp.status_code} {result["time"]:5.2f}s  <{url}>'
        if output:
            log += f'\n{resp.content}'
        elif head:
            log += f'\n{resp.content[:200]}'

        logger.info(log)
    except requests.exceptions.ConnectionError as e:
        result['status'] = shorter(repr(e))
        logger.error(f'ERR  {shorter(repr(e))}  <{url}>')
    except Exception as e:
        logger.exception(repr(e))
        result['status'] = shorter(repr(e))
    return result


def main(args):
    if args.p:
        from multiprocessing import Pool
    else:
        from multiprocessing.pool import ThreadPool as Pool

    logger.info('init')

    settings = dict(args.__dict__)

    with open(args.f, 'rt') as f:
        jobs_json = json.load(f)

    jobs = []

    for job_json in jobs_json:
        count = job_json.get('count', 1)

        filename = job_json.get('filename')
        if filename:
            with open(filename, 'rb') as f:
                job_json['data'] = f.read()

        for i in range(count):
            jobs.append(dict(
                **job_json,
                settings=settings,
            ))

    if not args.no_shuffle:
        random.shuffle(jobs)

    pool = Pool(processes=args.n)

    start_time = time.time()
    logger.info('starting')
    results = pool.map(make_request, jobs)
    logger.info('done')
    end_time = time.time()
    total_time = end_time - start_time

    statuses = Counter([r['status'] for r in results])
    times = [r['time'] for r in results if r['time'] is not None] or [-1.0]

    print(
        f'-----------------------------------------------------------------\n'
        f'total {len(results)} requests in {total_time:.3f} seconds\n'
        f'min: {min(times):.3f}, '
        f'max: {max(times):.3f}, '
        f'avg: {sum(times)/len(times):.3f}\n'
        f'P50: {percentile(times, 50):.3f}, '
        f'P90: {percentile(times, 90):.3f}, '
        f'P95: {percentile(times, 95):.3f}, '
        f'P99: {percentile(times, 99):.3f}\n'
        f'\n'
        f'============================ statuses ==========================='
    )
    for x in statuses:
        c = statuses[x]
        print(f'{x:<20} {c:6}    ({c/len(results)*100:5.2f}%)')
    print('-----------------------------------------------------------------')


if __name__ == '__main__':
    args = parse_arguments()
    main(args)
