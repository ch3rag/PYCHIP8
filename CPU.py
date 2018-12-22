import pyglet
from random import randint
from pyglet.sprite import Sprite

def log(message):
    print(message)

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
         0xE0, 0x90, 0xE0, 0x90, 0xE0, #Bs
         0xF0, 0x80, 0x80, 0x80, 0xF0, #C
         0xE0, 0x90, 0x90, 0x90, 0xE0, #D
         0xF0, 0x80, 0xF0, 0x80, 0xF0, #E
         0xF0, 0x80, 0xF0, 0x80, 0x80, #F
         ]

KEY_MAP = {
    pyglet.window.key.X:    0x0,
    pyglet.window.key._1:   0x1,
    pyglet.window.key._2:   0x2,
    pyglet.window.key._3:   0x3,
    pyglet.window.key.Q:    0x4,
    pyglet.window.key.W:    0x5,
    pyglet.window.key.E:    0x6,
    pyglet.window.key.A:    0x7,
    pyglet.window.key.S:    0x8,
    pyglet.window.key.D:    0x9,
    pyglet.window.key.Z:    0xA,
    pyglet.window.key.C:    0xB,
    pyglet.window.key._4:   0xC,
    pyglet.window.key.R:    0xD,
    pyglet.window.key.F:    0xE,
    pyglet.window.key.V:    0xF
}

class CPU(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = [0] * 4096
        self.register_set = [0] * 16
        self.display_buffer = [0] * 2048
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
        self.key_wait = False

        self.pixel = pyglet.resource.image("pixel.png")
        self.buzz  = pyglet.resource.media("buzz.wav", streaming = False)

        self.batch = pyglet.graphics.Batch()
        self.sprites = []
        i = 0
        while(i < 2048):
            self.sprites.append(pyglet.sprite.Sprite(self.pixel, batch = self.batch))
            i += 1

        self.func_map = {
            0x0000: self._0000,
            0x00E0: self._00E0,
            0x00EE: self._00EE,
            0x1000: self._1000,
            0x2000: self._2000,
            0x3000: self._3000,
            0x4000: self._4000,
            0x5000: self._5000,
            0x6000: self._6000,
            0x7000: self._7000,
            0x8000: self._8000,
            0x8FF0: self._8FF0,
            0x8FF1: self._8FF1,
            0x8FF2: self._8FF2,
            0x8FF3: self._8FF3,
            0x8FF4: self._8FF4,
            0x8FF5: self._8FF5,
            0x8FF6: self._8FF6,
            0x8FF7: self._8FF7,
            0x8FFE: self._8FFE,
            0x9000: self._9000,
            0xA000: self._A000,
            0xB000: self._B000,
            0xC000: self._C000,
            0xE000: self._E000,
            0xE09E: self._E09E,
            0xE0A1: self._E0A1,
            0xF000: self._F000,
            0xF007: self._F007,
            0xF00A: self._F00A,
            0xF015: self._F015,
            0xF018: self._F018,
            0xF01E: self._F01E,
            0xF029: self._F029,
            0xF033: self._F033,
            0xF055: self._F055,
            0xF065: self._F065,
            0xD000: self._D000
        }

        for i in range(80):
            self.memory[i] = fonts[i]
        #print(self.memory)

    def load_rom(self, rom_path: str):
        with open(rom_path, "rb") as file:
            rom_data = file.read()
        i = 0
        while i < len(rom_data):
            self.memory[i+0x200] = rom_data[i]
            i += 1

    def _0000(self):
        opcode = self.instruction & 0x00ff
        try:
            self.func_map[opcode]()
        except:
            # log"Invalid Instruction _0000: %X" % opcode)
            pass

    def _00E0(self):
        # Clears the screen
        # log"Clears the screen 0x00E0")
        self.display_buffer = [0] * 64 * 32
        self.draw = True

    def _00EE(self):
        # Return from a subroutine
        # log"Return from a sub routine: 0x00EE")
        self.pc = self.stack.pop()
    
    def _1000(self):
        # Set PC to XXX
        # log"Set PC to XXX: 0x1000")
        self.pc = self.instruction & 0x0fff
    
    def _2000(self):
        # Call to a subroutine
        # log"Call Subroutine: 0x2000")
        self.stack.append(self.pc)
        self.pc = self.instruction & 0x0fff
    
    def _3000(self):
        # Skip next instruction if Vx = Lower Byte
        # log"Skip next instruction if Vx = Lower Byte: 0x3000")
        if self.register_set[self.vx] == self.instruction & 0x00ff:
            self.pc += 2
    
    def _4000(self):
        # Skip next instruction if Vx != Lower Byte
        # log"Skip next instruction if Vx != Lower Byte: 0x4000")
        if self.register_set[self.vx] != self.instruction & 0x00ff:
            self.pc += 2
    
    def _5000(self):
        # Skip next instruction if Vx = Vy
        # log"Skip next instruction if Vx = Vy: 0x5000")
        if self.register_set[self.vx] == self.register_set[self.vy]:
            self.pc += 2
    
    def _6000(self):
        # Load lower Byte into Vx
        # log"Load lower Byte into Vx: 0x6000")
        self.register_set[self.vx] = self.instruction & 0x00ff

    def _7000(self):
        # Set Vx = Vx + Lower Byte
        # log"Set Vx = Vx + Lower Byte: 0x7000")
        self.register_set[self.vx] += self.instruction & 0x00ff
        self.register_set[self.vx] &= 0x00ff
    
    def _8000(self):
        opcode = self.instruction & 0xf00f
        opcode |= 0x0ff0
        try:
            self.func_map[opcode]()
        except:
            # log"Invalid Instruction _8000: %X" % opcode)
            pass
    
    def _8FF0(self):
        # Set Vx = Vy
        # log"Set Vx = Vy: 0x8FF0")
        self.register_set[self.vx] = self.register_set[self.vy]
        self.register_set[self.vx] &= 0xff

    def _8FF1(self):
        # Set Vx = Vx | Vy
        # log"Set Vx = Vx | Vy: 0x8FF1")
        self.register_set[self.vx] |= self.register_set[self.vy]
        self.register_set[self.vx] &= 0xff
    
    def _8FF2(self):
        # Set Vx = Vx & Vy
        # log"Set Vx = Vx & Vy: 0x8FF2")
        self.register_set[self.vx] &= self.register_set[self.vy]
        self.register_set[self.vx] &= 0xff
    
    def _8FF3(self):
        # Set Vx = Vx XOR Vy
        # log"Set Vx = Vx XOR Vy: 0x8FF3")
        self.register_set[self.vx] ^= self.register_set[self.vy]
        self.register_set[self.vx] &= 0xff
    
    def _8FF4(self):
        # Set Vx = Vx + Vy With Carry
        # log"Set Vx = Vx + Vy With Carry: 0x8FF4")
        addition = self.register_set[self.vx] + self.register_set[self.vy]
        if addition > 0xff:
            self.register_set[0xf] = 0x1
        else:
            self.register_set[0xf] = 0x0
        self.register_set[self.vx] = addition & 0xff
    
    def _8FF5(self):
        # Vx = Vx - Vy and set Vy = 0 if Borrow
        # log"Vx = Vx - Vy and set Vy = 0 if Borrow: 0x8FF5")
        # TODO : Cleanup
        if self.register_set[self.vy] > self.register_set[self.vx]: 
            self.register_set[0xf] = 0
        else:
            self.register_set[0xf] = 1
        self.register_set[self.vx] -= self.register_set[self.vy]
        self.register_set[self.vx] &= 0xff

    def _8FF6(self):
        # SHR Vx By 1 and Set Vy = 1 if LSB of Vx = 1
        # log"SHR Vx By 1 and Set Vy = 1 if LSB of Vx = 1: 0x8FF6")
        self.register_set[0xf] = self.register_set[self.vx] & 0x0001
        self.register_set[self.vx] >>= 1

    def _8FF7(self):
        # Set Vx = Vx - Vy and set Vy = 1 if Borrow
        # log"Set Vx = Vx - Vy and set Vy = 1 if Borrow: 0x8FF7")
        # TODO : Cleanup
        if self.register_set[self.vx] > self.register_set[self.vy]: 
            self.register_set[0xf] = 0
        else:
            self.register_set[0xf] = 1
        self.register_set[self.vx] -= self.register_set[self.vy]
        #self.register_set[self.vx] &= 0xff
    
    def _8FFE(self):
        # SHL Vx By 1 and set Vy = 1 if MSB of Vx = 1
        # log"SHL Vx By 1 and set Vy = 1 if MSB of Vx = 1: 0x8FFE")
        self.register_set[0xf] = (self.register_set[self.vx] & 0x0080) >> 7
        self.register_set[self.vx] <<= 1
        self.register_set[self.vx] &= 0xff
    
    def _9000(self):
        # Skip Next Instruction If Vx != Vy
        # log"Skip Next Instruction If Vx != Vy: 0x9000")
        if self.register_set[self.vx] != self.register_set[self.vy]:
            self.pc += 2
    
    def _A000(self):
        # Set Index Register to nnn in Annn
        # log"Set Index Register to nnn in Annn: 0xA000")
        self.index = self.instruction & 0x0fff
    
    def _B000(self):
        # Set PC = V0 + (nnn in Bnnn)
        # log"Set PC = V0 + (nnn in Bnnn): 0xB000")
        self.pc = (self.instruction & 0x0fff) + self.register_set[0]
    
    def _C000(self):
        # TODO : Test Overflow
        # Set Vx = Random(255) & (kk in Cxkk)
        # log"Set Vx = Random(255) & (kk in Cxkk): 0xC000")
        rnd_num = randint(0, 255)
        self.register_set[self.vx] = rnd_num & (self.instruction & 0x00ff)
        self.register_set[self.vx] &= 0xff
    
    def _D000(self):
        # Draw a sprite at Vx, Vy
        # log"Draw a sprite at Vx, Vy: 0xD000")
        # Dxyn - DRW Vx, Vy, nibble
        # Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.
        # The interpreter reads n bytes from memory, starting at the address stored in I. 
        # These bytes are then displayed as sprites on screen at coordinates (Vx, Vy). 
        # Each sprite is 1 Byte wide and n Byte tall consisting total of 8 X n bits
        # Sprites are XORed onto the existing screen. If this causes any pixels to be erased, VF is set to 1, 
        # otherwise it is set to 0. If the sprite is positioned so part of it is outside the coordinates of the display, 
        # it wraps around to the opposite side of the screen.
        x = self.register_set[self.vx] & 0xff # Get X Coordinate
        y = self.register_set[self.vy] & 0xff # Get Y Coordinate
        self.register_set[0xf] = 0      # Set flag to 0
        height = self.instruction & 0x000f  # Height Of The Sprite
        for row in range(0, height):        # For Each Row Of The Sprite
            curr_row = self.memory[row + self.index]    # Current Bit Row 
            for bit in range(0, 8):                     # For Each Bit In The Current Row
                if (y + row) >= 32 or (x + bit) >= 64:  # Pixel outside the screen
                    continue
                pix_loc = x + bit + ((y + row) * 64)    # Get The Location Of The Pixel
                mask = 1 << (7 - bit)
                curr_bit = (curr_row & mask) >> (7 - bit)
                if curr_bit == 0x1:
                    if self.display_buffer[pix_loc] == 0x1:
                        self.register_set[0xf] = 0x1
                    self.display_buffer[pix_loc] ^= curr_bit
        self.draw = True

    def _E000(self):
        opcode = self.instruction & 0xf0ff
        try:
            self.func_map[opcode]()
        except:
            # log"Invalid Instruction _E000: %4X" % opcode)
            pass
    
    def _E09E(self):
        # Skip next instruction if key stored in Vx is pressed
        # log"Skip next instruction if key stored in Vx is pressed: 0xE09E")
        key = self.register_set[self.vx] & 0xf
        if self.key_inputs[key] == 1:
            self.pc += 2
    
    def _E0A1(self):
        # Skip next instruction if key stored in Vx is not pressed
        # log"Skip next instruction if key stored in Vx is not pressed: 0xE0A1")
        key = self.register_set[self.vx] & 0xf
        if self.key_inputs[key] == 0:
            self.pc += 2
    
    def _F000(self):
        opcode = self.instruction & 0xf0ff
        try:
            self.func_map[opcode]()
        except:
            # log"Invalid Instruction _F000: %4X" % opcode)
            pass
    
    def _F007(self):
        # Set Vx = Delay Timer
        # log"Set Vx = Delay Timer: 0xF007")
        self.register_set[self.vx] = self.delay_timer
    
    def _F00A(self):
        # Wait for the key and set Vx = Key
        # log"Wait for the key and set Vx = Key: 0xF00A")
        # TODO : Implement get_key()
        key = self.get_key()
        if key >= 0:
            self.register_set[self.vx] = key
        else:
            self.pc -= 2
    
    def _F015(self):
        # Set Delay Timer = Vx
        # log"Set Delay Timer = Vx: 0xF015")
        self.delay_timer = self.register_set[self.vx]
    
    def _F018(self):
        # Set Sound Timer = Vx
        # log"Set Sound Timer = Vx: 0xF018")
        self.sound_timer = self.register_set[self.vx]

    def _F01E(self):
        # Set I = I + Vx. If Overflow Vf = 1
        # log"Set I = I + Vx. If Overflow Vf = 1: 0xF01E")
        self.index += self.register_set[self.vx]
        if self.index > 0xfff:
            self.index &= 0xfff
            self.register_set[0xf] = 1
        else:
            self.register_set[0xf] = 0

    def _F029(self):
        # Set Index = Location of Hex Sprite Stored in memory for digit stored in Vx
        # log"Set Index = Location of Hex Sprite Stored in memory for digit stored in Vx: 0xF029")
        self.index = (5 * self.register_set[self.vx]) & 0xfff
    
    def _F033(self):
        # Store BCD Represention of Vx In Memory at I, I+1, I+2
        # log"Store BCD Represention of Vx In Memory at I, I+1, I+2: 0xF033")
        number = self.register_set[self.vx]
        self.memory[self.index]     = int(number / 100)
        self.memory[self.index + 1] = int((number / 10) % 10)
        self.memory[self.index + 2] = int(number % 10)

    def _F055(self):
        # Store the values of Registers V0 to Vx in memory starting at location Index
        # log"Store the values of Registers V0 to Vx in memory starting at location Index: 0xF055")
        for i in range(0, self.vx + 1):
            self.memory[self.index + i] = self.register_set[i]
    
    def _F065(self):
        # Load the Registers V0 to Vx from memory starting at location Index
        # log"Load the Registers V0 to Vx from memory starting at location Index: 0xF065")
        for i in range(0, self.vx + 1):
            self.register_set[i] = self.memory[self.index + i]

    def get_key(self):
        for i in range(0, 16):
            if self.key_inputs[i] == 1:
                return i
            else:
                return -1

    def on_key_press(self, symbol, modifiers):
        if symbol in KEY_MAP.keys():
            self.key_inputs[KEY_MAP[symbol]] = 1
            if self.key_wait:
                self.key_wait = False
        else:
            super(CPU, self).on_key_press(symbol, modifiers)
    
    def on_key_release(self, symbol, modifiers):
        if symbol in KEY_MAP.keys():
            self.key_inputs[KEY_MAP[symbol]] = 0
        
    def cycle(self):
        self.instruction = ((self.memory[self.pc]) << 8) | (self.memory[self.pc + 1])
        self.pc += 2
        self.vx = (self.instruction & 0x0f00) >> 8
        self.vy = (self.instruction & 0x00f0) >> 4
        opcode  = (self.instruction & 0xf000)
        try:
            self.func_map[opcode]()
        except:
            # log(Invalid Instruction _CYCLE: %X" % opcode)
            pass
        if self.sound_timer > 0:
            self.sound_timer -= 1
            if self.sound_timer == 0:
                self.buzz.play()
        
        if self.delay_timer > 0:
            self.delay_timer -= 1
    
    def draw_graphics(self):
        if self.draw:
            i = 0
            line_counter = 0
            while i < 2048:
                if self.display_buffer[i] == 1:
                    self.sprites[i].x = (i % 64) * 10
                    self.sprites[i].y = 310 - int(i / 64) * 10
                    self.sprites[i].batch = self.batch
                else:
                    self.sprites[i].batch = None
                i += 1
        self.clear()
        self.batch.draw()
        self.flip()
        self.draw = False
