from rootpy.tree import Cut
from rootpy.io import root_open
from ROOT import TMVA

variables = ["absolute_eta", "angle_bl", "M3"]

def train_and_test_MVA(name, signal_tree, background_tree, output_file_name, n_sig, n_bgk ):
    outfile = root_open( output_file_name, 'recreate' )
    factory = TMVA.Factory( name, outfile, "!V:!Silent:Color:DrawProgressBar" )
    # signal_tree.SetBranchStatus('*', 0)
#     background_tree.SetBranchStatus('*', 0)
    for var in variables:
#         signal_tree.SetBranchStatus(var, 1)
#         background_tree.SetBranchStatus(var, 1)
        factory.AddVariable( var, 'F' )
    factory.AddSignalTree( signal_tree )
    factory.AddBackgroundTree( bkg_tree )
    # passes selection (currently marked as all variables are defined.
    cut1 = Cut( 'absolute_eta > 0' )
    cut2 = Cut( 'angle_bl > 0' )
    cut3 = Cut( 'M3 > 0' )
    cut = cut1 & cut2 & cut3

    training_options = "nTrain_Signal=%d:nTrain_Background=%d:nTest_Signal=%d:nTest_Background=%d:!V" % ( n_sig, n_bgk, n_sig, n_bgk )
    factory.PrepareTrainingAndTestTree( cut, cut, training_options )

    # methods are
    # PDE - RS method (PDERS)
    # K-Nearest Neighbour classifier (KNN)
    # Linear discriminant (LD)
    factory.BookMethod( TMVA.Types.kLikelihood, "Likelihood", "!V:NAvEvtPerBin=50" )
    
    # factory.BookMethod( TMVA.Types.kMLP, "MLP", "!V:NCycles=50:HiddenLayers=10,10:TestRate=5" )
    # 
    # factory.BookMethod( TMVA.Types.kBDT, "BDT", "!V:BoostType=Grad:nCuts=20:NNodesMax=5" );
    # Train MVAs using the set of training events
    factory.TrainAllMethods()
    # ---- Evaluate all MVAs using the set of test events
    factory.TestAllMethods()
    # ----- Evaluate and compare performance of all configured MVAs
    factory.EvaluateAllMethods()
    
    outfile.close()
    bkg_file.close()
    

signal_file = root_open( 'TTJets_madgraph_tree.root' )
outfile = 'tmva_singetop.root'
tree_path = "TTbar_plus_X_analysis/EPlusJets/Ref selection/FitVariables"
bkg_file = root_open( 'SingleTop_tree.root' )
# bkg3_file = root_open('QCD_Electron_tree.root')

signal_tree = signal_file.Get( tree_path )
bkg_tree = bkg_file.Get( tree_path )

train_and_test_MVA('MVA_BkgSingleTop', signal_tree, bkg_tree, outfile, 20000, 2000 )


outfile = 'tmva_vjets.root'
bkg_file = root_open('VJets_tree.root')
bkg_tree = bkg_file.Get(tree_path)
 
train_and_test_MVA('MVA_BkgVJets',signal_tree, bkg_tree, outfile, 20000, 200)

signal_file.close()
