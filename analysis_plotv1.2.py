#Imports packages and dependencies
import pandas as pd
import matplotlib.pyplot as plt
import os.path
from pathlib import Path

#Converts a dat file to csv
def dat2df(dat_file):
  df = pd.read_csv(dat_file, sep='\s+', header=None, skiprows=1)
  new_indexes = list(range(1,df.shape[0]+1))
  df[0] = new_indexes
  return df

#Generalizable plotting function
def get_plot(df, yaxis, title, color, saveloc):
  plt.rc('axes', linewidth=2.5)
  df.plot(0,1, color=color, legend=False)
  plt.title(title, fontsize=18)
  plt.ylabel(yaxis, fontsize=16)
  plt.xlabel('Frames', fontsize=16)
  plt.xticks(rotation=45)
  plt.tick_params(labelsize=14)
  plt.savefig('figures/{}'.format(saveloc), bbox_inches='tight')
  plt.show()

#Welcome user and print some instructions
print('Welcome to QuickPlotter')
print('-----------------------\n')
print('This script will search your directory for the following output:')
print('+ Energy levels > energy.dat')
print('+ Water density of solvent box > density.dat')
print('+ Root mean square deviation > rmsd.dat')
print('+ Radius of gyration > rog.dat')
print('------------------------\n')

#Files, titles, labels, colors, etc.
expected_dat = ['energy.dat','density.dat','rmsd.dat','rog.dat']
xaxes = ['Energy (kcal/mol)','Density (1.0 g/cm$^3$)','RMSD (Å)','Radius of gyration (Å)']
titles = ['Energy over time',
          'Density over time',
          'RMSD over time',
          'RoG over time']
colors = ['#ef476f','#06d6a0','#118ab2','#073b4c']
savelocs = ['energy.pdf','density.pdf','rmsd.pdf','rog.pdf']

#Check the users directory for analyzeable files
for i,dat in enumerate(expected_dat):
  data_file = Path(dat)
  if data_file.exists():
    print('Found {}'.format(dat))
    csv_df = dat2df(data_file)
    get_plot(csv_df, xaxes[i], titles[i], colors[i], savelocs[i])
  else:
    print('No {}'.format(dat))