from ..new_sort import assign_dataNum
import glob
from astropy.table import Table
DataStart = 1000000


def test_assign_dataNum():
    filelist = glob.glob('assign_dataNum_testdata/*.csv')
    newfilelist = assign_dataNum(filelist)

    # length of the lists sent should be the same as the lists returned
    assert len(filelist) == len(newfilelist)

    other_data = 0  # variable to track total number of data points
    # for each file in the list of files it compares the new file to the old
    for infile, outfile in zip(filelist, newfilelist):
        # makes sure they are the same length
        assert len(Table.read(infile)) == len(outfile)

        # makes sure the new file has the new columns added
        assert 'SourceFile' in outfile.colnames
        assert 'DataNum' in outfile.colnames

        # checkes that the DataNum's in all the files are sequential
        print(infile)  # prints input filename if there is an error in the code
        assert all(list(range(DataStart + other_data, DataStart + len(outfile) + other_data)) == outfile['DataNum'])
        other_data += len(outfile)
