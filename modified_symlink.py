#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Fix issues of broken symlink
# Author: Ziyun Yu (zy2478@nyu.edu)
#
import sys
import os
import subprocess

def main():
    directory = sys.argv[1]
    for item in os.listdir(directory):
    	item_path = os.path.join(directory, item)
    	if os.path.isdir(item_path):
    		for link_file in os.listdir(item_path):
    			link_file_path = os.path.join(item_path, link_file)

    			if os.path.islink(link_file_path):
    				target_path = os.readlink(link_file_path)
    				new_target_path = target_path.replace(' ', '_')   
    				os.unlink(link_file_path)
    				os.symlink(new_target_path, link_file_path)
    		
if __name__ == '__main__':
    main()
