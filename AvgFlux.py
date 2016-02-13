"""
-Still need to add the FluxErr because right now it's just set to always
be 0 which would rock but is not true
-Maybe track somewhere which files the sources were averaged from
-Need to see if there are more columns that should be preserved from
the old sheets
-Possibly combine filter colors into one sheet
"""
import glob
import os

from astropy.table import Table

# what will be the names of the columns in the table created when
# fluxes are averaged
column_names = ['DataNum', 'AvgRA', 'AvgDec', 'AvgFlux', 'FluxErr', 'NumSources']


def avg_flux(location,target_dir):
    files = glob.glob(location)
    # print (files)

    for file in files:
        # creates a new empty table to put the averaged data in
        new_table = Table(names=column_names)
        print (file)

        # retrieve file name minus extension and location for later use
        base_name = os.path.basename(file)
        first_part, _ = os.path.splitext(base_name)
        # print (first_part)

        # read file as table
        file = Table.read(file)

        num = 1
        while num in file['DataNum']:
            # finds the rows in the file that match the current DataNum
            matches = (file['DataNum'] == num)
            # print (matches)

            # makes a copy of the file that only contains the rows that match
            # the desired DataNum
            file2 = file[matches]
            num_in_avg = len(file2)
            # print(num_in_avg)

            # makes sure there are enough points to matter
            if num_in_avg > 1:
                # averages the data for the current DataNum
                flux_avg = sum(file2['flux'])/num_in_avg
                ra_avg = sum(file2['RA'])/num_in_avg
                dec_avg = sum(file2['Dec'])/num_in_avg
                flux_err = 0

                # adds the new row to the table
                # print (num, ra_avg, dec_avg, flux_avg, flux_err, num_in_avg)
                row = [num, ra_avg, dec_avg, flux_avg, flux_err, num_in_avg]
                new_table.add_row(row)
            num += 1  # increment counter

        # write averaged table out to disk
        print (new_table)
        new_table.write(os.path.join(target_dir, first_part+'(Averaged).csv'))


avg_flux(r'C:\Users\ShakAttack\Desktop\Everything\Class\Git\TestFilesv7\*Filt*.csv','garbage')