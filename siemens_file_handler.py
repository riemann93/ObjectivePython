import pandas as pd
import math


class SiemensFileHandler:
    """handler that that acts as an interface between the program and outside files"""
    @staticmethod
    def load_siemens(path):
        try:
            siemens = pd.read_csv(path, sep=',', header=None)
            s_type = siemens.shape[0]
            return siemens, s_type
        except IOError as e:
            print("IO Error. path: {} e: {}".format(path, e))

    @staticmethod
    def save_siemens(path, df):
        try:
            df.to_csv(path, sep=',', header=None, mode='a')
        except IOError as e:
            print("IO Error. path: {} e: {}".format(path, e))
