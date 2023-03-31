import cv2
import mediapipe as mp
from cvzone import (HandTrackingModule as htm)
from cvzone import FPS
import numpy as np
import pyautogui
import autopy

################################


def mssg(text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = text
    textsize = cv2.getTextSize(text, font, 2, 3)[0]
    textX = int(((img.shape[1]) - textsize[0])/2)
    textY = int(((img.shape[0]) + textsize[1]) / 6 * 5.3)
    cv2.putText(img, text, (textX, textY), font, 2, (0, 255, 0), 3)
    
def distance(p1, p2, img=None):
        x1, y1 = p1
        x2, y2 = p2
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = -((x2 - x1) + (y2 - y1))
        info = (x1, y1, x2, y2, cx, cy)
        if img is not None:
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
            return length, info, img
        else:
            return length, info


################################


#################################
wCam, hCam = 640, 480
# wScr, hScr = pyautogui.size()
wScr, hScr = autopy.screen.size()
frameR = 100  # Frame Reduction
smoothening = 5
buttonPress = False
#################################

plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
fpsRead = FPS()
detector = htm.HandDetector(maxHands=1)

while True:
    success, img = cap.read()
    # img = cv2.flip(img, 1)
    fps, img = fpsRead.update(img)
    hands, img = detector.findHands(img, True, True)
    # cv2.rectangle(img, (frameR, frameR), (wCam - frameR,
    #               hCam - frameR), (255, 0, 255), 2)
    if hands:
        hand1 = hands[0]
        lmList1 = hand1["lmList"]
        bbox1 = hand1["bbox"]
        centerPoint1 = hand1['center']
        handType1 = hand1["type"]

        # x, y = lmList1[8][0:2]
        # print(f"{x} , {y}")

        if len(lmList1) != 0:
            x1, y1, _ = lmList1[8][:]  # index finger
            x2, y2, _ = lmList1[12][:]  # niddle finger

            # Find which finger are up
            finger1 = detector.fingersUp(hand1)
            # print(finger1)
            
            ###################
            ### MOVE CURSOR ###
            ###################
            if finger1 == [0, 1, 0, 0, 0]:
                mssg("Moving Mode")
                cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
                cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

                # Smoothen value
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening

                # pyautogui.moveTo(wScr - clocX, clocY)
                autopy.mouse.move(wScr - clocX, clocY)
                plocX, plocY = clocX, clocY

            ###################
            ### LEFT  CLICK ###
            ###################
            if finger1 == [0, 1, 1, 0, 0]:
                mssg("Left Click Mode")
                length, info, img = detector.findDistance(lmList1[8][0:2], lmList1[12][0:2], img)
                # print(length)
                if length < 40:
                    cv2.circle(img, (info[-2], info[-1]), 10, (0, 255, 0), cv2.FILLED)
                    print("left Click")
                    pyautogui.leftClick()

            ###################
            ### RIGHT CLICK ###
            ###################
            if finger1 == [1, 1, 0, 0, 0]:
                mssg("Right Click Mode")
                length, info, img = detector.findDistance(lmList1[4][0:2], lmList1[8][0:2], img)
                # print(length)
                if length < 30:
                    cv2.circle(img, (info[-2], info[-1]), 10, (0, 255, 0), cv2.FILLED)
                    print(f"right click")
                    pyautogui.rightClick()
                    
            ###################
            ### SCROLL MODE ###
            ###################
            if finger1 == [1, 1, 1, 1, 1]:
                mssg("scroll mode")

                cv2.line(img=img, pt1=(int(wCam/4), int(hCam/2) + 50), pt2=(wCam - int(wCam / 4), int(hCam / 2) + 50), color=(0, 255, 0), thickness=3)
                cv2.circle(img=img, center=(int(wCam / 2), int(hCam / 2) + 50), radius=10, color=(0, 0, 255), thickness=cv2.FILLED)
                
                lengthP, infoP= distance(lmList1[0][0:2], lmList1[9][0:2])
                center_of_wCam = int(wCam / 2), int(hCam / 2) + 50
                center_of_hand = infoP[-2], infoP[-1]
                scrollValue, info, img = distance(center_of_wCam, center_of_hand, img)
                
                if scrollValue > 68:                    
                    print('UP')
                    pyautogui.scroll(scrollValue)
                    
                if scrollValue < -40:
                    print('DOWN')
                    pyautogui.scroll(scrollValue)

            ###########################
            ### Left Arrow Keypress ###
            ###########################
            if finger1 == [0, 0, 0, 0, 0]:
                buttonPress = True
            if finger1 == [1, 0, 0, 0, 0]:
                mssg("<-- Mode")
                if buttonPress == True:
                    autopy.key.tap(autopy.key.Code.LEFT_ARROW)
                    print("LEFT KEYPRESS")
                    buttonPress = False

            ############################
            ### Right Arrow Keypress ###
            ############################
            if finger1 == [0, 0, 0, 0, 0]:
                buttonPress = True
            if finger1 == [0, 0, 0, 0, 1]:
                mssg("--> Mode")
                if buttonPress == True:
                    autopy.key.tap(autopy.key.Code.RIGHT_ARROW)
                    print("Right KEYPRESS")
                    buttonPress = False

            
    
    cv2.imshow("output", img)
    if cv2.waitKey(1) == ord('q'):
        break
    
cap.release()
