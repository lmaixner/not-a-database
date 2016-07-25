from __future__ import print_function, division, absolute_import

import os
import shutil

import pytest
import numpy as np

from astropy.table import Table
from ..sort_photometry import f_group


def data_directory():
    current_file = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file)
    return(os.path.join(current_directory, 'data'))


def copy_data_to_temp(temp_path):
    source = data_directory()
    dest = os.path.join(temp_path, 'data')
    shutil.copytree(source, dest)
    return dest


def test_catalogue_with_self(tmpdir):
    """
    Two identical lists should produce a results in which the second
    matches the first exactly.
    """
    # Copy just one file to the temporary directory...
    original_data = data_directory()
    data = tmpdir.strpath
    shutil.copyfile(os.path.join(original_data, 'M71-001-trimmed-R.csv'),
                    os.path.join(data, 'M71-001-trimmed-R.csv'))

    # Make a copy of the data file...
    shutil.copyfile(os.path.join(data, 'M71-001-trimmed-R.csv'),
                    os.path.join(data, 'M71-002-trimmed-R.csv'))

    files_to_match = os.path.join(data, '*-trimmed-R.csv')

    print(files_to_match)
    source = Table.read(os.path.join(data, 'M71-001-trimmed-R.csv'))
    result = f_group(files_to_match)

    # Every source should appear exactly twice.
    assert len(result) == 2 * len(source)

    n_original = len(source)
    # The first n_original sources should have their own number as match.
    assert np.all(result['DataNum'][:n_original] ==
                  (np.arange(n_original) + 1))

    # The second batch of n_original sources should also have their own number
    # as match since they were identical to the first.
    print(result[n_original:])
    assert np.all(result['DataNum'][n_original:] ==
                  (np.arange(n_original) + 1))


@pytest.mark.parametrize("start_offset", [0, 5])
def test_catalog_with_self_offset(tmpdir, start_offset):
    # Copy just one file to the temporary directory...
    original_data = data_directory()
    data = tmpdir.strpath
    shutil.copyfile(os.path.join(original_data, 'M71-001-trimmed-R.csv'),
                    os.path.join(data, 'M71-001-trimmed-R.csv'))

    source = Table.read(os.path.join(data, 'M71-001-trimmed-R.csv'))

    # Shift some of the RAs by half a degree.
    source['RA'][start_offset:] += 0.5

    source.write(os.path.join(data, 'M71-002-trimmed-R.csv'))
    files_to_match = os.path.join(data, '*.csv')

    result = f_group(files_to_match)

    n_original = len(source)

    # The offset objects in the second group should not match. No match is
    # indicated by a DataNum of zero.
    assert np.all(result['DataNum'][len(source) + start_offset:] == 0)

    # Any objects not offset should match the original source.
    assert np.all(result['DataNum'][n_original:n_original + start_offset] ==
                  np.arange(start_offset) + 1)
