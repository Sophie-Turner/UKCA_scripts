'''
Name: Sophie Turner.
Date: 4/6/2024.
Contact: st838@cam.ac.uk
Try to predict UKCA J rates with a neural network using UKCA data as inputs.
For use on JASMIN's GPUs. 
'''

import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler


# Create a class that inherits nn.Module.
class Model(nn.Module):

  # Set up NN structure.
  def __init__(self, inputs=5, h1=8, h2=8, outputs=1):
    super().__init__() # Instantiate nn.module.
    self.fc1 = nn.Linear(inputs, h1) 
    self.fc2 = nn.Linear(h1, h2) 
    self.out = nn.Linear(h2, outputs) 

  # Set up movement of data through net.
  def forward(self, x):
    x = F.relu(self.fc1(x)) 
    x = F.relu(self.fc2(x)) 
    x = self.out(x) 
    return(x)


# File paths.
dir_path = '/scratch/st838/netscratch/ukca_npy'
name_file = f'{dir_path}/idx_names'
train_file = f'{dir_path}/4days.npy'
test_file = f'{dir_path}/20170115.npy' 

# Indices of some common combinations to use as inputs and outputs.
phys_all = np.linspace(0,13,14, dtype=int)
NO2 = 15
HCHO = 18 # Molecular product.
H2O2 = 73
O3 = 77 # O(1D) product.

print('Loading numpy data.')

# Training data.
train_days = np.load(train_file)
# Testing data.
test_day = np.load(test_file)

print('\ntrain data:', train_days.shape)
print('test data:', test_day.shape)

print('\nSelecting inputs and targets and making tensors.')

# Select input and output data.
# Chose the 5 best inputs from linear selection for now. Do proper NN feature selection later.
features = [1,7,8,9,10]
target_idx = NO2
in_train = train_days[features]
in_test = test_day[features]
out_train = train_days[target_idx]
out_test = test_day[target_idx]

# Make them the right shape.
in_train = np.rot90(in_train, 3)
in_test = np.rot90(in_test, 3)
out_train = out_train.reshape(-1, 1)
out_test = out_test.reshape(-1, 1)
'''
# Standardisation (optional).
scaler = StandardScaler()
in_train = scaler.fit_transform(in_train)
in_test = scaler.fit_transform(in_test)
out_train = scaler.fit_transform(out_train)
out_test = scaler.fit_transform(out_test)
'''
# Turn them into torch tensors.
in_train = torch.from_numpy(in_train.copy())
in_test = torch.from_numpy(in_test.copy())
out_train = torch.from_numpy(out_train)
out_test = torch.from_numpy(out_test)

print('\nin_train:', in_train.shape)
print('in_test:', in_test.shape)
print('out_train:', out_train.shape)
print('out_test:', out_test.shape)

# Create instance of model.
model = Model()

# Tell the model to measure the error as fitness function to compare pred with label.
criterion = nn.MSELoss()
# Choose optimiser and learning rate. Parameters are fc1, fc2, out, defined above.
opt = torch.optim.Adam(model.parameters(), lr=0.01)

# Train model.
epochs = 300 # Choose num epochs.
print()
start = time.time()
for i in range(epochs):
  # Get predicted results.
  pred = model.forward(in_train) 
  # Measure error. Compare predicted values to training targets.
  loss = criterion(pred, out_train)
  # Print every 10 epochs.
  if (i+1) % 10 == 0:
    print(f'Epoch {i+1} \tMSE: {loss.detach().numpy()}')
    
  # Backpropagation. Tune weights using loss.
  opt.zero_grad() 
  loss.backward() # Send loss back through the net.
  opt.step() # Step optimiser forward through the net.
end = time.time()
minutes = round(((end - start) / 60))
print(f'Training took {minutes} minutes.')

# Evaluate model on test set.
with torch.no_grad(): # Turn off backpropagation.
  pred = model.forward(in_test) # Send the test inputs through the net.
  loss = criterion(pred, out_test) # Compare to test labels.
print('\nLoss on test data:', loss)
print('R2:', round(r2_score(out_test.detach().numpy(), pred.detach().numpy()), 2))

# Remove scaling to view actual values.
#out_test = scaler.inverse_transform(out_test.detach().numpy())
#pred = scaler.inverse_transform(pred.detach().numpy())

# Show a plot of results.
plt.scatter(out_test, pred)
plt.title('jNO2 on 15/1/2017')
plt.xlabel('targets from UKCA')
plt.ylabel('predictions by NN')
plt.show()
