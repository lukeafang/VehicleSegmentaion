#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 16:12:43 2018

@author: lukefang

segment vehicles and count the number of vehicles from the input video

"""
from argparse import ArgumentParser
import os
from method import segmentation
    
def initialParameters(args):
    """
    grab input params
    """
    params = {}
    
    #get vedio file path
    #rootPath = os.path.dirname(__file__)
    rootPath = os.getcwd()
    if args.file_path is None:
        #use default path
        params['filePath'] = os.path.join(rootPath, 'data', 'T1.mp4')
    else:
        params['filePath'] = os.path.join(rootPath, args.file_path)   
             
    if args.updateRatio is None:
        params['BKUpdateRatio'] = 1
    else:
        temp = float(args.updateRatio);
        if temp < 0:
            temp = 0
        if temp > 10:
            temp = 10
        params['BKUpdateRatio'] = temp / 10  
        
    if args.updateFrequence is None:
        params['BKUpdateFrequence'] = 2
    else:   
        temp = int(args.updateFrequence);
        if temp < 0 :
            temp = 0
        params['BKUpdateFrequence'] = temp
        
    if args.scaleImage is None:
        params['scaleImage'] = False
    else:
        temp = int(args.scaleImage)
        if temp == 1:
            params['scaleImage'] = True
        else:
            params['scaleImage'] = False
                    
    return params

if __name__ == '__main__':
    """
    main function
    mode1: update bk by frame diff
    mode2: update bk by components
    """
    parser = ArgumentParser(description="vehicle segmentation")
    
    parser.add_argument("BackgroundUpdateMode", type=str, choices=['mode1','mode2'], help="different background update mode")
    parser.add_argument('-p', '--file_path', type=str, help='path of input video file')
    
    parser.add_argument('-u', '--updateRatio', type=str, help='updateRatio of pixels in background Image(1-10)')
    parser.add_argument('-uc', '--updateFrequence', type=str, help='update frequence of background Image')  
    parser.add_argument('-s', '--scaleImage', type=str, help='If scale image or not(0:false, 1:true)')      
    args = parser.parse_args()    
    
    params = initialParameters(args)
    #print(params['filePath'])
    
    filePath = params['filePath']
    #check file exist or not
    if os.path.exists(filePath):
        mode = str(args.BackgroundUpdateMode)
        segmentation(filePath, mode, params)       
    else:
        print('Error. File does not exist.')

        