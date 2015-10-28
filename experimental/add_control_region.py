'''
Created on 26 Aug 2015

@author: kreczko
'''
from rootpy.io.file import root_open, File
from tools.ROOT_utils import root_mkdir
import shutil
import subprocess

input_folder = '/hdfs/TopQuarkGroup/run2/atOutput/13TeV/50ns/'
output_folder = input_folder.replace('/hdfs', '')
input_files = [
'data_electron_tree.root', 'data_muon_tree.root', 
               'SingleTop_tree.root', 
               'TTJets_PowhegPythia8_tree.root', 
               'VJets_tree.root', 'QCD_Muon_tree.root'
               ]


def create_new_trees(input_file, suffix = ''):
    tree1_name = 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets/FitVariables' + suffix
    tree2_name = 'TTbar_plus_X_analysis/MuPlusJets/QCD non iso mu+jets/Muon/Muons' + suffix
    s_cr1 = 'relIso_04_deltaBeta <= 0.3 && relIso_04_deltaBeta > 0.12'
    s_cr2 = 'relIso_04_deltaBeta > 0.3'
    cr1 = 'TTbar_plus_X_analysis/MuPlusJets/QCD 0.12 < iso <= 0.3'
    cr2 = 'TTbar_plus_X_analysis/MuPlusJets/QCD iso > 0.3'
    
    with root_open(input_file) as file:
        t1 = file.Get(tree1_name)
        t2 = file.Get(tree2_name)
        t1.AddFriend(t2)
    
    #     h1 = t1.Draw('MET', 'relIso_04_deltaBeta > 0.3')
    #     h2 = t1.Draw(
    #         'MET', 'relIso_04_deltaBeta <= 0.3 && relIso_04_deltaBeta > 0.12')
    #     h3 = t1.Draw('MET', 'relIso_04_deltaBeta > 0.12')
    #     h4 = t2.Draw('relIso_04_deltaBeta', 'relIso_04_deltaBeta > 0.12')
    #     print h1.integral()
    #     print h2.integral()
    #     print h3.integral(), h1.integral() + h2.integral()
    
        output = File('test.root', 'recreate')
        output.mkdir(cr1, recurse=True)
        output.mkdir(cr2, recurse=True)
        output.cd(cr2)
        new_tree1 = t1.CopyTree(s_cr2)
        new_tree1.Write()
        output.cd(cr1)
        new_tree2 = t1.CopyTree(s_cr1)
        new_tree2.Write()
        output.close()
        
    new_tree1 = None
    new_tree2 = None
    
    f_out = File(input_file, 'update')
    root_mkdir(f_out, cr1)
    root_mkdir(f_out, cr2)
    with root_open('test.root') as f_in:
        f_out.cd(cr1)
        new_tree1 = f_in.Get(cr1 + '/FitVariables' + suffix).CloneTree()
        f_out.cd(cr2)
        new_tree2 = f_in.Get(cr2 + '/FitVariables' + suffix).CloneTree()
        
for f in input_files:
    for suffix in ['', '_JERDown', '_JERUp', '_JESDown', '_JESUp']:
        fileToUse = f
        if 'data' in f and not suffix == '':
            continue

        if suffix == '_JERDown':
            fileToUse = f.replace('tree','minusJER_tree')
        elif suffix == '_JERUp':
            fileToUse = f.replace('tree','plusJER_tree')
        elif suffix == '_JESDown':
            fileToUse = f.replace('tree','minusJES_tree')
        elif suffix == '_JESUp':
            fileToUse = f.replace('tree','plusJES_tree')

        shutil.copy(input_folder + fileToUse, fileToUse)

        create_new_trees(fileToUse, suffix=suffix)
        subprocess.call(['hadoop', 'fs','-rm','-skipTrash', output_folder + fileToUse])
        subprocess.call(['hadoop', 'fs', '-copyFromLocal', fileToUse, output_folder + fileToUse])
