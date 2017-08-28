import os


def get_test_data():
    """
    Return the directory in which this file resides, which should also be
    the directory which contains the data.
    """

    this_file = __file__

    location = os.path.dirname(this_file)

    return location
