from dataclasses import InitVar, dataclass, field
from pathlib import Path
from math import isclose
import re


HEADER = 3500
HEADERSPACE = 1750
MARK = 435
SPACE0 = 435
SPACE1 = 1300
ENDOFFRAMESPACE = 9900
DELTA = 200


FRAME1 = [0, 1, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 1, 0, 0,
          0, 0, 0, 0, 0, 1, 1, 1,
          0, 0, 1, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0,
          0, 1, 1, 0, 0, 0, 0, 0]

FRAME2 = [0, 1, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 1, 0, 0,
          0, 0, 0, 0, 0, 1, 1, 1,
          0, 0, 1, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0,
          1, 0, 0, 0, 0, 0, 1, 0,
          0, 0, 0, 0, 0, 1, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 1,
          1, 1, 1, 1, 0, 1, 0, 1,
          0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0,
          0, 1, 1, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 1, 1, 0,
          0, 0, 0, 0, 0, 0, 0, 0,
          0, 1, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 1,
          0, 0, 0, 0, 0, 0, 0, 0,
          0, 1, 1, 0, 0, 0, 0, 0,
          0, 0, 1, 0, 0, 0, 0, 1]


DATA_MODE_SWITCH_BYTE = 6

DATA_TEMPERATURE_BYTE = 7
DATA_TEMPERATURE_HALF_BYTE = 15
TEMPERATURE_MIN = 16
TEMPERATURE_MAX = 30

DATA_SWING_FAN_BYTE = 9
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

DATA_ON_TIMER_1 = 11
DATA_ON_TIMER_2 = 12 # First half of byte?
DATA_ON_TIMER_1 = 12 # Last half of byte?
DATA_ON_TIMER_2 = 13

DATA_PROFILE = 14
DATA_CHECKSUM_BYTE = 19



def check_header(pulse_duration: int, space_duration: int) -> bool:
    if isclose(pulse_duration, HEADER, abs_tol=DELTA) and \
       isclose(space_duration, HEADERSPACE, abs_tol=DELTA): return True

    return False

def check_end_of_frame(pulse_duration: int, space_duration: int) -> bool:
    if isclose(pulse_duration, MARK, abs_tol=DELTA) and \
       isclose(space_duration, ENDOFFRAMESPACE, abs_tol=DELTA): return True

    return False

def get_value(pulse_duration: int, space_duration: int) -> int:
    if isclose(pulse_duration, MARK, abs_tol=DELTA) and \
       isclose(space_duration, SPACE0, abs_tol=DELTA): return 0

    if isclose(pulse_duration, MARK, abs_tol=DELTA) and \
       isclose(space_duration, SPACE1, abs_tol=DELTA): return 1

    return 2


def int_to_data_byte(value: int, byte_size: int = 8) -> list[int]:
    """Convert int to lsb byte, of width <byte_size>."""
    byte_data_lsb = [int(s) for s in format(value, 'b').zfill(byte_size)]
    byte_data_msb = list(reversed(byte_data_lsb))
    return byte_data_msb

def data_byte_to_int(byte_msb: list[int], byte_size: int = 8) -> int:
    """Convert lsb byte, of width <byte_size>, to int."""
    byte_lsb = list(reversed(byte_msb))
    byte_str = "".join([f"{d}" for d in byte_lsb])
    return int(f'0b{byte_str:0{byte_size}}', base=2)


@dataclass
class Frame:
    data: list[int]

    def get_byte(self, byte_num: int) -> list[int]:
        start_idx = (byte_num - 1) * 8
        end_idx = start_idx + 8
        byte_data_msb = self.data[start_idx:end_idx]
        return byte_data_msb

    def set_byte(self, byte_num: int, value: list[int]):
        start_idx = (byte_num - 1) * 8
        end_idx = start_idx + 8
        self.data[start_idx:end_idx] = value

    def __str__(self) -> str:
        data_str = ''.join([f'{d}' for d in self.data])
        data_str = re.sub(r'([01]{8})', r'\1 ', data_str)
        return data_str


@dataclass
class CommandFrame(Frame):
    pass

@dataclass
class DataFrame(Frame):

    @property
    def temperature(self) -> float:
        temp_degree_byte = self.get_byte(DATA_TEMPERATURE_BYTE)

        half_degree_byte = self.get_byte(DATA_TEMPERATURE_HALF_BYTE)

        temp_degree = data_byte_to_int(temp_degree_byte) // 2
        half_degree = (data_byte_to_int(half_degree_byte) == 128) * 0.5

        return temp_degree + half_degree

    @temperature.setter
    def temperature(self, value: int):
        half_degree = 0
        if value <= TEMPERATURE_MIN:
            value = TEMPERATURE_MIN
            half_degree = 2

        elif value >= TEMPERATURE_MAX:
            value = TEMPERATURE_MAX
            half_degree = 2

        temp_degree = int(value * 2)

        if value % 1 == 0.5:
            half_degree = 128

        temp_degree_byte = int_to_data_byte(temp_degree)
        half_degree_byte = int_to_data_byte(half_degree)

        self.set_byte(DATA_TEMPERATURE_BYTE, temp_degree_byte)
        self.set_byte(DATA_TEMPERATURE_HALF_BYTE, half_degree_byte)

    @property
    def fan(self) -> str:
        fan_byte = self.get_byte(DATA_SWING_FAN_BYTE)
        fan_half_byte = fan_byte[4:]
        fan_value = data_byte_to_int(fan_half_byte, 4)

        if fan_value in FAN_VALUES.keys():
            return FAN_VALUES[fan_value]

        return f"Unknown Fan Setting {fan_value}"

    @fan.setter
    def fan(self, fan_setting: str):
        set_value = FAN_SETTINGS[fan_setting]
        fan_half_byte = int_to_data_byte(set_value, byte_size=4)
        fan_byte = self.get_byte(DATA_SWING_FAN_BYTE)
        fan_byte[4:] = fan_half_byte
        self.set_byte(DATA_SWING_FAN_BYTE, fan_byte)

    @property
    def swing(self) -> str:
        swing_byte = self.get_byte(DATA_SWING_FAN_BYTE)
        swing_value = data_byte_to_int(swing_byte[:4], 4)

        if swing_value in SWING_VALUES.keys():
            return SWING_VALUES[swing_value]

        return f"Unknown Swing Setting {swing_value}"

    @swing.setter
    def swing(self, swing_setting: str):
        set_value = SWING_SETTINGS[swing_setting]
        swing_half_byte = int_to_data_byte(set_value, byte_size=4)
        swing_byte = self.get_byte(DATA_SWING_FAN_BYTE)
        swing_byte[4:] = swing_half_byte
        self.set_byte(DATA_SWING_FAN_BYTE, swing_byte)




@dataclass
class Command:
    frame1_data: InitVar[list[int]]
    frame2_data: InitVar[list[int]]

    cmd_frame: CommandFrame = field(init=False)
    data_frame: DataFrame = field(init=False)

    def __post_init__(self, frame1_data, frame2_data):
        self.cmd_frame = CommandFrame(frame1_data)
        self.data_frame = DataFrame(frame2_data)

    def __str__(self) -> str:
        output = []
        output.append(f"Frame1  {self.cmd_frame}")
        output.append(f"Frame2  {self.data_frame}")
        return "\n".join(output)


def main(filepath: Path) -> list:
    lines = filepath.read_text().splitlines()

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

            if check_header(pulse_duration, space_duration):
                continue

            if check_end_of_frame(pulse_duration, space_duration):
                frame_idx = not frame_idx
                continue

            bit_value = get_value(pulse_duration, space_duration)
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

    return data[:-1]

if __name__ == "__main__":

    # testfile = Path("airconcontroller\\data\\off_set.dat").resolve()
    # testfile = Path("airconcontroller\\data\\heat_16_to_30.dat").resolve()
    testfile = Path("airconcontroller\\data\\dry_16_strength_auto_strong.dat").resolve()
    # testfile = Path("airconcontroller\\data\\dry_16_angle_auto_shallow_steep.dat").resolve()
    # testfile = Path("airconcontroller\\data\\dry_16_timer_off_1_12.dat").resolve()
    # testfile = Path("airconcontroller\\data\\dry_16_timer_on_1_12.dat").resolve()
    # testfile = Path("airconcontroller\\data\\cool_16.dat").resolve()
    # testfile = Path("airconcontroller\\data\\dry_16.dat").resolve()
    # testfile = Path("airconcontroller\\data\\heat_16.dat").resolve()

    data = main(testfile)

    cmds = [Command(d[0], d[1]) for d in data]

    for idx, cmd in enumerate(cmds):
        print(f"Event {idx}")
        print(f"Temperature:   {cmd.data_frame.temperature}")
        print(f"Fan Setting:   {cmd.data_frame.fan}")
        print(f"Swing Setting: {cmd.data_frame.swing}")

    print(FAN_VALUES)
    # print(f"Event{18: >2}  {cmds[18].data_frame.temperature}")
    # print(cmds[18])

    # new_cmd = Command(FRAME1, FRAME2)
    # print(new_cmd)
    # print(new_cmd.data_frame.temperature)

    # new_cmd.data_frame.temperature = 25
    # print(new_cmd)
    # print(new_cmd.data_frame.temperature)
