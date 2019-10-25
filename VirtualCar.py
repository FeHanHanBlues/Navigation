import time

def VirtualCar(UI):
    fakemove = [2, 3, 4, 5, 6, 5, 4, 15]
    it = iter(fakemove)
    while True:
        time.sleep(3)
        try:
            print(UI.updatePosition(next(it)))
        except:
            break