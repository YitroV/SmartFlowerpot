import spidev


class Mcp:
    def __init__(self, bus=0, device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)  # Bus SPI0, slave op CE 0
        self.spi.max_speed_hz = 10 ** 5  # 100 kHz

    def read_channel(self, ch):
        self.verstuur_bytes = [1, ((8 | ch) << 4), 0]
        self.adc = self.spi.xfer(self.verstuur_bytes)
        self.data = ((self.adc[1] & 3) << 8) | self.adc[2]
        return self.data

    def closespi(self):
        self.spi.close()

    # ********** property verstuur_bytes - (setter/getter) ***********

    @property
    def verstuur_bytes(self):
        """ The verstuur_bytes property. """
        return self.__verstuur_bytes

    @verstuur_bytes.setter
    def verstuur_bytes(self, value):
        self.__verstuur_bytes = value

    # ********** property spi - (setter/getter) ***********
    @property
    def spi(self):
        """ The spi property. """
        return self.__spi

    @spi.setter
    def spi(self, value):
        self.__spi = value

    # ********** property data - (setter/getter) ***********
    @property
    def data(self):
        """ The data property. """
        return self.__data

    @data.setter
    def data(self, value):
        self.__data = value
