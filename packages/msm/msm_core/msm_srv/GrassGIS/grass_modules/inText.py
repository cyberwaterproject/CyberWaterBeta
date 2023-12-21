#!/usr/bin/env python
# -*- coding: utf-8 -*-
############################################################################
#
# MODULE:       r.in.text
#
# AUTHOR(S):    University of Pittsburgh:
#                   Daniel Luna
#                   Felipe Hernández
#                   Daniel Salas
#                   Xu Liang (Principal Investigator) xuliang@pitt.edu
#               Indiana University - Purdue University Indianapolis:
#                   Rui Wang
#                   Yao Liang (Principal Investigator) yaoliang@iupui.edu
#               NASA Goddard Earth Sciences Data and Information Services Center (ADNET):
#                   William Teng
#
# PURPOSE:      Import a raster map based on an existing text file with the 
#               numerical data of each cell
#               The Hydrologic Disaster Forecasting and Response (HDFR) System is
#               developed for the Pennsylvania Department of Transportation (PennDOT) 
#               to provide estimates for identifying scour critical bridges in need of 
#               inspection. HDFR is a lightweight software framework that streamlines 
#               the process of automatically (1) acquiring real-time and near real-time 
#               observations and forecast data from numerous data sources/providers; 
#               and (2) translating them into concrete actionable information for field-team 
#               deployment. At present, HDFR includes precipitation data from rain gauges 
#               published by USGS and NOAA METAR system, NOAA NEXRAD radar precipitaiton 
#               data, NLDAS forcing data, NASA satellite data from TRMM, GPM, SMAP, and 
#               MODIS snow cover, SNODAS data, and NOAA model forecast data from GFS and 
#               NAM. HDFR integrates data and severity modules behind a unified GIS 
#               graphical user interface. The latter interface allows non-expert users to 
#               easily execute complex workflows. The data fusion module in HDFR is based 
#               on an extended multi-scale Kalman smoother-based (MKS-based) algorithm 
#               (Parada and Liang, 2004) to provide enhanced data products.
#
# REFERENCES:   Parada, L. M., and X. Liang, Optimal multiscale Kalman filter for 
#               assimilation of near-surface soil moisture into land surface models, 
#               J. Geophys. Res., 109(D24), doi:10.1029/2004JD004745, (21 pages), 2004. 
#
# COPYRIGHT:    (C) 2017, University of Pittsburgh and Indiana University - Purdue University
#               Indianapolis. All rights reserved. 
#
#               HDFR (Hydrologic Disaster Forecasting and Response) System is 
#               developed through a collaboration between the University of
#               Pittsburgh, Indiana University - Purdue University Indianapolis,
#               and NASA/ADNET. The HDFR System has been funded by the U.S.
#               Department of Transportation (OASRTRS-14-H-PIT), Pennsylvania
#               Department of Transportation (PennDOT) (PITT WO 009), the National 
#               Aeronautics and Space Administration (NASA) (NNX12AQ25G), the University of
#               Pittsburgh, and Indiana University - Purdue University Indianapolis.
#
#############################################################################

import os
import numpy
import grass.script as grass
import traceback

def main(rasterMapName, pathFile, northLimit, southLimit, westLimit, eastLimit):
    try:
        #Loading the text file in a matrix and exporting it as floating binary 
        tableData=numpy.loadtxt(pathFile)
        dir_temp = pathFile+'_temp'
        tableData.astype(numpy.float32).tofile(dir_temp)
		
        #Taking the size of the matrix
        nRows = len(tableData)
        nColumns = len(tableData[0])
        # Setting the region
        grass.run_command('g.region', n=northLimit, s=southLimit, e=eastLimit, w=westLimit, rows=nRows, cols=nColumns)
		# Importing the map as binary float with 4 bytes
        grass.run_command('r.in.bin', input=dir_temp, output=rasterMapName, bytes=4, north=northLimit,
        south=southLimit, east=eastLimit, west=westLimit, rows=nRows, cols=nColumns, overwrite=True, flags='f')
		
        # Removing temporal binary file
        os.remove(dir_temp)
        grass.message(rasterMapName+" succesfully imported.")

    except Exception as e:
        grass.error(e)
        traceback.print_exc()
    
