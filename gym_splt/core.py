"""
core.py

Original Author: Craig Polley (https://gitlab.com/flashingLEDs/brute_spl-t)
Modifications: Kasper Lauritzen

Simulates a game of SPL-T, one move at a time. Intended to be called from a wrapper script (see playScriptXX examples)

For debugging purposes, you can set the 'verbose' flag to 1. During move executions this will result
in a lot of output to the console about the gameboard and the decisions being made, and also a lot
of 'press any key' pauses.

Example usages:
    # Initialize a board 8 wide x 16 tall
    gameBoard=core.Board(8,16)

    # Get a list of legal moves for a given game board:
    moveOptions=core.getMoveOptions(gameBoard)

    # Split box #1 on a gameboard:
    core.makeMove(gameBoard,1)

    # Draw a gameboard in ascii in the console:
    core.drawScreen(gameBoard)

"""


import math

verbose=0
startBeingVerboseAfterMoveNumber=999999 #If you are only interested in debug information after a certain move


HORIZONTAL='-'
VERTICAL='|'
VOID='*'
NOPOINT=' '


##########################################
class Board(object): # Board class represents the gameboard during play.
##########################################

    def __init__(self,width=None,height=None,splitRecord=None):
        self.width=width if width is not None else 8
        self.height=height if width is not None else 16
        self.splitRecord=splitRecord if splitRecord is not None else []
        self.score=0
        self.box=[]
        self.box.append(Box(0,0,self.width,self.height,0))	#Initialize the board with a single box
        self.splitAction=HORIZONTAL


        # Initialize an ascii screen buffer. It's bigger than BoardWidth*BoardHeight because we also want to draw borders
        # This is not just for display to the console! Certain game logic will rely on this
        self.screenBuffer = [[NOPOINT for x in range((self.width*2)+1)] for x in range(((self.height)*2)+1)]


    def makeBox(self,x,y,width,height,points):
        self.box.append(Box(x,y,width,height,points))
        self.box[-1].index=len(self.box)-1

    # Equality check at the gameBoard level is more than just a simple list compare of each board's box[] list, because the box ordering in the lists may differ.
    # We also can't use the box class equality check, since that one ignores position on the board
    def __eq__(self, other):
        duplicateScore=0
        for b1 in self.box:
            for b2 in other.box:
                if (b1.x==b2.x) and (b1.y==b2.y) and (b1.width==b2.width) and (b1.height==b2.height) and (b1.points==b2.points):
                    duplicateScore+=1

        if duplicateScore==len(self.box): #If the number of duplicates is the same as the number of boxes
            return 1
        else:
            return 0

    def split(self,box):
        if box.splitPossible(self.splitAction)==0:
            if verbose: print("Impossible split requested")
            return 0

        if self.splitAction==VERTICAL:
            box.modify(box.x,box.y,box.width//2,box.height,0)
            self.makeBox(box.x+box.width,box.y,box.width,box.height,0)
            self.splitAction=HORIZONTAL
            return 1

        if self.splitAction==HORIZONTAL:
            box.modify(box.x,box.y,box.width,box.height//2,0)
            self.makeBox(box.x,box.y+box.height,box.width,box.height,0)
            self.splitAction=VERTICAL
            return 1

    def getMoveOptions(self):
        moveOptions=[]
        for boxindex,box in enumerate(self.box):
            if box.splitPossible(self.splitAction):
                moveOptions.append(boxindex)
        if verbose and len(moveOptions)==0:	print("---> No valid moves available! <---")
        return moveOptions


##########################################
class Box(object): # Box class represents individual boxes within a gameboard
##########################################

    def __init__(self,x,y,width,height,points):
        self.x=x
        self.y=y 	#y axis points towards the floor, so 0 is the top of the board
        self.width=width
        self.height=height
        self.points=points
        self.index=0


        # temporary variables used while processing a move
        self.temppoints=0
        self.halvePointsFlag=0
        self.fellFlag=0

    def __eq__(self, other):
        if self.width==other.width and self.height==other.height and self.points==other.points:
            return True
        else:
            return False

    def modify(self,x,y,width,height,points):
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.points=points

    def splitPossible(self,splitAction):
        if self.points>0:
            return 0
        elif splitAction==VERTICAL and self.width>1:
            return 1
        elif splitAction==HORIZONTAL and self.height>1:
            return 1
        else:
            return 0




# updateScreenBuffer updates the ascii representation of the input gameboard. This is used for both
# decision making as well as drawing the gameboard in the console when debugging.
##########################################
def updateScreenBuffer(gameBoard):
##########################################
    for ii in range((gameBoard.width*2)+1):
        for jj in range((gameBoard.height*2)+1):
            gameBoard.screenBuffer[jj][ii]=NOPOINT

    for ii in range(gameBoard.width):
        for jj in range(gameBoard.height):
            gameBoard.screenBuffer[(jj*2)+1][(ii*2)+1]=VOID

    #for all boxes
    for boxindex,box in enumerate(gameBoard.box):
        #Draw the top and bottom lines
        for ii in range((box.width*2)+1):
            gameBoard.screenBuffer[box.y*2][(box.x*2)+ii]=HORIZONTAL
            gameBoard.screenBuffer[(box.y*2)+(box.height*2)][(box.x*2)+ii]=HORIZONTAL

        #Draw the sides
        for ii in range((box.height*2)+1):
            gameBoard.screenBuffer[(box.y*2)+ii][(box.x*2)]=VERTICAL
            gameBoard.screenBuffer[(box.y*2)+ii][(box.x*2)+(box.width*2)]=VERTICAL

        #Draw the nature of the space: void, no-point block or point block
        for jj in range(box.height):
            for ii in range(box.width):
                if box.points==-1:
                    gameBoard.screenBuffer[((box.y+jj)*2)+1][((box.x+ii)*2)+1]=VOID

                elif box.points==0:
                    gameBoard.screenBuffer[((box.y+jj)*2)+1][((box.x+ii)*2)+1]=NOPOINT

                else:
                    gameBoard.screenBuffer[((box.y+jj)*2)+1][((box.x+ii)*2)+1]=box.points
                    # TODO: This could be box.points instead




# drawScreen draws an ascii representation of the input gameboard to the console.
# Used only for debugging when the 'verbose' flag is set
##########################################
def drawScreen(gameBoard):
##########################################
    updateScreenBuffer(gameBoard)
    for jj in range((gameBoard.height*2)+1):
        for ii in range((gameBoard.width*2)+1):
            print(gameBoard.screenBuffer[jj][ii],end='')
        print('\n',end='')


# Evolves an input gameBoard forward, given that you are choosing to split chosenBox on that gameBoard
##########################################
def makeMove(gameBoard,chosenBox):
##########################################

    global verbose

    # -------- 1. Try to execute the split: -------------------------------------------------------------------------------------
    #
    if verbose:
        print("\n\n**************** Start of move ****************")
        drawScreen(gameBoard)
        print("-------- 1. Try to execute the split")
    if gameBoard.split(gameBoard.box[chosenBox])==0:
        #print("Problem trying to split box {0}, aborting".format(chosenBox))
        return False

    gameBoard.splitRecord.append(chosenBox)

    if len(gameBoard.splitRecord)>=startBeingVerboseAfterMoveNumber:
        verbose=1




    # -------- 2. Determine whether four or more similar boxes are now adjacent   -----------------------------------------------
    #
    # Algorithm:
    # 	Scan through all boxes, for each check whether it is in the upper left hand corner of a set of at least 4 identical boxes
    #
    # 	If there is a set of 6, it will register twice: once as the correct set of 6 plus another again as a subset of 4
    # 	This doesn't matter beyond efficiency concerns! The end effect is still correct

    # 	Optimization: The only clusters that could have formed at this stage involve the box you just split
    # 	So while scanning through the boxes, only subscan boxes which are the same size (box equality method compares size)

    if verbose:
        drawScreen(gameBoard)
        print("\n-------- 2. Look for new clusters\n")

    lastCreatedBox=gameBoard.box[-1]

    for box in gameBoard.box:

        if box.points==0:
            if box==lastCreatedBox:	#See optimization note above

                setMembers=[] #A list of identical neighbours for this box

                for otherboxindex,otherbox in enumerate(gameBoard.box):
                    if otherbox.points==0:
                        if box==otherbox:	#Equality method compares width, height and number of points.
                            # If otherbox is beside box
                            if otherbox.x==(box.x+box.width) and otherbox.y==box.y:	setMembers.append(otherboxindex)
                            # If otherbox is diagonal to box
                            elif otherbox.x==(box.x+box.width) and otherbox.y==(box.y+box.height):	setMembers.append(otherboxindex)
                            # If otherbox is below box
                            elif otherbox.x==box.x and otherbox.y==(box.y+box.height):	setMembers.append(otherboxindex)

                if len(setMembers)==3:

                    # We found a set of four, and {box} is the one in the upper left
                    # So we should assign points to the whole set
                    # For now we just make a note to assign these points, but don't actually do it until the end of the scan.
                    # Otherwise we'll mess up the ongoing scan e.g. if you find a group of 4 and immediately make them point
                    # blocks, you will not notice if they are actually part of 6+ block cluster
                    box.temppoints=len(gameBoard.splitRecord)+1
                    gameBoard.box[setMembers[0]].temppoints=len(gameBoard.splitRecord)+1
                    gameBoard.box[setMembers[1]].temppoints=len(gameBoard.splitRecord)+1
                    gameBoard.box[setMembers[2]].temppoints=len(gameBoard.splitRecord)+1

                    if verbose:	print("\t Found a cluster")

    # Once the cluster scanning is complete, assign points to any boxes which were found to be in new clusters
    for box in gameBoard.box:
        if box.temppoints>0:
            box.points+=box.temppoints
            box.temppoints=0




    # -------- 3. Process decrement of point blocks  ----------------------------------------------------------------------------
    #
    if verbose:
        print("\n-------- 3. Process point block decrements\n")

    countDownScore=0	# Keep track of this for point allocation at the end of the turn

    for box in gameBoard.box:
        if box.points>1:
            box.points-=1
            countDownScore+=1

        elif box.points==1:
            box.points=-1 #-1 is a special value to denote 'just exploded'
            countDownScore+=1
        else:
            pass



    # -------- 4. Process destruction of point blocks which have counted down to zero -------------------------------------------
    #
    if verbose:
        print("\n-------- 4. Process block destruction\n")
        drawScreen(gameBoard)

    blockDestructionScore=0 # Keep track of this for point allocation
    rowsWithDestruction=[]

    for box in gameBoard.box:
        if box.points<0: #box should be destroyed
                blockDestructionScore+=(box.width*box.height)
                for ii in range(box.y,box.y+box.height):
                    if not ii in rowsWithDestruction: rowsWithDestruction.append(ii)
    #Remove the boxes from gameBoard.box[]
    gameBoard.box[:] = [box for box in gameBoard.box if box.points>=0]




    # -------- 5. Process falling of blocks which now have voids below them -----------------------------------------------------
    #
    # e.g.
    #		   __
    #		  |__|
    #          		-->	  __
    #		   __	 	 |__|
    #		  |__|  	 |__|
    #
    #
    # We do this by looping through every box. If a box falls, it may causes other boxes
    # above it to also fall. So we then loop again, and repeat until there is no movement of any block

    if verbose:
        print("\n-------- 5. Process falling\n")
        drawScreen(gameBoard)

    updateScreenBuffer(gameBoard)

    columnsWithFalling=[]

    #Optimization: first figure out which columns have voids. We can then cheaply check whether a box is eligible for falling
    columnsWithVoids=[]

    for ii in range(gameBoard.width):
        for jj in range(gameBoard.height):
            if gameBoard.screenBuffer[((jj)*2)+1][((ii)*2)+1] ==VOID:
                if not ii in columnsWithVoids: columnsWithVoids.append(ii)


    fallingHappened=False
    movementScanRequired=True

    while movementScanRequired is True: # Continue looping until nothing falls

        movementScanRequired=False #Assume nothing falls - we'll reset this if needed

        for boxindex,box in enumerate(gameBoard.box):

            if not box.x in columnsWithVoids:	#The left side of this box is not on a column with voids in it, so it can't fall
                pass

            elif (box.y+box.height==gameBoard.height): #This box is already on the floor, so it can't fall
                pass

            else:
                # We want to know if every tile in contact with the bottom edge of this box is void, and to what
                # depth that is true. An easy way to do it is by looking at the ascii screen buffer

                distanceToFall=9999 #assume the box will fall a long way, then adjust it down to the true value

                for ii in range(box.width):

                    stopFound=False
                    jj=0	# jj= number of voids below the ii'th column of this box
                    while stopFound==False:
                        if box.y+box.height+jj<gameBoard.height:
                            if gameBoard.screenBuffer[((box.y+jj+box.height)*2)+1][((box.x+ii)*2)+1] !=VOID:
                                stopFound=True
                            else:
                                jj+=1
                        else:
                            stopFound=True

                    if jj<distanceToFall:
                        distanceToFall=jj

                    if jj==0:	#If any column of the box has no voids below it, it can't fall so we can stop immediately.
                        break

                # If falling needs to happen, do it
                if distanceToFall>0:
                    if verbose: print("\tBox {0} at ({1},{2}) should fall a distance of {3}".format(boxindex,box.x,box.y,distanceToFall))
                    box.modify(box.x,box.y+distanceToFall,box.width,box.height,box.points)
                    if box.points>0: box.fellFlag=1 	#Make a note to halve the points later - it's too soon to do it now
                    fallingHappened=True

                    for ii in range(box.x,box.x+box.width):
                        if not ii in columnsWithFalling: columnsWithFalling.append(ii)

                    updateScreenBuffer(gameBoard)

                    movementScanRequired=True 	#Setting this flag causes the parent loop to run through all blocks one more time

                # else this box should not fall
                else:
                    pass

    columnsWithFalling.sort()

    # -------- 6. Process new blocks coming in from the top ---------------------------------------------------------------------
    #

    if verbose:
        print("\n-------- 6. Process filling\n")
        drawScreen(gameBoard)

    #------------- 6.1. Scan across columns to maps out the space that need filling ----------
    #
    # There is some strangeness here: pre-existing voids are never filled, unless a block has fallen through it.
    # For this reason we kept track of 'columnsWithFalling'

    updateScreenBuffer(gameBoard)
    voidCount=0
    numVoids=[] #If for example the gameboard has a 2x2 pocket in the upper left corner, numVoids will be [2,2,0,0,0,0,0,0]

    if verbose:
        print("\n\t--- 6.1 Map out the space to be filled")

    if len(columnsWithFalling)==0 and len(rowsWithDestruction)>0:

        if verbose: print("\tNo falling happened, but block destruction did. Exclude pre-exisiting voids")

        for column in range(gameBoard.width):	#For each column on the game board
            row=0 				#Start scanning down the rows starting at zero (top of the board)
            stopRowScan=False

            while stopRowScan==False:
                if gameBoard.screenBuffer[(row*2)+1][(column*2)+1] == VOID and row in rowsWithDestruction: voidCount+=1
                else: stopRowScan=True # As soon as you hit a non-void, you're done with this column

                row+=1

                # If you get to the bottom of the game board, you're done. -1 because we count rows from zero
                if row>(gameBoard.height-1): stopRowScan=True

            numVoids.append(voidCount)
            voidCount=0
    else:
        for column in range(gameBoard.width):
            row=0 				#Start scanning down the rows starting at zero (top of the board)
            stopRowScan=False

            while stopRowScan==False:
                if gameBoard.screenBuffer[(row*2)+1][(column*2)+1] == VOID: voidCount+=1
                else: stopRowScan=True # As soon as you hit a non-void, you're done with this column

                row+=1

                # If you get to the bottom of the game board, you're done. -1 because we count rows from zero
                if row>(gameBoard.height-1): stopRowScan=True

            numVoids.append(voidCount)
            voidCount=0

    if verbose: print("\tnumVoids array is",numVoids)

    #------------- 6.2. Fill the space with new blocks from the top ----------
    #


    if verbose:
        print("\n\t--- 6.2 Fill the space with new blocks from the top")

    if all(ii == 0 for ii in numVoids):
        continueFilling=False
        if verbose: print("\tNo space to fill, so nothing to do.")


    # If you have partially filled the void, at what height should the next filling block be placed?
    # numVoidsOffset array tells you this. If numVoids=[6,6,0,0,0,0,0,0] and numVoidsOffset=[4,4,0,0,0,0,0,0],
    # then the final 2x2 block you make should be positioned at a y value of (6-4)=2
    numVoidsOffset=[]
    for column in range(gameBoard.width):
        numVoidsOffset.append(0)


    continueFilling=True
    fillingHappened=False

    while continueFilling==True:
        if verbose:	print("\tSub loop: do while numVoids is not empty")

        if all(v == 0 for v in numVoids):
            continueFilling=False
            if verbose: print('\t\tnumVoids array empty, no space left to fill so should stop now')
            break

        if verbose: print('\t\tnumVoids =',numVoids)

        #	Scan through the numVoids list left to right. Identify the the first isolated pocket you come across
        #	(i.e. bordered by an edge or zero depth).

        pocketFound=0

        for index,voidCount in enumerate(numVoids):
            if voidCount>0 and pocketFound==0:
                pocketFound=1
                if verbose:	print("\t\tPocket found, starting at column",index)
                pocketStartIndex=index

            if voidCount==0 and pocketFound==1:
                pocketEndIndex=index-1
                if verbose: print("\t\tEnding at column",index-1)
                pocketFound=2


        if pocketFound==1:
            if verbose: print("\t\tEnding at the board edge (column {0})".format(index))
            pocketEndIndex=index


        #	Identify the deepest depth in this pocket. Create the largest single block which will fit in it, subject to some extra rules:
        #
        #	1. Only pieces with side lengths of 2^n can exist on the board. This means, for example, that a 6xN void is filled by
        #		a 4xN block and a 2xN block
        #
        #	2. 1xN or Nx1 voids are ignored
        #
        #	3. When multiple blocks are required, filling happens from the bottom up, not top down.

        if pocketStartIndex==pocketEndIndex:
            if verbose:	print("\t\tPocket is only one tile wide, so we're not going to fill it")
            numVoids[pocketStartIndex]=0
        else:
            deepestDepth=max(numVoids[pocketStartIndex:pocketEndIndex+1])
            valleyStartX=numVoids.index(deepestDepth)

            # The pocket may consist of a 'cityscape' profile rather than a simple flat bottom
            # For this reason we identify the deepest valley in the pocket, and treat that as the subspace to be filled

            valleyWidth=0
            for ii in numVoids[valleyStartX:]:
                if ii==deepestDepth:	valleyWidth+=1
                else:break

            if verbose: print("\t\tDeepest depth in this pocket is {0}, and it's {1} tiles wide".format(deepestDepth,valleyWidth))

            # Round the width down to the nearest 2^n value
            reducedWidth=0
            for ii in [1,2,4,8,16,32]:
                if valleyWidth>=ii:
                    reducedWidth=ii
            valleyWidth=reducedWidth

            if verbose: print("\t\tThis can be filled with a block {0} tiles wide".format(valleyWidth))

            if valleyWidth==1:
                if verbose: print("\t\t But if it's 1 unit wide, we cannot fill it. Subtracting 1 layer from numVoids and restarting")
                for jj in range(0,valleyWidth):
                    numVoids[valleyStartX+jj]-=1
                    numVoidsOffset[valleyStartX+jj]+=1

            elif (deepestDepth%2==1):
                if verbose: print("\t\tOdd value depth, cannot fill it completely. Subtracting 1 layer and restarting")
                for jj in range(0,valleyWidth):
                    numVoids[valleyStartX+jj]-=1
                    numVoidsOffset[valleyStartX+jj]+=1

            else:
                for ii in [32,16,8,4,2]:

                    if deepestDepth>=ii:
                        if verbose: print("\t\tTallest legal block which fits in this hole is ",ii)

                        height=ii
                        y=numVoids[valleyStartX]-height	+numVoidsOffset[valleyStartX]
                        y=0
                        if verbose: print("\t\tMaking box at x,y=",valleyStartX,y,"with height",height)
                        gameBoard.makeBox(valleyStartX,y,valleyWidth,height,0)
                        updateScreenBuffer(gameBoard)

                        distanceToFall=999
                        if verbose: print("\t\tComputing fall distance over range",valleyStartX,valleyStartX+valleyWidth)
                        for kk in range(valleyStartX,valleyStartX+valleyWidth):
                            stopFound=False
                            jj=0
                            while stopFound==False:
                                if height+jj<gameBoard.height:
                                    if gameBoard.screenBuffer[((height+jj)*2)+1][((kk)*2)+1] !=VOID:
                                        stopFound=True
                                    else:
                                        jj+=1
                                else:
                                    stopFound=True

                            if distanceToFall>jj:
                                distanceToFall=jj

                        if distanceToFall>0:
                            if verbose: print("\t\tReadjusting y position (fall",distanceToFall,"units)")
                            box=gameBoard.box[-1]
                            box.modify(box.x,box.y+distanceToFall,box.width,box.height,box.points)

                        updateScreenBuffer(gameBoard)
                        fillingHappened=True
                        for jj in range(0,valleyWidth):
                            numVoids[valleyStartX+jj]-=ii
                            deepestDepth-=ii


    # -------- 7. Determine whether four or more similar boxes are now adjacent   -----------------------------------------------
    #
    #	This is almost a copy paste of step 2, except there we only had to look in the vicinity of the box we just split. Now we
    #	have to scan all boxes

    if verbose:
        drawScreen(gameBoard)
        print("\n-------- 7. Look for new clusters\n")

    if fallingHappened==False:
        if verbose: print("\tNo falling occured, so we can skip this")

    else:
        if verbose:	print("\tSomething fell, so looking for new clusters")

        for box in gameBoard.box:
            if box.points==0:

                setMembers=[] #Set of identical neighbours for this box

                for otherboxindex,otherbox in enumerate(gameBoard.box):
                    if otherbox.points==0:
                        if box==otherbox:	#Equality method compares width, height and number of points.
                            # If otherbox is beside box
                            if otherbox.x==(box.x+box.width) and otherbox.y==box.y:	setMembers.append(otherboxindex)
                            # If otherbox is diagonal to box
                            elif otherbox.x==(box.x+box.width) and otherbox.y==(box.y+box.height):	setMembers.append(otherboxindex)
                            # If otherbox is below box
                            elif otherbox.x==box.x and otherbox.y==(box.y+box.height):	setMembers.append(otherboxindex)

                if len(setMembers)==3:
                    # We found a set of four, and {box} is the one in the upper left
                    # So we should assign points to the whole set
                    # For now we just make a note to assign these points, but don't actually do it until the end of the scan. Otherwise we'll mess up the ongoing scan
                    # e.g. if you find a group of 4 and immediately make them point blocks, you will not notice if they are actually part of 6+ block cluster
                    box.temppoints=len(gameBoard.splitRecord)+1
                    gameBoard.box[setMembers[0]].temppoints=len(gameBoard.splitRecord)+1
                    gameBoard.box[setMembers[1]].temppoints=len(gameBoard.splitRecord)+1
                    gameBoard.box[setMembers[2]].temppoints=len(gameBoard.splitRecord)+1
                    if verbose:	print("Found a cluster")

        # Any newly created clusters should also be immediately decremented and points awarded (they weren't around when the rest of the blocks had this done)
        for box in gameBoard.box:
            if box.temppoints is not 0:
                box.points+=box.temppoints-1
                countDownScore+=1
                box.temppoints=0

    # -------- 8. Process halving of points from falling   ----------------------------------------------------------------------
    #
    #	Simogo's SPL-T rounds UP, e.g if a 5 point block falls the new point count will be 3 instead of 2

    if verbose:	print("\n-------- 8. Process halving of points from falling\n")

    if fallingHappened==False:
        if verbose: print("\tNo falling occured, so we can skip this")

    else:
        if verbose:
            print("\tFalling happened, so halving points of fallen blocks")

        for boxindex,box in enumerate(gameBoard.box):
            if box.fellFlag:
                if box.points>1:
                    if verbose: print("\tBox",boxindex,"had",box.points,"points, reducing it to",box.points//2,"and incrementing score by",int(math.ceil(box.points/2.0)))
                    countDownScore+=int(math.ceil(box.points/2.0))
                    box.points=box.points//2
                else:
                    if verbose: print("\tBox",boxindex,"only had",box.points,"point, leaving it alone")

                box.temppoints=0
                box.fellFlag=0



    if verbose:
        print("\n\n**************** Move complete ****************")
        print("Scoring:")
        print("\t +1 for a split")
        print("\t +{0} for point block countdowns".format(countDownScore))
        print("\t +{0} for point block destruction".format(blockDestructionScore))
        print("\t Score update {0} --> {1}\n\n".format(gameBoard.score,gameBoard.score+1+countDownScore+blockDestructionScore))

    gameBoard.score=gameBoard.score+1+countDownScore+blockDestructionScore
    return True
