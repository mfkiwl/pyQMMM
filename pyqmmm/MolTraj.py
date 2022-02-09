# @file MolTraj.py
#  Defines MolTraj class and trajectory manipulation methods.
#
#  Written by David W. Kastner
#
#  Department of Chemical Engineering, MIT

class MolTraj:
  '''
  Stores a molecular trajectory and facilitates manipulations.
  Reads information from an multiframe xyz file.
  
  Example instantiation of a molecular scan from an molecular trajectory:
  
  >>> mol_scan = MolTraj()
  >>> mol_scan.get_xyz('tc_scan.xyz')
  '''
  
  def __init__(self, name=''):
    # The number of frames
    self.frames = []
    # The number of atoms in the structure
    self.natoms = 0
    # The multiplicty of the structure
    self.multiplicty = 0
    # Thecharge of the structure
    self.charge = 0
    
  def get_traj(self, filename):
    return
    
