from __future__ import print_function

import dask.bag
import dask.multiprocessing
from dask.distributed import Client


def serial(func, parameters):
    """Run the function with the parameters serially."""
    results = []
    for p in parameters:
        results.append(func(p))
    return results

def multiprocess(func, parameters):
    """Run the function with the parameters in parallel using multiprocessing."""
    bag = dask.bag.from_sequence(parameters)
    
    with dask.set_options(get=dask.multiprocessing.get):
        if hasattr(parameters[0], 'num_workers'):
            results = bag.map(func).compute(num_workers=parameters[0].num_workers)
        else:
            # num of workers is defaulted to the number of logical processes
            results = bag.map(func).compute()

        return results

def distribute(func, parameters):
    """Run the function with the parameters in parallel distributedly."""
    try:
        if not hasattr(parameters[0], 'scheduler_addr'):
            raise RuntimeError('scheduler_addr parameter is needed to run diagnostics distributedly.')

        client = Client(parameters[0].scheduler_addr)
        results = client.map(func, parameters)
        client.gather(results)
    except Exception as e:
        print('Distributed run failed.')
        print(e)
        return []
    finally:
        client.close()

    return results
