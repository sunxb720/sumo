#!/usr/bin/env python
"""
@file    neteditTestFunctions.py
@author  Pablo Alvarez Lopez
@date    2016-11-25
@version $Id$

Simplify writing of sikulix test scripts for netedit

SUMO, Simulation of Urban MObility; see http://sumo.dlr.de/
Copyright (C) 2009-2017 DLR/TS, Germany

This file is part of SUMO.
SUMO is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.
"""
# Import libraries
import os
import sys
import subprocess
import platform
import atexit
from sikuli import *

Settings.MoveMouseDelay = 0.1
Settings.DelayBeforeDrop = 0.1
Settings.DelayAfterDrag = 0.1

neteditApp = os.environ.get("NETEDIT_BINARY", "netedit")
textTestSandBox = os.environ.get("TEXTTEST_SANDBOX", ".")
referenceImage = os.path.join("imageResources", "reference.png")

def setup(neteditTests):
    # Open current environment file to obtain path to the netedit app,
    # textTestSandBox
    envFile = os.path.join(neteditTests, "currentEnvironment.tmp")
    if os.path.exists(envFile):
        global neteditApp, textTestSandBox, currentOS
        with open(envFile) as env:
            neteditApp, sandBox = [l.strip() for l in env.readlines()]
        if os.path.exists(sandBox):
            textTestSandBox = sandBox
        os.remove(envFile)
    # get reference for match
    global referenceImage
    referenceImage = os.path.join(
        neteditTests, "imageResources", "reference.png")

def Popen(newNet):
    # set the default parameters of netedit
    neteditCall = [neteditApp, '--gui-testing', '--window-pos', '50,50',
                   '--window-size', '700,500', '--no-warnings',
                   '--error-log', os.path.join(textTestSandBox, 'log.txt')]

    # check if a new net must be created
    if newNet:
        neteditCall += ['--new']

    # check if an existent net must be loaded
    if os.path.exists(os.path.join(textTestSandBox, "input_net.net.xml")):
        neteditCall += ['--sumo-net-file',
                        os.path.join(textTestSandBox, "input_net.net.xml")]

    # set output for net
    neteditCall += ['--output-file',
                    os.path.join(textTestSandBox, 'net.net.xml')]

    # Check if additionals must be loaded (additionals output will be
    # automatically set)
    if os.path.exists(os.path.join(textTestSandBox, "input_additionals.add.xml")):
        neteditCall += ['--sumo-additionals-file',
                        os.path.join(textTestSandBox, "input_additionals.add.xml")]

    # set output for additionals
    neteditCall += ['--additionals-output',
                    os.path.join(textTestSandBox, "additionals.xml")]

    return subprocess.Popen(neteditCall, env=os.environ, stdout=sys.stdout, stderr=sys.stderr)

# obtain match
def getReferenceMatch(neProcess, waitTime):
    try:
        return wait(referenceImage, waitTime)
    except:
        neProcess.kill()
        sys.exit("Killed netedit process. 'reference.png' not found")

# setup and start netedit
def setupAndStart(testRoot, newNet=False, searchReference=True, waitTime=20):
    setup(testRoot)
    # Open netedit
    neteditProcess = Popen(newNet)
    atexit.register(quit, neteditProcess, False, False)
    # Wait for netedit reference
    if(searchReference):
        # Wait for netedit reference
        return neteditProcess, getReferenceMatch(neteditProcess, waitTime)
    else:
        # Wait 1 second for netedit
        wait(1)
        return neteditProcess

# rebuild network
def rebuildNetwork():
    type(Key.F5)

# netedit undo
def undo(match, number):
    # needed to avoid errors with undo/redo
    type("i")
    click(match)
    for x in range(0, number):
        type("z", Key.CTRL)

# netedit redo
def redo(match, number):
    # needed to avoid errors with undo/redo
    type("i")
    click(match)
    for x in range(0, number):
        type("y", Key.CTRL)


# def left click over element
def leftClick(match, positionx, positiony):
    click(match.getTarget().offset(positionx, positiony))

# zoom in
def zoomIn(position, level):
    # set mouse over position
    hover(position)
    # apply zoom it using key +
    for x in range(level):
        type(Key.ADD)

# zoom out
def zoomOut(position, level):
    # set mouse over position
    hover(position)
    # apply zoom it using key -
    for x in range(level):
        type(Key.MINUS)

# netedit wait question
def waitQuestion(answer):
    # wait 0.5 second to question dialog
    wait(0.5)
    # Answer can be "y" or "n"
    type(answer, Key.ALT)

# netedit quit
def quit(neteditProcess, mustBeSaved, save):
    if neteditProcess.poll() is not None:
        # already quit
        return

    # quit using hotkey
    type("q", Key.CTRL)

    # Check if net must be saved
    if mustBeSaved:
        if save:
            waitQuestion("y")
        else:
            waitQuestion("n")

    # wait some seconds
    for t in xrange(3):
        wait(t)
        if neteditProcess.poll() is not None:
            print("[log] netedit closed successfully")
            return
    neteditProcess.kill()
    print("error closing netedit")

# save network
def saveNetwork():
    # save newtork using hotkey
    type("s", Key.CTRL)

# save additionals
def saveAdditionals():
    # save additionals using hotkey
    type("d", Key.CTRL + Key.SHIFT)

#################################################
# Create edge
#################################################

# Change to delete  mode
def createEdgeMode():
    type("e")

# Cancel current created edge (used in chain mode)
def cancelEdge():
    type(Key.ESC)

# Change chain option
def changeChainOption(match):
    click(match.getTarget().offset(350, -50))

# Change two-way mode
def changeTwoWayOption(match):
    click(match.getTarget().offset(400, -50))
    
#################################################
# Inspect mode
#################################################

# go to inspect mode
def inspectMode():
    type("i")

# netedit modify int/float/string
def modifyAttribute(attributeNumber, value):
    type("i")
    # jump to attribute
    for x in range(0, attributeNumber + 1):
        type(Key.TAB)
    # select all values
    type("a", Key.CTRL)
    # paste the new value
    paste(value)
    # type ESC to save changea and avoid edit accidentally
    type(Key.ESC)

# netedit modify bool attribute
def modifyBoolAttribute(attributeNumber):
    type("i")
    # jump to attribute
    for x in range(0, attributeNumber + 1):
        type(Key.TAB)
    # type SPACE to change value
    type(Key.SPACE)
    
#################################################
# Move mode
#################################################

# set move mode
def moveMode():
    type("m")

# move element
def moveElement(match, startX, startY, endX, endY):
    # change mouse move delay
    Settings.MoveMouseDelay = 0.5
    # move element
    dragDrop(match.getTarget().offset(startX, startY),
             match.getTarget().offset(endX, endY))
    # set back mouse move delay
    Settings.MoveMouseDelay = 0.1

#################################################
# crossings
#################################################

# Change to crossing mode
def crossingMode():
    type("r")

# create crossing
def createCrossing(match):
    # select edges attribute
    click(match.getTarget().offset(-100, 250))
    # jump to create edge
    for x in range(0, 4):
        type(Key.TAB)
    # type enter to create crossing
    type(Key.SPACE)

def modifyCrossingEdges(match, value):
    # select edges attribute
    click(match.getTarget().offset(-100, 250))
    # select all values
    type("a", Key.CTRL)
    # paste the new value
    paste(value)
    # type enter to save change
    type(Key.ENTER)

def modifyCrossingPriority(match):
    # select edges attribute
    click(match.getTarget().offset(-100, 250))
    # jump to priority
    type(Key.TAB)
    # type enter to save change
    type(Key.SPACE)

def modifyCrossingWidth(match, value):
    # select edges attribute
    click(match.getTarget().offset(-100, 250))
    # jump to create edge
    for x in range(0, 2):
        type(Key.TAB)
    # select all values
    type("a", Key.CTRL)
    # paste the new value
    paste(value)
    # type enter to save change
    type(Key.ENTER)

def clearCrossings(match):
    # select edges attribute
    click(match.getTarget().offset(-100, 250))
    # jump to clear button
    for x in range(0, 3):
        type(Key.TAB, Key.SHIFT)
    # type space to activate button
    type(Key.SPACE)

def invertCrossings(match):
    # select edges attribute
    click(match.getTarget().offset(-100, 250))
    # jump to invert button
    for x in range(0, 2):
        type(Key.TAB, Key.SHIFT)
    # type space to activate button
    type(Key.SPACE)

#################################################
# additionals
#################################################

# change additional
def changeAdditional(additional):
    type('a')
    type(Key.TAB)
    # select current value
    type("a", Key.CTRL)
    # paste the new value
    paste(additional)
    # type enter to save change
    type(Key.ENTER)
    # type ESC to avoid edit combobox accidentally
    type(Key.ESC)


# modify default int/double/string value of an additional
def modifyAdditionalDefaultValue(numTabs, length):
    type('a')
    # go to length textfield
    for x in range(0, numTabs + 1):
        type(Key.TAB)
    # select current value
    type("a", Key.CTRL)
    # paste new lenght
    paste(length)
    # type enter to save new lenght
    type(Key.ENTER)
    # type ESC to avoid edit combobox accidentally
    type(Key.ESC)
    
# modify default boolean value of an additional
def modifyAdditionalDefaultBoolValue(numTabs):
    type('a')
    # place cursor in force position checkbox
    for x in range(numTabs + 1):
        type(Key.TAB)
    # Change current value
    type(Key.SPACE)

# modify number of stopping place lines
def modifyStoppingPlaceLines(numTabs, numLines):
    type('a')
    # go to add line
    for x in range(0, numTabs+1):
        type(Key.TAB)
    # add lines
    for x in range(0, numLines):
        type(Key.SPACE)

# fill lines to stopping places
def fillStoppingPlaceLines(numTabs, numLines):
    type('a')
    # place cursor in the first line
    for x in range(0, numTabs + 1):
        type(Key.TAB)
    # fill lines
    for x in range(0, numLines):
        paste("Line" + str(x))
        type(Key.TAB)
    # type ESC to avoid edit combobox accidentally
    type(Key.ESC)

# select child of additional
def selectAdditionalChild(numTabs, childNumber):
    type('a')
    # place cursor in the list of childs
    for x in range(0, numTabs + 1):
        type(Key.TAB)
    type(Key.SPACE)
    # now child can be selected
    click(comboboxAdditional)
    # place cursor in the list of childs
    for x in range(0, numTabs):
        type(Key.TAB)
    # select child
    for x in range(0, childNumber):
        type(Key.DOWN)


#################################################
# delete
#################################################

# Change to delete mode
def deleteMode():
    type("d")

# Enable or disable 'automatically delete Additionals'
def changeAutomaticallyDeleteAdditionals(match):
    click(match.getTarget().offset(-120, 100))

# close warning about automatically delete additionals
def waitAutomaticallyDeleteAdditionalsWarning():
    # wait 0.5 second to question dialog
    wait(0.5)
    # press enter to close dialog
    type(Key.ENTER)

#################################################
# select mode
#################################################

# Change to select mode
def selectMode():
    type("s")    
    
# netedit selection reference
def getSelectReference(match):
    return match.getTarget().offset(-120, 270)
        
# select items
def selectItems(selectType, elementClass, elementType, attribute, value):
    click(selectType)
    # select all
    type("a", Key.CTRL)
    # paste the new elementClass
    paste(elementClass)
    # type two times enter to set elementClass
    for x in range(0, 2):
        type(Key.ENTER)
    
    # jump to element
    for x in range(0, 2):
        type(Key.TAB)
    # select all
    type("a", Key.CTRL)
    # paste the new elementType
    paste(elementType)
    # type enter to set elementType
    type(Key.ENTER)
    
    # jump to attribute
    for x in range(0, 2):
        type(Key.TAB)
    # select all
    type("a", Key.CTRL)
    # paste the new attribute
    paste(attribute)
    # type enter to set attribute
    type(Key.ENTER)
    
    # jump to value
    for x in range(0, 2):
        type(Key.TAB)
    # select all
    type("a", Key.CTRL)
    # paste the new value
    paste(value)
    # type enter to set value and select items
    type(Key.ENTER)

# delete selected items
def deleteSelectedItems():
    type(Key.DELETE)
    
# set modification mode "add"
def modificationModeAdd(match):
    click(match.getTarget().offset(-225, 150))
    
# set modification mode "remove"
def modificationModeRemove(match):
    click(match.getTarget().offset(-225, 150))
    # jump to value
    for x in range(0, 1):
        type(Key.TAB)
    # change value
    type(Key.SPACE)
    
# set modification mode "keep"
def modificationModeKeep(match):
    click(match.getTarget().offset(-225, 150))
    # jump to value
    for x in range(0, 2):
        type(Key.TAB)
    # change value
    type(Key.SPACE)
    
# set modification mode "replace"
def modificationModeReplace(match):
    click(match.getTarget().offset(-225, 150))
    # jump to value
    for x in range(0, 3):
        type(Key.TAB)
    # change value
    type(Key.SPACE)

def selectionRectangle(match, startX, startY, endX, endY):
    keyDown(Key.SHIFT)
    # change mouse move delay
    Settings.MoveMouseDelay = 0.5
    # move element
    dragDrop(match.getTarget().offset(startX, startY), match.getTarget().offset(endX, endY))
    # set back mouse move delay
    Settings.MoveMouseDelay = 0.1
    keyUp(Key.SHIFT)
