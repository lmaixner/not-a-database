import glob
from os import path

from astropy.table import Table

from .get_test_data import get_test_data
from ..avg_photometry import *


def test_avg_photometry():
    """
    Initial file1 will have points with matching RA/Dec and the final file
    should have one point with the values of the AvgDec, AvgRA, AvgFlux, a_Avg,
    b_Avg, and thetaAvg columns being the averages of those in the initial.

    Initial file2 will have points with non-matching RA/Dec and the final file
    should have the same number of points with the values being the same as
    those in the initial.

    Initial file3 will have 1 line.  The values in the final Avg" " columns
    should match those in their initial columns.

    Initial file must have at least one more than the columns :NumSources,
    AvgRA, AvgDec, AvgFlux, FluxErr, InstruMag, MaxPeak, a_Avg, b_Avg, and
    thetaAvg. Final file must have only those columns.
    """

    final_column_names = ['DataNum', 'NumSources', 'AvgRA', 'AvgDec',
    'AvgFlux', 'FluxErr', 'InstruMag', 'MaxPeak', 'a_Avg', 'b_Avg', 'thetaAvg']


    # Locations of test files
    base_directory = get_test_data()
    test_file_dir = path.join(base_directory, 'avg_photometry_testdata')
    file1loc = path.join(test_file_dir, '1', '*')
    file2loc = path.join(test_file_dir, '2', '*')
    file3loc = path.join(test_file_dir, '3', '*')

    # run through function
    avgd_file1loc = avg_photometry(file1loc)
    avgd_file2loc = avg_photometry(file2loc)
    avgd_file3loc = avg_photometry(file3loc)

    # retrieve original files from test folder for comparison
    # must glob separately in order to ensure each file
    # gets assigned to the correct position
    file1list = glob.glob(file1loc)
    file2list = glob.glob(file2loc)
    file3list = glob.glob(file3loc)
    file1 = file1list[0]
    file2 = file2list[0]
    file3 = file3list[0]

    # Method requires read astropy tables
    file1 = Table.read(file1)
    file2 = Table.read(file2)
    file3 = Table.read(file3)

    # retrieve final files from test folder for comparison
    avgd_file1list = glob.glob(os.path.join(avgd_file1loc, '*'))
    avgd_file2list = glob.glob(os.path.join(avgd_file2loc, '*'))
    avgd_file3list = glob.glob(os.path.join(avgd_file3loc, '*'))
    avgd_file1 = avgd_file1list[0]
    avgd_file2 = avgd_file2list[0]
    avgd_file3 = avgd_file3list[0]

    # Method requires read astropy tables
    avgd_file1 = Table.read(avgd_file1)
    avgd_file2 = Table.read(avgd_file2)
    avgd_file3 = Table.read(avgd_file3)

    # Now compare the files and their avgd versions with expectations

    # File1
    # final file should have 1 line
    assert len(avgd_file1) == 1

    # final files should have certain columns
    for i in avgd_file1.colnames:
        assert i in final_column_names

    # final column values should the the average or other expected value
    # respecive to the initial file
    n = len(file1)
    AvgFlux = avgd_file1['AvgFlux'][0]
    assert file1['DataNum'][0] == avgd_file1['DataNum'][0]
    assert avgd_file1['NumSources'][0] == n
    assert sum(file1['RA']) / n == avgd_file1['AvgRA'][0]
    assert sum(file1['Dec']) / n == avgd_file1['AvgDec'][0]
    assert sum(file1['flux']) / n == avgd_file1['AvgFlux'][0]
    f_er = sum((file1['FluxErr'] / file1['flux'])**2)
    assert ((sqrt(f_er) / n) * AvgFlux) == avgd_file1['FluxErr'][0]
    assert -2.5 * log10(AvgFlux) == avgd_file1['InstruMag'][0]
    assert max(file1['peak']) == avgd_file1['MaxPeak'][0]
    assert sum(file1['a']) / n == avgd_file1['a_Avg'][0]
    assert sum(file1['b']) / n == avgd_file1['b_Avg'][0]
    assert sum(file1['theta']) / n == avgd_file1['thetaAvg'][0]

    # File2
    # final and initial file should be the same length
    assert len(avgd_file2) == len(file2)

    # final files should have certain columns
    for i in avgd_file2.colnames:
        assert i in final_column_names

    # File3
    # final file should have 1 line
    assert len(avgd_file3) == 1

    # final file's columns should have the same values as their respective
    # initial column's values
    n3 = len(file3)
    AvgFlux3 = avgd_file3['AvgFlux'][0]
    assert file3['DataNum'][0] == avgd_file3['DataNum'][0]
    assert avgd_file3['NumSources'][0] == n3
    assert file3['RA'][0] == avgd_file3['AvgRA'][0]
    assert file3['Dec'][0] == avgd_file3['AvgDec'][0]
    assert file3['flux'][0] == AvgFlux3
    fr_er = sum((file3['FluxErr'] / file3['flux'])**2)
    assert (((sqrt(fr_er)) / n3) * AvgFlux3) == avgd_file3['FluxErr'][0]
    assert -2.5 * log10(AvgFlux3) == avgd_file3['InstruMag'][0]
    assert file3['peak'][0] == avgd_file3['MaxPeak'][0]
    assert file3['a'][0] == avgd_file3['a_Avg'][0]
    assert file3['b'][0] == avgd_file3['b_Avg'][0]
    assert file3['theta'][0] == avgd_file3['thetaAvg'][0]
