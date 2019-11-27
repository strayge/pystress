import argparse
import json
import logging
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
    parser.add_argument("-n", help="threads/processes count", type=int, default=10)
    parser.add_argument("-p", help="use processes in pool (default - threads)", action="store_true")
    parser.add_argument("--no-shuffle", help="shuffle all jobs", action="store_true")
    parser.add_argument("--head", help="show head of each response", action="store_true")
    parser.add_argument("--output", help="show full response", action="store_true")
    parser.add_argument("-j", help="parse json response", action="store_true")
    parser.add_argument("-t", help="read timeout for requests", type=int, default=20)
    return parser.parse_args()

def make_request(params):
    result = {'status': None, 'time': None}
    try:
        settings = params.get('settings', {})
        timeout = settings.get('t')
        head = settings.get('head')
        output = settings.get('output')
        read_json = settings.get('j')

        method = params.get('method', 'GET')
        url = params.get('url')
        headers = params.get('headers')
        data = (
            params.get('data')
            if isinstance(params.get('data'), dict)
            else params.get('data')
        )

        req_start_time = time.time()
        resp = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            timeout=timeout,
        )
        req_end_time = time.time()

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

        if hits:
            log = f'{resp.status_code} [{hits}] <{url}>'
        else:
            log = f'{resp.status_code} <{url}>'
        if output:
            log += f'\n{resp.content}'
        elif head:
            log += f'\n{resp.content[:200]}'

        logger.info(log)

        result['status'] = resp.status_code
        result['time'] = req_end_time - req_start_time
    except Exception as e:
        logger.exception(repr(e))
        result['status'] = repr(e)
    return result


def main(args):
    global queue
    if args.p:
        from multiprocessing import Pool, Queue
    else:
        from multiprocessing.pool import ThreadPool as Pool

    logger.info('init')

    settings = dict(args.__dict__)

    with open('stress.json', 'rt') as f:
        jobs_json = json.load(f)

    jobs = []

    for job_json in jobs_json:
        method = job_json.get('method')
        url = job_json.get('url')
        headers = job_json.get('headers')
        data = job_json.get('data')
        count = job_json.get('count', 1)

        for i in range(count):
            jobs.append(dict(
                method=method,
                url=url,
                headers=headers,
                data=data,
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
    times = [r['time'] for r in results if r['time'] is not None]

    print(
        f'-----------------------------------------------------------------\n'
        f'total {len(results)} requests in {total_time:.3} seconds\n'
        f'min: {min(times):.3}s, '
        f'max: {max(times):.3}s, '
        f'avg: {sum(times)/len(times):.3}\n'
        f'statuses:'
    )
    print('\n'.join([f'{x}: {statuses[x]}' for x in statuses]))
    print('-----------------------------------------------------------------')


if __name__ == '__main__':
    args = parse_arguments()
    main(args)
