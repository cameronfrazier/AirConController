
import re

from dataclasses import dataclass


@dataclass
class Frame:
    """Storage of Frame byte data.

    Data is stored as a string of ints
    """
    data: list[int]

    def get_byte(self, byte_num: int) -> list[int]:
        """Return specified byte of the frame.

        Args:
            byte_num (int): 1-indexed byte index

        Returns:
            list[int]: list of bit values
        """
        start_idx = (byte_num - 1) * 8
        end_idx = start_idx + 8
        byte_data_msb = self.data[start_idx:end_idx]
        return byte_data_msb

    def set_byte(self, byte_num: int, value: list[int]):
        """Set specified byte of the frame.

        Args:
            byte_num (int): 1-indexed byte index
            value (list[int]): list of bit values
        """
        start_idx = (byte_num - 1) * 8
        end_idx = start_idx + 8
        self.data[start_idx:end_idx] = value

    def __str__(self) -> str:
        data_str = ''.join([f'{d}' for d in self.data])
        data_str = re.sub(r'([01]{8})', r'\1 ', data_str)
        return data_str