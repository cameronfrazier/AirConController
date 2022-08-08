# from dataclasses import InitVar, dataclass, field
from cgi import test
from pathlib import Path
# from math import isclose
# import re

from controllers import Panasonic


def extract_cmds(filepaths: list[str]) -> dict[str, list[Panasonic]]:
    cmds: dict[str, list[Panasonic]] = {}

    for filepath in filepaths:
        fp = Path(filepath)
        cmds[fp.name] = Panasonic.parse_file(fp)

    return cmds


def print_cmds(cmds_dict: dict[str, list[Panasonic]]):
    for name, cmds in cmds_dict.items():
        print(f"Set Name {name}")
        for idx, cmd in enumerate(cmds):
            print(f"Event {idx:>2} | ", end="")
            print(f"Mode: {cmd.mode:<4}", end="; ")
            print(f"Temperature: {cmd.temperature:02.1}", end="; ")
            print(f"Fan Setting: {cmd.fan:<4}", end="; ")
            print(f"Swing Setting: {cmd.swing:<4}", end="; ")
            print(f"CRC: {cmd.crc:>3}", end="; ")
            # print(f"Event {idx: >2}", cmd.data_frame, end="; ")
            print()

if __name__ == "__main__":

    testfiles = [
        "airconcontroller\data\off_set.dat",
        "airconcontroller\data\heat_16_to_30.dat",
        "airconcontroller\data\dry_16_strength_auto_strong.dat",
        "airconcontroller\data\dry_16_angle_auto_shallow_steep.dat",
        # "airconcontroller\data\dry_16_timer_off_1_12.dat",
        # "airconcontroller\data\dry_16_timer_on_1_12.dat",
        "airconcontroller\data\cool_16.dat",
        "airconcontroller\data\dry_16.dat",
        "airconcontroller\data\heat_16.dat",
    ]

    cmds_dict = extract_cmds(testfiles)
    print_cmds(cmds_dict)

    # cmds = Panasonic.parse_file(testfile)[-5:]



    # for idx, cmd in enumerate(cmds):
    #     print(f"Event {idx}")
    #     print(f"Temperature:   {cmd.temperature}")
    #     print(f"Fan Setting:   {cmd.fan}")
    #     print(f"Swing Setting: {cmd.swing}")
    #     print(f"CRC: {cmd.crc}")
    #     print(cmd.data_frame)

        # cmd.temperature = cmd.temperature
        # cmd.set_crc()
        # print(f"new CRC: {cmd.crc}")
        # print(cmd.data_frame)

    # print(f"Event{18: >2}  {cmds[18].temperature}")
    # print(cmds[18])

    # new_cmd = Panasonic(FRAME1, FRAME2)
    # print(new_cmd)
    # print(new_cmd.temperature)

    # new_cmd.temperature = 25
    # print(new_cmd)
    # print(new_cmd.temperature)
