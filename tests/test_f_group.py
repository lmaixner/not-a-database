import glob
import os
from os import path

from astropy.table import Table

from .get_test_data import get_test_data
from ..sort_photometry import f_group


def test_f_group():
    """ testing that the final input file is the length of the combined input
    files, input files must not have DataNum and SourceFile columns
    """

    # separately retrieve files that f_group should have for comparison
    base_directory = get_test_data()
    test_file_dir = path.join(base_directory, 'f_group_testdata')
    R_filelist = glob.glob('{}/*R.csv'.format(test_file_dir))
    I_filelist = glob.glob('{}/*I.csv'.format(test_file_dir))
    V_filelist = glob.glob('{}/*V.csv'.format(test_file_dir))
    B_filelist = glob.glob('{}/*B.csv'.format(test_file_dir))

    len_R = 0
    len_I = 0
    len_V = 0
    len_B = 0

    # retrieve combined lengths of each filter color files
    for file in R_filelist:
        len_R += len(Table.read(file))
    for file in I_filelist:
        len_I += len(Table.read(file))
    for file in V_filelist:
        len_V += len(Table.read(file))
    for file in B_filelist:
        len_B += len(Table.read(file))

    # creating filename pattern that is sent to f_group that it uses for file
    # retrieval
    f_ext = test_file_dir
    pattern = os.path.join(f_ext, '*{}.csv')

    # send f_group: f_ext + '\*I.csv' for each filter in the list
    bigR_file = f_group(pattern.format('R'))
    bigI_file = f_group(pattern.format('I'))
    bigB_file = f_group(pattern.format('B'))
    bigV_file = f_group(pattern.format('V'))

    assert len(bigR_file) == len_R
    assert len(bigI_file) == len_I
    assert len(bigB_file) == len_B
    assert len(bigV_file) == len_V
