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

import numpy
import os
import shutil
import math

import grass.script as grass
from datetime import datetime

from grass.pygrass.modules import Module

def main(pointCoord, path, elevationMapName, vegetationMap, soilMap, soilDepth, metPath, threshold, n, inf, C, minSlope, resolutionModel, flow_out):
    myPath = r''+os.path.dirname(os.path.abspath(__file__))
    date = datetime.now()
    grass.message("Executing HDFR DHSVM: "+str(date.year)+'/'+str(date.month)+'/'+str(date.day)+'  '+str(date.hour)+':'+str(date.minute)+" ===================")
    
    numberOfSoilLayers = 3
    point = (float(pointCoord[0]),float(pointCoord[1]))
    
    # Input verification
    metData = numpy.loadtxt(metPath,
            dtype={'names': ('Time', 'Temp', 'Wind', 'RH', 'Short', 'Long', 'Precip'),
                   'formats': ('|S19', numpy.float, numpy.float, numpy.float, numpy.float, numpy.float, numpy.float)})
    if len(metData)<1: raise Exception("Met file should have more than two entries")
    
    #Input Data
    streamSegmentsMapName = "BStreamSegments"
    PAAccumulation = "PA_Accumulation"
    drainageMap = 'PA_DrainageDirection'
    
    drainageDirectionWatershed = "BDrainageDirectio"
    watershedMapName = "BWatershed"
    elevationFilledMapName = "BElevationFilled"
    watershedStreams = "BStreams"
    BElevation = "BElevation"
    temporalDirectionRasterMap = "TempDirection" 

    #Clean and create folders
    folders = ["input", "output", "met", "state"]
    for name in folders:
        full_path_name = os.path.join(path, name)
        if not os.path.exists(full_path_name):
            os.mkdir(full_path_name)

    Module('g.region', raster=elevationMapName)
    metadata = fromTableToDictionary(convertSelectTableToTable(grass.read_command('r.info', map=elevationMapName, flags='gre'),'='))
    #METADATA:creator,cols,ncats,rows,min,west,comments,location,timestamp,units,east,nsres,vdatum,map,north,description,max,source2,source1,ewres,date,mapset,database,datatype,cells,title,south    
    metersInDegree = computeResolutionInMeters((metadata['south']+metadata['north'])*0.5)
    resolution = str("%.2f"%((metadata['nsres']+metadata['ewres'])*0.5*metersInDegree))
    grass.message("Original Resolution: "+resolution+"m.")
    Module('g.remove', type='vector', f=True, name=[streamSegmentsMapName,watershedStreams], quiet=True)

    Module('r.watershed', elevation=elevationMapName, drainage=drainageMap, stream=streamSegmentsMapName, accumulation=PAAccumulation, threshold=threshold, memory=1000, overwrite=True, quiet=True, a=True)
    Module('r.water.outlet', input=drainageMap, output=watershedMapName, coordinates=point, overwrite=True, quiet=True)
    Module('r.fill.dir', input=elevationMapName, output=elevationFilledMapName, direction=temporalDirectionRasterMap, quiet=True, overwrite=True)

    Module('r.mapcalc', expression=BElevation+'=if('+watershedMapName+','+elevationFilledMapName+')', overwrite=True, quiet=True)
    Module('r.mapcalc', expression=drainageDirectionWatershed+'=if('+watershedMapName+','+drainageMap+')', overwrite=True, quiet=True)
    Module('r.mapcalc', expression=watershedStreams+'=if('+watershedMapName+','+streamSegmentsMapName+')', overwrite=True, quiet=True)

    grass.run_command(myPath+'//r.stream.order.exe',stream_rast=watershedStreams, direction=drainageDirectionWatershed, elevation=BElevation, accumulation=PAAccumulation, stream_vect=watershedStreams,flags='a', overwrite=True,quiet=True)
    Module('g.region', ewres=resolutionModel/metersInDegree, nsres=resolutionModel/metersInDegree)
    Module('r.resample', input=watershedMapName, output=watershedMapName, overwrite=True,quiet=True)
    Module('r.mapcalc', expression=BElevation+'=if('+watershedMapName+','+elevationFilledMapName+')', overwrite=True, quiet=True)
    
    grass.run_command('g.region', zoom=BElevation)
    Module('r.resample', input=watershedMapName, output=watershedMapName, overwrite=True,quiet=True)
    Module('r.mapcalc', expression=BElevation+'=if('+watershedMapName+','+elevationFilledMapName+')', overwrite=True, quiet=True)
    
    Module('r.mapcalc', expression=drainageDirectionWatershed+'=if('+watershedMapName+','+drainageMap+')', overwrite=True, quiet=True)
    metadata = fromTableToDictionary(convertSelectTableToTable(grass.read_command('r.info', map=BElevation, flags='gre'),'='))
    grass.message("Model Dimensions:   Rows("+str(int(metadata['rows']))+")xCols("+str(int(metadata['cols']))+")")
    resolution = str("%.2f"%((metadata['nsres']+metadata['ewres'])*0.5*metersInDegree))
    grass.message("Model Resolution: "+resolution+"m.")
    
    #Create the vegetation (soil cover) map
    Module('r.mapcalc', expression='BAccumulation=if('+watershedMapName+','+PAAccumulation+')', overwrite=True, quiet=True)
    Module('r.mapcalc', expression='BVegetation=int(if('+watershedMapName+','+vegetationMap+'))', overwrite=True, quiet=True)
    Module('r.mapcalc', expression='BSoil=int(if('+watershedMapName+','+soilMap+'))', overwrite=True, quiet=True)
    Module('r.mapcalc', expression='BSoilDepth=if('+watershedMapName+','+soilDepth+')', overwrite=True, quiet=True)    
    
    #Exporting the INPUT files
    grass.message('Creating model raster maps')
    if not os.path.exists(path + '\\input\\Mask.bin'):
        Module('r.out.bin', input=watershedMapName, output=path+'\\input\\Mask.bin', bytes=1, quiet=True)
    if not os.path.exists(path + '\\input\\DEM.bin'):
        Module('r.out.bin', input=BElevation, output=path+'\\input\\DEM.bin', bytes=4, quiet=True)
    if not os.path.exists(path + '\\input\\Vegetation.bin'):
        Module('r.out.bin', input='BVegetation', output=path+'\\input\\Vegetation.bin', bytes=1, quiet=True)
    if not os.path.exists(path + '\\input\\Soil.bin'):
        Module('r.out.bin', input='BSoil', output=path+'\\input\\Soil.bin', bytes=1, quiet=True)
    if not os.path.exists(path + '\\input\\Soil_depth.bin'):
        Module('r.out.bin', input='BSoilDepth', output=path+'\\input\\Soil_depth.bin', bytes=4, quiet=True)
    if not os.path.exists(path + '\\input\\Flow_dir.bin'):
        Module('r.out.bin', input=formatFlowDirection(drainageDirectionWatershed), output=path+'\\input\\Flow_dir.bin', bytes=1, quiet=True)
    
    #Coping the met file
    shutil.copyfile(metPath,path+"\\met\\met.txt")    
    
    #Creating STREAM-CLASS file
    grass.message("Creating Stream-Class file")
    streamsRawTable = convertSelectTableToTable(grass.read_command('db.select', sql="SELECT cat,next_stream,flow_accum,gradient,shreve,length FROM "+watershedStreams+" ORDER BY flow_accum DESC", flags='c'),'|')    
    streamClassList = [] #ID|Width|Depth|Friction|Infiltration
    factorFlow = float(flow_out)/float(streamsRawTable[0][2])
    for row in streamsRawTable:
        channelID = int(row[0])
        Q = factorFlow*float(row[2])
        W = C*pow(Q,0.5)
        S = max(float(row[3]),minSlope)
        D = ((-((-2) * pow((n * Q),1.5)) + pow(pow((-2) * pow((n * Q),1.5), 2) - 4 * (pow(W,2.5) * pow(S,0.75)) * ((-1) * W * pow((n * Q),1.5)),0.5)) / (2 * (pow(W,2.5) * pow(S,0.75)))) * 0.7119324 * pow(Q,-0.0747718) * pow(S,0.076795) * pow(n,-0.757838)   
        streamClassList.append([channelID,W,D,n,inf])
    streamClassList = sorted(streamClassList,key=getKey)
    if not os.path.exists(path+'\\input\\stream_class.txt'):
        numpy.savetxt(path+'\\input\\stream_class.txt', streamClassList, fmt=["%d","%f","%f","%f","%f"], delimiter='\t')
    
    #Creating STREAM-NETWORK file (and initial state of Channels)
    grass.message("Creating Stream-Network file")
    streamNetworkList = [] #ID|Order|Slope|Length|Class|Destination
    channelState = []
    for row in streamsRawTable:
        channelID = int(row[0])
        channelOrder = int(row[4])
        channelSlope = max(float(row[3]),minSlope)
        channelLenght = 1.15*float(row[5])+2
        channelDestination = [int(row[1]),0][row[1]==-1]
        streamNetworkList.append([channelID,channelOrder,channelSlope,channelLenght,channelID,channelDestination])
        channelState.append([channelID, 0.0])
    if not os.path.exists(path + '\\input\\stream_network.txt'):
        numpy.savetxt(path+'\\input\\stream_network.txt', streamNetworkList, fmt=["%d","%d","%0.6f","%0.2f","%d","%d"], delimiter='\t')
    streamNetworkList = sorted(streamNetworkList,key=getKey)     
    
    #Creating a STREAM-MAP file
    grass.message("Creating Stream-Map file...")
    Module('v.to.points', input=watershedStreams, output=watershedStreams+"Points", use='vertex', type='line', overwrite=True, quiet=True)
    Module('v.to.rast', input=watershedStreams+"Points", output="BStreamRaster", use='cat', layer=2, type='point', overwrite=True, quiet=True)  
    Module('r.mapcalc', expression="BStreamRaster2=if(BStreamRaster && "+watershedMapName+", BStreamRaster)", overwrite=True, quiet=True)
    Module('r.to.vect', input='BStreamRaster2', output='BStreamAreas', type='area', overwrite=True, quiet=True, v=True)
    Module('v.db.addcolumn', map=watershedStreams+"Points", layer=2, columns='cell int')
    Module('v.what.vect', map=watershedStreams+"Points", layer=2, column='cell', query_map='BStreamAreas', query_column='cat', quiet=True)
    pointsCellTable = convertSelectTableToTable(grass.read_command('db.select', sql="SELECT * FROM "+watershedStreams+"Points_2 WHERE cell IS NOT NULL GROUP BY lcat, cell", flags='c'),'|')
    partialLengthsTable = convertSelectTableToTable(grass.read_command('db.select', sql="SELECT b1.lcat,num,total FROM (SELECT lcat,cell,COUNT(cat) as num FROM "+watershedStreams+"Points_2  GROUP BY lcat,cell) b1 JOIN (SELECT lcat,SUM(num) AS total FROM (SELECT lcat,COUNT(cat) AS num FROM "+watershedStreams+"Points_2  GROUP BY lcat,cell) GROUP BY lcat) b2 ON b1.lcat=b2.lcat", flags='c'),'|')
    areaCellsTable = convertSelectTableToTable(grass.read_command('v.out.ascii', input="BStreamAreas", format='point'),'|')
    areaCellsTable = sorted(areaCellsTable, key=getKey2)
    streamMapList = [] #Row|Col|Channel|Lenth|Depth|Width
    i=0
    for row in pointsCellTable:
            coordX = binarySearch(areaCellsTable, 2, row[3], 0)
            coordY = binarySearch(areaCellsTable, 2, row[3], 1) 
            rowNumber = int((float(metadata['north'])-coordY)/float(metadata['nsres']))
            colNumber = int((coordX-float(metadata['west']))/float(metadata['ewres']))
            channelID = row[1]
            channelLength = binarySearch(streamNetworkList, 0, row[1], 3)
            lengthInCell = channelLength*(partialLengthsTable[i][1]/partialLengthsTable[i][2])
            width = binarySearch(streamClassList,0,channelID,1)
            depth = binarySearch(streamClassList,0,channelID,2)
            streamMapList.append([colNumber,rowNumber,channelID,lengthInCell,depth,width])
            i=i+1
    streamMapList = sorted(streamMapList,key=getKey)
    if not os.path.exists(path + '\\input\\stream_map.txt'):
        numpy.savetxt(path+'\\input\\stream_map.txt', streamMapList, fmt=["%d","%d","%d","%0.2f","%f","%f"], delimiter='\t')
    
    # Creation of the SURFACE_ROUTING text file
    grass.message('Creating Surface Routing file')
    createSurfaceRouting("BStreamAreas", watershedMapName, path, metadata)
    
    #Creating initial state Maps
    startDate = datetime.strptime(metData[0][0], '%m/%d/%Y-%H.%M.%S')
    endDate = datetime.strptime(metData[len(metData)-1][0], '%m/%d/%Y-%H.%M.%S')
    startString = startDate.strftime('%m.%d.%Y.%H.%M.%S')
    startDate1 = datetime.strptime(metData[1][0], '%m/%d/%Y-%H.%M.%S')
    timeStepH = int((startDate1-startDate).total_seconds()/3600)
        
    grass.message('Creating initial state Maps')
    createStateMap("Interception", startString, path, 5, metadata)
    createStateMap("Snow", startString, path, 8, metadata)
    createStateMap("Soil", startString, path, numberOfSoilLayers*2+1+3, metadata)
    if not os.path.exists(path+'\\state\\Channel.State.'+startString):
        numpy.savetxt(path+'\\state\\Channel.State.'+startString, channelState, fmt=["%d","%f"], delimiter='\t')
    
    grass.message('Creating Config file')
    createConfigFile(path, metadata, startDate, endDate, timeStepH, point, metersInDegree)

    #Removing extra layers in GRASS
    
    Module('g.remove', type='raster', f=True, name=("BStreamRaster","BStreamRaster2",streamSegmentsMapName,"BAccumulation"), quiet=True)
    Module('g.remove', type='vector', f=True, name=(watershedStreams+"Points","BStreamAreas"), quiet=True)
    Module('g.remove', type='raster', f=True, name=(drainageDirectionWatershed,PAAccumulation,watershedStreams,drainageMap,elevationFilledMapName,temporalDirectionRasterMap,streamSegmentsMapName+'_thin'), quiet=True)
    '''
    myPath = r""+os.path.dirname(os.path.abspath(__file__))
    libraryPath = myPath+"\\DHSVM"
    with add_paths([libraryPath]):
        #grass.message("Running DHSVM Version 3.1.1...")
        pathExe = myPath+"\\DHSVM\\dhsvm312.exe"
        grass.message(pathExe.replace('\\', '/'))
        pathExe = pathExe.replace('\\', '/')
        subprocess.call(pathExe +' Configuration.txt', shell=True, stdout=None, stderr=None, cwd=path)
        
        script = "cd "+path+" & \""+pathExe+"\" \""+path+"\\Configuration.txt\""
        script = "\""+pathExe+"\" \""+path+"\\Configuration.txt\""
        os.system(script)
        
    
    with open(os.devnull, 'wb') as devnull:
        try:
            subprocess.check_call(script, stdout=devnull, stderr=subprocess.STDOUT, shell=True)
        except Exception as error:
            grass.message(type(error))
    '''
#========================================================================================================================================
#========================================================================================================================================
# r.in.bin --overwrite input=D:\DanielLuna\10. Pitt\HDFR\DHSVM - Copy\DHSVMOriginal\Indiantown Run\input\Soil.bin output=ASoil bytes=1 north=40.47172778 south=40.425894 east=-76.586650 west=-76.653433 rows=55 cols=60 anull=0
def createConfigFile(path, metadata, startDate, endDate, timeStepH, output, metersInDegree):
    #Getting the table with the data
    pathMaps = r''+os.path.dirname(os.path.abspath(__file__))+"\\Configuration.txt"
    config = numpy.loadtxt(pathMaps, delimiter='#', dtype=[('x', numpy.chararray)])
    #[OPTIONS] No CHANGES so far---------------------------------------------------
    #[AREA]------------------------------------------------------------------------
    GridSpacing = float(metadata['ewres'])*metersInDegree
    replaceInConfig("Extreme North", float(metadata['rows'])*GridSpacing,config)
    replaceInConfig("Extreme West", 0,config)
    replaceInConfig("Center Latitude", (float(metadata['north'])+float(metadata['south']))/2,config)
    replaceInConfig("Center Longitude", (float(metadata['west'])+float(metadata['east']))/2,config)
    replaceInConfig("Number of Rows", int(metadata['rows']),config)
    replaceInConfig("Number of Columns", int(metadata['cols']),config)
    replaceInConfig("Grid spacing", GridSpacing,config)
    #[Time]------------------------------------------------------------------------
    replaceInConfig("Time Step", timeStepH,config)
    replaceInConfig("Model Start", getStrDate(startDate),config)
    replaceInConfig("Model End",getStrDate(endDate),config)
    #[Constants] No CHANGES so far-------------------------------------------------
    #[Terrain] No CHANGES so far---------------------------------------------------
    #[Routing]No CHANGES so far----------------------------------------------------
    #[Meteorology]-----------------------------------------------------------------
    replaceInConfig("North Coordinate 1",(output[1]-float(metadata['south']))*metersInDegree,config)
    replaceInConfig("East Coordinate  1",(output[0]-float(metadata['west']) )*metersInDegree,config)
    replaceInConfig("Elevation",metadata['min'],config)
    #[Soils]-----------------------------------------------------------------------
    #[Vegetation]------------------------------------------------------------------
    #[Output]----------------------------------------------------------------------
    replaceInConfig("North Coordinate         1",(output[1]-float(metadata['south']))*metersInDegree,config)
    replaceInConfig("East Coordinate          1",(output[0]-float(metadata['west']))*metersInDegree,config)
    replaceInConfig("Name                     1","Gauge station",config)
    replaceInConfig("State Date               1", getStrDate(endDate), config)
    # Saving the Config file again
    if not os.path.exists(path + '\\Configuration.txt'):
        numpy.savetxt(path+'\\Configuration.txt', config, fmt=["%s"], delimiter='=')

def replaceInConfig(rowToReplace, newResult, config):
    for i in range(0,len(config)):
        row = config[i][0].split('=')
        if rowToReplace in  row[0]:
            row[1] = " "+str(newResult)
            config[i][0] = row[0]+"="+row[1]
            i=len(config)

def createStateMap(name, startDate, path, numberOfmaps, metadata):
    myPath = os.path.dirname(os.path.abspath(__file__))
    rows = int(metadata['rows'])
    cols = int(metadata['cols'])
    north = float(metadata['north'])
    south = float(metadata['south'])
    east = float(metadata['east'])
    west = float(metadata['west'])
    # Create matrix of zeros
    stateMap = numpy.zeros((rows*numberOfmaps,cols))
    if name=="Soil": #10 Layers
        defaults = [0.3541, 0.2919, 0.2884, 0.2872, -4.9675, 0.178, 1.363, 3.183, 0.0, 0.0]
        for L in range(0,10):
            for row in range(L*rows,(L+1)*rows):
                for col in range(0,cols):
                    stateMap[row][col]=defaults[L]
    numpy.savetxt(path+'\\state\\'+name+startDate, stateMap, delimiter='\t')
    grass.run_command(myPath+'\\r.in.text.bat', output="B"+name+"Sate", path=path+'\\state\\'+name+startDate, north=north, south=north-(north-south)*numberOfmaps, east=east, west=west, overwrite=True, quiet=False)
    #print "name: %s\t rows: %s\t cols: %s\t numberOfmaps: %s\t"%(name, rows, cols, numberOfmaps)
    os.remove(path+'\\state\\'+name+startDate)
    if not os.path.exists(path+'\\state\\'+name+".State."+startDate+'.bin'):
        Module('r.out.bin', input="B"+name+"Sate", output=path+'\\state\\'+name+".State."+startDate+'.bin', bytes=4, quiet=True)
    Module('g.remove', type='raster', f=True, name="B"+name+"Sate", quiet=True)
    #return stateMap

# Creates the surface routing file using:
# shapeStreamAreas: A vector map with a polygon in each cell where there is a stream
# rasterWatershed: A raster map with the watershed MASK
def createSurfaceRouting(shapeStreamAreas, rasterWatershed, path, metadata):
    vectorWatershedPoints = rasterWatershed
    Module('r.to.vect', input=rasterWatershed, output=vectorWatershedPoints, type='point', overwrite=True, quiet=True)
    Module('v.db.addcolumn', map=vectorWatershedPoints, columns='x double precision')
    Module('v.db.addcolumn', map=vectorWatershedPoints, columns='y double precision')
    grass.read_command('v.distance', from_=vectorWatershedPoints, from_type='point', to=shapeStreamAreas, to_type='centroid', upload=['to_x','to_y'], column=['x','y'], quiet=True)
    tableCoord = convertSelectTableToTable(grass.read_command('v.out.ascii', input=vectorWatershedPoints, type='point', columns=['x','y'], format='point', quiet=True),'|')
    ImpervList = []
    for row in tableCoord:
        fromRow = int((float(metadata['north'])-row[1])/float(metadata['nsres']))
        fromCol = int((row[0]-float(metadata['west']))/float(metadata['ewres']))
        toRow = int((float(metadata['north'])-row[4])/float(metadata['nsres']))
        toCol = int((row[3]-float(metadata['west']))/float(metadata['ewres']))
        ImpervList.append([fromRow, fromCol,toRow,toCol])
    if not os.path.exists(path+'\\input\\surface_routing.txt'):
        numpy.savetxt(path+'\\input\\surface_routing.txt', ImpervList, fmt="%s", delimiter='\t')
    Module('g.remove', type='vector', f=True, name=[vectorWatershedPoints,shapeStreamAreas+'Points'], quiet=True)

#https://github.com/UW-Hydro/DHSVM/blob/master/processing_scripts/find_nearest_channel_bin.c
def formatFlowDirection(flowDirectionMap):
    #flowDirectionMapName = flowDirectionMap.split("@")[0]
    #Filling the new raster map with the data from the text file
    Module('r.mapcalc', expression=flowDirectionMap+'n =2^(8-abs('+flowDirectionMap+'))', overwrite=True)
    return flowDirectionMap+"n"

#Transform a table in a ("Text",val) format into a dictionary
def fromTableToDictionary(table):
    dictionary = {}
    for row in table:
        dictionary[row[0]]=row[1] 
    return dictionary
    
def getStrDate(date):
    #Taking the values of the "date" variable
    actualYear=str(date.year)
    actualMonth=[str(date.month), "0"+str(date.month)][len(str(date.month))==1]
    actualDay=[str(date.day), "0"+str(date.day)][len(str(date.day))==1]
    actualHour=[str(date.hour), "0"+str(date.hour)][len(str(date.hour))==1]
    actualMinute=[str(date.minute), "0"+str(date.minute)][len(str(date.minute))==1]
    actualSecond=[str(date.second), "0"+str(date.second)][len(str(date.second))==1]
    
    return actualMonth+"/"+actualDay+"/"+actualYear+"-"+actualHour

def getKey(item):
    return item[0]
    
def getKey2(item):
    return item[2]


def convertSelectTableToTable(SelectTable, char):
    SelectTable = SelectTable.replace('\r', '')
    table = SelectTable.split('\n')
    del table[-1]
    # del table[0]
    for i in range(0, len(table)):
        table[i] = table[i].split(char)
        for j in range(0, len(table[i])):
            if is_number(table[i][j]):
                table[i][j] = float(table[i][j])
    return table

def verifyInputs():
        return 0

class add_paths():
    def __init__(self, pathList):
        self.pathList = pathList

    def __enter__(self):
        import sys
        for path in self.pathList:
            sys.path.insert(1, path)

    def __exit__(self, exc_type, exc_value, traceback):
        import sys
        for path in self.pathList:
            sys.path.remove(path)
         

#Finds an ID in an ordered list using a binary search
def binarySearch(orderedList, columnId, idRequested, columnRequested):
    iterations = 0
    answer = 0
    idL = 0
    idU = len(orderedList)-1
    idR = -1
    while answer==0 or iterations<30:
        #grass.message("Looking for: "+str(idRequested)+" iteration "+str(iterations))
        oldIdR = idR
        iterations = iterations+1
        idR = int((idL+idU)*0.5)
        if oldIdR == idR: idR = idU
        if idRequested<orderedList[idR][columnId]:
            idU = idR
        elif idRequested>orderedList[idR][columnId]:
            idL = idR
        elif idRequested==orderedList[idR][columnId]:
            answer = orderedList[idR][columnRequested]
            break
    return answer

def is_number(s):
    try:
        complex(s) # for int, long, float and complex
    except ValueError:
        return False
    return True

def computeResolutionInMeters(meanLatitude):
    oneDegree = math.pi/180
    EarthRadius = 6371000
    return EarthRadius*oneDegree*math.cos(meanLatitude*math.pi/180)
