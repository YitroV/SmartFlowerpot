#pylint: skip-file
from RPi import GPIO
from smbus import SMBus
import time

i2c = SMBus()
i2c.open(1)


class KlasseLCDPCF:
    # Constructor
    def __init__(self, is4Bits=False, E=20, RS=21, DB0=16, DB1=12, DB2=25, DB3=24, DB4=23, DB5=26, DB6=19, DB7=13):
        self.E = E
        self.RS = RS
        self.DB0 = DB0
        self.DB1 = DB1
        self.DB2 = DB2
        self.DB3 = DB3
        self.DB4 = DB4
        self.DB5 = DB5
        self.DB6 = DB6
        self.DB7 = DB7
        self.Bits = is4Bits
        self.dbPinnen = [DB0, DB1, DB2, DB3, DB4, DB5, DB6, DB7]
        self.controlPinnen = [E, RS]
        self.__GPIOinit()

    def __GPIOinit(self):
        GPIO.setmode(GPIO.BCM)
        for pin in self.dbPinnen:
            GPIO.setup(pin, GPIO.OUT)

        for pin in self.controlPinnen:
            GPIO.setup(pin, GPIO.OUT)

    def __sendDataBits(self, value):
        i2c.write_byte(0x38, value)

    def __sendCharacter(self, value):
        GPIO.output(self.RS, GPIO.HIGH)
        self.__sendDataBits(value)
        time.sleep(0.002)

        GPIO.output(self.E, GPIO.LOW)
        time.sleep(0.002)
        GPIO.output(self.E, GPIO.HIGH)
        time.sleep(0.01)

    def __sendInstruction(self, value):
        GPIO.output(self.RS, GPIO.LOW)
        self.__sendDataBits(value)
        time.sleep(0.002)

        GPIO.output(self.E, GPIO.LOW)
        time.sleep(0.002)
        GPIO.output(self.E, GPIO.HIGH)
        time.sleep(0.01)

    def secondRow(self):
        self.__sendInstruction((0x80 | 0x40))
        time.sleep(0.001)

    def selecPosition(self, position):
        self.__sendInstruction((0x80 | position))
        time.sleep(0.001)

    def LCDInit(self):
        if self.Bits == False:
            self.__sendInstruction(0x3f)
        else:
            self.__sendInstruction(0x2f)
        self.displayOn()
        self.__sendInstruction(0x01)

    def sendMessage(self, message):
        # listMessage = list(message)
        aantal = 0
        for letter in message:
            aantal = aantal + 1
            if aantal == 17:
                self.secondRow()

            self.__sendCharacter(ord(letter))

    def resetCLD(self):
        self.__sendInstruction(0x01)

    def displayOn(self):
        self.__sendInstruction(0x0C)

    def displayOff(self):
        self.__sendInstruction(0x08)

    def selectCursor(self, typeCursor=1):
        if typeCursor == 1:
            self.__sendInstruction(0x0F)
        elif typeCursor == 2:
            self.__sendInstruction(0x0E)
        elif typeCursor == 3:
            self.__sendInstruction(0x0D)
        elif typeCursor == 4:
            self.__sendInstruction(0x0C)

    def sendList(self, listCodes):
        for i in listCodes:
            self.__sendCharacter(i)
