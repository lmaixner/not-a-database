"""
-Would like to seperate the glob mask from the source directory but
it's not behaving as I expected it to
-Maybe track somewhere which files the source files were averaged from
"""
import glob
import os
from math import sqrt, log10
from astropy.table import Table
from load_photometry import make_folder


def __init__(self, tstuff):
    self.__stuff = tstuff


def avg_photometry(location, target_dir='Averaged', parent_dir='', ident_column='DataNum', flux_name='flux', srcs=1):
    """Averages the flux by source for each filter.

    Creates a directory in the location specified by parent_dir/target_dir.
    Averages the sources for each filter using the ident_column as a reference
    and saves the new file with a reduced number of columns in the created
    folder.

    Parameters
    ------
    location: file extension
        where to retrieve data from for processing
    target_dir: string, optional
        name of the directory that it will place created files
    parent_dir: string, optional
        name of parent directory of where it will place files
    ident_column: string, optional
        table key, used as the identifier when averaging sources
    flux_name: string, optional
        table key, name of flux comun in data table if different
    srcs: int, optional
        source must appear at least this many times before it will be added to
        the averaged table

    Returns
    ------
    write_location: file extension
        location the created files were saved
    """

    make_folder(target_dir, parent_dir)

    files = glob.glob(location)
    # what will be the names of the columns in the table created when
    column_names = [ident_column, 'NumSources', 'AvgRA', 'AvgDec', 'AvgFlux', 'FluxErr', 'InstruMag', 'MaxPeak', 'a_Avg', 'b_Avg', 'thetaAvg']

    write_location = os.path.join(os.getcwd(), os.path.join(parent_dir, target_dir))

    for file in files:
        # creates a new empty table to put the averaged data in
        new_table = Table(names=column_names)

        # retrieve file name minus extension and location for later use
        base_name = os.path.basename(file)
        first_part, _ = os.path.splitext(base_name)

        # read file as table
        file = Table.read(file)

        dataNum_list = []
        for row in file:
            if row[ident_column] not in dataNum_list:
                dataNum_list.append(row[ident_column])

        for num in dataNum_list:
            # finds the rows in the file that match the current DataNum
            matches = (file[ident_column] == num)

            # makes a copy of the file that only contains the rows that match
            # the desired DataNum
            file2 = file[matches]
            num_in_avg = len(file2)

            # makes sure there are enough points to matter
            if num_in_avg >= srcs:
                # averages the data for the current DataNum
                flux_avg = sum(file2[flux_name]) / num_in_avg
                max_peak = max(file2['peak'])
                ra_avg = sum(file2['RA']) / num_in_avg
                dec_avg = sum(file2['Dec']) / num_in_avg
                # make fractional square add root divide de-fractionalize
                frac_errs = sum((file2['FluxErr'] / file2['flux'])**2)
                flux_err = ((sqrt(frac_errs)) / num_in_avg) * flux_avg
                inst_mag = -2.5 * log10(flux_avg)

                a_avg = sum(file2['a']) / num_in_avg
                b_avg = sum(file2['b']) / num_in_avg
                theta_avg = sum(file2['theta']) / num_in_avg

                # adds the new row to the table
                # print (num, ra_avg, dec_avg, flux_avg, flux_err, num_in_avg)
                row = [num, num_in_avg, ra_avg, dec_avg, flux_avg, flux_err, inst_mag, max_peak, a_avg, b_avg, theta_avg]
                new_table.add_row(row)
                #num += 1  # increment counter

        #print(new_table[ident_column, 'NumSources'])
        #print(max(new_table['NumSources']))

        # write averaged table out to disk
        new_table.write(os.path.join(write_location, 'Avg' + first_part + '.csv'))

    return write_location
