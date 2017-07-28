#!/usr/bin/env python

import argparse
import subprocess
import shlex
import sys

P = argparse.ArgumentParser(
    description='CDP-based conda packages manager',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

P.add_argument(
    "-l",
    "--list",
    action="store_true",
    default=False,
    help="List all cdp-based packages")
P.add_argument(
    "-c",
    "--channel",
    nargs="+",
    default=[
        "pcmdi",
        "conda-forge",
        "acme"],
    help="Channel where to look")
args = P.parse_args()

if args.list:
    cmd = "conda search -c %s --names-only --reverse-dependency cdp" % " -c ".join(
        args.channel)
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
    out = []
    while p.poll() is None:
        a = p.stdout.readline()
        if len(a) > 0:
            out.append(a)
        sys.stdout.write(a)
