#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 20:47:45 2018

@author: lukefang
"""
import os
import cv2
import numpy as np

def shadowDectection(BGRImg):
    #shadowMask = np.zeros((row, col)
    
    #RGB -> Ycbcr
    img_YCB = cv2.cvtColor(BGRImg, cv2.COLOR_BGR2YCrCb)
    y = img_YCB[:,:,0]
    #cr = img_YCB[:,:,1]
    #cb = img_YCB[:,:,2]
    
    averageY = np.mean(y) - 40
    shadowMask = y < averageY
    return shadowMask

def updateBKImage(OldBKImage, bgMask, Img, updateRatio):
    """
    update Background Image by new input image and bgmask
    """
    row, col = OldBKImage.shape
    newBKImage = (((1-updateRatio) * OldBKImage) + (updateRatio * Img)) * bgMask
    newBKImage[newBKImage == 0] = OldBKImage[newBKImage == 0]
    return newBKImage

def updateBKMask_mode1(frame_diff):
    """
    update background mask by frame different 
    """
    bgMask = np.ones((frame_diff.shape)) 
    kernel = np.ones((5,5), np.uint8)
    frame_diff = cv2.erode(frame_diff, kernel, iterations = 1)
    bgMask[frame_diff != 0] = 0
    return bgMask

def updateBKMask_mode2(labels, stats):
    """
    update background mask by component
    """
    bgMask = np.ones((labels.shape))  
    kernel = np.ones((5,5), np.uint8)
    labels = cv2.erode(labels, kernel, iterations = 1)    
    bgMask[labels != 0] = 0
    return bgMask

def filterComponents(labels, stats, params):
    """
    filter components, remove noice components
    """
    row, col = labels.shape
    newLabels = np.zeros((row, col))
    newStats = []
    
    minArea = 500
    index = 0
    for i in range(len(stats)):
        stat = stats[i, :]
        if i == 0:
            index = index + 1
            newStats.append(stat)          
            continue
        
        #omit noise component
        if stat[cv2.CC_STAT_AREA] <= minArea:
            continue
        
        #consider shape of component
        height = stat[cv2.CC_STAT_HEIGHT]
        width = stat[cv2.CC_STAT_WIDTH]
        if height > width:
            continue
        if float(width/height) > 3:
            continue
        
        #put label index into labels
        newLabels[labels == i] = index
        index = index + 1
        newStats.append(stat)
        
    newStats = np.array(newStats)
    #sortedIndices = np.argsort(-newStats[:,cv2.CC_STAT_AREA]) 
                
    return newLabels, newStats 

def outputImages(saveImageIndex, frame, frame_gray, bgImg_show, bkMask_show, fgImg, resultFrame):
    #save frame
    fileName = "frame_%04d.png" % saveImageIndex
    filePath = os.path.join('output', fileName)   
    cv2.imwrite(filePath, frame)
    #save frame_Gray
    fileName = "frameGray_%04d.png" % saveImageIndex
    filePath = os.path.join('output', fileName)   
    cv2.imwrite(filePath, frame_gray)    
    #save bgImage
    fileName = "bg_%04d.png" % saveImageIndex
    filePath = os.path.join('output', fileName)   
    cv2.imwrite(filePath, bgImg_show)
    #save bg Mask
    fileName = "bgMask_%04d.png" % saveImageIndex
    filePath = os.path.join('output', fileName)   
    cv2.imwrite(filePath, bkMask_show)
    #save fg
    fileName = "fg_%04d.png" % saveImageIndex
    filePath = os.path.join('output', fileName)   
    cv2.imwrite(filePath, fgImg) 
    #save result frame
    fileName = "result_%04d.png" % saveImageIndex
    filePath = os.path.join('output', fileName)   
    cv2.imwrite(filePath, resultFrame) 
    

def segmentation(filePath, mode, params):
    """
    segment vehicle from video
    filePath: video file path
    mode: background mask update mode, 
            mode1 : update by frame different
            mode2 : update by founded components
    params: input params
    """
    #create windows and set the position
    cv2.namedWindow('result', cv2.WINDOW_NORMAL)
    cv2.moveWindow('result',100,100)    
    cv2.namedWindow('background', cv2.WINDOW_NORMAL)
    cv2.moveWindow('background',550,100)
    cv2.namedWindow('backgroundMask', cv2.WINDOW_NORMAL)
    cv2.moveWindow('backgroundMask',1000,100)
    cv2.namedWindow('foreground', cv2.WINDOW_NORMAL)
    cv2.moveWindow('foreground',100,500)   
    
    #initial parameters
    saveImageIndex = 0
    isBackgroundInitialized = False
    
    cap = cv2.VideoCapture(filePath)
    ret, frame = cap.read()
    
    row_Row, col_Row, channel = frame.shape
    row = row_Row
    col = col_Row
    if params['scaleImage'] == True:
        #resize all frame to (320,xxx)
        row = 320;
        ratio = row / row_Row;
        col = int(col_Row * ratio)
    #initial bg image
    bgCycleCount = 0
    bgImg = np.zeros((row,col))
    bgMask = np.ones((row,col))
    
    
    
    while True:
        if params['scaleImage'] == True:
            #resize original frame
            frame = cv2.resize(frame, (col, row), interpolation = cv2.INTER_AREA)
        
        #RGB -> Gray
        frame_temp = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #smooth image
        frame_gray = cv2.blur(frame_temp, (5, 5))
        
        #initial bk image
        if isBackgroundInitialized == False:
            isBackgroundInitialized = True
            bgImg = updateBKImage(bgImg, bgMask, frame_gray, 1)
            pastFrame = frame_gray
        
        #background subtraction
        tempImg_1 = np.uint8(np.abs(frame_gray - bgImg))
        threshold = 20
        ret,tempImg_2 = cv2.threshold(tempImg_1, threshold, 254, cv2.THRESH_BINARY)
        
        #morphology operation, reduce noise, connect blocks
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        tempImg_1 = cv2.morphologyEx(tempImg_2, cv2.MORPH_OPEN, kernel)
        kernel_Dilation = np.ones((3,3), np.uint8)
        fgImg = cv2.dilate(tempImg_1, kernel_Dilation, iterations = 1)
        cv2.imshow('foreground', fgImg)
        
        #find connected component
        #use 8 for connectivity type (4 or 8)  
        connectivity = 8 
        output = cv2.connectedComponentsWithStats(fgImg, connectivity, cv2.CV_32S)
        #label matrix
        labels = output[1]
        #stat matrix
        stats = output[2]
        
        #reduce noise components
        labels, stats = filterComponents(labels, stats, params)
        nComponent = stats.shape[0] - 1
        
        #mode = "mode3"
        #update background mask and image
        ratio = params['BKUpdateRatio']
        freq = params['BKUpdateFrequence']
        if bgCycleCount >= freq:
            bgCycleCount = 0           
            if mode == "mode1":
                frame_diff = np.uint8(np.abs(frame_gray - pastFrame))
                bgMask = updateBKMask_mode1(frame_diff)
                pastFrame = frame_gray
            elif mode == "mode2":
                bgMask = updateBKMask_mode2(labels, stats)
            else:
                bgMask = np.ones((row,col))
            bgImg = updateBKImage(bgImg, bgMask, frame_gray, ratio)
        else:
            bgCycleCount = bgCycleCount + 1
            
        #show bkMaskImage
        bkMask_show = np.uint8(bgMask * 254)
        cv2.imshow('backgroundMask', bkMask_show)
        #show bkImage
        bgImg_show = np.uint8(bgImg)
        cv2.imshow('background', bgImg_show) 
                
        
        #resultFrame = frame
        resultFrame = cv2.copyMakeBorder(frame,0,0,0,0,cv2.BORDER_REPLICATE)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = 'Car: ' + str(nComponent)
        cv2.putText(resultFrame, text, (10,50), font, 2, (0,0,255), 3)
        
        #draw rectengle
        if nComponent >= 1:
            #colors = [(255,0,0), (0,255,0), (0,0,255), (127,127,0)]
            color = (0,255,0)
            for index in range(len(stats)):
                if index == 0:
                    continue
                stat = stats[index,:]
                LT = (stat[0], stat[1])
                RB = ((LT[0]+stat[2]), (LT[1]+stat[3]))
                cv2.rectangle(resultFrame, LT, RB, color, 3)
        #show frame
        cv2.imshow('result', resultFrame)

        key = cv2.waitKey(1)
        if key == ord('q'):#terminate program
            break
        if key == ord('s'):#save image
            outputImages(saveImageIndex, frame, frame_gray, bgImg_show, bkMask_show, fgImg, resultFrame)
            saveImageIndex = saveImageIndex + 1
        
        #No more new frame, exit loop
        if ret == False:
            break
        
        #grab next frame
        ret, frame = cap.read()
    
    cap.release()
    cv2.destroyAllWindows() 
    
    return True

