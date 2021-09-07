'''
See more here: https://github.com/davidkastner/quick-csa/blob/main/README.md
DESCRIPTION
   Performs charge shift analysis (CSA) form TeraChem output.
   Author: David Kastner
   Massachusetts Institute of Technology
   kastner (at) mit . edu
SEE ALSO
   mask_maker.py
'''
################################ DEPENDENCIES ################################## 
import sys
import glob
################################## FUNCTIONS ################################### 
'''
Get the residues that will make the mask files.

Parameters
----------
type : str
    Tell function if it is the holo or apo mask
    
Returns
-------
mask_res_list : res_type_array
    An array of all the residues that the user wants included in their mask
'''
def get_mask_res(type):
    try:
        with open('./1_input/{}_residues'.format(type)) as mask_res_file:
            mask_list = mask_res_file.read().strip().split(',')
    except:
        print('File {}_residues does not exist'.format(type))
        sys.exit()
    return mask_list

'''
Identify the users primary PDB file.

Parameters
----------
    
Returns
-------
pdb_name : str
    The file name of the users PDB that will be used to create masks.
'''    
def get_pdb_name():
    pdb_name_pattern = r'./1_input/*.pdb'
    pdbs = glob.glob(pdb_name_pattern)
    if len(pdbs) == 0:
        print('No PDB file in 1_input.')
        sys.exit()
    if len(pdbs) > 1:
        print('More than one PDB has been provided.')
        sys.exit()
    pdb_name = pdbs[0].split('/')[-1]
    return pdb_name

'''
Using the input from the user, 
this funtino will create the apo and holo masks from the original PDB file.

Parameters
----------
raw_mask : str
    A list of residues that the user would like pulled from the original PDB.
pdb_name : str
    The name of the users original PDB file that will will create the mask from.
type : str
    Tell function if it is the holo or apo mask
'''
def mask_maker(mask, pdb_name, type):
    
    print('Creating the {} mask...'.format(type))
    #Create a list from the users input
    #The code for Mask Maker begins here
    res_type_array = []
    new_pdb = '{}_mask'.format(type)
    with open('./2_interm/{}'.format(new_pdb), 'w') as new_mask:
        with open('./1_input/{}'.format(pdb_name), 'r') as original:
            for line in original:
            #Start checking once we reach the ATOM section
                res_index = line[22:28].strip()
                res_type = line[:4]
                if res_type == 'ATOM' and res_index in mask:
                    new_mask.write(line)
                    res_type_array.append(res_index)
                    continue
                #We don't won't to count chain breaks as a discarded residue
                if line[:3] == 'TER':
                    continue
                #We don't want to include the last line so we will watch for END
                if line[:3] == 'END':
                    break
    #Print important statistics for the user
    print('Extracted {} residues'.format(len(set(res_type_array)), type))
    print('Your new file is named {}\n'.format(new_pdb))
    #Make temporary empty link files
    open('./2_interm/{}_link_atoms'.format(type), 'w') # TODO: add section
    

'''
Collect the charges from the charge_mull.xls file.

Parameters
----------
type : str
    Tell function if it is the holo or apo mask
'''
def collect_charges(type):
    
    #Open the mask atoms and link atoms files
    mask_atoms = open('./2_interm/{}_mask'.format(type),'r').readlines()
    link_atoms = open('./2_interm/{}_link_atoms'.format(type),'r').readlines()

    #Initialize variables and lists
    prev_res_index = 0
    tot_charge = []
    res_list = []
    tot_charge_link = []
    res_list_link = []
    mull_charges = open('./1_input/{}_charge_mull.xls'.format(type),'r').readlines()
  
    #Loop through each atom in mask file and get residue name and its index
    for index,line in enumerate(mask_atoms):
        mask_atom_info = line.split()
        res_name = mask_atom_info[3]
        res_index = int(mask_atom_info[4])
      
        #For each new residue, record the current residue and set as previous
        if res_index > prev_res_index:
            res_name_index = res_name + str(res_index)
            res_list.append(res_name_index)
            res_list_link.append(res_name_index)
            tot_charge.append(0.0)
            tot_charge_link.append(0.0)
            prev_res_index = res_index
        
        #Create running list of all charges in charge_mull.xls
        curr_mull_charges = float(mull_charges[index].split()[2])
        tot_charge[-1] += curr_mull_charges
        tot_charge_link[-1] += curr_mull_charges
  
    #Get residue name and index for each line
    for index,line in enumerate(link_atoms):
        mask_atom_info = line.split()
        res_name = mask_atom_info[3]
        res_index = int(mask_atom_info[4])
        res_combo = res_name + str(res_index + 1)   
        
        #If the same residues types are side-by-side get the link atom charge
        if res_combo in res_list:
            res_combo_index = res_list.index(res_combo)
            curr_link_index = res_combo_index + len(mask_atoms) - 1
            link_atom_charge = float(mull_charges[curr_link_index].split()[2])
            tot_charge_link[res_combo_index] += link_atom_charge
            res_list_link[res_combo_index] = res_combo + '*'
    
    #Create files for link and mulliken residue data           
    #Write residues to files
    mull = open('./2_interm/{}.mullres'.format(type), 'w')
    link = open('./2_interm/{}.linkres'.format(type), 'w')
    
    for res in range(len(res_list)):
        mull.write('{} {}\n'.format(res_list[res],tot_charge[res]))
        link.write('{} {}\n'.format(res_list_link[res],tot_charge_link[res]))    
                  
    mull.close()
    link.close()

'''
Calculate the difference in the charges for the apo and holo residue list files.

Parameters
----------

Returns
-------
res_diff : list
    A list of the residues or ligands that were removed in the holo structure,
    creating the apo structure.
'''
def get_res_diff():
    holo_mull = open('./2_interm/holo.mullres','r').readlines()
    apo_mull = open('./2_interm/apo.mullres','r').readlines()
    
    #Loop thorugh the mullres files and get the holo residues
    holo_residues = []
    for line in holo_mull:
        holo_res = line.strip('\n').split()[0]
        holo_residues.append(holo_res)

    #Loop thorugh the mullres files and get the apo residues
    apo_residues = []
    for line in apo_mull:
        apo_res = line.strip('\n').split()[0]
        apo_residues.append(apo_res)

    #Get the difference between the two lists
    holo_residues_set = set(holo_residues)
    apo_residues_set = set(apo_residues)
    res_diff = list(holo_residues_set.difference(apo_residues_set))
    return res_diff

'''
Calculate the difference in the charges for the apo and holo residue list files.

Parameters
----------
ns_res_list : list
    A list of the residues or ligands that were removed in the holo structure,
    creating the apo structure.
'''
def charge_diff():
    
    res_diff = get_res_diff()
    #Open recently created holo and apo charge files
    holo_mull = open('./2_interm/holo.mullres','r').readlines()
    holo_link = open('./2_interm/holo.linkres','r').readlines()
    apo_mull = open('./2_interm/apo.mullres','r').readlines()
    apo_link = open('./2_interm/apo.linkres','r').readlines()
    
    #Initialize variables
    diff_charge = []
    res_list = []
    diff_charge_link = []
    res_list_link = []
    n = 0
    
    #Calculate the differences in the charges for the holo and apo
    for line in range(len(holo_mull)):
        holo_mull_res, holo_mull_charge = holo_mull[line].strip('\n').split()
        holo_link_res, holo_link_charge = holo_link[line].strip('\n').split()
        if holo_mull_res in res_diff:
            n -= 1
        else:
            _, apo_mull_charge = apo_mull[line + n].strip('\n').split()
            _, apo_link_charge = apo_link[line + n].strip('\n').split()
            diff = float(holo_mull_charge) - float(apo_mull_charge)
            diff_link = float(holo_link_charge) - float(apo_link_charge)
            res_list.append(holo_mull_res)
            res_list_link.append(holo_link_res)
            diff_charge.append(diff)
            diff_charge_link.append(diff_link)
    
    #Create final files with the differences in charges for all residues
    diff_all = open('./3_output/all.diffmullres','w')
    diff_link_all = open('./3_output/all.difflinkmullres','w')
    
    #Create final files with the differences in charges for differences > 0.05
    diff_cutoff = open('./3_output/cutoff.diffmullres','w')
    diff_link_cutoff = open('./3_output/cutoff.difflinkmullres','w')
    
    #Write the final charge differences out to a new file
    for res in range(len(apo_mull)):
        diff_all.write('{} {}\n'.format(res_list[res], diff_charge[res])) 
        diff_link_all.write('{} {}\n'.format(res_list_link[res], diff_charge_link[res])) 
    
    for res in range(len(apo_mull)):
        if diff_charge[res] >= 0.05:
            diff_cutoff.write('{} {}\n'.format(res_list[res], diff_charge[res])) 
        if diff_charge_link[res] >= 0.05:
            diff_link_cutoff.write('{} {}\n'.format(res_list_link[res], diff_charge_link[res])) 


################################## QUICK CSA ###################################   
#Introduce user to Quick CSA functionality
print('WELCOME TO QUICK CSA')
print('--------------------------\n')
print('Calculates the charge shift from the apo and holo TeraChem output.')
print('Check the README for the files to add to the 1_input directory.')
print('--------------------------\n')

#Get mask arrays from user-provided input difflinkmullres
apo_mask = get_mask_res('apo')
holo_mask = get_mask_res('holo')

#Create apo and holo mask files
pdb_name = get_pdb_name()
mask_maker(apo_mask, pdb_name, 'apo')
mask_maker(holo_mask, pdb_name, 'holo')

#Create list of residues with their associated charges for apo and holo_link
collect_charges('apo')
collect_charges('holo')

#Create the final output file with the charge differences for all residues
#Create output files for only the residues with a charge differences > 0.50.
charge_diff()
