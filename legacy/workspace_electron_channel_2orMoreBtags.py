from ROOT import RooWorkspace

workspace = RooWorkspace("electron_channel_2orMoreBtags")

workspace.factory('lepton_AbsoluteEta[0]')
workspace.factory('lumi[0]')

workspace.factory('n_signal[2200,0,10000]')
workspace.factory('n_VPlusJets[200,0,10000]')
workspace.factory('n_QCD[10,0,10000]')
workspace.factory('sum::yield(n_signal,n_VPlusJets,n_QCD)')

workspace.factory( "Poisson::model_core(n,yield)" )

workspace.factory( "lumi[0]" );

# cross section - parameter of interest
workspace.factory( "xsec[0,0,0.1]" );

# selection efficiency * acceptance
workspace.factory( "efficiency[0]" );

# signal yield
workspace.factory( "prod::nsig(lumi,xsec,efficiency)" );
workspace.factory( "Uniform::prior(xsec)" )
workspace.Print()

workspace.SaveAs('electron_channel_2orMoreBtags.root')