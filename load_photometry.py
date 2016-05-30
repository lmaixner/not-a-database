"""
need to add targeting in make_folder for where the directory gets made then
make the object name the parent directory for all the ones created by the
program.
"""
from __future__ import division, print_function

import os
import numpy as np
import sep

from astropy.table import Table, Column
from astropy.wcs import WCS
from msumastro import ImageFileCollection

# to display image with sources circled
from ccdproc import CCDData
from astropy.visualization import scale_image
import matplotlib.pyplot as plt

__inner_rad__ = 20.
__outer_rad__ = 30.
__t_gain__ = 1.5
__read_noise__ = 30


def __init__(self, tstuff):
    self.__stuff = tstuff


def load_photometry(file_location):
    """Retrieves files from the given location that contain the correct keys.

    Retrieves files with correct keys from the given file_location and returns
    the files as an image ImageFileCollection.

    Parameters
    ------
    file_location: file extension
        location of the files to retrieve

    Returns
    ------
    files: list of strings
        list of filenames of files at the location that fit the conditions
    """
    keys = ['imagetyp', 'object', 'filter', 'exposure']
    files = ImageFileCollection(file_location, keywords=keys)
    return files


def get_fluxes(object1, data1, iR, oR, G, rN):
    """Estimates the flux and flux error of given positions.

    Uses a sep extracted array of objects and the image data that it's from to
    estimate the flux at the points given by the array it's error.

    Parameters
    ------
    object1: numpy array
        array containing sep extracted object data including coordinates
    data1: hdu data unit
        image file from an hdu that will be referenced by the object array
    iR: float
        inner radius of the averaging annulus
    oR: float
        outer radius of the averaging annulus
    G: float
        gain of the telescope
    rN: integer
        read noise of the telescope

    Returns
    ------
    flux: list of floats
        flux values at the locations minus the background flux
    fluxerr: lost of floats
        amount of error in the flux calculations
    """

    flux, fluxerr, flag = sep.sum_circle(data1, object1['x'], object1['y'], 16.0, bkgann=(iR, oR), gain=G, err=rN)

    return flux, np.sqrt(fluxerr)


def make_folder(target_dir, parent_dir=''):
    """Creates a folder with the name given.

    Creates a directory in the location specified by parent_dir/target_dir. If
    there is no parent_dir specified only a target_dir will be created. If the
    parent_dir does not exist yet it will apso be created.

    Parameters
    ------
    target_dir: string
        name of the folder to create
    parent_dir: string, optional
        name of parent folder if you want there to ge one
    """
    if parent_dir == '':
        try:
            os.mkdir(target_dir)
        except WindowsError as e:
            if 'Cannot create a file when that file already exists' in e.strerror:
                pass
            else:
                raise
    else:
        make_folder(parent_dir)
        try:
            os.mkdir(os.path.join(parent_dir, target_dir))
        except WindowsError as e:
            if 'Cannot create a file when that file already exists' in e.strerror:
                pass
            else:
                raise


def write_tables(ic1, target_dir='output', obj_name='M71', plot_graph=False, I=__inner_rad__, O=__outer_rad__, G=__t_gain__, N=__read_noise__):
    """

    Creates a directory in the location specified by obj_name/target_dir to
    save the files it creates. Finds sources that are significantly brighter
    than the background flux and uses their locations as the object list. Finds
    the flux minus background and flux error at these points and adds these as
    columns to the data table. Calculates the RA/Dec at these poisitions and
    adds these to the table along with InnerRad, OuterRad, Gain, ReadNoise, and
    Filter. Writes the tables with the added columns as .csv files under the
    same name as the image they same from in the location that was created for
    them.

    Parameters
    ------
    ic1: list of strings
        list of filenames containing data to be analyzed
    target_dir: string, optional
        name of the directory that it will place created files
    parent_dir: string, optional
        name of parent directory of where it will place files
    I: float
        inner radius of the averaging annulus
    O: float
        outer radius of the averaging annulus
    G: float
        gain of the telescope
    N: integer
        read noise of the telescope

    Returns
    ------
    write_location: file extension
        location the created files were saved
    """
    # creates a folder to put the created files
    make_folder(target_dir, obj_name)
    write_location = os.path.join(obj_name, target_dir)

    for hdu, fname in ic1.hdus(imagetyp='light', object=obj_name, return_fname=True):
        # made 'object' above a variable, hope it still works
        header = hdu.header
        data = hdu.data
        data = data.byteswap(True).newbyteorder()

        Dmask = np.isnan(data)

        bkg = sep.Background(data, mask=Dmask)

        # Directly subtract the background from the data in place
        bkg.subfrom(data)

        bkg.globalback  # Global "average" background level
        bkg.globalrms  # Global "avergage" RMS of background

        thresh = 3.0 * bkg.globalrms
        objects = sep.extract(data, thresh)

        header = hdu.header
        wcs = WCS(header=header)
        # create a table for the object to fill
        object_table = Table(objects)
        # print(object_table.colnames)
        # retrieve the list of RA/Decs
        ra_decs = wcs.all_pix2world(objects['x'], objects['y'], 0)
        # separate RA column
        ra_column = Column(data=ra_decs[0], unit='degree', name='RA')
        object_table.add_column(ra_column)  # add RA column to table
        # separate Dec column
        dec_column = Column(data=ra_decs[1], unit='degree', name='Dec')
        object_table.add_column(dec_column)  # add Dec column to table

        flux, fluxErr = get_fluxes(objects, data, I, O, G, N)

        # Replace source detection flux with sum_circle flux
        object_table['flux'] = flux

        # Make column for fluxerr and add it to table
        fluxerr_col = Column(data=fluxErr, name='FluxErr')
        object_table.add_column(fluxerr_col)
        good_flux = flux > 0
        object_table = object_table[good_flux]
        n_objects = len(object_table)

        Ofilter = hdu.header["Filter"]

        # make and add columns for inner/outer radius, gain, and read noise
        innerRad_col = Column(data=[I] * n_objects, name='InnerRad')
        object_table.add_column(innerRad_col)
        outerRad_col = Column(data=[O] * n_objects, name='OuterRad')
        object_table.add_column(outerRad_col)
        Tgain_col = Column(data=[G] * n_objects, name='Gain')
        object_table.add_column(Tgain_col)
        readNoise_col = Column(data=[N] * n_objects, name='ReadNoise')
        object_table.add_column(readNoise_col)
        filter_col = Column(data=[Ofilter] * n_objects, name='Filter')
        object_table.add_column(filter_col)

        base_name = os.path.basename(fname)
        first_part, _ = os.path.splitext(base_name)

        if plot_graph is True:
            # to plot image with circles around sources
            my_image = CCDData.read(fname)
            scaled = scale_image(my_image, min_percent=20, max_percent=99)
            plt.imshow(scaled, cmap='gray')
            mean_flux = flux[good_flux].mean()
            scale = 20 * np.sqrt(flux[good_flux] / mean_flux)
            plt.scatter(objects['x'][good_flux], objects['y'][good_flux], marker='o', facecolor='none', s=scale, edgecolor='cyan', lw=1)
            plt.show()

        # outputs table of located object's info in .csv format
        object_table.write(os.path.join(write_location, first_part + '.csv'))

    return write_location
