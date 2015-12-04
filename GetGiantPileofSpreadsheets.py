from __future__ import division, print_function

import os

import numpy as np
import sep

from astropy.table import Table, Column
from astropy.wcs import WCS

from msumastro import ImageFileCollection

# constants
innerRad = 20.
outerRad = 30.
Tgain = 1.5
readNoise = 30


def __init__(self, tstuff):
    self.__stuff = tstuff


def loadFiles(fileLocation):
    """
    Preconditions: Requires directory location of image files to be processed.
    Postcontions: Returns files as an image ImageFileCollection.
    """
    keys = ['imagetyp', 'object', 'filter', 'exposure']
    files = ImageFileCollection(fileLocation, keywords=keys)
    return files


def getFluxes(object1, data1, iR, oR, G, rN):
    """
    Preconditions: Expects a sep extracted list of objects and the image data
    the objectlist is from. Can also take the inner radius, outer radius,
    gain, and read noise.
    Postcontions: Returns the flux and flux error for each object in the list.
    """

    flux, fluxerr, flag = sep.sum_circle(data1, object1['x'], object1['y'], 16.0, bkgann=(iR, oR), gain=G, err=rN)

    return flux, np.sqrt(fluxerr)


def writeTables(ic1, target_dir='output', I=innerRad, O=outerRad, G=Tgain, N=readNoise):
    """
    Preconditions: Requires an image collection and a directory location to
    put the created files. Can also take the inner radius, outer radius, gain,
    and read noise.
    Postconditions: Writes csv tables containing the information from each
    image with added columns for RA, Dec, flux , fluxerr, InnerRad, OuterRad,
    Gain, ReadNoise, and Filter.
    """
    try:
        os.mkdir(target_dir)
    except WindowsError as e:
        if 'Cannot create a file when that file already exists' in e.strerror:
            pass
        else:
            raise
    for hdu, fname in ic1.hdus(imagetyp='light', object='m71', return_fname=True):
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
        # retrieve the list of RA/Decs
        ra_decs = wcs.all_pix2world(objects['x'], objects['y'], 0)
        # separate RA column
        ra_column = Column(data=ra_decs[0], unit='degree', name='RA')
        object_table.add_column(ra_column)  # add RA column to table
        # separate Dec column
        dec_column = Column(data=ra_decs[1], unit='degree', name='Dec')
        object_table.add_column(dec_column)  # add Dec column to table

        flux, fluxErr = getFluxes(objects, data, I, O, G, N)

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
        innerRad_col = Column(data=[innerRad]*n_objects, name='InnerRad')
        object_table.add_column(innerRad_col)
        outerRad_col = Column(data=[outerRad]*n_objects, name='OuterRad')
        object_table.add_column(outerRad_col)
        Tgain_col = Column(data=[Tgain]*n_objects, name='Gain')
        object_table.add_column(Tgain_col)
        readNoise_col = Column(data=[readNoise]*n_objects, name='ReadNoise')
        object_table.add_column(readNoise_col)
        filter_col = Column(data=[Ofilter]*n_objects, name='Filter')
        object_table.add_column(filter_col)

        base_name = os.path.basename(fname)
        first_part, _ = os.path.splitext(base_name)

        # outputs table of located object's info in .csv format
        object_table.write(os.path.join(target_dir, first_part+'.csv'))
