'''
Created on 10 Oct 2014

@author: phxlk
'''
from ROOT import gROOT, TChain
from rootpy.interactive import wait
from rootpy.plotting import Hist
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from dps.utils.plotting import make_plot, Histogram_properties

if __name__ == '__main__':
    # file available on soolin:
    input_file = "/hdfs/TopQuarkGroup/mc/8TeV/v11/NoSkimUnfolding/BLT/TTJets_MassiveBinDECAY_TuneZ2star_8TeV/TTJets_nTuple_53X_mc_merged.root"
    # this file contains multiple trees. For now we will focus on the electron channel
    target_tree = "rootTupleTreeEPlusJets/ePlusJetsTree"
    gROOT.SetBatch(1);
    chain = TChain(target_tree);
    chain.Add(input_file);
    
    # now, we want to be fast and just read one variabe
    # first disable all variables
    chain.SetBranchStatus("*", 0);
    # now enable the one we are interested in:
    chain.SetBranchStatus("unfolding.genMET", 1);
    
    
    # We want to store this variable in a histogram
    # 80 bins, from 0 to 400 (GeV)
    h_gen_met = Hist(80, 0, 400)
    # since we are planning to run over many events, let's cache the fill function
    fill = h_gen_met.Fill
    # ready to read all events
    n_processed_events = 0 
    stop_at = 10**5 # this is enough for this example
    for event in chain:
        gen_met = event.__getattr__("unfolding.genMET")
        fill(gen_met)
        n_processed_events += 1
        if (n_processed_events % 50000 == 0):
            print 'Processed', n_processed_events, 'events.'
        if n_processed_events >= stop_at:
            break
            
    print 'Processed', n_processed_events, 'events.'    
    # lets draw this histogram
    # define the style
    histogram_properties = Histogram_properties()
    histogram_properties.name = 'read_ntuples_gen_met' # it will be saved as that
    histogram_properties.title = 'My awesome MET plot'
    histogram_properties.x_axis_title = 'MET [GeV]'
    histogram_properties.y_axis_title = 'Events / 5 GeV'
    make_plot(h_gen_met, r'$t\bar{t}$', histogram_properties, 
              save_folder = 'examples/plots/', 
              save_as = ['png'])
    
