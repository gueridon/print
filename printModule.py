# -*-coding:utf-8 -*

# based on PRInt (Nicholas Bacuez, 2012)
from ToneFinder3 import *
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
    programPause = input("\n\tPress <ENTER> to continue...")

######################################################################
##
#   clean all previously generated graph
#
def cleanGraph():
    fileListClean = [ f for f in os.listdir(".") if f.endswith(".png") ]
    for f in fileListClean:
        os.remove(f)
    print("All graphs removed from directory.")

######################################################################
##
#   MAIN MENU
#
def mainMenuContent():
    os.system('clear')
    print("\t## PRInt - MAIN MENU ##\n")
    print("\n\tFor complete documentation, please see: \
        \n\twww.nicholasbacuez.com/print.php\
        \n\n\tChoose one of the following options:\n \
            ")
    print("\t[1] file mode")
    print("\t[2] folder mode")
    print("\t[3] batch mode")
    print("\t[4] remove graphs files")
    print("\t[5] documentation")
    #print "\t[f] fast mode for testing"
    print("\t[6] exit PRInt")

def mainMenu():
    mainMenuChoice = ""
    while mainMenuChoice != "6":
        mainMenuContent()
        mainMenuChoice = input("\n\t[choice] ")
        if mainMenuChoice == "1":
            fileMenu()
        if mainMenuChoice == "2":
            folderMenu()
        if mainMenuChoice == "4":
            cleanGraph()
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
#   FILE MENU
#
def fileMenuContent():
    os.system('clear')
    print("\n\t## PRInt - FILE MODE MENU ##\n")
    print("\t[1] edit configuration")
    print("\t[2] see configuration")
    print("\t[3] process file")
    print("\t[4] back to main menu")

def fileMenu():
    printConfig.processingOption = "file"
    fileMenuChoice = ""
    while fileMenuChoice != "4":
        fileMenuContent()
        fileMenuChoice = input("\n\t[choice] ")
        if fileMenuChoice == "1":
            editVariablePanel()
        if fileMenuChoice == "2":
            showVariablePanel()
        if fileMenuChoice == "3":
            fileModeProcessing(printConfig.folderPath, printConfig.scalingMethod)
    # go back to main menu
    mainMenu()



######################################################################
##
#   FOLDER MENU
#
def folderMenuContent():
    os.system('clear')
    print("\n\t## PRInt - BATCH MODE MENU ##\n")
    print("\t[1] edit configuration")
    print("\t[2] see configuration")
    print("\t[3] process data")
    print("\t[4] back to main menu")

def folderMenu():
    printConfig.processingOption = 'folder'
    folderMenuChoice = ""
    while folderMenuChoice != "4":
        folderMenuContent()
        folderMenuChoice = input("\n\t[choice] ")
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
    #check for presence of folder path, offer to change it
    if printConfig.folderPath != "":
        print("\n\tfolder path:\t", printConfig.folderPath)
        changePathYN = input("\twould you like to change it [y/n]?: ")
        if changePathYN == "y":
            printConfig.folderPath = ""
            getFolderPath()
        else:
            pass
    else:
        getFolderPath()

    #check for presence of file name, offer to change it
    if printConfig.processingOption == 'file':
        if printConfig.gp_name != "":
            print("\n\tfile name:\t", printConfig.gp_name)
            changeNameYN = input("\twould you like to change it [y/n]?: ")
            if changeNameYN == "y":
                printConfig.gp_name = ""
                getFileName()
            else:
                pass
        else:
            getFileName()






    #check for presence of scaling method, offer to change it
    if printConfig.scalingMethod != "":
        print("\n\tscaling method:\t", printConfig.scalingMethod)
        changeScalingYN = input("\twould you like to change it [y/n]?: ")
        if changeScalingYN == "y":
            printConfig.scalingMethod = ""
            getScalingChoice()
        else:
            pass
    else:
        getScalingChoice()

    #check for presence of graph output choice, offer to change it
    if printConfig.graphOutput != "":
        print("\n\toutput graphs:\t", printConfig.graphOutput)
        changeGraphOptionYN = input("\twould you like to change it [y/n]?: ")
        if changeGraphOptionYN == "y":
            printConfig.graphOutput = ""
            getGraphOption()
        else:
            pass
    else:
        getGraphOption()

def getFileName():
    printConfig.gp_name = input("\n\tType in the name to the file:\n\t> ")


def getFolderPath():
    while not os.path.isdir(printConfig.folderPath):
        # auto-complete path
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(complete)
        printConfig.folderPath = input("\n\tType in the path to the folder:\n\t> ")
        # add missing final slash if needed
        if printConfig.folderPath.endswith("/"):
            continue
        else:
            printConfig.folderPath = printConfig.folderPath + "/"
        if os.path.isdir(printConfig.folderPath):
            continue
        else:
            print("\tpath not found")

def getScalingChoice():
    while printConfig.scalingMethod not in ["ERB","PCT"]:
        printConfig.scalingMethod = input("\n\tWhat scaling would you like [ERB/PCT]?\n\t> ")
        if printConfig.scalingMethod in ["ERB","PCT"]:
            continue
        else:
            print("\tinvalid choice")

def getGraphOption():
    while printConfig.graphOutput not in ["n","y"]:
        printConfig.graphOutput = input("\n\tWould you like individual graphs output [y/n]?\n\t> ")
        if printConfig.graphOutput in ["n","y"]:
            continue
        else:
            print("\tinvalid choice")

def showVariablePanel():
    print("\n\t-- variable panel --\n")
    print("\tfolder path: ", bcolors.HEADER + printConfig.folderPath + bcolors.ENDC)
    if printConfig.processingOption == 'file':
        print("\tfile name: ", bcolors.HEADER + printConfig.gp_name + bcolors.ENDC)
    print("\tscaling method: ", bcolors.HEADER + printConfig.scalingMethod + bcolors.ENDC)
    print("\tgraphs: ", bcolors.HEADER + printConfig.graphOutput + bcolors.ENDC)
    pause()



######################################################################
##
#   RUN PRINT PROGRAM
#
if __name__ == "__main__":
    mainMenu()
