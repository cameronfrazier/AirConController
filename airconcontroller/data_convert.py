#! python
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from struct import pack, unpack
from typing import Tuple, Union

import numpy as np
from colorama import Fore, Style, init

from cCmdString import CmdString


# Colorama settings
init(autoreset=True)


def make_mask(collected, ref=None, spacing=8):
    c = collected.copy()
    if ref is not None:
        if isinstance(ref[0], (list,)):
            c.extend(ref)
        else:
            c.append(ref)

    mask = [False] * (len(c[0]) // spacing)
    for cIdx in range(len(c) - 1):
        for mIdx in range(len(c[0])):
            mask[mIdx // spacing] |= (
                c[cIdx][mIdx] ^ c[cIdx + 1][mIdx])

    return mask


def print_capture(c, mask=None, spacing=8, display_filter=None):
    if isinstance(c[0], (list,)):
        mask = make_mask(c, mask, spacing=spacing)
        [print_capture(d, mask, spacing=spacing,
                       display_filter=display_filter) for d in c]

    else:
        length = len(c)

        cc = [f"{''.join([f'{j}' for j in c[spacing * i:spacing * i + spacing]])}" for i in range(38)]  # noqa
        for mIdx in range(len(mask or [])):
            if mask[mIdx]:
                cc[mIdx] = Style.BRIGHT + cc[mIdx] + Style.RESET_ALL
            else:
                cc[mIdx] = Fore.LIGHTBLACK_EX + cc[mIdx] + Style.RESET_ALL

        if display_filter is not None:
            cc = [cc[idx] for idx in range(len(cc)) if idx * 8 in display_filter]

        print((" ".join(cc)).strip(), f"  {length}")


def parse_file(file: Path):
    # CmdStr = CmdString.default()
    out: list[int] = []
    collected = []
    with open(file) as ifp:
        for line in ifp:

            line = line.strip()
            t, pulse_len, *_ = line.split(" ")

            if t == "space":
                length = int(pulse_len)

                if CmdString.get_space(length) == CmdString.SEPARATOR:
                    out = []  # uncomment to exclude leadin
                    continue

                elif CmdString.get_space(length) == CmdString.SPACE_INTRO:
                    continue

                elif CmdString.get_space(length) == CmdString.SPACE_SHORT:
                    out.append(0)
                    continue

                elif CmdString.get_space(length) == CmdString.SPACE_LONG:
                    out.append(1)
                    continue

            elif t == "timeout":
                if len(out):
                    collected.append(list(out))
                # if len(out) == CmdString.EXPECTED_LENGTH:
                #     collected.append(list(out))
                # else:
                #     print(f"Line too short ({len(out)}), dropped")
                #     print(out)

                out = []
                # break

    print(f"{file.name}: {len(collected or [])}")
    if len(collected):
        return collected

    return None


def process_to_csv(files: list[Path]):

    for file in files:
        outfile = file.with_suffix(".csv")
        with open(file) as ifp:
            data = []
            data_set = []
            for line in ifp:
                if line.startswith("Running"):
                    continue
                t, length, *_ = line.strip().split(" ")
                data_set.append([t, int(length)])
                if t == "timeout":
                    data.append(data_set.copy())
                    data_set = []

        csv_data = [[data[0][dIdx][0]] for dIdx in range(len(data[0]))]
        for dsIdx in range(len(data)):
            for dIdx in range(len(data[dsIdx])):
                csv_data[dIdx].append(data[dsIdx][dIdx][1])

        with open(outfile, 'w', newline='') as ofp:
            csvwriter = csv.writer(ofp)
            csvwriter.writerows(csv_data)


def processs(
        files: list[Path],
        masks: list[Path] = None,
        display_filter: list[int] = None):

    mask = None
    if masks is not None:
        for m in masks:
            mask = parse_file(m)
            if mask:
                break

    for file in files:
        collected = parse_file(file)
        print_capture(collected, mask, display_filter=display_filter)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--startswith")
    parser.add_argument("-e", "--endswith")
    parser.add_argument("-ms", "--mask-startswith")
    parser.add_argument("-me", "--mask-endswith")
    parser.add_argument("-f", "--filter", action="append")
    parser.add_argument("--to-csv", action="store_true")

    args = parser.parse_args()

    FILES = [f.resolve() for f in Path("./data").iterdir()]
    FILES = [f for f in FILES if f.name.endswith(".dat")]

    files = list(FILES)
    if args.startswith:
        files = [f for f in files if f.name.startswith(args.startswith)]

    if args.endswith:
        files = [f for f in files if f.name.endswith(args.startswith)]

    mask = None
    if args.mask_startswith:
        mask = [f for f in FILES if f.name.startswith(args.mask_startswith)]

    if args.mask_endswith:
        mask = [f for f in (mask or FILES)
                if f.name.startswith(args.mask_endswith)]

    filters = None
    print(args.filter)
    if args.filter:
        filters = []
        for fil in args.filter:
            if fil in ["BYTE_00", "ID0_BYTE"]:
                filters.append(CmdString.BYTE_00)
            if fil in ["BYTE_01", "ID1_BYTE"]:
                filters.append(CmdString.BYTE_01)
            if fil in ["BYTE_02", "ID2_BYTE"]:
                filters.append(CmdString.BYTE_02)
            if fil in ["BYTE_03", "ID3_BYTE"]:
                filters.append(CmdString.BYTE_03)
            if fil in ["BYTE_04", "ID4_BYTE"]:
                filters.append(CmdString.BYTE_04)
            if fil in ["BYTE_05", "MODE_BYTE"]:
                filters.append(CmdString.BYTE_05)
            if fil in ["BYTE_06", "TEMP_BYTE"]:
                filters.append(CmdString.BYTE_06)
            if fil in ["BYTE_07"]:
                filters.append(CmdString.BYTE_07)
            if fil in ["BYTE_08", "FAN_BYTE"]:
                filters.append(CmdString.BYTE_08)
            if fil in ["BYTE_09"]:
                filters.append(CmdString.BYTE_09)
            if fil in ["BYTE_10", "TIMER_ON_BYTE"]:
                filters.append(CmdString.BYTE_10)
            if fil in ["BYTE_11", "TIMER_DATA_BYTE"]:
                filters.append(CmdString.BYTE_11)
            if fil in ["BYTE_12", "TIMER_OFF_BYTE"]:
                filters.append(CmdString.BYTE_12)
            if fil in ["BYTE_13"]:
                filters.append(CmdString.BYTE_13)
            if fil in ["BYTE_14", "TEMP_MOD_BYTE"]:
                filters.append(CmdString.BYTE_14)
            if fil in ["BYTE_15"]:
                filters.append(CmdString.BYTE_15)
            if fil in ["BYTE_16"]:
                filters.append(CmdString.BYTE_16)
            if fil in ["BYTE_17", "CHECKSUM0_BYTE"]:
                filters.append(CmdString.BYTE_17)
            if fil in ["BYTE_18", "CHECKSUM1_BYTE"]:
                filters.append(CmdString.BYTE_18)

    if args.to_csv:
        process_to_csv(files)
    else:
        processs(files, mask, display_filter=filters)

    # cmd = CmdString()
    # print(cmd.command)

