from ..sort_photometry import assign_id
import glob
from astropy.table import Table


def test_assign_id():
    """ Comparing two files that are not nessecarily the same length
    still makes sure that the altered file has the same number of rows ouput
    as input
    file1 is file matched to, contains only one point
    file2 has points that all match to file1 but different DataNums
    file3 has points that none match to file1 and same DataNums
    """

    # retrieve files from test folder
    # must glob separately in order to ensure each file gets assigned to the
    # correct position
    file1list = glob.glob('assign_id_testdata/1*.csv')
    file2list = glob.glob('assign_id_testdata/2*.csv')
    file3list = glob.glob('assign_id_testdata/3*.csv')
    file1 = file1list[0]
    file2 = file2list[0]
    file3 = file3list[0]

    # Method requires read astropy tables
    file1 = Table.read(file1)
    file2 = Table.read(file2)
    file3 = Table.read(file3)

    # run through function
    new_file2 = assign_id(file1, file2)
    new_file3 = assign_id(file1, file3)

    # check results
    # output files are the same length
    assert len(file3) == len(new_file3)
    assert len(file2) == len(new_file2)

    # check DataNums are as expected
    for row in new_file2['DataNum']:
        assert row == file1['DataNum'][0]
        # if true: matching points are being reassigned to a matching datanum

    for row in new_file3['DataNum']:
        assert row != file1['DataNum'][0]
        # if true: non-matching points are being reassigned to non-matching datanum
