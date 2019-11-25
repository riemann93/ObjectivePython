import os
import siemens_io
import pandas as pd


class CI:
    def __init__(self, s, s_type):
        self.cursor = [0, 0]
        self.io = siemens_io.IO()
        self.siemens_static = pd.DataFrame(0, index=range(s_type), columns=range(s_type))
        for i in range(0, s_type):
            for j in range(0, s_type):
                self.siemens_static[i][j] = s[i][j]

        self.siemens_pretty = self.build_siemens_pretty(s, self.siemens_static, s_type)
        self.print_cursor()

    def update_siemens(self, siemens_current, time, siemens_type, return_string):
        self.clear_screen()
        self.print_header(time, siemens_type)
        self.update_siemens_pretty(siemens_current, siemens_type)
        self.print_siemens(self.siemens_pretty)
        siemens_state = 1
        if len(return_string) > 0:
            print(return_string)
        print("Please enter a command: ")
        io_input = self.io.input()

        if io_input == 'q':
            print("quitting game")
            siemens_state = 0

        elif io_input == 'w' or io_input == 'a' or io_input == 's' or io_input == 'd':
            direction_string = self.move_cursor(io_input, siemens_type)
            if len(direction_string) > 0:
                s = ['Moved ', direction_string]
                return_string = ''.join(s)
            else:
                return_string = "Cannot move that direction"

        elif io_input == 'v':
            return_string = "Validating"

        elif io_input == 'l':
            return_string = "Solving"

        elif io_input.isdigit():
            value = int(io_input)
            if value < 0 or value > siemens_type:
                return_string = "Value is out of bounds"
            elif self.siemens_static[self.cursor[0]][self.cursor[1]] != 0:
                return_string = "Cannot change original values"
            else:
                siemens_current = self.enter_value(siemens_current, value)
                self.siemens_pretty = self.build_siemens_pretty(siemens_current, self.siemens_static, siemens_type)
                self.print_cursor()
                s = ["entered ", str(value)]
                return_string = ''.join(s)

        else:
            return_string = "value is not a number"

        return return_string, siemens_state

    def enter_value(self, siemens_current, value):
        siemens_current[self.cursor[0]][self.cursor[1]] = value
        return siemens_current

    @staticmethod
    def clear_screen():
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    @staticmethod
    def print_header(time, s_type):
        s_length = s_type
        print("This is a {} by {} Siemens. elapsed time: {}".format(s_length, s_length, time))
        print("move cursor: 'w', 'a', 's' or 'd'")
        print("enter value: number[1-9], 0 for empty")
        print("close siemens: 'q'.    Validate: 'v'.    Solve: 'l'")

    def build_siemens_pretty(self, s_current, s_static, s_type):
        s_print_size_x = (s_type * 4) + 1
        s_print_size_y = (s_type * 8) + 1

        siemens = pd.DataFrame(' ', index=range(s_print_size_x), columns=range(s_print_size_y))

        siemens_rows = siemens.shape[0]
        siemens_columns = siemens.shape[1]

        def loop_siemens(x_offset, y_offset, sign):
            for k in range(0, siemens_columns, y_offset):
                for l in range(0, siemens_rows, x_offset):
                    siemens[k][l] = sign

        loop_siemens(4, 2, '.')
        loop_siemens(1, 8, '.')
        loop_siemens(12, 2, '+')
        loop_siemens(1, 24, '+')

        for i in range(s_type):
            for j in range(s_type):
                x, y = self.index_converter(i, j)
                siemens[x][y] = s_current[i][j]
                if s_current[i][j] == s_static[i][j] and s_current[i][j] != 0:
                    siemens[x-1][y] = '|'
                    siemens[x+1][y] = '|'

        return siemens

    def update_siemens_pretty(self, siemens_current, s_type):
        for i in range(0, s_type):
            for j in range(0, s_type):
                n, m = self.index_converter(i, j)
                self.siemens_pretty[n][m] = siemens_current[i][j]

    @staticmethod
    def index_converter(n, m):
        n = n * 8 + 4
        m = m * 4 + 2
        return n, m

    @staticmethod
    def print_siemens(siemens):
        siemens_rows = siemens.shape[0]
        siemens_columns = siemens.shape[1]

        for j in range(0, siemens_rows):
            for i in range(0, siemens_columns):
                if siemens[i][j] == 0:
                    print(' ', end='')
                else:
                    print(siemens[i][j], end='')
            print('')

    def move_cursor(self, direction, s_type):
        vector = [0, 0]
        direction_string = ""

        if direction == 'w' and self.cursor[1] > 0:
            vector = [0, -1]
            direction_string = "up"
        elif direction == 's' and self.cursor[1] < s_type - 1:
            vector = [0, 1]
            direction_string = "down"
        elif direction == 'a' and self.cursor[0] > 0:
            vector = [-1, 0]
            direction_string = "left"
        elif direction == 'd' and self.cursor[0] < s_type - 1:
            vector = [1, 0]
            direction_string = "right"

        self.print_cursor(True)
        self.cursor[0] += vector[0]
        self.cursor[1] += vector[1]
        self.print_cursor()
        return direction_string

    def print_cursor(self, remove=False):
        cursor_print = [0, 0]
        cursor_sign = '#'
        if remove:
            cursor_sign = ' '

        cursor_print[0], cursor_print[1] = self.index_converter(self.cursor[0], self.cursor[1])
        self.siemens_pretty[cursor_print[0] - 2][cursor_print[1]] = cursor_sign
        self.siemens_pretty[cursor_print[0] + 2][cursor_print[1]] = cursor_sign
        self.siemens_pretty[cursor_print[0]][cursor_print[1] - 1] = cursor_sign
        self.siemens_pretty[cursor_print[0]][cursor_print[1] + 1] = cursor_sign
