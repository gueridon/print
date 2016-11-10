# -*-coding:utf-8 -*

# based on PRInt (Nicholas Bacuez, 2012)
from printPatternReader import *
import printConfig

import  sys, os, csv, pylab, math
import readline, glob


def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

######################################################################
##
#   tools for the menu(s)
#
def pause():
    programPause = raw_input("\n\tPress <ENTER> to continue...")

######################################################################
##
#   clean all previously generated graph
#
def cleanGraph():
    fileListClean = [ f for f in os.listdir(".") if f.endswith(".png") ]
    for f in fileListClean:
        os.remove(f)
    print "All graphs removed from directory."

######################################################################
##
#   MAIN MENU
#
def mainMenuContent():
    os.system('clear')
    print "\n\t## PRInt - MAIN MENU ##\n"
    print "\t[1] file mode"
    print "\t[2] folder mode"
    print "\t[3] batch mode"
    print "\t[4] remove graphs files"
    #print "\t[f] fast mode for testing"
    print "\t[5] exit PRInt"

def mainMenu():
    mainMenuChoice = ""
    while mainMenuChoice != "5":
        mainMenuContent()
        mainMenuChoice = raw_input("\n\t[choice] ")
        if mainMenuChoice == "4":
            cleanGraph()
        if mainMenuChoice == "2":
            folderMenu()
        #fast mode for testing
        if mainMenuChoice == "f":
            printConfig.folderPath = "./EM/foCsv/"
            printConfig.scalingMethod = "ERB"
            printConfig.graphOutput = "n"
            folderModeProcessing(printConfig.folderPath, printConfig.scalingMethod)
            pause()
    #clear screen and exit
    os.system('clear')
    sys.exit()

######################################################################
##
#   FOLDER MENU
#
def folderMenuContent():
    os.system('clear')
    print "\n\t## PRInt - BATCH MODE MENU ##\n"
    print "\t[1] edit configuration"
    print "\t[2] see configuration"
    print "\t[3] process data"
    print "\t[4] back to main menu"

def folderMenu():
    folderMenuChoice = ""
    while folderMenuChoice != "4":
        folderMenuContent()
        folderMenuChoice = raw_input("\n\t[choice] ")
        if folderMenuChoice == "1":
            editVariablePanel()
        if folderMenuChoice == "2":
            showVariablePanel()
        if folderMenuChoice == "3":
            folderModeProcessing(printConfig.folderPath, printConfig.scalingMethod)
    # go back to main menu
    mainMenu()

######################################################################
##
#   VARIABLE PANEL
#
def editVariablePanel():
    #check for presence of folder path, offers to change it
    if printConfig.folderPath != "":
        print "\n\tfolder path:\t", printConfig.folderPath
        changePathYN = raw_input("\twould you like to change it [y/n]?: ")
        if changePathYN == "y":
            printConfig.folderPath = ""
            getFolderPath()
        else:
            pass
    else:
        getFolderPath()
    #check for presence of scaling method, offers to change it
    if printConfig.scalingMethod != "":
        print "\n\tscaling method:\t", printConfig.scalingMethod
        changeScalingYN = raw_input("\twould you like to change it [y/n]?: ")
        if changeScalingYN == "y":
            printConfig.scalingMethod = ""
            getScalingChoice()
        else:
            pass
    else:
        getScalingChoice()

    #check for presence of graph output choice, offers to change it
    if printConfig.graphOutput != "":
        print "\n\toutput graphs:\t", printConfig.graphOutput
        changeGraphOptionYN = raw_input("\twould you like to change it [y/n]?: ")
        if changeGraphOptionYN == "y":
            printConfig.graphOutput = ""
            getGraphOption()
        else:
            pass
    else:
        getGraphOption()

def getFolderPath():
    while not os.path.isdir(printConfig.folderPath):
        # auto-complete path
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(complete)
        printConfig.folderPath = raw_input("\n\tType in the path to the folder:\n\t> ")
        # add missing final slash if needed
        if printConfig.folderPath.endswith("/"):
            continue
        else:
            printConfig.folderPath = printConfig.folderPath + "/"
        if os.path.isdir(printConfig.folderPath):
            continue
        else:
            print "\tpath not found"

def getScalingChoice():
    while printConfig.scalingMethod not in ["ERB","PCT"]:
        printConfig.scalingMethod = raw_input("\n\tWhat scaling would you like [ERB/PCT]?\n\t> ")
        if printConfig.scalingMethod in ["ERB","PCT"]:
            continue
        else:
            print "\tinvalid choice"

def getGraphOption():
    while printConfig.graphOutput not in ["n","y"]:
        printConfig.graphOutput = raw_input("\n\tWould you like individual graphs output [y/n]?\n\t> ")
        if printConfig.graphOutput in ["n","y"]:
            continue
        else:
            print "\tinvalid choice"

def showVariablePanel():
    print "\n\t-- variable panel --\n"
    print "\tfolder path: ", bcolors.HEADER + printConfig.folderPath + bcolors.ENDC
    print "\tscaling method: ", bcolors.HEADER + printConfig.scalingMethod + bcolors.ENDC
    print "\tgraphs: ", bcolors.HEADER + printConfig.graphOutput + bcolors.ENDC
    pause()

######################################################################
##
#   RUN PRINT PROGRAM
#
if __name__ == "__main__":
    mainMenu()
