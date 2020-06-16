"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [i * 0 for i in range(8)]
        self.ram = [i * 0 for i in range(256)]
        self.pc = 0

    def load(self):
        """Load a program into memory."""

        # address = 0

        # For now, we've just hardcoded a program:

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

        while running:
            ir = self.ram_read(self.pc)

            # opcode's arguments
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)

            if ir == 0b10000010: # LDI
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif ir == 0b01000111: # PRN
                print(self.reg[operand_a])
                self.pc += 2
            elif ir == 0b00000001: # HLT
                running = False
                self.pc += 1
            else:
                print(f'Unknown instruction {ir} at address {self.pc}')
                sys.exit(1)
