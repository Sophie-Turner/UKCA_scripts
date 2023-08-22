# -*- coding: utf-8 -*-
"""Specify_dates.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OqVl_Xi876KugGw7agLkNyKFme3V22fe

This Python script makes a bash file to run on MOOSE to get all the relevant files when the list of files is very long and would take too long to sift through manually. It moves the files to a specified location (netscratch) in a directory.
"""

import glob

from google.colab import drive
drive.mount('/content/drive')

# 1. Make a folder on JASMIN to put all the files into. DONE
# 2. Find the files and put them in the folder 1 by 1. Test the command. DONE
# 3. SCP the folder to netscratch. DONE
# 4. Delete the folder off JASMIN. DONE
# 5. Make a shell script to do all this.

# the UM output files are named like: moose:/crum/u-cy731/apl.pp/cy731a.pl20180531.pp
um_file_prefix = 'moose:/crum/u-cy731/apl.pp/cy731a.pl'
moo_get = 'moo get -v'
folder_name = 'UM_nudged_J_outputs_for_ATom'
dest_jasmin = './{}/'.format(folder_name)

# Find all the dates.
atom_folder_path = '/content/drive/MyDrive/Photolysis data/ATom_MER10_Dataset.20210613'
atom_files = glob.glob(atom_folder_path + '/*.ict')

moo_commands = ''

for atom_file in atom_files:
   date = atom_file[-16:-8]
   um_file = '{}{}.pp'.format(um_file_prefix, date)
   moo_command = '{} {} {}'.format(moo_get, um_file, dest_jasmin)
   moo_commands = '{}\n{}'.format(moo_commands, moo_command)

dest_scratch = 'st838@atm-farman.ch.private.cam.ac.uk:/scratch/st838/netscratch/'
scp_command = 'scp -r {} {}'.format(folder_name, dest_scratch)

delete_command = 'rm -r {}'.format(folder_name)

# Make the bash script.
bash_file_path = '/content/drive/MyDrive/Photolysis data/get_store_data.sh'
bash_script = open(bash_file_path, 'w')
bash_content = '#!/bin/bash\n{}\n{}\n{}'.format(moo_commands, scp_command, delete_command)
print(bash_content)
bash_script.write(bash_content)
bash_script.close()