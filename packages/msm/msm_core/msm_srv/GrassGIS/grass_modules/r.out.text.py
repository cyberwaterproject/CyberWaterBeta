#!/usr/bin/env python
# -*- coding: utf-8 -*-
############################################################################
#
# MODULE:       r.out.text
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
# PURPOSE:      Export a raster map to a text file with the numerical data of each cell
#               The Hydrologic Disaster Forecasting and Response (HDFR) System is
#               further developed for the Pennsylvania Department of Transportation (PennDOT) 
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
#               assimilation of near-surface soil moisture into land surface models”, 
#               J. Geophys. Res., 109(D24), doi:10.1029/2004JD004745, (21 pages), 2004. 
#
# COPYRIGHT:    HDFR (Hydrologic Disaster Forecasting and Response) System is 
#               further developed through a collaboration between the University of
#               Pittsburgh, Indiana University - Purdue University Indianapolis,
#               and NASA/ADNET. The HDFR System has been funded by the U.S.
#               Department of Transportation (OASRTRS-14-H-PIT), Pennsylvania
#               Department of Transportation (PennDOT) (PITT WO 009), the National 
#               Aeronautics and Space Administration (NASA) (NNX12AQ25G), the University of
#               Pittsburgh, and Indiana University - Purdue University Indianapolis.
#
#               (C) 2015 by the GRASS Development Team. GRASS is a free software
#               under the  GNU General Public License (version 2). Read the file
#               COPYING that comes with GRASS for details.
#
#############################################################################

#%module
#% description:  Export a raster map to a text file with the numerical data of each cell
#% keyword: Export
#% keyword: Raster
#% keyword: Text
#%end

#%option G_OPT_R_INPUT
#% guisection: Input
#% label:Name of the raster map to be exported
#%end

#%option
#% key: new_name
#% required: no
#% description: if you want to rename the output file, here you can type the new name
#% label: New name of the produced file
#% guisection: Input
#%end

#%option G_OPT_M_DIR 
#% key: directory
#% required: yes
#% label: Folder where the text file will be created
#% guisection: Input
#%end

import os
import numpy
import grass.script as grass
from grass.hdfr.utils import hdfr_operations
#from hdfr.utils import hdfr_operations
from grass.pygrass.modules.shortcuts import general as g

def main():
    try:
        options, flags = grass.parser()
        #Reading input values
        rasterMapName = options["input"].split('@')[0]
        pathFolder = options["directory"]
        new_name = options["new_name"]
        if new_name is None or new_name == "": new_name = ""
        #Set the current region to coincide with the existing raster map
        g.region(raster=rasterMapName)
        #Create a matrix with the data stored in the raster map
        matrix = hdfr_operations.getNumpyMap(rasterMapName)
        
        if not os.path.exists(pathFolder):
            os.makedirs(pathFolder)

        if new_name == "": new_name = rasterMapName
        #Create the new file with the data from the raster map
        numpy.savetxt(os.path.join(pathFolder,new_name), matrix, fmt="%s", delimiter='\t')
        grass.message(rasterMapName+" succesfully exported!")
    except Exception as e:
        grass.error(e)

if __name__ == "__main__":
    main()
    
