from math import pi
from operator import truediv
from string import printable
from windowcapture import WindowCapture
import cv2 as cv
import numpy as np
import os
import os.path
import win32api, win32con
from numpy.lib.shape_base import tile
from PIL import ImageGrab
from windowcapture import WindowCapture
import keyboard
import time
from math import sqrt
import random
import win32gui, win32ui, win32con


def euqli_dist(p, q, squared=False):
    # Calculates the euclidean distance, the "ordinary" distance between two
    # points
    # 
    # The standard Euclidean distance can be squared in order to place
    # progressively greater weight on objects that are farther apart. This
    # frequently used in optimization problems in which distances only have
    # to be compared.
    if squared:
        return ((p[0] - q[0]) ** 2) + ((p[1] - q[1]) ** 2)
    else:
        return sqrt(((p[0] - q[0]) ** 2) + ((p[1] - q[1]) ** 2))

def closest(cur_pos, positions):
    low_dist = float('inf')
    closest_pos = None
    for pos in positions:
        dist = euqli_dist(cur_pos,pos)
        if dist < low_dist:
            low_dist = dist
            closest_pos = pos
    return closest_pos


os.chdir(os.path.dirname(os.path.abspath(__file__)))

# List all windows headers for headers.txt
def ListWindowNames():
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            print(win32gui.GetWindowText(hwnd))
    win32gui.EnumWindows(winEnumHandler, None)


def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    time.sleep(0.02) #This pauses the script for 0.02 seconds
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)


def findClickPositions(needle_img_path, haystack_img, threshold, debug_mode=None):
        
    # https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html

    needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)
    locations = []
    # Save the dimensions of the needle image

    needle_w = needle_img.shape[1]
    needle_h = needle_img.shape[0]




    # There are 6 methods to choose from:
    # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
    method = cv.TM_CCOEFF_NORMED
    result = cv.matchTemplate(haystack_img, needle_img, method)

    # Get the all the positions from the match result that exceed our threshold
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))
    # print(locations)

    # You'll notice a lot of overlapping rectangles get drawn. We can eliminate those redundant
    # locations by using groupRectangles().
    # First we need to create the list of [x, y, w, h] rectangles
    rectangles = []
    for loc in locations:
        rect = [int(loc[0]), int(loc[1]), needle_w, needle_h]
        # Add every box to the list twice in order to retain single (non-overlapping) boxes
        rectangles.append(rect)
        rectangles.append(rect)
    # Apply group rectangles.
    # The groupThreshold parameter should usually be 1. If you put it at 0 then no grouping is
    # done. If you put it at 2 then an object needs at least 3 overlapping rectangles to appear
    # in the result. I've set eps to 0.5, which is:
    # "Relative difference between sides of the rectangles to merge them into a group."
    rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
    #print(rectangles)

    points = []
    if len(rectangles):
        #print('Found needle.')

        line_color = (0, 255, 0)
        line_type = cv.LINE_4
        marker_color = (255, 0, 255)
        marker_type = cv.MARKER_CROSS

        # Loop over all the rectangles
        for (x, y, w, h) in rectangles:

            # Determine the center position
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            # Save the points
            points.append((center_x, center_y))

            if debug_mode == 'rectangles':
                # Determine the box position
                top_left = (x, y)
                bottom_right = (x + w, y + h)
                # Draw the box
                cv.rectangle(haystack_img, top_left, bottom_right, color=line_color, 
                             lineType=line_type, thickness=2)
            elif debug_mode == 'points':
                # Draw the center point
                cv.drawMarker(haystack_img, (center_x, center_y), 
                              color=marker_color, markerType=marker_type, 
                              markerSize=20, thickness=2)

        #if debug_mode:
            # cv.imshow('Matches', haystack_img)
            # cv.waitKey()
            # cv.imwrite('result_click_point.jpg', haystack_img)

    return points


def tryAllHeaders():
    file = open("headers.txt","r")
    headers = []
    for header in file:
        clearheader = header.replace('\n','')
        headers.append(clearheader)
        # print(headers)
    for header in headers:
        try:
            wincap = WindowCapture(header)
            return header
            break
        except:
            continue

def findCorrectStone(wincap,header,stoneTreshold):
    file = open("stones.txt","r")
    stones = []
    for stone in file:
        clearstone = stone.replace('\n','')
        stones.append(clearstone)
    for stone in stones:
        screen = wincap.get_screenshot()
        points = findClickPositions(stone, screen,stoneTreshold, debug_mode='points'  )
        if (len(points)>0):
            return stone
            break

def urielPass(Uriel,missingWindowHeight):
    urielX = Uriel[0][0]
    urielY = Uriel[0][1]+missingWindowHeight
    urielPossibleCords=[(urielX,urielY+100),(urielX+100,urielY+100),(urielX+250,urielY+100),
    (urielX,urielY+200),(urielX+100,urielY+200),(urielX+250,urielY+200)]
    randomSelect = random.choice(urielPossibleCords)
    click(randomSelect[0],randomSelect[1])                            
    time.sleep(1)
    
def Start():
    char = "char.jpg"
    uriel = 'uriel.jpg'    
    i = 0    
    missingWindowHeight = 110
    stoneTreshold = 0.6
    playerTreshold = 0.6
    urielTreshold = 0.6
    pause = True
    while keyboard.is_pressed('end') == False:
        if (keyboard.is_pressed('f12') == True):                
            pause = True
            print("Bot Started")
            time.sleep(1)  

        if pause !=True:
            time.sleep(1)                   
        
        if pause:
            # Try All Headers
            header = tryAllHeaders()
            wincap = WindowCapture(header)

            # Find Correct Stone
            correctStone = findCorrectStone(wincap,header,stoneTreshold)

        while pause:

            if (keyboard.is_pressed('f12') == True):
                    pause = False
                    print("Bot Stopped")
                    time.sleep(1)
                    break

            if (keyboard.is_pressed('end') == True):
                break
            
            try:                

                screen = wincap.get_screenshot()

                StonePoints = findClickPositions(correctStone, screen,stoneTreshold)
                if(i%10 ==0):
                    playerLocation = findClickPositions(char, screen,playerTreshold)
                if(i%100 ==0):
                    Uriel = findClickPositions(uriel, screen,urielTreshold)
                if(len(Uriel)>0):
                    isActive = True
                    while isActive:    
                        screen = wincap.get_screenshot() 
                        Uriel = findClickPositions(uriel, screen,urielTreshold)
                        if (len(Uriel)>0):
                            urielPass(Uriel,missingWindowHeight)                            
                        else:
                            isActive=False
                             
                stoneX = StonePoints[0][0]
                stoneY = StonePoints[0][1]+missingWindowHeight
                
                playerX = playerLocation[0][0]
                playerY = playerLocation[0][1]+missingWindowHeight

                if(i%20 ==0):
                    print("I'm Going To The Stone Nearest To You")


                closestStone = []               
                closestStone.append(closest((playerX, playerY), StonePoints))

                closestStoneX = closestStone[0][0]
                closestStoneY = closestStone[0][1]+missingWindowHeight

                click(closestStoneX,closestStoneY)     

                i = i+1
                    
            except:
                i = i+1 
                Uriel =[]
                if(i%100 ==0):
                    Uriel = findClickPositions(uriel, screen,urielTreshold, debug_mode='rectangles')
                if(len(Uriel)>0):
                    isActive = True
                    while isActive:    
                        screen = wincap.get_screenshot() 
                        Uriel = findClickPositions(uriel, screen,urielTreshold, debug_mode='rectangles')
                        if (len(Uriel)>0):
                            urielPass(Uriel,missingWindowHeight)                            
                        else:
                            isActive=False                             
                    
                StonePoints = findClickPositions(correctStone, screen,stoneTreshold, debug_mode='rectangles'  )
                playerLocation = findClickPositions(char, screen,playerTreshold, debug_mode='points')
                if(len(StonePoints)>0):
                    stoneX = StonePoints[0][0]
                    stoneY = StonePoints[0][1]+missingWindowHeight
                    click(stoneX,stoneY)
                else:
                    click(500,500)

                if(len(playerLocation)==0):   
                    print('Cant find Character')
                if(len(StonePoints)==0):   
                    print('Cant Find Stone')


def Test():
    char = "char.jpg"
    i = 0  
    missingWindowHeight = 110
    stoneTreshold = 0.6
    playerTreshold = 0.6
    
    #Try All headers
    header = tryAllHeaders()
    wincap = WindowCapture(header)  
    # Find Correct Stone
    correctStone = findCorrectStone(wincap,header,stoneTreshold)
    loop_time = time.time()
    while keyboard.is_pressed('end') == False:
        try:            
            # FPS printer
            fps = format(1 / (time.time() - loop_time))
            loop_time = time.time()
            print(fps)

            screen = wincap.get_screenshot()

            StonePoints = findClickPositions(correctStone, screen, stoneTreshold, debug_mode='rectangles')
            playerLocation = findClickPositions(char, screen, playerTreshold, debug_mode='points')
            cv.imshow("Points",screen)
            cv.waitKey(5)
            i+=1

        except:
            print("Cant find stone or character")


# ListWindowNames()
# Start()
Test()






