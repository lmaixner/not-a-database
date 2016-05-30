from __future__ import division, print_function, absolute_import

import os
import glob

from astropy.table import Table, Column, vstack
from astropy.coordinates import SkyCoord
from astropy import units as u
from GetGiantPileofSpreadsheets import make_folder


def __init__(self, tstuff):
    self.__stuff = tstuff


def assign_id(file1, file2, RA='RA', Dec='Dec', search_range=.5):
    """Compares two files and fills the DataNum column of the smaller file.

    Fills the DataNum column in the second file with the DataNum of the closest
    RA/Dec match within the given arcsecond range in the first file.

    Parameters
    ------
    file1: astropy table
        file containing more data sources and DataNum column filled
    file2: astropy table
        file to have DataNum column matched to file1
    RA: string, optional
        table key, name of column holding Right Ascension data
    Dec: string, optional
        table key, name of column holding Declination data

    Returns
    ------
    file2: astropy table
        the DataNum column will be filled with the DataNum of the closest
        source from the other table
    """
    ra1 = file1[RA]
    dec1 = file1[Dec]

    ra2 = file2[RA]
    dec2 = file2[Dec]

    # returns two catalogs comparing file2 to file 1
    catalog = SkyCoord(ra=ra1 * u.degree, dec=dec1 * u.degree)
    c = SkyCoord(ra=ra2 * u.degree, dec=dec2 * u.degree)
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
    file2['DataNum'][good_matches] = file1['DataNum'][idx2]
    # now have 2 files with the DataName column matching for stars with RA/Dec
    # close enough

    return file2


def sort_files(files):
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
    new_files2 = list(new_files)  # duplicate list

    fileNames = []
    for file in new_files:
        base_name = os.path.basename(file)
        fileNames.append(base_name)

    ct = 0
    ind = ct
    file1 = Table.read(new_files[ct])
    # find the longest red file to use for assigning indexes
    for file in new_files:
        file2 = Table.read(file)
        if len(file2) > len(file1):
            file1 = file2
            ind = ct
        ct += 1

    # removes file1 from new_files
    new_files.pop(ind)
    new_files2.pop(ind)

    # imports file as numpy Table
    n_objects1 = len(file1)
    # adds a DataNum Column to the table with sequential values to be match to
    # the rest of the files
    dataNum1_col = Column(data=range(1, n_objects1 + 1), name='DataNum')
    file1.add_column(dataNum1_col)
    # adds a SourceFile Column to the table
    fileName_col = Column(data=[fileNames[ind]] * n_objects1, name='SourceFile')
    file1.add_column(fileName_col)
    # removes file1 name from it's position in fileNames list
    del fileNames[ind]

    # run through the rest of the files, adds Filename and DataNum column and
    # assigns them DataNums concurrent with file1's
    ct = 0
    for file in new_files:
        cur_file = Table.read(file)
        # imports file as numpy Table
        file2 = Table.read(new_files2[ct])
        n_objects2 = len(file2)
        # adds a DataNum Column to the table with 0000 values to be matched to
        # file1 values
        dataNum2_col = Column(data=[0000] * n_objects2, name='DataNum')
        cur_file.add_column(dataNum2_col)
        fileName_col = Column(data=[fileNames[ct]] * n_objects2, name='SourceFile')
        cur_file.add_column(fileName_col)

        new_files[ct] = assign_id(file1, cur_file)
        ct += 1

    return file1, new_files


def f_group(filename):
    """
    For the function to run the files must have the filter type letter as the
    last letter of the filename. Glob something... confused. Hmm. Assigns the
    DataNums of file1 to the sources at the same locations in the rest of the
    files. Stacks all the files for one filter together into one larger file
    using file1 as a base.

    Parameters
    ------
    filename: file extension... glob mask?
        location of the files to be used?

    Returns
    ------
    big_file: astropy table
        all files of that filter stacked together into one large table
    """

    files = glob.glob(filename)

    file1, files2 = sort_files(files)

    # creates new csv file to pile all the new files onto
    big_file = file1
    # and add all files to big_file
    for file in files2:
        big_file = vstack([big_file, file], join_type='exact')

    return big_file


def sort_photometry(f_ext, object, filters=None, target_dir='Sorted', parent_dir=''):
    """
    For the function to run the files must have the filter type letter as the
    last letter of the filename. Creates a directory in the location specified
    by parent_dir/target_dir to put the files it creates. The files in the
    source location are comined into one large file per filter color and saved
    in .csv format named for the observed object and filter color for each
    filter type available. The csv files for each image have DataNum (matched
    by RA/Dec) and SourceFile columns added.

    Parameters
    ------
    f_ext: file extension
        location of the files to use
    object: string
        name of the object the images are of for naming the output files
    filters: list of strings, optional
        filter colors grouping will be done for, default value is ['I', 'R', 'V', 'B']
    target_dir: string, optional
        name of the directory that it will place created files
    parent_dir: string, optional
        name of parent directory of where it will place files

    Returns
    ------
    write_location: file extension
        location the created files were saved
    """

    if filters is None:
        filters = ['I', 'R', 'V', 'B']

    make_folder(target_dir, parent_dir)
    write_location = os.path.join(parent_dir, target_dir)

    # f_ext is where I'm trying to grab the files from
    pattern = f_ext + '\*{}.csv'

    # send all the files to f_group for each filter
    for filter in filters:
        big_file = f_group(pattern.format(filter))

        # outputs table of located object's info in .csv format
        big_file.write(os.path.join(write_location, object + filter + 'Filt.csv'))

    return write_location
