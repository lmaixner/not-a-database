from __future__ import division, print_function, absolute_import
import matplotlib.pyplot as plt
from astropy.table import Table, Column

import glob
from sort_photometry import assign_id
import numpy as np
import os


def __init__(self, tstuff):
    self.__stuff = tstuff


def make_CMD(extension, short_w, long_w, cluster_members=False, member_RA="RA",
    member_Dec="Dec", prob_col="prob_member", threshold=70,
    plt_nonmembers=False, plot_separate=True, object_name=False, legend_loc=4):
    """Links the two data sets it is given so the RA/Decs agree and plots a CMD.

    Compares second data set to first data set and assigns second data set the
    DataNum of first data set where the RA and Dec columns are within a
    reasonable range.  Uses function from another module to do so.  Removes the
    points not in both data sets so they can be ploted together and creates a
    CM Diagram of the data.

    Parameters
    ------
    extension: file extension
        folder location where the files can be found on disk
    short_w: string
        letter indicator for the shorter wavelength to be compared
    long_w: string
        letter indicator for the longer wavelength to be compared
    cluster_members: string, optional
        file extension for file containing cluster membership data
    member_RA: string, optional
        table key, name of column containing Right Ascension data in cluster
        membership data file
    member_Dec: string, optional
        table key, name of column containing Declination data in cluster
        membership data file
    prob_col: string, optional
        able key, name of column in the cluster membership list containing
        the probablility each source is a member of the given cluster
    threshold: int, optional
        required probability that a source is in the cluster, give value
        dependant on how they are entered in the table submitted to the
        function
    plt_nonmembers: bool, optional
        gives the option to plot the sources that are not part of the cluster
        membership list provided along with the members (plots in different
        color)
    plot_separate: bool, optional
        gives the option to plot the field stars on the same plot as the
        cluster stars or on a separate plot
    object_name: string, optional
        name of object being plotted
    legend_loc: int, optional
        indicates corner of plot the legent will appear if there is more than
        one data source, numbers correspond to standard cartesian quadrant
        system
    """
    # create glob masks
    short_mask = os.path.join(extension, '*' + short_w + '.csv')
    long_mask = os.path.join(extension, '*' + long_w + '.csv')

    # retrieve the table data from the given locations
    short_w_file = glob.glob(short_mask)
    short_w_table = Table.read(short_w_file[0])
    long_w_file = glob.glob(long_mask)
    long_w_table = Table.read(long_w_file[0])

    # change ID in one of the lists so they are the same for given RA/Dec
    print('assigning ids to long based on short')
    long_w_table = assign_id(short_w_table, long_w_table, 'AvgRA', 'AvgDec', 'AvgRA', 'AvgDec')

    # send through matching function in Sort module to make the DataNum's match
    #long_w_table.pprint(max_lines=10)
    #short_w_table.pprint(max_lines=-1)
    print('matching short to long\n')
    short_w_table = match(short_w_table, long_w_table)
    print('matching long to short\n')
    long_w_table = match(long_w_table, short_w_table)
    print("short", len(short_w_table))
    print("long", len(long_w_table))
    # use cluster membership list to exclude sources not part of the target
    extra_long = 0
    extra_short = 0
    if cluster_members is not False:
        # if not given a membership list skips matching
        short_w_table, extra_short = sort_cluster(short_w_table, member_RA, member_Dec, prob_col, cluster_members, threshold)
        long_w_table, extra_long = sort_cluster(long_w_table, member_RA, member_Dec, prob_col, cluster_members, threshold)

        # send through matching again to ensure tables are same length
        print("matching short_w_table and long_w_table")
        short_w_table = match(short_w_table, long_w_table)
        long_w_table = match(long_w_table, short_w_table)

        # matches field stars to ensure tables are the same length
        print("matching extra_short and extra_long")
        extra_short = match(extra_short, extra_long)
        extra_long = match(extra_long, extra_short)

    # initiate values for plot
    fig = plt.figure()
    if object_name is False:
        plot_name = 'Color-Magnitude Diagram'
    else:
        plot_name = 'Color-Magnitude Diagram for ' + object_name
    fig.suptitle(plot_name, fontsize=14, fontweight='bold')
    CMD = fig.add_subplot(111, axisbg='k')
    CMD.set_xlabel(short_w + ' - ' + long_w + ' Magnitude')
    CMD.set_ylabel(long_w + ' Magnitude')
    CMD.set_title(str(len(short_w_table)) + ' members found')

    # plot short - long vs instrumental mag
    cluster_stars = CMD.scatter(short_w_table["InstruMag"] - long_w_table["InstruMag"], long_w_table["InstruMag"],
        marker='o', facecolor='blue', edgecolor='magenta', lw=1, label='Cluster Stars')

    if plt_nonmembers is True:
        if plot_separate is True:
            fig2 = plt.figure()
            plot2_name = plot_name + ' Field'
            fig2.suptitle(plot2_name, fontsize=14, fontweight='bold')
            field_CMD = fig2.add_subplot(111, axisbg='k')
            field_CMD.set_xlabel(short_w + ' - ' + long_w + ' Magnitude')
            field_CMD.set_ylabel(long_w + ' Magnitude')
            field_CMD.set_title(str(len(extra_short)) + ' non-members found')
            field_stars = field_CMD.scatter(extra_short["InstruMag"] - extra_long["InstruMag"],
                extra_long["InstruMag"], marker='D', facecolor='green', edgecolor='cyan', lw=1,
                label='Field Stars')
        else:
            field_stars = CMD.scatter(extra_short["InstruMag"] - extra_long["InstruMag"],
                extra_long["InstruMag"], marker='D', facecolor='green', edgecolor='cyan', lw=1,
                label='Field Stars')
            # create legend for plot
            plt.legend(handles=[cluster_stars, field_stars], loc=legend_loc)

    plt.show()


def match(first, second):
    """Finds which items are in both data sets.

    Matches 'first' to 'second'. Creates a list of True/False for whether the
    items of the first data set are in the second data set. Returns only the
    items of the first data set that are in the second data set.

    Parameters
    ------
    first: astropy table
        filter color data to be altered, read as a table
    second: astropy table
        filter color data to compared first to, read as a table

    Returns
    ------
    first: astropy table
        contains only values from first that are also in second
    """
    # creates a set of the DataNum's that are in both groups
    newset = set(first["DataNum"]) & set(second["DataNum"])
    print('newset', len(newset))
    print('first', len(first))
    print('second', len(second))

    newset = np.array(sorted(list(newset)))
    newset.astype(int)

    first.sort("DataNum")
    first['DataNum', 'AvgRA', 'AvgDec'].pprint(max_lines=-1)
    #print(first["DataNum"])
    print(newset)

    matches = []
    for i in first["DataNum"]:
        # makes a true false array to map to the first data set
        if i in newset:
            matches.append(True)
        else:
            matches.append(False)

    # converts matches to an array and limits 'first' to the locations where
    # 'matches' is True
    matches = np.array(matches)
    #print("T/F matches array \n", matches)
    first = first[matches]
    print('match is returning first with a size of: ', len(first), '\n')
    return first


def sort_cluster(source_list, member_RA_col, member_Dec_col, member_prob_col, members, match_threshold=70):
    """Removes stars from the images that are not part of the cluster.

    Uses a cluster membership list given by the user to remove stars that were
    in the frame from the list before they are plotted.

    Parameters
    ------
    source_list: astropy table
        data for stars in the field, read as table
    member_RA_col: string
        table key, name of column containing Right Ascension data in cluster
        membership data file
    member_Dec_col: string
        table key, name of column containing Declination data in cluster
        membership data file
    members: string
        fiilename location of the cluster membership list in .csv format for
        the object to be plotted
    member_prob_col: string
        table key, name of column in the cluster membership list containing
        the probablility each source is a member of the given cluster
    match_threshold: int, optional
        required probability that a source is in the cluster, give value
        dependant on how they are entered in the table submitted to the
        function

    Returns
    ------
    member_sources: astropy table
        data for stars in the field that where the locations match the cluster
        membership list, read as table
    """
    # load the cluster membership list as a table
    member_list = Table.read(members)

    # limit the list to only the members with a probability that meets the
    # set threshold
    #threshold_met = member_list[member_prob_col] > match_threshold
    threshold_met = []
    for i in member_list[member_prob_col]:
        if i.isdigit():
            i = int(i)
            # makes a true false array to map to the source_list data set
            if i > match_threshold:
                threshold_met.append(True)
            else:
                threshold_met.append(False)
        else:
            threshold_met.append(False)
    #print('threshold_met length = ', len(threshold_met))
    threshold_met = np.array(threshold_met)

    member_list = member_list[threshold_met]

    # add DataNum column to cluster Membership list so that it can filled when
    # matched with assign_id
    x_objects = len(member_list)
    dataNum_col = Column(data=[0] * x_objects, name="DataNum")
    member_list.add_column(dataNum_col)

    # fill DataNum column by matching cluster membership list to source list
    print('assigning ids to member_list\n')
    member_list = assign_id(source_list, member_list, RA1='AvgRA', Dec1='AvgDec', RA2=member_RA_col, Dec2=member_Dec_col)

    # create list of sources that are not members of the cluster
    #   hah! do this before restricting source_list to those in member_list
    #print('member_list = ', len(member_list))
    non_member_set = set(source_list["DataNum"]) - set(member_list["DataNum"])
    non_member_set = np.array(sorted(list(non_member_set))).astype(int)
    non_member_matches = []
    for i in source_list["DataNum"]:
        # makes a true false array to map to the source_list data set
        if i in non_member_set:
            non_member_matches.append(True)
        else:
            non_member_matches.append(False)
    #print('non_member_matches = ', len(non_member_matches))
    non_member_matches = np.array(non_member_matches)
    non_member_sources = source_list[non_member_matches]

    # restrict source_list to those values that are also in member_list
    print('matching source_list to member_list\n')
    member_sources = match(source_list, member_list)

    #print('non_member_sources = ', len(non_member_sources))
    print('member_sources: length ', len(member_sources), '\n', member_sources)

    return member_sources, non_member_sources
