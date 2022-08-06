import attr
import numpy as np
from pathlib import Path
from typing import Union


class BitArray(np.ndarray):

    def __new__(cls, bit_str: str):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.array([bool(int(a)) for a in bit_str], dtype=bool).view(cls)

        # Finally, we must return the newly created object:
        return obj


@attr.s
class CmdString:
    bits: np.ndarray = attr.ib(default=None)
    # cmd:str = attr.ib(init=False, default="0" * 152)
    total_length: int = attr.ib(init=False, default=152)

    # NB: These length are defined in terms of the number of 38kHz modulated
    # ticks that occur in that time
    # I believe that the protocol is similar to an NEC variant, but extended

    # Format:
    #     PULSE_INTRO, SPACE_INTRO, LEADIN_BITS, SEPARATOR,
    #     PULSE_INTRO, SPACE_INTRO, DATA, PULSE

    # DATA (19 Bytes):
    BYTE_00 = ID0_BYTE = 8 * 0
    #   BYTE_00:     Unknown (Constant ID (manufacturer?), same as LEADIN_BITS)
    BYTE_01 = ID1_BYTE = 8 * 1
    #   BYTE_01:     Unknown (Constant ID (type?), same as LEADIN_BITS)
    BYTE_02 = ID2_BYTE = 8 * 2
    #   BYTE_02:     Unknown (Constant ID (model?), same as LEADIN_BITS)
    BYTE_03 = ID3_BYTE = 8 * 3
    #   BYTE_03:     Unknown (Constant ID (version?), same as LEADIN_BITS)
    BYTE_04 = ID4_BYTE = 8 * 4
    #   BYTE_04:     Unknown (Always 0?, same as LEADIN_BITS)
    BYTE_05 = MODE_BYTE = 8 * 5
    MODE_DRY = 0x1
    MODE_COOL = 0x2
    MODE_HEAT = 0x3
    MODES = {
        "DRY": BitArray("10000100"),
        "COOL": BitArray("10001100"),
        "HEAT": BitArray("10000010"),
    }
    #   BYTE_05:     Mode Setting
    #                10000100 ==  dry
    #                10001100 ==  cool
    #                10000010 ==  heat
    BYTE_06 = TEMP_BYTE = 8 * 6
    #   BYTE_06:     Temperature (int, little endien, shift >>1 )
    #                00000100 == 16 degC
    #                 ...
    #                00001100 == 24 degC
    #                 ...
    #                00111100 == 30 degC
    BYTE_07 = 8 * 7
    #   BYTE_07:     Unknown
    BYTE_08 = FAN_BYTE = 8 * 8
    FAN_ANGLE_MASK = BitArray("11110000")
    FAN_ANGLE_AUTO = 0x10
    FAN_ANGLE00 = 0x20
    FAN_ANGLE20 = 0x30
    FAN_ANGLE40 = 0x40
    FAN_ANGLE60 = 0x50
    FAN_ANGLE80 = 0x60
    FAN_ANGLES = {
        "ANGLE_AUTO": BitArray("11110000"),
        "ANGLE00": BitArray("10000000"),
        "ANGLE20": BitArray("01000000"),
        "ANGLE40": BitArray("11000000"),
        "ANGLE60": BitArray("00100000"),
        "ANGLE80": BitArray("10100000"),
    }
    #   BYTE_08:     Angle[:4] and Strength[4:]
    #                11110000 == Auto Angle / Sweeping
    #                10000000 == Angle 1 [~  0°] (almost horizontal)
    #                01000000 == Angle 2 [~ 20°]
    #                11000000 == Angle 3 [~ 40°]
    #                00100000 == Angle 4 [~ 60°]
    #                10100000 == Angle 5 [~ 80°] (Steepest angle down)
    #
    FAN_POWER_MASK = BitArray("00001111")
    FAN_POWER_AUTO = 0x100
    FAN_POWER025 = 0x200
    FAN_POWER050 = 0x300
    FAN_POWER075 = 0x400
    FAN_POWER100 = 0x500
    FAN_POWERS = {
        "FAN_POWER_AUTO": BitArray("00000101"),
        "FAN_POWER025": BitArray("00001100"),
        "FAN_POWER050": BitArray("00000010"),
        "FAN_POWER075": BitArray("00001010"),
        "FAN_POWER100": BitArray("00001110"),
    }
    #                00000101 == Auto Fan Strength
    #                00001100 ==  25%
    #                00000010 ==  50%
    #                00001010 ==  75%
    #                00001110 == 100%
    BYTE_09 = 8 * 9
    #   BYTE_09:     Unknown (Always 0?)
    BYTE_10 = TIMER_ON_BYTE = 8 * 10
    #   BYTE_10:     Unknown (Timer ON related)
    BYTE_11 = TIMER_DATA_BYTE = 8 * 11
    #   BYTE_11:     Unknown (Timer ON/OFF related)
    BYTE_12 = TIMER_OFF_BYTE = 8 * 12
    #   BYTE_12:     Unknown (Timer OFF related)
    BYTE_13 = 8 * 13
    #   BYTE_13:     Unknown
    BYTE_14 = TEMP_MOD_BYTE = 8 * 14
    #   BYTE_14:     Temp Limit / Half Degree modifiers
    #                01000000 == is limit of temp range (16.0 / 30.0 degC)
    #                00000001 == add 0.5 degC to value of BYTE_06
    BYTE_15 = 8 * 15
    #   BYTE_15:     Unknown
    BYTE_16 = 8 * 16
    #   BYTE_16:     Unknown
    BYTE_17 = CHECKSUM0_BYTE = 8 * 17
    #   BYTE_17:     Checksum (TBC)
    BYTE_18 = CHECKSUM1_BYTE = 8 * 18
    #   BYTE_18:     Checksum (TBC)

    SPACE_SHORT = 394  # 440
    SPACE_LONG = 1250  # 1280
    PULSE = 496
    MARGIN = 100  # 150
    PULSE_INTRO = 3550  # 3500
    SPACE_INTRO = 1680  # 1750
    SEPARATOR = 9990  # 9880
    EXPECTED_LENGTH = 152

    LEADIN_BITS = "".join([
        "01000000",  # 2, Constant ID (manufacturer?)
        "00000100",  # 32, Constant ID (type?)
        "00000111",  # 224, Constant ID (model?)
        "00100000",  # 4, Constant ID (version?)
        "00000000",
        "00000000",
        "00000000",
        "01100000"
    ])

    max_temp = 30
    min_temp = 16

    def __attrs_post_init__(self):
        if self.bits is None:
            self.bits = np.zeros(152, dtype=bool)
            copy_bytes = [
                self.ID0_BYTE, self.ID1_BYTE,
                self.ID2_BYTE, self.ID3_BYTE,
                self.ID4_BYTE
            ]
            for bt in copy_bytes:
                self.set_byte(bt, self.get_byte(bt, src=self.lead))
            self.temp = 20

    @classmethod
    def default(cls):
        c = cls(bits=np.zeros(152, dtype=bool))
        copy_bytes = [
            c.ID0_BYTE, c.ID1_BYTE,
            c.ID2_BYTE, c.ID3_BYTE,
            c.ID4_BYTE
        ]
        for bt in copy_bytes:
            c.set_byte(bt, c.get_byte(bt, src=c.lead))

        c.temp = 20
        c.mode = CmdString.MODE_HEAT

        c.fan_set_power_auto()
        c.fan_set_angle_auto()

        return c


    @classmethod
    def from_array(cls, array: np.ndarray):
        array = np.array(array, dtype=bool)
        c = cls(bits=array)
        return c

    @classmethod
    def load_file(cls, file: Path):
        cmd = cls()
        return cmd

    @property
    def lead(self):
        return BitArray(self.LEADIN_BITS)

    @property
    def lead_timings(self):
        L = [self.PULSE_INTRO, self.SPACE_INTRO]
        L.extend(self.bit_to_pulse(self.lead))
        L.extend([self.PULSE, self.SEPARATOR])
        return L

    @property
    def cmd_timings(self):
        C = self.lead
        C.extend([self.PULSE_INTRO, self.SPACE_INTRO])
        C.extend(self.bit_to_pulse(self.bits))
        C.extend([self.PULSE])
        return C

    def get_byte(self, start_bit, src=None):
        sb = start_bit
        eb = start_bit + 8
        if src is not None:
            value = src[sb:eb]
        else:
            value = self.bits[sb:eb]
        # print(f"Getting Byte[{sb}:{eb}] = {value} | src = {src}")
        return value

    def set_byte(self, start_bit, value: np.ndarray, trg=None):
        sb = start_bit
        eb = start_bit + 8
        if trg is not None:
            trg[sb:eb] = value
        else:
            self.bits[sb:eb] = value
        # print(f"Setting Byte[{sb}:{eb}] = {value} | trg = {trg}")

    def bit_to_pulse(self, bit):
        if isinstance(bit, (str, list,)):
            bits = []
            for b in bit:
                bits.extend(self.bit_to_pulse(int(b)))

            if len(bit) == 1:
                return bits[0]
            return bits

        if isinstance(bit, (int,)):
            if bit:  # a 1 bit
                return [self.PULSE, self.SPACE_LONG]
            else:    # a 0 bit
                return [self.PULSE, self.SPACE_SHORT]

    def display(self, bit_array=None):
        bts = bit_array or self.bits
        cc = ""
        for idx in range(len(bts // 8)):
            cc += ''.join([f"{int(b)}" for b in bts[idx * 8:(idx + 1) * 8]]) + " "
        print(cc.strip())
        # print("")

    @property
    def isTempLimit(self):
        if self.bits is not None:
            return bool(self.bits[123])
        return None

    @property
    def temp(self):
        if self.bits is not None:
            half_degree = 0.5 * self.get_byte(self.TEMP_MOD_BYTE)[7]
            temp = self.get_byte(self.TEMP_BYTE)
            temp = self.from_little_endien(temp, lshift=1) + half_degree
            return temp
        return None

    @temp.setter
    def temp(self, value: float):
        if value is not None:
            if value > self.max_temp:
                value = self.max_temp

            if value < self.min_temp:
                value = self.min_temp

            temp_int = int(value)
            temp_bits = self.to_little_endien(temp_int, lpad=1)
            self.set_byte(self.TEMP_BYTE, temp_bits)

            mod_bits = np.zeros(8, dtype=bool)
            if value in [self.min_temp, self.max_temp]:
                mod_bits[1] = 1
            else:
                mod_bits[7] = bool(value - temp_int)
            self.set_byte(self.TEMP_MOD_BYTE, mod_bits)

    @property
    def mode(self):
        if self.bits is not None:
            mode = self.get_byte(self.MODE_BYTE)
            return mode
        return None

    @mode.setter
    def mode(self, mode_to_set: Union[str, BitArray]):
        if mode_to_set is not None:
            if mode_to_set in ["DRY", self.MODE_DRY]:
                self.set_byte(self.MODE_BYTE, self.MODES["DRY"])
            elif mode_to_set in ["COOL", self.MODE_COOL]:
                self.set_byte(self.MODE_BYTE, self.MODES["COOL"])
            elif mode_to_set in ["HEAT", self.MODE_HEAT]:
                self.set_byte(self.MODE_BYTE, self.MODES["HEAT"])
            else:
                print(f"Unknown mode: [{mode_to_set}]")

    def mode_set_dry(self):
        self.mode = self.MODE_DRY

    def mode_set_cool(self):
        self.mode = self.MODE_COOL

    def mode_set_heat(self):
        self.mode = self.MODE_HEAT

    @property
    def fan(self):
        if self.bits is not None:
            fan = self.get_byte(self.FAN_BYTE)
            return fan
        return None

    @fan.setter
    def fan(self, fan_power_and_angle):
        if fan_power_and_angle is not None:
            self.set_byte(self.FAN_BYTE, fan_power_and_angle)

    def fan_set_power_angle(self, power=None, angle=None):
        if power is not None or angle is not None:
            if angle is None:
                angle = self.get_byte(self.FAN_BYTE)
                angle &= self.FAN_ANGLE_MASK
            if power is None:
                power = self.get_byte(self.FAN_BYTE)
                power &= self.FAN_POWER_MASK

            self.fan = power | angle

    def fan_set_power_auto(self):
        self.fan_set_power_angle(power=self.FAN_POWER_AUTO)

    def fan_set_power_25(self):
        self.fan_set_power_angle(power=self.FAN_POWER025)

    def fan_set_power_50(self):
        self.fan_set_power_angle(power=self.FAN_POWER050)

    def fan_set_power_75(self):
        self.fan_set_power_angle(power=self.FAN_POWER075)

    def fan_set_power_100(self):
        self.fan_set_power_angle(power=self.FAN_POWER100)

    def fan_set_angle_auto(self):
        self.fan_set_power_angle(angle=self.FAN_ANGLE_AUTO)

    def fan_set_angle_00(self):
        self.fan_set_power_angle(angle=self.FAN_ANGLE00)

    def fan_set_angle_20(self):
        self.fan_set_power_angle(angle=self.FAN_ANGLE20)

    def fan_set_angle_40(self):
        self.fan_set_power_angle(angle=self.FAN_ANGLE40)

    def fan_set_angle_60(self):
        self.fan_set_power_angle(angle=self.FAN_ANGLE60)

    def fan_set_angle_80(self):
        self.fan_set_power_angle(angle=self.FAN_ANGLE80)

    @staticmethod
    def from_little_endien(bit_array, bits=8, lshift=0, rshift=0):
        val = 0
        if lshift > 0:
            bit_array = bit_array[lshift:] + [0] * lshift
            bit_array = bit_array[:bits]
        if rshift > 0:
            bit_array = [0] * rshift + bit_array
            bit_array = bit_array[:bits]

        for idx in range(len(bit_array)):
            if bit_array[idx]:
                val += 2**idx
        return val

    @staticmethod
    def to_little_endien(value, bits=8, lpad=0, rpad=0):
        val = [int(b) for b in list(reversed(f"{value:0{bits}b}"))]
        val = [0] * lpad + val + [0] * rpad
        return np.array(val[:bits], dtype=bool)

    @staticmethod
    def get_pulse(test_length):

        lengths = np.array([
            CmdString.PULSE,
            CmdString.PULSE_INTRO],
            dtype=int)
        return lengths[np.argmin(np.abs(lengths - test_length))]

    @staticmethod
    def get_space(test_length):

        lengths = np.array([
            CmdString.SPACE_SHORT,
            CmdString.SPACE_LONG,
            CmdString.SEPARATOR,
            CmdString.SPACE_INTRO],
            dtype=int)
        return lengths[np.argmin(np.abs(lengths - test_length))]


if __name__ == '__main__':
    cmd = CmdString.default()
    print(cmd.display())
