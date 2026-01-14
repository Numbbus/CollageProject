import uuid
import ast
import numpy as np
from datetime import datetime
import cv2
import os
import tkinter as tk


totalElapsedTime = datetime.now()

# ====================== CONFIG ======================
INPUT_IMAGE = "helldiver.png"
INPUT_IMAGES_PATH = "images"
#SCALE = 100 # How many images per pixel of the input image
RESOLUTION = 2 # Size of each tile
useWebcam = True
webcamResolution = (640,  480)
# ====================================================

def showWebcam():
    # Open the default webcam (0). Try 1 or 2 if you have multiple cameras.
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, webcamResolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, webcamResolution[1])
    cap.set(cv2.CAP_PROP_FPS, 30)

    while True:
        ret, frame = cap.read()

        if not ret or frame is None or frame.size == 0:
            continue

        print(f"Frame size: {frame.shape[0]}, {frame.shape[1]}")

        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.imshow("Collage Webcam", createCollage(frame))


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cap.release()
    cv2.destroyAllWindows()

def quantize(rgb):
    r, g, b = rgb
    return(r >> 3, g >> 3, b >> 3)

def progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    """
    Displays a progress bar in the terminal.
    iteration: current iteration
    total: total iterations
    prefix: prefix string
    suffix: suffix string
    length: character length of the bar
    fill: character used to fill the progress bar
    """
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='', flush=True)

def cacheInputImages(path = INPUT_IMAGES_PATH):
    cache = []
    counter=0
    for filename in os.listdir(path):
        if filename.lower().endswith(".png"):
            imgPath = os.path.join(path, f"picsumImg{counter}.png")
            cache.append(cv2.imread(imgPath))
            counter+=1
    
    return cache

def computeAvgRGB(img):

    # Get average across both axises and all three channels
    average_color = np.mean(img, axis=(0, 1))

    # Assign each channel to the color 


    try:
        r, g, b = int(average_color[0]), int(average_color[1]), int(average_color[2])
    except:
        return 0,0,0
    return(r, g, b)

def spliceInputImage(img, res):

    splicedImage = []
    splicedCoords = []

    for y in range(int(img.shape[0]/res)):
        for x in range(int(img.shape[1]/res)):

            # Crop image and convert and append

            startY = y*res
            endY = y*res+res

            startX = x*res
            endX = x*res+res

            splicedImage.append(img[startY:endY, startX:endX])

            splicedCoords.append((x*res, y*res))
            
    return splicedImage, splicedCoords

def createCollage(img):
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    
    completedNum = 0

    collageStart = datetime.now()

    height = img.shape[1]
    width = img.shape[0]

    outputWidth = int(height/RESOLUTION)*RESOLUTION
    outputHeight = int(width/RESOLUTION)*RESOLUTION

    output_img = np.zeros((outputHeight, outputWidth, 3), np.uint8)

    splicedImageArr, splicedImageCoordsArr = spliceInputImage(img, RESOLUTION)

    for i in range(len(splicedImageArr)):

        # Get its avg rgb
        croppedImageAverageRgbValues = computeAvgRGB(splicedImageArr[i])

        selectedImg = cahcedImages[LUT[quantize(croppedImageAverageRgbValues)]]


        
        selectedImg = cv2.resize(selectedImg, (RESOLUTION, RESOLUTION))

        # Paste it to the output
        #output_img.paste(selectedImg, splicedImageCoordsArr[i])
        yOffset = splicedImageCoordsArr[i][1]
        xOffset = splicedImageCoordsArr[i][0]


        #exit()

        #roi = output_img[yOffset:yOffset+RESOLUTION, xOffset:xOffset+RESOLUTION]
        output_img[yOffset:yOffset+RESOLUTION, xOffset:xOffset+RESOLUTION] = selectedImg
        
        # Increment how many sections completed
        completedNum+=1

        # Update the progress bar
        progress_bar(completedNum, total, 'Generating:', 'Complete')     

    elapsedSeconds = (datetime.now() - collageStart).total_seconds()

    print(f"\n✅ Time To Generate: {elapsedSeconds:.2f} seconds") 

    return output_img  



def createCollageForWebServer(img, res, LUT, cachedImages, path=None):
    
    """ Intended for use with the web server"""

    if(res == 0 or img is None):
        return "static/images/error.png"

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    height = img.shape[1]
    width = img.shape[0]

    outputWidth = int(height/res)*res
    outputHeight = int(width/res)*res

    output_img = np.zeros((outputHeight, outputWidth, 3), np.uint8)

    splicedImageArr, splicedImageCoordsArr = spliceInputImage(img, res)

    for i in range(len(splicedImageArr)):

        # Get its avg rgb
        croppedImageAverageRgbValues = computeAvgRGB(splicedImageArr[i])

        selectedImg = cachedImages[LUT[quantize(croppedImageAverageRgbValues)]]

        selectedImg = cv2.resize(selectedImg, (res, res))

        # Paste it to the output
        yOffset = splicedImageCoordsArr[i][1]
        xOffset = splicedImageCoordsArr[i][0]

        output_img[yOffset:yOffset+res, xOffset:xOffset+res] = selectedImg

    if(path is None):
        savePath = f"static/processed/{uuid.uuid4().hex}.png"
        cv2.imwrite(savePath, output_img)
    else:
        savePath = path+f"{uuid.uuid4().hex}.png"
        cv2.imwrite(savePath, output_img)

    return savePath 

def createCollageForDOOM(img, res, LUT, cachedImages):
    
    """ Intended for use with DOOM_Collage_Game.py"""

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    height = img.shape[1]
    width = img.shape[0]

    outputWidth = int(height/res)*res
    outputHeight = int(width/res)*res

    output_img = np.zeros((outputHeight, outputWidth, 3), np.uint8)

    splicedImageArr, splicedImageCoordsArr = spliceInputImage(img, res)

    for i in range(len(splicedImageArr)):

        # Get its avg rgb
        croppedImageAverageRgbValues = computeAvgRGB(splicedImageArr[i])

        selectedImg = cachedImages[LUT[quantize(croppedImageAverageRgbValues)]]

        selectedImg = cv2.resize(selectedImg, (res, res))

        # Paste it to the output
        yOffset = splicedImageCoordsArr[i][1]
        xOffset = splicedImageCoordsArr[i][0]

        output_img[yOffset:yOffset+res, xOffset:xOffset+res] = selectedImg

    return output_img 

if __name__ == "__main__":

    inputImg = cv2.imread(INPUT_IMAGE)
        
    cahcedImages = cacheInputImages()

    LUT = np.load("lut.npy")

    if(useWebcam):
        total = (int(inputImg.shape[1]/RESOLUTION) * int(inputImg.shape[0]/RESOLUTION))
        showWebcam()
    else:

        total = (int(inputImg.shape[1]/RESOLUTION) * int(inputImg.shape[0]/RESOLUTION)) 

        finalImg = createCollage(inputImg)

        savePath = f"{INPUT_IMAGE.strip('.png')}-collage.png"

        cv2.imwrite(savePath, finalImg)

        cv2.imshow("Collage", finalImg)
        
        elapsedSeconds = (datetime.now() - totalElapsedTime).total_seconds()
        print(f"\n✅ Total Elapsed Time: {elapsedSeconds:.2f} seconds") 

        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break



