from astropy.table import Table, Column
from astropy.coordinates import SkyCoord
from astropy import units as u
import os

def __init__(self, tstuff):
    self.__stuff = tstuff

def assign_dataNum(files):
    """Finds the longest file in the list and separates it, also adds two columns.

    Searches the list of files for the longest file, removes it to be the
    comparison file, and creates a shorter list with the longest file removed.
    It adds the SourceFile and DataNum columns to each file which combined
    identify the source and its image once the files are combined later.
    The Source file column is filed with the name of the file and the DataNum
    column is filled with zeros except for the longest file which is filled
    with sequential numbers.

    Parameters
    ------
    files: list of .csv files
        .csv files that have not yet been read as tables

    Returns
    ------
    file1: astropy table
        the longest file from the list of files it started with with the
        SourceFile and DataNum columns added
    new_files: list of astropy tables
        the list of files it started with with file1 removed and the remaining
        files read as astropy tables with the SourceFile and DataNum columns
        added to each table
    """
    new_files = list(files)
    #new_files2 = list(new_files)  # duplicate list

    # run through the rest of the files, adds Filename and DataNum column and
    # assigns them DataNums concurrent with file1's
    ct = 0
    new_files2 = []
    for file in new_files:
        base_name = os.path.basename(file)
        file = Table.read(file)
        # imports file as numpy Table
        n_objects = len(file)

        DataNums = []
        for row in file:
            new_iden = str(int(row['RA'] * 1000)) + str(int(row['Dec'] * 1000))
            #print(new_iden)
            DataNums.append(new_iden)

        # adds a DataNum Column to the table with 0000 values to be matched to
        # file1 values
        dataNum2_col = Column(data=DataNums, name='DataNum')
        file.add_column(dataNum2_col)
        #n_objects = len(DataNums)
        fileName_col = Column(data=[base_name] * n_objects, name='SourceFile')
        file.add_column(fileName_col)

        #new_files[ct] = assign_id(file1, cur_file)
        ct += 1
        #print(file)
        new_files2.append(file)
    # print(Table.read(new_files[0]))#['DataNum']))
    #print(new_files2)
    return new_files2


def assign_id2(file1, RA1='RA', Dec1='Dec', search_range=.5):
    """Compares two files and fills the DataNum column of the smaller file.

    Fills the DataNum column in the second file with the DataNum of the closest
    RA/Dec match within the given arcsecond range in the first file.

    Parameters
    ------
    file1: astropy table
        file containing more data sources and DataNum column filled
    RA1: string, optional
        table key, name of column holding Right Ascension data for file1
    Dec1: string, optional
        table key, name of column holding Declination data for file1
    RA2: string, optional
        table key, name of column holding Right Ascension data for file2
    Dec2: string, optional
        table key, name of column holding Declination data for file2

    Returns
    ------
    file2: astropy table
        the DataNum column will be filled with the DataNum of the closest
        source from the other table
    """
    ra1 = file1[RA1]
    dec1 = file1[Dec1]

    file2 = file1['DataNum', RA1, Dec1]

    #print('file1 before \n', file1['DataNum', RA1, Dec1])
    # returns two catalogs comparing file2 to file 1
    catalog = SkyCoord(ra=ra1 * u.degree, dec=dec1 * u.degree)
    c = SkyCoord(ra=ra1 * u.degree, dec=dec1 * u.degree)
    idx, d2d, d3d = c.match_to_catalog_sky(catalog)  # changed from .3d
    # some of the matches are likely to be duplicates and not within a
    # reasonable distance to be the same star

    # return an array of true's and false's where match is within specified
    # range (.5 arcsec is best)
    good_matches = d2d < search_range * u.arcsec

    # get all matches that are within 2 arcsec of the target
    idx2 = idx[good_matches]

    # apply file1's dataname to file2's dataname at the indexes specified by
    # idx2
    file1['DataNum'][good_matches] = file2['DataNum'][idx2]
    file1['DataNum'][~good_matches] = 00000000000
    # now have 2 files with the DataName column matching for stars with RA/Dec
    # radius
    #print('file1 after \n', file1['DataNum', RA1, Dec1])
    return file1
