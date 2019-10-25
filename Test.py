import AlphaBotEX
import TRSensors
import time

AB = AlphaBotEX.AlphaBot()
TR = TRSensors.TRSensor()

pre_data = TR.AnalogRead()
now_data = pre_data

def check_diff(pre, now):
    diff = [a - b for a, b in zip(now, pre)]
    print("pre: {}\t now: {}\t diff: {}".format(pre, now, diff))
    max_diff = max(diff)
    min_diff = min(diff)

    if max_diff > 300:
        return -1           # off
    elif min_diff < -300:
        return 1            # on
    else:
        return 0

while True:
    pre_data = now_data
    AB.forward_time(t=1)
    time.sleep(2)
    # input()
    now_data = TR.AnalogRead()
    if check_diff(pre=pre_data, now=now_data) != 0:
        AB.forward_time(t=1)
        break

print("Finish !")
