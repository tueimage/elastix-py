#!/usr/bin/env python
#
# A class that handles Elastix log files
#
# @author: Koen Eppenhof
# @email: k.a.j.eppenhof@tue.nl
# @version: 0.0.3
# @date: 2015/10/20


from __future__ import division, print_function
from collections import OrderedDict


def logfile(path):
    # path should be a string containing a path to the IterationInfo.*.txt file
    with open(path) as f:
        lines = f.readlines()

    head = lines[0].split()

    d = OrderedDict()

    for cap in head[:-1]:
        c = ''.join(cap.split(':')[1:])
        c = c.lower()
        d[c] = []
    d[head[-1].lower()] = []

    for line in lines[1:]:
        for k, v in zip(d.keys(), line.split()):
            try:
                a = int(v)
            except ValueError:
                a = float(v)
            d[k].append(a)

    return d
