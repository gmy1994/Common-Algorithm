#!/usr/bin python3
# -*- coding:utf-8 -*-
import os
import os.path
import math
import time
import subprocess
import numpy as np
import netCDF4 as nc


TEMPLATE        = './sm_0.1_template.cdl'
INPUT_FILE      = '/scratch/06956/mguo/SM/weighted/weighted_sm.nc'
OUTPUT_FILE     = '/scratch/06956/mguo/SM/weighted/weighted_sm_0.1.nc'
LON_LAT_FILE    = '/scratch/06956/mguo/CMFD_DY/Data_forcing_01dy_010deg/srad_CMFD_V0106_B-01_01dy_010deg_197901-197912.nc'

# Variable names
lon_25 = nc.Dataset(INPUT_FILE).variables['lon'][:]
lat_25 = nc.Dataset(INPUT_FILE).variables['lat'][:]
lvl = nc.Dataset(INPUT_FILE).variables['lvl'][:]
lev = nc.Dataset(INPUT_FILE).variables['lev'][:]
time = nc.Dataset(INPUT_FILE).variables['time'][:]
www_25 = nc.Dataset(INPUT_FILE).variables['www'][:]
www_25.filled(fill_value=-999)  # return www_25 as an array with masked data replaced by a fill value

lon_1 = nc.Dataset(LON_LAT_FILE).variables['lon'][:]
lat_1 = nc.Dataset(LON_LAT_FILE).variables['lat'][:]

def bilinear_interpolate(t, x, y):
    www = www_25[t]
    x2 = np.searchsorted(lat_25, x)
    # x2 = [ 1 if x2[i]-1<0 else x2[i] for i in range(400)]
    x1 = [ 0 if x2[i]-1<0 else x2[i]-1 for i in range(400)]

    x2 = np.array([ [ x2[i] for j in range(700)] for i in range(400)])
    x1 = np.array([ [ x1[i] for j in range(700)] for i in range(400)])
    x =  np.array([ [ x[i] for j in range(700)] for i in range(400)])

    y2 = np.searchsorted(lon_25, y)
    # y2 = [ 1 if y2[i]-1<0 else y2[i] for i in range(700)]
    y1 = [ 0 if y2[i]-1<0 else y2[i]-1 for i in range(700)]

    y2 = np.array([ y2 for i in range(400)])
    y1 = np.array([ y1 for i in range(400)])
    y  = np.array([ y for i in range(400)])
    Ia = www[x1, y1]
    Ib = www[x1, y2]
    Ic = www[x2, y1]
    Id = www[x2, y2]
    wa = np.ma.(lat_25[x2]-x) * (lon_25[y2]-y)
    wb = np.ma.(lat_25[x2]-x) * (y-lon_25[y1])
    wc = np.ma.(x-lat_25[x1]) * (lon_25[y2]-y)
    wd = np.ma.(x-lat_25[x1]) * (y-lon_25[y1])
    return (wa*Ia + wb*Ib + wc*Ic + wd*Id)/((lat_25[x2]-lat_25[x1]) * (lon_25[y2]-lon_25[y1]))

if os.path.exists(OUTPUT_FILE) == False:
    subprocess.run(['ncgen', '-3', '-o', OUTPUT_FILE, TEMPLATE])
with nc.Dataset(OUTPUT_FILE, 'a') as ncf:
    ncf.variables['lon'][:] = lon_1[:]
    ncf.variables['lat'][:] = lat_1[:]
    ncf.variables['lvl'][:] = lvl[:]
    ncf.variables['lev'][:] = lev[:]
    ncf.variables['time'][:] = time[:]
    for i in range(3384):
        ncf.variables['www'][i] = bilinear_interpolate(i, lat_1, lon_1)
