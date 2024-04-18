'''
Name: Sophie Turner.
Date: 8/3/2024.
Contact: st838@cam.ac.uk
Compile data from daily UM .pp files and make a big .npy file containing all UKCA data flattened.
For use on Cambridge chemistry department's atmospheric servers. 
Files are located at scratch/st838/netscratch.
'''
# module load anaconda/python3/2022.05
# conda activate /home/st838/nethome/condaenv
# Tell this script to run with the currently active Python environment, not the computer's local versions. 
#!/usr/bin/env python

import os
import cf
import time
import glob
import numpy as np

# Base.
dir_path = '/scratch/st838/netscratch/ukca_npy/' 
# Input files.
ukca_files = glob.glob(dir_path + '/*.pp') # Just .pp files. 
dims_file = dir_path + 'dims.npy' # Dims to match the flattened data.
# Output paths.
npy_file = dir_path + 'fields.npy' # Flattened fields to re-use.

# True if 1 npy file for each day of data, False if 1 npy file for all the data.
npy_day = True

field = cf.read(ukca_files[0], select='stash_code=50500')[0]

# If there are dims available, use them. If not, continue without them and add them later.
if os.path.exists(dims_file):
  dims = np.load(dims_file)
else:
  dims = np.empty(0, dtype = np.float32)

print(f'Shape of dims: {dims.shape}')

if not npy_day:
  # We might need to build up the big np array in sections depending on the amount of data.
  if os.path.exists(npy_file):
    table = np.load(npy_file)
    # Add the dims as the first 4 rows.
    table = np.vstack((dims, table))
  else:
    table = dims
  del(dims) # There is no need to re-use the dims if making 1 big file. 

# Pick the day file to read.
for fi in range(len(ukca_files)):
  ukca_file = ukca_files[fi]
  print(f'Reading .pp file {fi+1} of {len(ukca_files)}:')
  print(ukca_file)
  day = cf.read(ukca_file)

  # Get the number of vertical levels.
  field = day[0]
  nalts = field.coord('atmosphere_hybrid_height_coordinate').size

  # If making multiple files.
  if npy_day:
    table = dims.copy() # Re-use the dims if making multiple files. 

  # For each field, save all the field data in another row.
  for i in range(len(day)):
    start = time.time()
    print(f'Converting field {i+1} of {len(day)}.')
    field = day[i]
    # We don't want section 30 pressure level outputs here.
    if field.identity()[:13] == 'id%UM_m01s30i':
      continue    
    # If there are only 3 dimensions add a 4th and pad it so that the data match the flattened dims.
    if field.ndim == 3:    
      field = field.array
      times = nalts
      stride = field.shape[1] * field.shape[2]
      field = field.flatten()
      # Make a new 1d field array.
      padded = np.empty(0, dtype=np.float32)
      # Loop through old 1d field indices with strides of nlat x nlon until the end.
      for i in range(0, len(field), stride):
        # Pick sub arrays in sections of len nlat x nlon
        rep = field[i : i + stride]
        # Repeat that sub array ntime x nalt.
        rep = np.tile(rep, times)
        # Append it to the new field array.
        padded = np.append(padded, rep)
      field = padded
    else:
      field = field.flatten()     
    table = np.vstack((table, field), dtype=np.float32)
    print('Shape of table:', table.shape)
    end = time.time()
    elapsed = end - start
    print(f'That field took {round(elapsed / 1)} seconds.')
  
  # Save the np array as a npy file containing this day of data.
  if npy_day:
    npy_file = dir_path + ukca_file[-11:-3] + '.npy'
    np.save(npy_file, table)
  
# Save the np array as a npy file containing all data.
if not npy_day:
  npy_file = dir_path + 'all.npy' 
  np.save(npy_file, table)