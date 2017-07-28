import argparse
import socket
from datetime import datetime
from dask.distributed import Client

def display_workers(scheduler_addr, client):
    """Display all of the workers for the client"""
    raw_info = client.scheduler_info()
    workers_dict = raw_info['workers']
    print 'Scheduler {} has {} workers attached to it'.format(scheduler_addr, len(workers_dict))
    print ''
    for worker_name in sorted(workers_dict):
        _display_single_worker(worker_name, workers_dict[worker_name])

def _display_single_worker(name, worker_info):
    """Unpack a dictionary for a single worker and print relevent information"""
    ip_and_port = name.split('//')[-1]
    ip, port = ip_and_port.split(':')
    hostname = socket.gethostbyaddr(ip)[0]

    print 'Information about worker at {}({}):{}'.format(hostname, ip, port)
    # stuff_to_print = ['name', 'memory_limit', 'pid', 'last-seen', 'ncores', 'executing', 'last-task']
    stuff_to_print = ['name', 'ncores', 'executing', 'memory_limit', 'pid', 'last-task', 'last-seen']

    for stuff in stuff_to_print:
        if stuff in ['name', 'pid', 'ncores']:
            s = '\t{}:\t\t{}'
        else:
            s = '\t{}:\t{}'
        
        if stuff in ['last-seen', 'last-task']:
            worker_info[stuff] = datetime.fromtimestamp(int(worker_info[stuff])).strftime('%Y-%m-%d %H:%M:%S')
        print s.format(stuff, worker_info[stuff]) 
    print ''

parser = argparse.ArgumentParser("cdp-distrib")

parser.add_argument(
    "scheduler_addr",
    help="Address and port of the scheduler to query in the form ADDR:PORT"
)

parser.add_argument(
    "-w",
    "--workers",
    action="store_true",
    help="Display information of all of the workers on the scheduler"
)

args = parser.parse_args()
client = Client(args.scheduler_addr)


if args.workers:
    display_workers(args.scheduler_addr, client)



client.close()
