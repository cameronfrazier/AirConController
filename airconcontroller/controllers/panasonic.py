from __future__ import annotations
from enum import Enum

from pathlib import Path
from airconcontroller.controllers.controller import Frame

from dataclasses import InitVar, dataclass, field
from math import isclose


def byte_reverse(byte_list: list[int]) -> list[int]:
    return list(reversed(byte_list))


@dataclass
class Panasonic:
    """Controller for Panasonic AC Protocol
    """
    frame1_data: InitVar[list[int] | None] = None
    frame2_data: InitVar[list[int] | None] = None

    cmd_frame: Frame = field(init=False)
    data_frame: Frame = field(init=False)

    def __post_init__(self, frame1_data: list[int] | None, frame2_data: list[int] | None):
        if frame1_data is None:
            self.cmd_frame = Frame(Panasonic.FRAME1_DEFAULT)
        else:
            self.cmd_frame = Frame(frame1_data)

        if frame2_data is None:
            self.data_frame = Frame(Panasonic.FRAME2_DEFAULT)
        else:
            self.data_frame = Frame(frame2_data)

    def __str__(self) -> str:
        output = []
        output.append(f"Frame1  {self.cmd_frame}")
        output.append(f"Frame2  {self.data_frame}")
        return "\n".join(output)






    ################################################################
    ################################################################
    ###
    ### Class Variables (Constant values)
    ###
    ################################################################
    ################################################################

    # FRAME1 Default - Never Chances
    FRAME1_DEFAULT = [0, 1, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 1, 0, 0,
            0, 0, 0, 0, 0, 1, 1, 1,
            0, 0, 1, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 1, 1, 0, 0, 0, 0, 0]

    # FRAME2 Default - Data for OFF Cmd
    FRAME2_DEFAULT = [0, 1, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 1, 0, 0,
            0, 0, 0, 0, 0, 1, 1, 1,
            0, 0, 1, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 1, 0,
            0, 0, 1, 1, 0, 1, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 1,
            1, 1, 1, 1, 0, 1, 0, 1,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 1, 1, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 1, 1, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 1,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 1, 1, 0, 0, 0, 0, 0,
            1, 0, 1, 1, 0, 0, 0, 1]

    # Protocol Properties
    HEADER = 3500
    HEADERSPACE = 1750
    MARK = 435
    SPACE0 = 435
    SPACE1 = 1300
    ENDOFFRAMESPACE = 9900
    DELTA = 200

    # Byte Index:
    MODE_SWITCH_BYTE = 6
    TEMPERATURE_BYTE = 7
    SWING_FAN_BYTE = 9
    ON_TIMER_1 = 11
    ON_TIMER_2 = 12 # First half of byte?
    ON_TIMER_1 = 12 # Last half of byte?
    ON_TIMER_2 = 13
    PROFILE_BYTE = 14
    TEMPERATURE_HALF_BYTE = 15
    MODE_MISC_BYTE = 18
    CHECKSUM_BYTE = 19

    # Limits:
    TEMPERATURE_MIN = 16
    TEMPERATURE_MAX = 30

    FAN_VALUES = {
        int("0b1010", base=2): "AUTO",
        int("0b0011", base=2): "F1", # (Slowest)
        int("0b0100", base=2): "F2",
        int("0b0101", base=2): "F3",
        int("0b0110", base=2): "F4",
        int("0b0111", base=2): "F5", # (Fastest)
    }
    FAN_SETTINGS = {
        "AUTO": int("0b1010", base=2),
        "F1": int("0b0011", base=2), # (Slowest)
        "F2": int("0b0100", base=2),
        "F3": int("0b0101", base=2),
        "F4": int("0b0110", base=2),
        "F5": int("0b0111", base=2), # (Fastest)
    }

    SWING_VALUES = {
        int("0b1111", base=2): "AUTO",
        int("0b0001", base=2): "P1", # (Horizontal)
        int("0b0010", base=2): "P2",
        int("0b0011", base=2): "P3",
        int("0b0100", base=2): "P4",
        int("0b0101", base=2): "P5", # (Ground)
    }
    SWING_SETTINGS = {
        "AUTO": int("0b1111", base=2),
        "P1": int("0b0001", base=2), # (Horizontal)
        "P2": int("0b0010", base=2),
        "P3": int("0b0011", base=2),
        "P4": int("0b0100", base=2),
        "P5": int("0b0101", base=2), # (Ground)
    }

    class MODES(Enum):
        FAN: list[int] = [0, 1, 1, 0]
        DRY: list[int] = [0, 0, 1, 0]
        COOL: list[int] = [0, 0, 1, 1]
        HEAT: list[int] = [0, 1, 0, 0]
        AUTO: list[int] = [0, 0, 0, 0]

    MODE_VALUES = {
        int("0b0110", base=2): "FAN",
        int("0b0010", base=2): "DRY",
        int("0b0011", base=2): "COOL",
        int("0b0100", base=2): "HEAT",
        int("0b0000", base=2): "AUTO",
    }
    MODE_SETTINGS = {
        "FAN": int("0b0110", base=2),
        "DRY": int("0b0010", base=2),
        "COOL": int("0b0011", base=2),
        "HEAT": int("0b0100", base=2),
        "AUTO": int("0b0000", base=2),
    }




    ################################################################
    ################################################################
    ###
    ### Static Methods
    ###
    ################################################################
    ################################################################

    @staticmethod
    def parse_file(filepath: str | Path) -> list[Panasonic]:
        lines = Path(filepath).read_text().splitlines()

        data: list[list[list[int]]] = [[[], []]]

        frame_idx = 0

        pulse_duration: int = 0
        space_duration: int = 0

        for line_idx, line in enumerate(lines):
            event, duration = line.split(" ")
            if event == "pulse":
                pulse_duration = int(duration)
                continue

            if event == "space":
                space_duration = int(duration)

                if Panasonic.check_header(pulse_duration, space_duration):
                    continue

                if Panasonic.check_end_of_frame(pulse_duration, space_duration):
                    frame_idx = not frame_idx
                    continue

                bit_value = Panasonic.get_value(pulse_duration, space_duration)
                if bit_value == 2:
                    raise ValueError(f"Bit value error at: ln{line_idx:>4}: {line} [{pulse_duration}, {space_duration}]")
                else:
                    data[-1][frame_idx].append(bit_value)

                continue

            elif event == "timeout":
                frame_idx = not frame_idx
                data.append([[], []])
            else:
                raise ValueError(f"Error of some sort at: ln{line_idx:>4}: {line} [{pulse_duration}, {space_duration}]")

        return [Panasonic(d[0], d[1]) for d in data[:-1]]

    @staticmethod
    def check_header(pulse_duration: int, space_duration: int) -> bool:
        if isclose(pulse_duration, Panasonic.HEADER, abs_tol=Panasonic.DELTA) and \
        isclose(space_duration, Panasonic.HEADERSPACE, abs_tol=Panasonic.DELTA): return True

        return False

    @staticmethod
    def check_end_of_frame(pulse_duration: int, space_duration: int) -> bool:
        if isclose(pulse_duration, Panasonic.MARK, abs_tol=Panasonic.DELTA) and \
        isclose(space_duration, Panasonic.ENDOFFRAMESPACE, abs_tol=Panasonic.DELTA): return True

        return False

    @staticmethod
    def get_value(pulse_duration: int, space_duration: int) -> int:
        if isclose(pulse_duration, Panasonic.MARK, abs_tol=Panasonic.DELTA) and \
        isclose(space_duration, Panasonic.SPACE0, abs_tol=Panasonic.DELTA): return 0

        if isclose(pulse_duration, Panasonic.MARK, abs_tol=Panasonic.DELTA) and \
        isclose(space_duration, Panasonic.SPACE1, abs_tol=Panasonic.DELTA): return 1

        return 2

    @staticmethod
    def int_to_data_byte(value: int, byte_size: int = 8) -> list[int]:
        """Convert int to lsb byte, of width <byte_size>."""
        byte_data_lsb = [int(s) for s in format(value, 'b').zfill(byte_size)]
        byte_data_msb = list(reversed(byte_data_lsb))
        return byte_data_msb

    @staticmethod
    def data_byte_to_int(byte_msb: list[int], byte_size: int = 8) -> int:
        """Convert lsb byte, of width <byte_size>, to int."""
        byte_lsb = list(reversed(byte_msb))
        byte_str = "".join([f"{d}" for d in byte_lsb])
        return int(f'0b{byte_str:0{byte_size}}', base=2)






    ################################################################
    ################################################################
    ###
    ### Data Properties
    ###
    ################################################################
    ################################################################

    @property
    def temperature(self) -> float:
        temp_degree_byte = self.data_frame.get_byte(Panasonic.TEMPERATURE_BYTE)
        half_degree_byte = self.data_frame.get_byte(Panasonic.TEMPERATURE_HALF_BYTE)
        temp_degree = Panasonic.data_byte_to_int(temp_degree_byte) // 2
        half_degree = (Panasonic.data_byte_to_int(half_degree_byte) == 128) * 0.5
        return temp_degree + half_degree

    @temperature.setter
    def temperature(self, value: int):
        print(f"Setting to {value}°C")
        half_degree = 0
        if value <= Panasonic.TEMPERATURE_MIN:
            value = Panasonic.TEMPERATURE_MIN
            half_degree = 2

        elif value >= Panasonic.TEMPERATURE_MAX:
            value = Panasonic.TEMPERATURE_MAX
            half_degree = 2

        temp_degree = int(int(value) - 16)

        if value % 1 == 0.5:
            half_degree = 128

        temp_degree_nibble = Panasonic.int_to_data_byte(temp_degree, byte_size=4)
        temp_degree_byte = [0, *temp_degree_nibble, 1, 0, 0]
        half_degree_byte = Panasonic.int_to_data_byte(half_degree)

        self.data_frame.set_byte(Panasonic.TEMPERATURE_BYTE, temp_degree_byte)
        self.data_frame.set_byte(Panasonic.TEMPERATURE_HALF_BYTE, half_degree_byte)

    @property
    def fan(self) -> str:
        fan_byte = self.data_frame.get_byte(Panasonic.SWING_FAN_BYTE)
        fan_half_byte = fan_byte[4:]
        fan_value = Panasonic.data_byte_to_int(fan_half_byte, 4)

        if fan_value in Panasonic.FAN_VALUES.keys():
            return Panasonic.FAN_VALUES[fan_value]

        return f"Unknown Fan Setting {fan_value}"

    @fan.setter
    def fan(self, fan_setting: str):
        set_value = Panasonic.FAN_SETTINGS[fan_setting]
        fan_half_byte = Panasonic.int_to_data_byte(set_value, byte_size=4)
        fan_byte = self.data_frame.get_byte(Panasonic.SWING_FAN_BYTE)
        fan_byte[4:] = fan_half_byte
        self.data_frame.set_byte(Panasonic.SWING_FAN_BYTE, fan_byte)

    @property
    def swing(self) -> str:
        swing_byte = self.data_frame.get_byte(Panasonic.SWING_FAN_BYTE)
        swing_value = Panasonic.data_byte_to_int(swing_byte[:4], 4)

        if swing_value in Panasonic.SWING_VALUES.keys():
            return Panasonic.SWING_VALUES[swing_value]

        return f"Unknown Swing Setting {swing_value}"

    @swing.setter
    def swing(self, swing_setting: str):
        set_value = Panasonic.SWING_SETTINGS[swing_setting]
        swing_half_byte = Panasonic.int_to_data_byte(set_value, byte_size=4)
        swing_byte = self.data_frame.get_byte(Panasonic.SWING_FAN_BYTE)
        swing_byte[4:] = swing_half_byte
        self.data_frame.set_byte(Panasonic.SWING_FAN_BYTE, swing_byte)

    @property
    def mode(self) -> str:
        mode_byte_lsb = self.data_frame.get_byte(Panasonic.MODE_SWITCH_BYTE)
        mode_byte_msb = byte_reverse(mode_byte_lsb)
        mode_nibble = mode_byte_msb[:4]
        modes = [e.value for e in Panasonic.MODES]
        try:
            mode_name = [e.name for e in Panasonic.MODES][modes.index(mode_nibble)]
        except ValueError:
            print(f"{modes=}")
            print(f"{mode_byte_lsb=}")
            print(f"{mode_byte_msb=}")
            raise
        return mode_name

    @mode.setter
    def mode(self, mode: Panasonic.MODES):
        mode_byte_lsb = self.data_frame.get_byte(Panasonic.MODE_SWITCH_BYTE)
        mode_byte_msb = byte_reverse(mode_byte_lsb)
        mode_byte_msb[4:] = mode.value
        mode_byte_lsb = byte_reverse(mode_byte_msb)
        self.data_frame.set_byte(Panasonic.MODE_SWITCH_BYTE, mode_byte_lsb)

        misc_byte_lsb = self.data_frame.get_byte(Panasonic.MODE_MISC_BYTE)
        misc_byte_msb = byte_reverse(misc_byte_lsb)
        if mode in [Panasonic.MODES.COOL, Panasonic.MODES.DRY]:
            misc_byte_msb[4] = 1
        if mode in [Panasonic.MODES.HEAT]:
            misc_byte_msb[4] = 0
        misc_byte_lsb = byte_reverse(misc_byte_msb)
        self.data_frame.set_byte(Panasonic.MODE_MISC_BYTE, misc_byte_lsb)

    @property
    def crc(self) -> int:
        crc_byte = self.data_frame.get_byte(Panasonic.CHECKSUM_BYTE)
        crc_value = Panasonic.data_byte_to_int(crc_byte)
        return crc_value

    def set_crc(self) -> None:
        byte_list = [self.data_frame.get_byte(idx + 1) for idx in range(18)]
        value_list = [Panasonic.data_byte_to_int(b) for b in byte_list]
        crc_value = sum(value_list) % 256
        crc_byte = Panasonic.int_to_data_byte(crc_value)
        self.data_frame.set_byte(Panasonic.CHECKSUM_BYTE, crc_byte)
