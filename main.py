# CHIP - 8 Emulator
# Author: Chirag Singh Rajput

## Memory and Registers
# 4096 Bytes Of RAM
# Programs starts at loacation 0x200 (512)
# CPU has 16 general purpose registers V0 to Vf(8Bit Each)
# Also there is an Index Register I consisting of 16 Bits
# Vf shouldn't be used for programs as it is used for flags for some instructions
# 2 Special Purpose Register for Delay and Sound Timers (8 Bit Each)
# Program Counter is 16 Bits and Stack Pointer 8 Bit Wide
# Stack contains array of 16, 16 Bit values used to store the return address i.e. CHIP-8 allows 16 level of nesting

## Input Configuration
# 16 Key Hexadecimal Keyboard ranging from key 0 through f

## Display Configuration
# 64 X 32 Monochrome Display

## Instructions
# 36 Total Instructions
# All instructions are 2 Byte long
# They are stored at even addresses in the memory

import argparse
from CPU import CPU

def main():
    parser = argparse.ArgumentParser(description = "Chip-8 Emulator")
    parser.add_argument("rom_path",
                        type = str,
                        metavar = "ROM PATH",
                        help = "Path To ROM File")
    args = parser.parse_args()
    # TODO: Verify ROM Path
    cpu = CPU(args.rom_path)

if __name__ == "__main__":
    main()
