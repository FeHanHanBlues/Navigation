import RPi.GPIO as GPIO
import time


class AlphaBot(object):

    STOP = 0
    FRONT = 1
    LEFT = 2
    RIGHT = 3
    BACK = 4

    def __init__(self, in1=13, in2=12, ena=6, in3=21, in4=20, enb=26):
        self.r = 2.2    # cm
        self.pi = 3.1415926

        self.IN1 = in1
        self.IN2 = in2
        self.IN3 = in3
        self.IN4 = in4
        self.ENA = ena
        self.ENB = enb
        self.PA = 70
        self.PB = 60
        self.PA_turn = 60
        self.PB_turn = 45

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.ENB, GPIO.OUT)
        self.PWMA = GPIO.PWM(self.ENA, 500)
        self.PWMB = GPIO.PWM(self.ENB, 500)
        self.PWMA.start(self.PA)
        self.PWMB.start(self.PB)
        self.stop()

    def forward(self, speed=None):
        if speed is None:
            self.PWMA.ChangeDutyCycle(self.PA)
            self.PWMB.ChangeDutyCycle(self.PB)
        else:
            self.PWMA.ChangeDutyCycle(speed)
            self.PWMB.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)

    def stop(self):
        self.PWMA.ChangeDutyCycle(0)
        self.PWMB.ChangeDutyCycle(0)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.LOW)

    def backward(self, speed):
        if speed is None:
            self.PWMA.ChangeDutyCycle(self.PA)
            self.PWMB.ChangeDutyCycle(self.PB)
        else:
            self.PWMA.ChangeDutyCycle(speed)
            self.PWMB.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)

    def left(self, speed):
        if speed is None:
            self.PWMA.ChangeDutyCycle(self.PA_turn+20)
            self.PWMB.ChangeDutyCycle(self.PB_turn+20)
        else:
            self.PWMA.ChangeDutyCycle(speed)
            self.PWMB.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)

    def right(self, speed):
        if speed is None:
            self.PWMA.ChangeDutyCycle(self.PA_turn)
            self.PWMB.ChangeDutyCycle(self.PB_turn)
        else:
            self.PWMA.ChangeDutyCycle(speed)
            self.PWMB.ChangeDutyCycle(speed)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)

    def forward_time(self, t=1, speed=None):
        self.forward(speed)
        time.sleep(t)
        self.stop()

    def backward_time(self, t=1, speed=None):
        self.backward(speed)
        time.sleep(t)
        self.stop()

    def left_time(self, t=1, speed=None):
        self.left(speed)
        time.sleep(t)
        self.stop()

    def right_time(self, t=1, speed=None):
        self.right(speed)
        time.sleep(t)
        self.stop()

    def move_time(self, cmd, t=1, speed=None):
        if cmd == AlphaBot.STOP:
            self.stop()
        elif cmd == AlphaBot.FRONT:
            self.forward_time(t, speed)
        elif cmd == AlphaBot.LEFT:
            self.left_time(t, speed)
        elif cmd == AlphaBot.RIGHT:
            self.right_time(t, speed)
        elif cmd == AlphaBot.BACK:
            self.backward_time(t, speed)
        else:
            print("Unknown cmd!")

    def setPWMA(self, value):
        self.PA = value
        self.PWMA.ChangeDutyCycle(self.PA)

    def setPWMB(self, value):
        self.PB = value
        self.PWMB.ChangeDutyCycle(self.PB)

    def setMotor(self, left, right):
        if (right >= 0) and (right <= 100):
            GPIO.output(self.IN1, GPIO.HIGH)
            GPIO.output(self.IN2, GPIO.LOW)
            self.PWMA.ChangeDutyCycle(right)
        elif (right < 0) and (right >= -100):
            GPIO.output(self.IN1, GPIO.LOW)
            GPIO.output(self.IN2, GPIO.HIGH)
            self.PWMA.ChangeDutyCycle(0 - right)
        if (left >= 0) and (left <= 100):
            GPIO.output(self.IN3, GPIO.HIGH)
            GPIO.output(self.IN4, GPIO.LOW)
            self.PWMB.ChangeDutyCycle(left)
        elif (left < 0) and (left >= -100):
            GPIO.output(self.IN3, GPIO.LOW)
            GPIO.output(self.IN4, GPIO.HIGH)
            self.PWMB.ChangeDutyCycle(0 - left)


if __name__ == '__main__':

    Ab = AlphaBot()
    Ab.forward_time(t=2)

