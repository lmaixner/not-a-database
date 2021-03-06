"""
-Would like to seperate the glob mask from the source directory but
it's not behaving as I expected it to
-Maybe track somewhere which files the source files were averaged from
"""
import glob
import os
from math import sqrt, log10
from astropy.table import Table
from GetGiantPileofSpreadsheets import mk_fldr


def __init__(self, tstuff):
    self.__stuff = tstuff


def avg_flux(location, target_dir='Averaged', parent_dir='', identColumn='DataNum', flux_name='flux', srcs=0):
    mk_fldr(target_dir, parent_dir)

    files = glob.glob(location)
    # print (files)
    # what will be the names of the columns in the table created when
    column_names = [identColumn, 'NumSources', 'AvgRA', 'AvgDec', 'AvgFlux', 'FluxErr', 'InstruMag', 'MaxPeak', 'a_Avg', 'b_Avg', 'thetaAvg']
    write_location = os.path.join(parent_dir, target_dir)
    print (files)
    for file in files:
        print (file)
        # creates a new empty table to put the averaged data in
        new_table = Table(names=column_names)
        # print (file)

        # retrieve file name minus extension and location for later use
        base_name = os.path.basename(file)
        first_part, _ = os.path.splitext(base_name)
        # print (first_part)

        # read file as table
        file = Table.read(file)

        num = 1
        while num in file[identColumn]:
            # finds the rows in the file that match the current DataNum
            matches = (file[identColumn] == num)
            # print (matches)

            # makes a copy of the file that only contains the rows that match
            # the desired DataNum
            file2 = file[matches]
            num_in_avg = len(file2)
            # print(num_in_avg)

            # makes sure there are enough points to matter
            if num_in_avg > srcs:
                # averages the data for the current DataNum
                flux_avg = sum(file2[flux_name])/num_in_avg
                max_peak = max(file2['peak'])
                ra_avg = sum(file2['RA'])/num_in_avg
                dec_avg = sum(file2['Dec'])/num_in_avg
                # make fractional square add root divide de-fractionalize
                frac_errs = sum((file2['FluxErr']/file2['flux'])**2)
                flux_err = ((sqrt(frac_errs))/num_in_avg)*flux_avg
                inst_mag = -2.5*log10(flux_avg)

                a_avg = sum(file2['a'])/num_in_avg
                b_avg = sum(file2['b'])/num_in_avg
                theta_avg = sum(file2['theta'])/num_in_avg

                # adds the new row to the table
                # print (num, ra_avg, dec_avg, flux_avg, flux_err, num_in_avg)
                row = [num, num_in_avg, ra_avg, dec_avg, flux_avg, flux_err, inst_mag, max_peak, a_avg, b_avg, theta_avg]
                new_table.add_row(row)
            num += 1  # increment counter

        # write averaged table out to disk
        # print (new_table)
        new_table.write(os.path.join(write_location, first_part+'(Avg).csv'))

    return write_location
