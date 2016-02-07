import usb.core
import time

class Joystick:
    """
    Class for our PIC-controlled joystick
    """
    def __init__(self):
        """
        Initialize the joystick instance by setting constants and opening USB connection
        """
        # Command definitions
        self.ENC_READ_REG = 1
        self.MTR_SET_VEL = 2

        # Open USB connection
        self.dev = usb.core.find(idVendor = 0x6666, idProduct = 0x0003)
        if self.dev is None:
            raise ValueError('no USB device found matching idVendor = 0x6666 and idProduct = 0x0003')
        self.dev.set_configuration()

        # AS5048A Register Map
        self.ENC_NOP = 0x0000
        self.ENC_CLEAR_ERROR_FLAG = 0x0001
        self.ENC_PROGRAMMING_CTRL = 0x0003
        self.ENC_OTP_ZERO_POS_HI = 0x0016
        self.ENC_OTP_ZERO_POS_LO = 0x0017
        self.ENC_DIAG_AND_AUTO_GAIN_CTRL = 0x3FFD
        self.ENC_MAGNITUDE = 0x3FFE
        self.ENC_ANGLE_AFTER_ZERO_POS_ADDER = 0x3FFF

        # Encoder decoding
        self.enc_mask = 0x3FFF  # Sets first two bits (parity and error flag) to 0
        self.enc_slope = 0.022  # Slope of reading-to-angle curve 
        self.enc_offset = -9.4  # Intercept of reading-to-angle-curve

    def close(self):
        """
        Release USB connection
        """
        self.dev = None

    def toWord(self, byteArray):
        """
        Convert a byte array to a single word
        """
        val = 0
        for i,byte in enumerate(byteArray):
            val += int(byte) * 2**(8*i)
        return val

    def parity(self, v):
        """
        Calculate the parity of v, a 16 bit number
        Should be 0 if no bit errors occurred 
        """
        v ^= v >> 8
        v ^= v >> 4
        v ^= v >> 2
        v ^= v >> 1
        return v & 1

    def enc_readingToAngle(self, word):
        """
        Convert the encoder reading returned by the PIC to an angle in degrees
        """
        return float(word & self.enc_mask) * self.enc_slope + self.enc_offset

    def enc_readReg(self, address):
        """
        Send a request to read the encoder register at the given address and
        return the result
        """
        try:
            ret = self.dev.ctrl_transfer(0xC0, self.ENC_READ_REG, address, 0, 2)
        except usb.core.USBError:
            print "Could not send ENC_READ_REG vendor request."
        else:
            return self.toWord(ret)

    def mtr_setVelocity(self, speed, direction):
        """
        Send a request to set the motor velocity using a 16 bit unsigned
        integer: the 15 most significant bits are for the speed (we're 
        sacrificing 1 bit of precision) and the LSB is for the direction 
        (1 for forward, 0 for reverse)
        """
        velocity = speed & 0xFFFE | direction
        try:
            self.dev.ctrl_transfer(0x40, self.MTR_SET_VEL, velocity)
        except usb.core.USBError:
            print "Could not send MTR_SET_VEL vendor request."


if __name__ == '__main__':
    import csv

    myJoystick = Joystick()
    readings = []

    # Start motor
    start = time.time()
    myJoystick.mtr_setVelocity(0xFFFF, 1)

    # Run for 1 second, then stop motor and capture encoder readings
    now = time.time()
    while now - start < 1:
        time.sleep(0.1)
        now = time.time()
    myJoystick.mtr_setVelocity(0, 1)

    start = time.time()
    while now - start < 2:
        reading = myJoystick.enc_readReg(myJoystick.ENC_ANGLE_AFTER_ZERO_POS_ADDER)
        now = time.time()
        if not myJoystick.parity(reading):
            angle = myJoystick.enc_readingToAngle(reading)
            readings.append({
                'Time': now - start,
                'Angle': angle
            })
        else:
            pass

    with open('spin_down.csv', 'w') as f:
        fieldnames = ['Time', 'Angle']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(readings)
