# -*- coding: utf-8 -*-
"""
author: Vu Tran
Lab 5
date: 03/15/2022
"""

import arcpy
from arcpy import env
import sys
import numpy as np
import time

env.workspace = r"C:\Users\tuanv\Desktop\GIS_Programing\Lab5\data"
sys.path[0]
env.overwriteOutput = 1
arcpy.CheckOutExtension("Spatial")

raster = 'nlcd06_lab5'
nlcd = arcpy.RasterToNumPyArray(raster)


#Part 1 Rectangle Window
ti = time.time()
def SumCal(condition1):
    '''
    condition1: the condition to extract a certain type of land cover
    '''
    nlcd = arcpy.RasterToNumPyArray(raster)
    feature = np.where(condition1,1,0)
    featureSum = np.zeros(feature.shape,dtype=float)
    for i in range(5,np.size(feature,1)-5):
        for j in range(4,np.size(feature,0)-4):
            winSum=0
            for ii in range(i-5,i+6):
                for jj in range(j-4,j+5):
                    winSum=winSum+feature[jj][ii]
            featureSum[j][i]=winSum
    return featureSum


def ConditionCal(condition2):
    '''
    condition2: the condition which satisfied the determined criteria 
    '''
    featureCondition = np.where(condition2,1,0)
    return featureCondition

def SumCalSlope(feature):
    '''
    input a slope array to calculate the slope sum
    '''
    featureSum = np.zeros(feature.shape,dtype=float)
    for i in range(5,np.size(feature,1)-5):
        for j in range(4,np.size(feature,0)-4):
            winSum=0
            for ii in range(i-5,i+6):
                for jj in range(j-4,j+5):
                    winSum=winSum+feature[jj][ii]
            featureSum[j][i]=winSum
    return featureSum


greencoverSum = SumCal((nlcd == 41)|(nlcd ==42)|(nlcd==43)|(nlcd==51)|(nlcd==52))
greencoverCondition = ConditionCal((greencoverSum/99) >0.3)

agricultureSum = SumCal((nlcd==81)|(nlcd==82))
agricultureCondition = ConditionCal((agricultureSum/99)<0.05)

waterSum = SumCal(nlcd==11)
waterCondition = ConditionCal(((waterSum/99)>0.05) & ((waterSum/99) <0.2))

lowintensitySum = SumCal((nlcd==21)|(nlcd ==22))
lowintensityCondition = ConditionCal((lowintensitySum/99) <0.2)

slopeRaster = arcpy.sa.Slope(raster)
slope = arcpy.RasterToNumPyArray(slopeRaster)
slopeSum = SumCalSlope(slope)
slopeCondition = ConditionCal((slopeSum/99)<8)

finalCondition1 = greencoverCondition+agricultureCondition+waterCondition+lowintensityCondition+slopeCondition
finalRaster1 = arcpy.NumPyArrayToRaster(finalCondition1)
finalRaster1.save('FinalRasterRect.tif')



valueList = []
with arcpy.da.SearchCursor('FinalRasterRect.tif','Count') as cursor:
    for row in cursor:
         valueList.append(row[0])
Time = (time.time() - ti)
print'This code takes ', Time,'seconds to run (Rectangular Window)'
print'There are',valueList[-1],'sites which satisfied the conditions'
print''


#Part2 Circular Window
ti2 = time.time()
dims = (11,9)
rectWindow = np.ones(dims)
radius = (((float(11)/2)**2) + ((float(9)/2)**2))**.5
maskDims = ((int(radius)*2) +1 , (int(radius)*2)+1)
mask = np.zeros(maskDims)
for i in range(0,np.size(mask,1)):
    for j in range(0,np.size(mask,0)):
        if (((int(radius)-j)**2)+(int(radius)-i)**2)**.5 <= radius:
            mask[j][i] = 1

def CalCir(num1,num2,num3,num4,num5):
    '''
    num1,num2,num3,num4,num5 are the NLCD raster values. 
    input the values, but if the values needed are less than 5, then input zero for the rest
    example (for water): CalCir(11,0,0,0,0)
    '''
    feature = np.zeros(nlcd.shape,dtype=float)
    for i in range(7,np.size(nlcd,1)-7):
        for j in range(7,np.size(nlcd,0)-7):
            feature[j][i] = (np.where((nlcd[j-7:j+8,i-7:i+8] == num1)|(nlcd[j-7:j+8,i-7:i+8] ==num2)|(nlcd[j-7:j+8,i-7:i+8]==num3)|(nlcd[j-7:j+8,i-7:i+8]==num4)|(nlcd[j-7:j+8,i-7:i+8]==num5),1,0)*mask).sum()
    return feature

def CalSlope(slopeArray):
    '''
    input a slope array to calculate average slope with circular window
    '''
    feature = np.zeros(slopeArray.shape,dtype=float)
    for i in range(7,np.size(slopeArray,1)-7):
        for j in range(7,np.size(slopeArray,0)-7):
            feature[j][i] = (slopeArray[j-7:j+8,i-7:i+8]*mask).sum()
    return feature

greencover = CalCir(41,42,43,51,52)
greencoverConditionCir = ConditionCal((greencover/225) >0.3)

agriculture = CalCir(81,82,0,0,0)
agricultureConditionCir = ConditionCal((agriculture/225) <0.05)

water = CalCir(11,0,0,0,0)
waterConditionCir = ConditionCal(((water/225)>0.05) & ((water/225) <0.2))

lowintensity = CalCir(21,22,0,0,0)
lowintensityConditionCir = ConditionCal((lowintensity/225) <0.2)

slopeCir = CalSlope(slope)
slopeConditionCir = ConditionCal((slopeCir/225)<8)


finalCondition2 = greencoverConditionCir+agricultureConditionCir+waterConditionCir+lowintensityConditionCir+slopeConditionCir
finalRaster2 = arcpy.NumPyArrayToRaster(finalCondition2)
finalRaster2.save('FinalRasterCir.tif')

valueList2 = []
with arcpy.da.SearchCursor('FinalRasterCir.tif','Count') as cursor:
    for row in cursor:
         valueList2.append(row[0])
        
        
Time2 = (time.time() - ti2)
print'This code takes ', Time2,'seconds to run (Circular Window)'
print'There are',valueList2[-1],'sites which satisfied the conditions'