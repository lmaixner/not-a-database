from ..new_sort import assign_id2
import glob
from astropy.table import Table


def test_assign_id2():
    """ I will have all the points in the file1 be the same so all the assigned
    IDs should pop up the same and file2 they will all be different so none
    should pop the same.
    """

    # retrieve files from test folder
    # must glob separately in order to ensure each file gets assigned to the
    # correct position
    file1list = glob.glob('assign_id2_testdata/1*.csv')
    file2list = glob.glob('assign_id2_testdata/2*.csv')
    file1 = file1list[0]
    file2 = file2list[0]

    # Method requireds read astropy tables
    file1 = Table.read(file1)
    file2 = Table.read(file2)

    # run through function
    new_file1 = assign_id2(file1)
    new_file2 = assign_id2(file2)

    # check results
    # output files are the same length
    assert len(file1) == len(new_file1)
    assert len(file2) == len(new_file2)

    # check DataNums are as expected
    for row in file1['DataNum']:
        assert row == file1['DataNum'][0]

    for row in file2['DataNum']:
        for num in range(row + 1, len(file2['DataNum']) - 1):
            assert row != file2['DataNum'][num]
