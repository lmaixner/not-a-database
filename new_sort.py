from astropy.table import Table, Column
from astropy.coordinates import SkyCoord
from astropy import units as u
import os
import numpy as np

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

    # run through the rest of the files, adds Filename and DataNum column and
    # assigns them DataNums concurrent with file1's
    ct = 0
    DataStart = 1000000
    new_files2 = []
    for file in new_files:
        base_name = os.path.basename(file)
        file = Table.read(file)
        # imports file as numpy Table
        n_objects = len(file)

        # adds a DataNum Column to the table with sequential values
        n_objects = len(file)
        dataNum2_col = Column(data=range(DataStart, n_objects + DataStart), name='DataNum', dtype=np.int64)  ###
        file.add_column(dataNum2_col)
        fileName_col = Column(data=[base_name] * n_objects, name='SourceFile')
        file.add_column(fileName_col)

        #new_files[ct] = assign_id(file1, cur_file)
        ct += 1
        DataStart += n_objects
        #print(file)
        new_files2.append(file)
    # print(Table.read(new_files[0]))#['DataNum']))
    return new_files2


def assign_id2(file1, RA1='RA', Dec1='Dec', search_range=.5):
    """Compares RA/Decs within a file and fills the DataNum column of the smaller file.

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
    #import pdb; pdb.set_trace() #debuger

    ra1 = file1[RA1]
    dec1 = file1[Dec1]

    file2 = file1['DataNum', RA1, Dec1]

    #print('file1 before \n', file1['DataNum', RA1, Dec1])
    # returns two catalogs comparing file2 to file 1
    catalog = SkyCoord(ra=ra1 * u.degree, dec=dec1 * u.degree)
    c = SkyCoord(ra=ra1 * u.degree, dec=dec1 * u.degree)
    #fake_c = c[:10]
    #idxcatalog, idxc, d2d, d3d = fake_c.search_around_sky(catalog, 10*u.arcsec)
    #idx, d2d, d3d = c.match_to_catalog_sky(catalog) 
    # some of the matches are likely to be duplicates and not within a
    # reasonable distance to be the same star

    # array of objects that are within search_range of c[i]
    idxc, idxcatalog, d2d, d3d = catalog.search_around_sky(c, search_range * u.arcsec)
    #print(d2d)
    
    matched_rows = []
    for n in set(idxc):
        if n not in matched_rows:
            good_matches = np.array(idxc == n)
            #np.set_printoptions(threshold=np.nan)
            #print(good_matches)
            if good_matches.sum() > 1: #when I remove this if statement (or change the 1 to 0) all the dataNums are altered but there's a weird error, must check smaller data set
                #print('file1 DataNum before', file1['DataNum'][idxcatalog][good_matches])
                file1['DataNum'][idxcatalog[good_matches]] = str(n + 100000)
                #print('file1 DataNum after', file1['DataNum'][idxcatalog][good_matches])
                for i in idxcatalog[good_matches]:
                    matched_rows.append(i)
                #print("matched rows", matched_rows)
    # return an array of true's and false's where match is within specified
    # range (.5 arcsec is best)
    #good_matches = d2d < search_range * u.arcsec
    #good_matches = file2 == d2d

    # get all matches that are within 'search_range' of the target
    #idx2 = idx[good_matches]

    # apply file1's dataname to file2's dataname at the indexes specified by
    # idx2
    # new_rows = file1['DataNum'][good_matches]
    #file1['DataNum'][~good_matches] = 00000000000
    # now have 2 files with the DataName column matching for stars with RA/Dec
    # radius

    # if idxc = 0 then I want the row at the index coresponding to it in idxcatalog to change to the new data num
    # keep a list of the indecies that have been matched instead of removing them from the table
    # add table lines

    #print('file1 after \n', file1['DataNum', RA1, Dec1])
    return file1
