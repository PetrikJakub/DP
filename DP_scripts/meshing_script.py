import sys
import os, os.path
import shutil
import math
import time
import re
from pathlib import Path

dirname = os.path.dirname(os.path.abspath(__file__))  # Absolute path of this file

verboseLevel = "\"" + "error" + "\""  # detail of the logs (error, info, etc)

folder_number = 1
folder_prefix = "run"
def SilentMkdir(theDir):  # function to create a directory
    try:
        os.mkdir(theDir)
    except:
        pass
    return 0


def run_1_cameraInit(binPath, baseDir, imgDir):
    taskFolder = "/1_CameraInit"
    SilentMkdir(baseDir + taskFolder)

    print("----------------------- 1/9 CAMERA INITIALIZATION -----------------------")

    imageFolder = "\"" + imgDir + "\""
    sensorDatabase = "\"" + str(Path(
        binPath).parent) + "\\share\\aliceVision\\cameraSensors.db" "\""  # Path to the sensors database, might change in later versions of meshrrom

    output = "\"" + baseDir + taskFolder + "/cameraInit.sfm" + "\""

    cmdLine = binPath + "\\aliceVision_cameraInit.exe"
    cmdLine += " --imageFolder {0} --sensorDatabase {1} --output {2}".format(
        imageFolder, sensorDatabase, output)

    cmdLine += " --defaultFieldOfView 45"
    cmdLine += " --allowSingleView 1"
    cmdLine += " --verboseLevel " + verboseLevel

    print(cmdLine)
    os.system(cmdLine)

    return 0


def run_2_featureExtraction(binPath, baseDir, numberOfImages, imagesPerGroup=40):
    taskFolder = "/2_FeatureExtraction"
    SilentMkdir(baseDir + taskFolder)

    print("----------------------- 2/9 FEATURE EXTRACTION -----------------------")

    _input = "\"" + baseDir + "/1_CameraInit/cameraInit.sfm" + "\""
    output = "\"" + baseDir + taskFolder + "\""

    cmdLine = binPath + "\\aliceVision_featureExtraction"
    cmdLine += " --input {0} --output {1}".format(_input, output)
    cmdLine += " --forceCpuExtraction 1"

    # when there are more than 40 images, it is good to send them in groups
    if (numberOfImages > imagesPerGroup):
        numberOfGroups = int(math.ceil(numberOfImages / imagesPerGroup))
        for i in range(numberOfGroups):
            cmd = cmdLine + " --rangeStart {} --rangeSize {} ".format(i * imagesPerGroup, imagesPerGroup)
            print("------- group {} / {} --------".format(i + 1, numberOfGroups))
            print(cmd)
            os.system(cmd)

    else:
        print(cmdLine)
        os.system(cmdLine)


def run_3_imageMatching(binPath, baseDir):
    taskFolder = "/3_ImageMatching"
    SilentMkdir(baseDir + taskFolder)

    print("----------------------- 3/9 IMAGE MATCHING -----------------------")

    _input = "\"" + baseDir + "/1_CameraInit/cameraInit.sfm" + "\""
    featuresFolders = "\"" + baseDir + "/2_FeatureExtraction" + "\""
    output = "\"" + baseDir + taskFolder + "/imageMatches.txt" + "\""

    cmdLine = binPath + "\\aliceVision_imageMatching.exe"
    cmdLine += " --input {0} --featuresFolders {1} --output {2}".format(
        _input, featuresFolders, output)

    cmdLine += " --tree " + "\"" + str(Path(binPath).parent) + "/share/aliceVision/vlfeat_K80L3.SIFT.tree\""
    cmdLine += " --verboseLevel " + verboseLevel

    print(cmdLine)
    os.system(cmdLine)


def run_4_featureMatching(binPath, baseDir, numberOfImages, imagesPerGroup=20):
    taskFolder = "/4_featureMatching"
    SilentMkdir(baseDir + taskFolder)

    print("----------------------- 4/9 FEATURE MATCHING -----------------------")

    _input = "\"" + baseDir + "/1_CameraInit/cameraInit.sfm" + "\""
    output = "\"" + baseDir + taskFolder + "\""
    featuresFolders = "\"" + baseDir + "/2_FeatureExtraction" + "\""
    imagePairsList = "\"" + baseDir + "/3_ImageMatching/imageMatches.txt" + "\""

    cmdLine = binPath + "\\aliceVision_featureMatching.exe"
    cmdLine += " --input {0} --featuresFolders {1} --output {2} --imagePairsList {3}".format(
        _input, featuresFolders, output, imagePairsList)

    cmdLine += " --knownPosesGeometricErrorMax 5"
    cmdLine += " --verboseLevel " + verboseLevel

    cmdLine += " --describerTypes sift --photometricMatchingMethod ANN_L2 --geometricEstimator acransac --geometricFilterType fundamental_matrix --distanceRatio 0.8"
    cmdLine += " --maxIteration 2048 --geometricError 0.0 --maxMatches 0"
    cmdLine += " --savePutativeMatches False --guidedMatching False --matchFromKnownCameraPoses False --exportDebugFiles True"

    # when there are more than 20 images, it is good to send them in groups
    if (numberOfImages > imagesPerGroup):
        numberOfGroups = math.ceil(numberOfImages / imagesPerGroup)
        for i in range(numberOfGroups):
            cmd = cmdLine + " --rangeStart {} --rangeSize {} ".format(i * imagesPerGroup, imagesPerGroup)
            print("------- group {} / {} --------".format(i, numberOfGroups))
            print(cmd)
            os.system(cmd)

    else:
        print(cmdLine)
        os.system(cmdLine)


def run_5_structureFromMotion(binPath, baseDir):
    taskFolder = "/5_structureFromMotion"
    SilentMkdir(baseDir + taskFolder)

    print("----------------------- 5/9 STRUCTURE FROM MOTION -----------------------")

    _input = "\"" + baseDir + "/1_CameraInit/cameraInit.sfm" + "\""
    output = "\"" + baseDir + taskFolder + "/sfm.abc" + "\" "
    outputViewsAndPoses = "\"" + baseDir + taskFolder + "/cameras.sfm" + "\""
    extraInfoFolder = "\"" + baseDir + taskFolder + "\""
    featuresFolders = "\"" + baseDir + "/2_FeatureExtraction" + "\""
    matchesFolders = "\"" + baseDir + "/4_featureMatching" + "\""

    cmdLine = binPath + "\\aliceVision_incrementalSfm.exe"
    cmdLine += " --input {0} --output {1} --outputViewsAndPoses {2} --extraInfoFolder {3} --featuresFolders {4} --matchesFolders {5}".format(
        _input, output, outputViewsAndPoses, extraInfoFolder, featuresFolders, matchesFolders)

    cmdLine += " --verboseLevel " + verboseLevel

    print(cmdLine)
    os.system(cmdLine)


def run_6_prepareDenseScene(binPath, baseDir):
    taskFolder = "/6_PrepareDenseScene"
    SilentMkdir(baseDir + taskFolder)

    print("----------------------- 6/9 PREPARE DENSE SCENE -----------------------")
    _input = "\"" + baseDir + "/5_structureFromMotion/sfm.abc" + "\""
    output = "\"" + baseDir + taskFolder + "\" "

    cmdLine = binPath + "\\aliceVision_prepareDenseScene.exe"
    cmdLine += " --input {0}  --output {1} ".format(_input, output)

    cmdLine += " --verboseLevel " + verboseLevel

    print(cmdLine)
    os.system(cmdLine)


def run_7_depthMap(binPath, baseDir, numberOfImages, groupSize=6, downscale=2):
    taskFolder = "/7_DepthMap"
    SilentMkdir(baseDir + taskFolder)

    print("----------------------- 7/9 DEPTH MAP -----------------------")
    _input = "\"" + baseDir + "/5_structureFromMotion/sfm.abc" + "\""
    output = "\"" + baseDir + taskFolder + "\""
    imagesFolder = "\"" + baseDir + "/6_PrepareDenseScene" + "\""

    cmdLine = binPath + "\\aliceVision_depthMapEstimation.exe"
    cmdLine += " --input {0}  --output {1} --imagesFolder {2}".format(
        _input, output, imagesFolder)

    cmdLine += " --verboseLevel " + verboseLevel
    cmdLine += " --downscale " + str(downscale)

    numberOfBatches = int(math.ceil(numberOfImages / groupSize))

    for i in range(numberOfBatches):
        groupStart = groupSize * i
        currentGroupSize = min(groupSize, numberOfImages - groupStart)
        if groupSize > 1:
            print("DepthMap Group {} of {} : {} to {}".format(i, numberOfBatches, groupStart, currentGroupSize))
            cmd = cmdLine + (" --rangeStart {} --rangeSize {}".format(str(groupStart), str(groupSize)))
            print(cmd)
            os.system(cmd)


def run_8_depthMapFilter(binPath, baseDir):
    taskFolder = "/8_DepthMapFilter"
    SilentMkdir(baseDir + taskFolder)

    print("----------------------- 8/9 DEPTH MAP FILTER-----------------------")
    _input = "\"" + baseDir + "/5_structureFromMotion/sfm.abc" + "\""
    output = "\"" + baseDir + taskFolder + "\""
    depthMapsFolder = "\"" + baseDir + "/7_DepthMap" + "\""

    cmdLine = binPath + "\\aliceVision_depthMapFiltering.exe"
    cmdLine += " --input {0}  --output {1} --depthMapsFolder {2}".format(
        _input, output, depthMapsFolder)

    cmdLine += " --verboseLevel " + verboseLevel

    print(cmdLine)
    os.system(cmdLine)


def run_9_meshing(binPath, baseDir, maxInputPoints=50000000, maxPoints=1000000):
    taskFolder = "/9_Meshing"
    SilentMkdir(baseDir + taskFolder)

    print("----------------------- 9/9 MESHING -----------------------")
    _input = "\"" + baseDir + "/5_structureFromMotion/sfm.abc" + "\""
    output = "\"" + baseDir + taskFolder + "/densePointCloud.abc" "\""
    outputMesh = "\"" + baseDir + taskFolder + "/mesh.obj" + "\""
    depthMapsFolder = "\"" + baseDir + "/8_DepthMapFilter" + "\""

    cmdLine = binPath + "\\aliceVision_meshing.exe"
    cmdLine += " --input {0}  --output {1} --outputMesh {2} --depthMapsFolder {3} ".format(
        _input, output, outputMesh, depthMapsFolder)

    cmdLine += " --maxInputPoints " + str(maxInputPoints)
    cmdLine += " --maxPoints " + str(maxPoints)
    cmdLine += " --verboseLevel " + verboseLevel

    print(cmdLine)
    os.system(cmdLine)




def get_next_folder_number(base_path):
    folders = [folder for folder in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, folder)) and folder.startswith(folder_prefix)]
    if not folders:
        return 1

    # Find the last number and add one
    last_number = max([int(re.search(rf'{folder_prefix}(\d+)', folder).group(1)) for folder in folders], default=0)
    return last_number + 1


def meshing_proces():
    global folder_number  # Use the global variable
    folder_number = get_next_folder_number('builds')
    # Folder name for each run
    run_folder = f'{folder_prefix}{folder_number}'
    run_path = os.path.join('builds', run_folder)

    # If the folder doesn't exist, create it
    if not os.path.exists(run_path):
        os.makedirs(run_path)

    # Pass the arguments of the function as parameters in the command line code
    binPath = "C:\\Users\\kubip\\Desktop\\Meshroom-2023.3.0\\aliceVision\\bin"  ##  --> path of the binary files from Meshroom
    baseDir = f"{run_path}"  ##  --> name of the Folder containing the process (a new folder will be created)
    imgDir = f"pictures/{run_folder}"  ##  --> Folder containing the images

    numberOfImages = len([name for name in os.listdir(imgDir) if
                          os.path.isfile(os.path.join(imgDir, name))])  ## number of files in the folder

    SilentMkdir(baseDir)

    startTime = time.time()

    run_1_cameraInit(binPath, baseDir, imgDir)
    run_2_featureExtraction(binPath, baseDir, numberOfImages)
    run_3_imageMatching(binPath, baseDir)
    run_4_featureMatching(binPath, baseDir, numberOfImages)
    run_5_structureFromMotion(binPath, baseDir)
    run_6_prepareDenseScene(binPath, baseDir)
    run_7_depthMap(binPath, baseDir, numberOfImages)
    run_8_depthMapFilter(binPath, baseDir)
    run_9_meshing(binPath, baseDir)


    print("-------------------------------- DONE ----------------------")
    endTime = time.time()
    hours, rem = divmod(endTime - startTime, 3600)
    minutes, seconds = divmod(rem, 60)
    print("time elapsed: " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))


