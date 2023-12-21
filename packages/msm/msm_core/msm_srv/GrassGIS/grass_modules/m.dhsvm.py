#!/usr/bin/env python
# -*- coding: utf-8 -*-
############################################################################
#
# MODULE:       m.dhsvm
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
# PURPOSE:      Runs a DHSVM simulation, creating all the input files and 
#               writing the output files in the specified path.
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
#% description: Runs a DHSVM simulation, creating all the input files and writing the output files in the specified path.
#% keyword: DHSVM
#% keyword: Routing
#% keyword: Streamflow
#%end

#%option G_OPT_R_INPUT
#% key: elevation
#% label: Elevation map
#% guisection: Input
#% answer: DEMReduced
#%end

#%option G_OPT_R_INPUT
#% key: vegetation
#% label: Vegetation map
#% guisection: Input
#% answer: PA_Vegetation
#%end

#%option G_OPT_R_INPUT
#% key: soil
#% label: Soil map
#% guisection: Input
#% answer: PA_Soil
#%end

#%option G_OPT_R_INPUT
#% key: soil_depth
#% label: Soil depth map
#% guisection: Input
#% answer: PA_SoilDepth
#%end

#%option G_OPT_M_DIR 
#% key: directory
#% required: yes
#% label: Folder where the DHSVM information will be created
#% guisection: Input
#% answer: C:\temp\FrenchCreekDHSVM
#%end

#%option G_OPT_F_BIN_INPUT  
#% key: met_file
#% required: yes
#% label: File with the meteorology information
#% guisection: Input
#% answer: C:\temp\met.txt
#%end

## G_OPT_M_COORDS
#%option G_OPT_M_COORDS
#% key: long_lat
#% key_desc: coord
#% required: yes
#% label: Outlet coordinates (Long,Lat)
#% description: Outlet point in Longitude,Latitude
#% guisection: Waterhsed
#% answer: -75.60166666666,40.151544444444
#%end

#%option 
#% key: resolution
#% type: double
#% required: yes
#% label: Resolution of the output model (meters)
#% guisection: Waterhsed
#% answer: 1000
#%end
#500

#%option 
#% key: threshold
#% type: integer
#% label: Minimum size of exterior watershed basin (pixels)
#% guisection: Waterhsed
#% answer: 500
#%end
#100

#%option 
#% key: flow_out
#% type: double
#% required: yes
#% label: Mean flow in the outlet of the watershed (m3/s)
#% guisection: Waterhsed
#% answer: 1.56
#%end

#%option 
#% key: width_out
#% type: double
#% required: yes
#% label: With of the stream in the outlet of the watershed (m)
#% guisection: Waterhsed
#% answer: 20.6
#%end

#%option 
#% key: min_slope
#% type: double
#% required: yes
#% label: Minimum channel slope
#% guisection: Waterhsed
#% answer: 0.001
#%end

#%option 
#% key: manning
#% type: double
#% required: yes
#% label: Manning's n of the channels
#% guisection: Waterhsed
#% answer: 0.35
#%end

#%option 
#% key: max_inf
#% type: double
#% required: yes
#% label: Maximum infiltration rate through the channels (m/s)
#% guisection: Waterhsed
#% answer: 0.00001
#%end

import mDHSVM
import grass.script as grass

if __name__ == "__main__":
    options, flags = grass.parser()
    #Input Data (required)
    pointCoord = options["long_lat"].split(",")
    path = options["directory"]
    elevationMapName = options["elevation"]
    vegetationMap = options["vegetation"]
    soilMap = options["soil"]
    soilDepth = options["soil_depth"]    
    metPath = options["met_file"]
    threshold = int(options["threshold"])
    
    n = float(options["manning"])
    inf = float(options["max_inf"])
    C = float(options["width_out"])*pow(float(options["flow_out"]),-0.5)
    minSlope = float(options["min_slope"])
    resolutionModel = float(options["resolution"])
    flow_out = float(options["flow_out"])
    mDHSVM.main(pointCoord, path, elevationMapName, vegetationMap, soilMap, soilDepth, metPath, threshold, n, inf, C, minSlope, resolutionModel, flow_out)

    
