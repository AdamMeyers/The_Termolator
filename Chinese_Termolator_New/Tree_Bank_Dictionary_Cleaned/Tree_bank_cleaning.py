#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 11:04:48 2018

@author: leizhen
"""

from os import listdir
from os.path import isfile, join
import re
import sys

def main():
    in_path = sys.argv[0]
    out_path = sys.argv[1]
    read_dir(inpath, outpath)

if __name__ == "__main__":
    main()

def read_dir(in_path, out_path):
    in_dir = [f for f in listdir(in_path) if isfile(join(in_path, f))]
    for i in range(len(in_dir)):
        in_file = open(in_dir[i], "r")
        out_dir = f'./postagged_clean/Cleaned_{indir[i]}'
        out_file = open(out_dir, "w")
        
        content = in_file.read()
        