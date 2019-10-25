import AlphaBotEX
import TRSensors

import time
import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
import threading
import Queue

# state MACRO
FAR = 0
NEAR = 1

CHANCE_ORI = 3

TRY_TIME = 5

# direction MACRO
STOP = 0
FRONT = 1
LEFT = 2
RIGHT = 3
BACK = 4

cap = []
for i in range(2):
    cap.append(cv2.VideoCapture(i))
    cap[-1].set(3,640)
    cap[-1].set(4,480)
    cap[-1].set(cv2.CAP_PROP_FPS, 1)
    # print("fps", fps)

def getDirectionChange(pre, now, next):
    """
    we know where we are from (pre), and where we are now or which point is in front of us (now)
    our task is go to next point, this function tell us how to change direction
    :param pre: pre point
    :param now: now point
    :param next: next point we want to go
    :return: direction change (front, left, right, back)
    """
    return RIGHT


def getNextId(pre, now, dest):
    """
    1. calculate the route with (now, dest), and get next point
    2. get direction change with (pre, now, next)
    db & wy
    :param pre: pre point
    :param now: now point
    :param dest: final destination
    :return: direction change (front, left, right, back), next point id (target)
    """
    if now == 1:
        return FRONT, 2
    else:
        return RIGHT, 3


def getQrCode():
    """
    db & wy
    :return: position (left, right, front, none), value (Qr id, none)
    """
    global qLeft, qRight
    time.sleep(1)
    frames = [qLeft.get(), qRight.get()]
    # cv2.imshow('test', frames[0])
    # cv2.waitKey(0)
    # for i in range(2):
    #     frames.append(cv2.cvtColor(cap[i].read()[1], cv2.COLOR_BGR2GRAY))
    #     time.sleep(1)
    #     frames.append(cv2.cvtColor(cap[i].read()[1], cv2.COLOR_BGR2GRAY))
    #     time.sleep(1)
    #     frames.append(cv2.cvtColor(cap[i].read()[1], cv2.COLOR_BGR2GRAY))

    hearts = []
    QrValues = []
    for frame in frames:
        ret, binary = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        test, contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        polycontours = []
        for contour in contours:
            tmp = cv2.approxPolyDP(contour, 10, True)
            if len(tmp) == 4:
                polycontours.append(tmp)
        
        maxArea = 0
        maxContour = None
        for contour in polycontours:
            if(len(contour) != 4):
                continue
            if cv2.contourArea(contour) > maxArea:
                maxArea = cv2.contourArea(contour)
                maxContour = contour
        if maxArea < 3000:
            continue
        Points = np.array(maxContour, dtype=np.float32).reshape(4, 2)
        dstPoints = np.array([[0, 200],
                     [200, 200],
                     [200, 0],
                     [0, 0]], dtype=np.float32)
        transMat = cv2.getPerspectiveTransform(Points, dstPoints)
        QRimg = cv2.warpPerspective(frame, transMat, (200, 200))
        QrValues += pyzbar.decode(QRimg)
        ret, QRimg = cv2.threshold(QRimg, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        QrValues += pyzbar.decode(QRimg)
        heart = np.mean(maxContour.reshape(4,2), axis=0)
        hearts.append(heart[0])
    
    if len(hearts) == 0:
        return None, None
    position = None
    diff = np.mean(hearts) - frames[0].shape[1] / 2
    if diff > 100:
        position = RIGHT
    elif diff < -100:
        position = LEFT
    else:
        position = FRONT
    if len(QrValues) == 0:
        return position, None
    else:
        return position, int(QrValues[0].data.decode('utf-8'))

    return "", ""


def goQrCode():
    """
    wzl
    :return: bool, onto Qr code ???
    """

    def check_diff(pre, now):
        diff = [a - b for a, b in zip(now, pre)]
        print("pre: {}\t now: {}\t diff: {}".format(pre, now, diff))
        max_diff = max(diff)
        min_diff = min(diff)

        if max_diff > 300:
            return -1  # off
        elif min_diff < -300:
            return 1  # on
        else:
            return 0

    pre_data = TR.AnalogRead()
    AB.forward_time(t=1)
    time.sleep(1)
    # AB.right_time(t=0.1)
    time.sleep(1)
    now_data = TR.AnalogRead()
    if check_diff(pre=pre_data, now=now_data) == 1:
        return True
    else:
        return False

def image_put(qLeft, qRight):
    global cap
    while True:
        # cv2.imshow('test', cap[0].read()[1])
        # cv2.waitKey(0)
        qLeft.put(cv2.cvtColor(cap[0].read()[1], cv2.COLOR_BGR2GRAY))
        qLeft.get() if qLeft.qsize() > 1 else time.sleep(0.01)
        qRight.put(cv2.cvtColor(cap[1].read()[1], cv2.COLOR_BGR2GRAY))
        qRight.get() if qRight.qsize() > 1 else time.sleep(0.01)

# robot & sensor instance
AB = AlphaBotEX.AlphaBot()
TR = TRSensors.TRSensor()

# task:
START = 0
DESTINATION = 3

# job (one jump):
PRE = -1
FROM = 0
TARGET = 1

# state info:
distanceState = FAR  # far or near
chances = CHANCE_ORI

qLeft = Queue.Queue()
qRight = Queue.Queue()

#if __name__ == "__main__":
def run(UI):
    global AB, TR, START, DESTINATION, PRE, FROM, TARGET, distanceState, chances, FAR, NEAR, CHANCE_ORI, TRY_TIME, STOP, FRONT, LEFT, RIGHT, BACK,cap, qLeft, qRight

    CameraThread = threading.Thread(target=image_put, args=(qLeft,qRight,), name="thread-car")
    CameraThread.setDaemon(True)
    CameraThread.start()


    global_state = 0

    # position value ... definition !
    position = None
    value = None
    cnt = 0  # cannot see count; move every TRY_TIME times
    try_mode = 1
    pre_time = time.time()

    # wzl
    while True:
        print("global_state: ", global_state)
        if global_state == 0:
            # initial
            distanceState = FAR
            chances = CHANCE_ORI

            # refresh job
            PRE = FROM
            FROM = TARGET
            # direction_change, TARGET = getNextId(pre=PRE, now=FROM, dest=DESTINATION)
            TARGET, direction_change = UI.updatePosition(FROM)
            while TARGET == -1:
                print("**************** Have Reached! ***************")
                time.sleep(3)
                TARGET, direction_change = UI.updatePosition(FROM)
            print("TARGET", TARGET, "Direction_change", direction_change)
            # change direction according to the direction change cmd (l/r/f/b)
            if direction_change == LEFT or direction_change == RIGHT:
                AB.move_time(cmd=direction_change, t=0.8)
            elif direction_change == BACK:
                AB.move_time(cmd=RIGHT, t=1)

            # goto state 1
            global_state = 1

        elif global_state == 1:

            position, value = getQrCode()
            print('QRpostion', position)
            print('QRValue', value)

            if position is None:
                if cnt < TRY_TIME:
                    # global_state = 2
                    print("global_state: ", 2)
                    print("trymode", try_mode)
                    cnt += 1
                    if try_mode == 0:
                        AB.left_time(t=0.05*cnt+0.3)
                    else:
                        assert try_mode == 1
                        AB.right_time(t=0.05*cnt+0.1)
                    continue

                else:
                    # global_state = 3
                    print("global_state: ", 3)
                    assert cnt == TRY_TIME
                    cnt = 0
                    try_mode = 1 - try_mode
                    if distanceState == FAR:
                        AB.forward_time(t=1)
                    else:
                        AB.backward_time(t=1)
                    continue

            else:
                # global_state = 4
                print("global_state: ", 4)
                cnt = 0
                distanceState = NEAR

                if value is None or value == TARGET or chances == 0:
                    # global_state = 5
                    print("global_state: ", 5)
                    # refresh target
                    if chances == 0 and not value is None:
                        TARGET = value

                    if position == LEFT or position == RIGHT:
                        AB.move_time(position, t=0.2, speed=45)
                        continue

                    else:
                        assert position == FRONT
                        onToQrCode = goQrCode()
                        if onToQrCode and time.time() - pre_time > 5:
                            global_state = 0
                            print('Onto QRCODE!!!')
                            pre_time = time.time()
                            continue
                        else:
                            continue

                else:
                    # global_state = 8
                    print("global_state: ", 8)
                    assert value != TARGET and chances > 0
                    chances -= 1
                    direction_change = getDirectionChange(pre=FROM, now=value, next=TARGET)
                    AB.move_time(cmd=direction_change, t=0.5)
                    continue
        else:
            print("Unknown state !")
            break
