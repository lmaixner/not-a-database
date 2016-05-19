from __future__ import division, print_function, absolute_import

# import os

import glob
from SortGiantPileofSpreadsheets import assign_id

from astropy.table import Table, Column
from matplotlib.pyplot import plot


def __init__(self, tstuff):
    self.__stuff = tstuff


def make_CMD(short_w_file, long_w_file):
    short_w = glob.glob(short_w_file)
    short_w = Table.read(short_w[0])
    long_w = glob.glob(long_w_file)
    long_w = Table.read(long_w[0])

    # send through matching function in Sort module to make the DataNum's match
    long_w = assign_id(short_w, long_w, 'AvgRA', 'AvgDec')

    #print(long_w["DataNum", "AvgRA"], short_w["DataNum", "AvgRA"])
    short_w = match(short_w, long_w)
    #long_w = match(long_w, short_w)
    #print(long_w["DataNum", "AvgRA"], short_w["DataNum", "AvgRA"])

    # plot short - long vs instrumental mag
    plot(short_w["AvgFlux"]-long_w["AvgFlux"], short_w["InstruMag"])


def match(first, second):
    matches = []
    first_list = list(first["DataNum"])
    second_list = list(second["DataNum"])
    for i in first_list:
        if i in second_list:
            matches.append(True)
        else:
            matches.append(False)
    #print(len(matches))
    print(first["DataNum", "AvgRA"])
    first = first[matches]
    print(first["DataNum", "AvgRA"])
    #print(len(matches))
    return first
