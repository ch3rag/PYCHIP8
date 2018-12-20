#import pyglet

fonts = [0xF0, 0x90, 0x90, 0x90, 0xF0, #0
         0x20, 0x60, 0x20, 0x20, 0x70, #1
         0xF0, 0x10, 0xF0, 0x80, 0xF0, #2
         0xF0, 0x10, 0xF0, 0x10, 0xF0, #3
         0x90, 0x90, 0xF0, 0x10, 0x10, #4
         0xF0, 0x80, 0xF0, 0x10, 0xF0, #5
         0xF0, 0x80, 0xF0, 0x90, 0xF0, #6
         0xF0, 0x10, 0x20, 0x40, 0x40, #7
         0xF0, 0x90, 0xF0, 0x90, 0xF0, #8
         0xF0, 0x90, 0xF0, 0x10, 0xF0, #9
         0xF0, 0x90, 0xF0, 0x90, 0x90, #A
         0xE0, 0x90, 0xE0, 0x90, 0xE0, #B
         0xF0, 0x80, 0x80, 0x80, 0xF0, #C
         0xE0, 0x90, 0x90, 0x90, 0xE0, #D
         0xF0, 0x80, 0xF0, 0x80, 0xF0, #E
         0xF0, 0x80, 0xF0, 0x80, 0x80, #F
         ]

class CPU():
    def __init__(self, rom_path: str):
        
        self.memory = [0] * 4096
        self.register_set = [0] * 16
        self.display_buffer = [0] * 64 * 32
        self.stack = []
        self.key_inputs = [0] * 16
        self.instruction = 0
        self.index = 0
        self.sound_timer = 0
        self.delay_timer = 0
        self.draw = False
        self.pc = 0x200
        self.vx = 0
        self.vy = 0 

        self.func_map = {
            0x0000: self._0XXX,
            0x00E0: self._00E0,
            0x00EE: self._00EE,
            0x1000: self._1000,
            0x2000: self._2000,
            0x3000: self._3000,
            0x4000: self._4000,
            0x5000: self._5000,
            0x6000: self._6000,
            0x7000: self._7000,
            0x8000: self._8000

        }

        for i in range(80):
            self.memory[i] = fonts[i]
        
        with open(rom_path, "rb") as file:
            rom_data = file.read()

        i = 0
        
        while i < len(rom_data):
            self.memory[i+0x200] = rom_data[i]
            i += 1

    def _0XXX(self):
        opcode = self.instruction & 0xf0ff
        try:
            self.func_map[opcode]
        except:
            "Invalid Instruction: {}".format(opcode)

    def _00E0(self):
        # Clears the screen
        self.display_buffer = [0] * 64 * 32
        self.draw = True

    def _00EE(self):
        # Return from a subroutine
        self.pc = self.stack.pop()
    
    def _1000(self):
        # Set PC to XXX
        self.pc = self.instruction & 0x0fff
    
    def _2000(self):
        # Call to a subroutine
        self.stack.append(self.pc)
        self.pc = self.instruction & 0x0fff
    
    def _3000(self):
        # Skip next instruction if Vx = Lower Byte
        if self.register_set[self.vx] == self.instruction & 0x00ff:
            self.pc += 2
    
    def _4000(self):
        # Skip next instruction if Vx != Lower Byte
        if self.register_set[self.vx] != self.instruction & 0x00ff:
            self.pc += 2
    
    def _5000(self):
        # Skip next instruction if Vx = Vy
        if self.register_set[self.vx] == self.register_set[self.vy]:
            self.pc += 2
    
    def _6000(self):
        # Load lower Byte into Vx
        self.register_set[self.vx] = self.instruction & 0x00ff

    def _7000(self):
        # Set Vx = Vx + Lower Byte
        self.register_set[self.vx] += self.instruction & 0x00ff
    
    def _8000(self):
        opcode = self.instruction & 0xf00f
        opcode |= 0x0ff0
        try:
            self.func_map[opcode]()
        except:
            "Invalid Instruction: {}".format(opcode)
    
    def _8FF0(self):
        # Set Vx = Vy
        self.register_set[self.vx] = self.register_set[self.vy]
        self.register_set[self.vx] &= 0xff

    def _8FF1(self):
        # Set Vx = Vx | Vy
        self.register_set[self.vx] |= self.register_set[self.vy]
        self.register_set[self.vx] &= 0xff
    
    def _8FF2(self):
        # Set Vx = Vx & Vy
        self.register_set[self.vx] &= self.register_set[self.vy]
        self.register_set[self.vx] &= 0xff
    
    def _8FF3(self):
        # Set Vx = Vx XOR Vy
        self.register_set[self.vx] ^= self.register_set[self.vy]
        self.register_set[self.vx] &= 0xff
    
    def _8FF4(self):
        # Set Vx = Vx + Vy With Carry
        sum = self.register_set[self.vx] + self.register_set[self.vy]
        if sum > 0xff:
            self.register_set[0xf] = 0x1
        else:
            self.register_set[0xf] = 0x0
        self.register_set[self.vx] = sum & 0xff
    
    def _8FF5(self):
        # Vx = Vx - Vy and set Vy = 0 if Borrow
        # TODO : Cleanup
        if self.register_set[self.vy] > self.register_set[self.vx]: 
            self.register_set[0xf] = 0
        else:
            self.register_set[0xf] = 1
        self.register_set[self.vx] -= self.register_set[self.vy]
        self.register_set[self.vx] &= 0xff

    def _8FF6(self):
        # SHR Vx By 1 and Set Vy = 1 if LSB of Vx = 1
        self.register_set[0xf] = self.register_set[self.vx] & 0x0001
        self.register_set[self.vx] >>= 1

    def _8FF7(self):
        # Set Vx = Vx - Vy and set Vy = 1 if Borrow
        # TODO : Cleanup
        if self.register_set[self.vx] > self.register_set[self.vy]: 
            self.register_set[0xf] = 0
        else:
            self.register_set[0xf] = 1
        self.register_set[self.vx] -= self.register_set[self.vy]
        self.register_set[self.vx] &= 0xff
    
    def _8FFE(self):
        # SHL Vx By 1 and set Vy = 1 if MSB of Vx = 1
        self.register_set[0xf] = (self.register_set[self.vx] & 0x0080) >> 7
        self.register_set[self.vx] <<= 1
        self.register_set[self.vx] &= 0xff
    
    def _9000(self):
        # Skip Next Instruction If Vx != Vy
        if self.register_set[self.vx] != self.register_set[self.vy]:
            self.pc += 2
    
    def _A000(self):
        # Set Index Register to nnn in Annn
        self.index = self.instruction & 0x0fff
    
    
    def cycle(self):
        self.instruction = self.memory[self.pc]
        self.vx = (self.instruction & 0x0f00) >> 8
        self.vy = (self.instruction & 0x00f0) >> 4
        opcode  = (self.instruction & 0xf000)
        try:
            self.func_map[opcode]()
        except:
            "Invalid Instruction: {}".format(opcode)

        self.pc += 2
        if self.sound_timer > 0:
            self.sound_timer -= 1
            if self.sound_timer == 0:
                pass
        
        if self.delay_timer > 0:
            self.delay_timer -= 1


    
        