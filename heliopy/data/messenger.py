"""
Methods for importing data from the Messenger spacecraft.

All data is publically available at ftp://spdf.gsfc.nasa.gov/pub/data/messenger
"""
import os
import pandas as pd

import heliopy.time as spacetime
from heliopy.data import helper
from heliopy import config

data_dir = config['DEFAULT']['download_dir']
use_hdf = config['DEFAULT']['use_hdf']
mess_dir = os.path.join(data_dir, 'messenger')
remote_mess_dir = 'ftp://spdf.gsfc.nasa.gov/pub/data/messenger'


def mag_rtn(starttime, endtime):
    """
    Import magnetic field in RTN coordinates from Messenger.

    Parameters
    ----------
        starttime : datetime
            Interval start time.
        endtime : datetime
            Interval end time.

    Returns
    -------
        data : DataFrame
    """
    # Directory relative to main WIND data directory
    relative_dir = 'rtn'
    keys = {'B_normal': 'Bn',
            'B_radial': 'Br',
            'B_tangential': 'Bt',
            'Epoch': 'Time',
            'azimuth_ecliptic': 'sc_Az',
            'latitude_ecliptic': 'sc_Lat',
            'radialDistance': 'sc_r'}

    daylist = spacetime.daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]

        this_relative_dir = os.path.join(relative_dir, str(date.year))
        hdffile = 'messenger_mag_rtn_' +\
            str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2) +\
            '_v01.hdf'
        hdfloc = os.path.join(mess_dir, this_relative_dir, hdffile)
        # Try to load hdf file
        if os.path.isfile(hdfloc):
            df = pd.read_hdf(hdfloc)
            data.append(df)
            continue

        filename = hdffile[:-4] + '.cdf'
        # Absolute path to local directory for this data file
        local_dir = os.path.join(mess_dir, this_relative_dir)
        helper.checkdir(local_dir)

        remote_url = os.path.join(remote_mess_dir, this_relative_dir)

        cdf = helper.load(filename, local_dir, remote_url, guessversion=True)
        df = helper.cdf2df(cdf, index_key='Epoch', keys=keys)

        if use_hdf:
            hdffile = filename[:-4] + '.hdf'
            df.to_hdf(hdfloc, key='data', mode='w')
        data.append(df)

    return helper.timefilter(data, starttime, endtime)
