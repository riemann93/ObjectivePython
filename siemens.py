import ci
import siemens_file_handler
import array as arr
import math
import pandas as pd
import time
import random


class Siemens:
    """This is the Main class of the program 'Siemens'"""
    siemens_base_path = 'C:/Python/personalRepositories/objectivepython/siemens_files/new_siemens/extreme_001.csv'
    siemens_current_path = 'C:/Python/personalRepositories/objectivepython/siemens_files/' \
                           'current_siemens/beginner_001.csv'

    def __init__(self):
        self.csv_handler = siemens_file_handler.SiemensFileHandler()
        self.siemens_base, self.s_type = self.csv_handler.load_siemens(self.siemens_base_path)
        self.siemens_current = self.siemens_base
        self.cmdInterface = ci.CI(self.siemens_current, self.s_type)
        self.siemens_state = 1

    def start(self):
        return_string = ""
        error = self.validate_siemens()
        print(error)
        self.save_siemens()

        while self.siemens_state == 1:
            return_string, self.siemens_state = \
                self.cmdInterface.update_siemens(self.siemens_current, 12, self.s_type, return_string)

            if return_string == "Validating":
                return_string = self.validate_siemens()

            if return_string == "Solving":

                return_string = self.solve_siemens_single()
                """solve as much as possible until a stalemate or solution"""
                """in case of stalemate, make a 50/50 guess, and save all future cells which are being written"""
                """solve again. If an error occur, change the 50/50 guess, and mark it permanent.
                 if the solution meets a stalemate again, make another guess"""

    def siemens_is_filled(self):
        return_string = "Siemens is filled"

        for i in range(0, self.s_type):

            for j in range(0, self.s_type):

                if self.siemens_current[i][j] == 0:
                    return_string = "Siemens is not filled"
        return return_string

    def validate_value(self, column, row):
        value = self.siemens_current[column][row]
        dup_array = []

        if self.siemens_current[column][row] == 0:

            return dup_array
        """check row"""

        for i in range(0, self.s_type):

            if i != column and value == self.siemens_current[i][row]:
                dup_array.append([i, row])

        """check column"""

        for i in range(0, self.s_type):

            if i != row and value == self.siemens_current[column][i]:
                dup_array.append([column, i])

        """check quadrant"""
        quadrants_root = int(math.sqrt(self.s_type))
        quadrant = [column // quadrants_root, row // quadrants_root]

        for i in range(quadrant[1] * quadrants_root, quadrant[1] * quadrants_root + quadrants_root):

            for j in range(quadrant[0] * quadrants_root, quadrant[0] * quadrants_root + quadrants_root):

                if (not (i == row and j == column)) and value == self.siemens_current[j][i]:
                    dup_array.append([j, i])

        return dup_array

    def validate_siemens(self):
        return_string = "No conflicting values"

        for i in range(0, self.s_type):

            for j in range(0, self.s_type):
                error = self.validate_value(i, j)

                if len(error) > 0:
                    return_string = ['[', str(i), ', ', str(j),
                                     '] is conflicting with the following points: ', str(error)]
                    return_string = ''.join(return_string)

                    return return_string

        if self.siemens_is_filled() == "Siemens is filled" and return_string == "No conflicting values":
            return_string = "Siemens is solved!"

        return return_string

    def guess_value(self):
        """Return an array with a random cell which has two options for a value.
        The array:
        [column, row, option one, option two]"""
        zero_array = []

        for i in range(0, self.s_type):

            for j in range(0, self.s_type):
                value = self.siemens_current[j][i]

                if value == 0:
                    s = self.cell_elimination([j, i])

                    if len(s) == 2:
                        zero_array.append([j, i, s.pop(), s.pop()])

        rand = random.randint(0, len(zero_array))
        chosen_zero = zero_array[rand]

        return chosen_zero

    def cell_elimination(self, cell):
        """Cell elimination"""

        j, i = cell[0], cell[1]
        s = set()

        """check row"""
        for k in range(0, self.s_type):
            s.add(self.siemens_current[k][i])

        """check column"""
        for k in range(0, self.s_type):
            s.add(self.siemens_current[j][k])

        """check quadrant"""
        quadrants_root = int(math.sqrt(self.s_type))
        quadrant = [j // quadrants_root, i // quadrants_root]

        for k in range(quadrant[1] * quadrants_root, quadrant[1] * quadrants_root + quadrants_root):
            for l in range(quadrant[0] * quadrants_root, quadrant[0] * quadrants_root + quadrants_root):
                s.add(self.siemens_current[l][k])

        s.remove(0)
        s_temp = set()
        for x in range(1, self.s_type + 1):
            s_temp.add(x)

        s = (s_temp - s)
        return s

    def solve_siemens_multi(self):
        """solve multiple cells in the siemens, until no deterministic cells are left, or the siemens is unsolvable
        can return:
        siemens unsolveable"""
        could_solve = 1
        return_string = ""
        while could_solve == 1:
            return_string = self.validate_siemens()

            if return_string == "No conflicting values":
                return_string = self.solve_siemens_single()
                print(return_string)

                if return_string == "Siemens unsolvable":

                    return return_string

                elif return_string == "Siemens stalemate":

                    return return_string

            elif return_string == "Siemens is solved!":

                nothing = input()
                return return_string

            else:
                could_solve = 0
                return_string = "Cannot solve siemens since it cannot be validated"

        return return_string

    def solve_siemens_single(self):
        """
        solves a single cell in siemens. if successful, returns:
            VALUE inserted into [COLUMN, ROW] through 'SOLVING METHOD'.
        if error occurs, returns:
            Siemens unsolvable
        if stalemate occurs, returns:
            Siemens stalemate
        """
        def check_row(row, value, type):
            row_bool = 0
            for i in range(0, type):
                if self.siemens_current[i][row] == value:
                    row_bool = 1
            return row_bool

        def check_column(column, value, type):
            column_bool = 0

            for i in range(0, type):

                if self.siemens_current[column][i] == value:
                    column_bool = 1

            return column_bool

        def check_quadrant(column, row, value, type):
            quadrant_bool = 0
            quadrants_root = int(math.sqrt(type))
            quadrant = [column // quadrants_root, row // quadrants_root]

            for m in range(quadrant[1] * quadrants_root, quadrant[1] * quadrants_root + quadrants_root):

                for n in range(quadrant[0] * quadrants_root, quadrant[0] * quadrants_root + quadrants_root):

                    if self.siemens_current[n][m] == value:
                        quadrant_bool = 1

            return quadrant_bool

        return_string = "Siemens stalemate"
        siemens_error = 0
        """Row solving"""
        """loop through rows"""
        for i in range(0, self.s_type):
            """loop through numbers"""

            for j in range(1, self.s_type + 1):
                """check if row has number"""
                row_has_value = 0
                zero_array = []
                remove_zero_array = []

                for k in range(0, self.s_type):

                    if self.siemens_current[k][i] == j:
                        row_has_value = 1

                    if self.siemens_current[k][i] == 0:
                        zero_array.append(k)

                if row_has_value == 0:
                    """loop through each 0 in row"""

                    for l in range(len(zero_array)):
                        """check column for number"""
                        column_has_value = check_column(zero_array[l], j, self.s_type)

                        """check quadrant for number"""
                        quadrant_has_value = check_quadrant(zero_array[l], i, j, self.s_type)

                        if quadrant_has_value != 0 or column_has_value != 0:
                            remove_zero_array.append(zero_array[l])

                    for l in remove_zero_array:
                        zero_array.remove(l)

                    if len(zero_array) == 1:
                        self.siemens_current[zero_array[0]][i] = j
                        return_string = "{} inserted into [{}, {}] through 'Row solving'".format(j, zero_array[0], i)
                        ''.join(return_string)

                        return return_string

                    elif len(zero_array) == 0:
                        siemens_error = 1

        """Column solving"""
        """loop through columns"""

        for i in range(0, self.s_type):
            """loop through numbers"""

            for j in range(1, self.s_type + 1):
                """check if column has number"""
                column_has_value = 0
                zero_array = []
                remove_zero_array = []

                for k in range(0, self.s_type):

                    if self.siemens_current[i][k] == j:
                        column_has_value = 1

                    if self.siemens_current[i][k] == 0:
                        zero_array.append(k)

                if column_has_value == 0:
                    """loop through each 0 in column"""

                    for l in range(len(zero_array)):
                        """check row for number"""
                        row_has_value = check_row(zero_array[l], j, self.s_type)

                        """check quadrant for number"""
                        quadrant_has_value = check_quadrant(i, zero_array[l], j, self.s_type)

                        if quadrant_has_value != 0 or row_has_value != 0:
                            remove_zero_array.append(zero_array[l])

                    for l in remove_zero_array:
                        zero_array.remove(l)

                    if len(zero_array) == 1:
                        self.siemens_current[i][zero_array[0]] = j
                        return_string = "{} inserted into [{}, {}] through 'Column solving'".format(j, i, zero_array[0])
                        ''.join(return_string)

                        return return_string

                    elif len(zero_array) == 0:
                        siemens_error = 1

        """Quadrant solving"""
        """Looping through quadrants"""
        quadrants_root = int(math.sqrt(self.s_type))

        for i in range(0, quadrants_root):

            for j in range(0, quadrants_root):
                """Loop through numbers"""

                for k in range(1, self.s_type + 1):
                    """Check if quadrant has number"""
                    quadrant_has_value = 0
                    zero_array = []
                    remove_zero_array = []

                    for l in range(i*quadrants_root, i*quadrants_root + quadrants_root):

                        for m in range(j*quadrants_root, j*quadrants_root + quadrants_root):

                            if self.siemens_current[l][m] == k:
                                quadrant_has_value = 1

                            if self.siemens_current[l][m] == 0:
                                zero_array.append([l, m])

                    if quadrant_has_value == 0:
                        """loop through each 0 in quadrant"""

                        for l in range(len(zero_array)):
                            """Check row for number"""
                            row_has_value = check_row(zero_array[l][1], k, self.s_type)

                            """Check column for number"""
                            column_has_value = check_column(zero_array[l][0], k, self.s_type)

                            if row_has_value != 0 or column_has_value != 0:
                                remove_zero_array.append(zero_array[l])

                        for l in remove_zero_array:
                            zero_array.remove(l)

                        if len(zero_array) == 1:
                            self.siemens_current[zero_array[0][0]][zero_array[0][1]] = k
                            return_string = "{} inserted into [{}, {}]" \
                                            " through Quadrant solving".format(k, zero_array[0][0], zero_array[0][0])
                            ''.join(return_string)

                            return return_string

                        elif len(zero_array) == 0:
                            siemens_error = 1

        """Cell Elimination"""

        for i in range(0, self.s_type):

            for j in range(0, self.s_type):

                if self.siemens_current[j][i] == 0:
                    s = self.cell_elimination([j, i])

                    if len(s) == 1:
                        value = s.pop()
                        self.siemens_current[j][i] = value
                        return_string = "{} inserted into [{}, {}] through 'Cell elimination'".format(value, j, i)

                        return return_string

                    if len(s) == 0:
                        siemens_error = 1

        """if no solving algorithm succeeds, siemens is unsolvable"""
        if siemens_error == 1:
            return_string = "Siemens unsolvable"

        return return_string

    def enter_value(self, column, row, value):

        if self.siemens_base[column][row] == 0:
            self.siemens_current[column][row] = value

        else:

            return 1

        return 0

    def save_siemens(self):
        self.csv_handler.save_siemens(self.siemens_current_path, self.siemens_current)
