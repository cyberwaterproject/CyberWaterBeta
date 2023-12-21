#!/usr/bin/env python
# -*- coding: utf-8 -*-
############################################################################
#
# MODULE:       v.surf.idw2
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
# PURPOSE:      Provides surface interpolation from vector point data by 
#               Inverse Distance Weighting with a distance boundary. 
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
#               assimilation of near-surface soil moisture into land surface models, 
#               J. Geophys. Res., 109(D24), doi:10.1029/2004JD004745, (21 pages), 2004. 
#
# COPYRIGHT:    (C) 2017, University of Pittsburgh and Indiana University - Purdue University
#               Indianapolis. All rights reserved. 
#
#               HDFR (Hydrologic Disaster Forecasting and Response) System is 
#               further developed through a collaboration between the University of
#               Pittsburgh, Indiana University - Purdue University Indianapolis,
#               and NASA/ADNET. The HDFR System has been funded by the U.S.
#               Department of Transportation (OASRTRS-14-H-PIT), Pennsylvania
#               Department of Transportation (PennDOT) (PITT WO 009), the National 
#               Aeronautics and Space Administration (NASA) (NNX12AQ25G), the University of
#               Pittsburgh, and Indiana University - Purdue University Indianapolis.
#
#############################################################################

#%module
#% description: Provides surface interpolation from vector point data by Inverse Distance Weighting with a distance boundary. 
#% keyword: vector
#% keyword: surface
#% keyword: interpolation
#% keyword: IDW
#%end

#%option G_OPT_R_OUTPUT
#% guisection: Input
#%end
#%option G_OPT_V_INPUT 
#% guisection: Input
#% required: yes
#%end

#%option G_OPT_DB_COLUMN
#% description: Name of attribute column with values to interpolate:
#% required: yes
#% guisection: Settings
#%end
#%option
#% key: power
#% required: no
#% type: double
#% label: Power parameter
#% description: Greater values assign greater influence to closer points
#% answer: 2.0
#% guisection: Settings
#%end
#%option
#% key: distance
#% required: no
#% type: double
#% label: Maximum search distance around point (degrees)
#% answer: 0.0375
#% guisection: Settings
#%end

#%option
#% key: west
#% required: yes
#% type: double
#% label: West limit (degrees)
#% description: A number between -180 and 180
#% answer: -80.520108
#% guisection: Resolution
#%end
#%option
#% key: north
#% required: yes
#% type: double
#% label: North limit (degrees)
#% description: A number between 90 and -90
#% guisection: Resolution
#%end
#%option
#% key: east
#% required: yes
#% type: double
#% label: East limit (degrees)
#% description: A number between -180 and 180
#% guisection: Resolution
#%end
#%option
#% key: south
#% required: yes
#% type: double
#% label: South limit (degrees)
#% description: A number between 90 and -90
#% guisection: Resolution
#%end
#%option
#% key: resolution
#% required: yes
#% type: double
#% label: Cell resolution (degrees)
#% description: Minimum recomended value: 0.025

#% guisection: Resolution
#%end

import surfIDW
import grass.script as grass

if __name__ == "__main__":
    options, flags = grass.parser()
    #Reading input values
    newRaster = options["output"]
    pointsInput = options["input"]
    cellLength = float(options["resolution"])
    northLimit = float(options["north"])
    southLimit = float(options["south"])
    westLimit = float(options["west"])
    eastLimit = float(options["east"])
    attribute = (options["column"])
    power = float(options["power"])
    maxDistance = float(options["distance"])
    surfIDW.main(newRaster,pointsInput,cellLength,northLimit,southLimit,westLimit,eastLimit,attribute,power,maxDistance)
