"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [i * 0 for i in range(8)]
        self.ram = [i * 0 for i in range(256)]
        self.pc = 0

        self.branchtable = {
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100010: self.MUL,
            0b00000001: self.HLT,
            0b01000101: self.PUSH,
            0b01000110: self.POP
        }
        
    def LDI(self, *argv):
        self.reg[argv[0]] = argv[1]
        self.pc += argv[2]

    def PRN(self, *argv):
        print(self.reg[argv[0]])
        self.pc += argv[2]

    def MUL(self, *argv):
        self.alu('MUL', argv[0], argv[1])
        self.pc += argv[2]
    
    def HLT(self, *argv):
        self.pc += argv[2]
        return False
    
    def PUSH(self, *argv):
		# decrement SP
        self.reg[argv[3]] -= 1

		# Get the value we want to store from the register
        reg_num = self.ram[self.pc + 1]
        value = self.reg[reg_num]  # <-- this is the value that we want to push

		# Figure out where to store it; argv[3] == SP
        top_of_stack_addr = self.reg[argv[3]]

		# Store it
        self.ram[top_of_stack_addr] = value

        self.pc += argv[2]
    
    # argv = [operand_a, operand_b, how_far_to_move_pc, SP]
    def POP(self, *argv):
        # register 7 holds the address of the value we want to pop off
        address = self.reg[argv[3]]
        # we're getting the value by indexing it from ram by the address
        value = self.ram[address]
        # set value to the operand register of the program
        self.reg[argv[0]] = value

        # increment SP
        self.reg[argv[3]] += 1
        self.pc += argv[2]

    def load(self):
        """Load a program into memory."""
        filename = sys.argv[1]

        # check to make sure the user has put a command line argument where you expect, and print an error and exit if they didn't
        try:
            with open(filename) as f:
                address = 0

                for line in f:
                    
                    line = line.split("#")

                    try:
                        instruction = int(line[0], 2)
                    except ValueError:
                        continue
                        
                    self.ram[address] = instruction

                    address += 1
        except FileNotFoundError:
            print(f'File: {filename} is not found.')
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    # Memory Address Register (MAR)
    def ram_read(self, MAR):
        return self.ram[MAR]

    # Memory Data Register (MDR)
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def run(self):
        """Run the CPU."""
        # read the memory address that's stored in register PC, and store that result in the Instruction Register. 
        running = True
        SP = 7
        self.reg[SP] = 0xF4

        while running:
            ir = self.ram_read(self.pc)

            # opcode's arguments
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)

            # checks if function is in the branchtable
            try:
                # masking ir to get the first two bits that tell us the number of operands
                num_operands = (ir & 0b11000000) >> 6
                how_far_to_move_pc = num_operands + 1
                # exits loop when a function returns False
                if self.branchtable[ir](operand_a, operand_b, how_far_to_move_pc, SP) == False:
                    running = False
                else:
                    running = True
            except KeyError:
                print(f'Unknown instruction {ir} at address {self.pc}')
                sys.exit(1)
