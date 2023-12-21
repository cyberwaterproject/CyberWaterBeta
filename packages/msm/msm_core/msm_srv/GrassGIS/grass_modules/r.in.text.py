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

#%module
#% description:  Import a raster map based on an existing text file with the numerical data of each cell
#% keyword: Import
#% keyword: Raster
#% keyword: Text
#%end

#%option G_OPT_R_OUTPUT 
#% guisection: Input
#%end
#%option G_OPT_F_BIN_INPUT 
#% key: path
#% required: yes
#% label: File that contains the numerical matrix
#% guisection: Input
#%end

#%option
#% key: west
#% key_desc: coordinate
#% required: yes
#% type: double
#% label: West limit (degrees)
#% description: A number between -180 and 180
#% guisection: Resolution
#%end
#%option
#% key: north
#% key_desc: coordinate
#% required: yes
#% type: double
#% label: North limit (degrees)
#% description: A number between 90 and -90
#% guisection: Resolution
#%end
#%option
#% key: east
#% key_desc: coordinate
#% required: yes
#% type: double
#% label: East limit (degrees)
#% description: A number between -180 and 180
#% guisection: Resolution
#%end
#%option
#% key: south
#% key_desc: coordinate
#% required: yes
#% type: double
#% label: South limit (degrees)
#% description: A number between 90 and -90
#% guisection: Resolution
#%end

import inText
import grass.script as grass

if __name__ == "__main__":
    options, flags = grass.parser()
    #Reading input values
    rasterMapName = options["output"]
    pathFile = options["path"]
    northLimit = float(options["north"])
    southLimit = float(options["south"])
    westLimit = float(options["west"])
    eastLimit = float(options["east"])
    inText.main(rasterMapName, pathFile, northLimit, southLimit, westLimit, eastLimit)
    
