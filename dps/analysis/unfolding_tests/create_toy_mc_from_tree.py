#!/usr/bin/env python
# encoding: utf-8
'''
TODO
'''
from __future__ import print_function, division

import sys
import os

from optparse import OptionParser
from dps.config.xsection import XSectionConfig
from rootpy.io.file import root_open
# @BROKEN
from dps.config.variable_binning import bin_edges, bin_edges_vis
import numpy as np
from dps.utils.ROOT_utils import set_root_defaults
from rootpy.plotting.hist import Hist, Hist2D
from dps.config.variableBranchNames import branchNames, genBranchNames_particle,\
    genBranchNames_parton
from dps.utils.file_utilities import make_folder_if_not_exists
__all__ = []
__version__ = 0.1
__date__ = '2015-08-03'
__updated__ = '2015-08-03'

DEBUG = 0
TESTRUN = 0
PROFILE = 1


class ToySet():

    def __init__(self, f_out, variable, channel, n_toy):
        self.variable = variable
        self.channel = channel
        self.f_out = f_out
        self.n_toy = n_toy

        self.output_dir = f_out.mkdir(channel + '/' + variable, recurse=True)
#             'unfolding_' + variable + '_analyser_' + channel + '_channel_patType1CorrectedPFMet')
        self.create_histograms()

        self.recoVariable = branchNames[variable]
        self.genVariable_particle = genBranchNames_particle[variable]
        self.genVariable_parton = None
        if variable in genBranchNames_parton:
            self.genVariable_parton = genBranchNames_parton[variable]

        self.vis_flag = 'passesGenEventSelection'
        self.offline_flag = 'passSelection'
        self.gen_flag = ''
        if channel is 'muon':
            self.gen_flag = 'isSemiLeptonicMuon'
        else:
            self.gen_flag = 'isSemiLeptonicElectron'

    def create_histograms(self):
        self.histograms = []
        self.folders = []
        variable = self.variable
        for i in range(1, self.n_toy + 1):
            folder = self.output_dir.mkdir('toy_{0}'.format(i))
            folder.cd()
            self.folders.append(folder)
            histograms = {}
            #
            # Histograms to fill
            #
            # 1D histograms
            histograms['truth'] = Hist(bin_edges[variable], name='truth')
            histograms['truthVis'] = Hist(
                bin_edges_vis[variable], name='truthVis')
            histograms['truth_parton'] = Hist(
                bin_edges[variable], name='truth_parton')
            histograms['measured'] = Hist(bin_edges[variable], name='measured')
            histograms['measuredVis'] = Hist(
                bin_edges_vis[variable], name='measuredVis')
            histograms['fake'] = Hist(bin_edges[variable], name='fake')
            histograms['fakeVis'] = Hist(
                bin_edges_vis[variable], name='fakeVis')

            # 2D histograms
            histograms['response'] = Hist2D(
                bin_edges[variable], bin_edges[variable], name='response')
            histograms['response_without_fakes'] = Hist2D(
                bin_edges[variable], bin_edges[variable], name='response_without_fakes')
            histograms['response_only_fakes'] = Hist2D(
                bin_edges[variable], bin_edges[variable], name='response_only_fakes')

            histograms['responseVis'] = Hist2D(
                bin_edges_vis[variable], bin_edges_vis[variable], name='responseVis')
            histograms['responseVis_without_fakes'] = Hist2D(
                bin_edges_vis[variable], bin_edges_vis[variable], name='responseVis_without_fakes')
            histograms['responseVis_only_fakes'] = Hist2D(
                bin_edges_vis[variable], bin_edges_vis[variable], name='responseVis_only_fakes')

            histograms['response_parton'] = Hist2D(
                bin_edges[variable], bin_edges[variable], name='response_parton')
            histograms['response_without_fakes_parton'] = Hist2D(
                bin_edges[variable], bin_edges[variable], name='response_without_fakes_parton')
            histograms['response_only_fakes_parton'] = Hist2D(
                bin_edges[variable], bin_edges[variable], name='response_only_fakes_parton')
            # Some interesting histograms
            histograms['eventWeight'] = Hist(100, -2, 2, name='EventWeight')
            histograms['eventWeightVis'] = Hist(
                100, -2, 2, name='EventWeightVis')
            histograms['toy_mc_weight'] = Hist(
                200, 0, 2, name='toy_mc_weight')
            histograms['toy_mc_weight_vis'] = Hist(
                200, 0, 2, name='toy_mc_weight_vis')
            self.histograms.append(histograms)

    def fill(self, event, weight, mc_weights, mc_weights_vis):
        recoVariable = self.recoVariable
        genVariable_particle = self.genVariable_particle
        genVariable_parton = self.genVariable_parton
        histograms = self.histograms

        reco = event.__getattr__(recoVariable)
        gen_particle = event.__getattr__(genVariable_particle)
        gen_parton = None
        if genVariable_parton:
            gen_parton = event.__getattr__(genVariable_parton)
        passes_gen_selection = event.__getattr__(self.gen_flag) == 1
        passes_gen_selection_vis = event.__getattr__(self.vis_flag) == 1
        passes_offline_selection = False
        if self.channel == 'muon':
            passes_offline_selection = event.__getattr__(
                self.offline_flag) == 1
        else:
            passes_offline_selection = event.__getattr__(
                self.offline_flag) == 2

        for i in range(self.n_toy):
            mc_weight = mc_weights[i]
            mc_weight_vis = mc_weights_vis[i]
            this_weight = weight * mc_weight
            this_weight_vis = weight * mc_weight_vis

            histograms[i]['eventWeight'].Fill(this_weight)
            histograms[i]['eventWeightVis'].Fill(this_weight_vis)
            histograms[i]['toy_mc_weight'].Fill(mc_weight)
            histograms[i]['toy_mc_weight_vis'].Fill(mc_weight_vis)

            if passes_gen_selection:
                histograms[i]['truth'].Fill(
                    gen_particle, this_weight)
                if gen_parton:
                    histograms[i]['truth_parton'].Fill(
                        gen_parton, this_weight)

            if passes_gen_selection_vis:
                histograms[i]['truthVis'].Fill(
                    gen_particle, this_weight_vis)

            if passes_offline_selection:
                histograms[i]['measured'].Fill(reco, this_weight)
                histograms[i]['response'].Fill(
                    reco, gen_particle, this_weight)

                histograms[i]['measuredVis'].Fill(
                    reco, this_weight_vis)
                histograms[i]['responseVis'].Fill(
                    reco, gen_particle, this_weight_vis)

                if gen_parton:
                    histograms[i]['response_parton'].Fill(
                        reco, gen_parton, this_weight)

                if passes_gen_selection:  # signal
                    histograms[i]['response_without_fakes'].Fill(
                        reco, gen_particle, this_weight)
                    if gen_parton:
                        histograms[i]['response_without_fakes_parton'].Fill(
                            reco, gen_parton, this_weight)
                else:  # fake
                    histograms[i]['fake'].Fill(reco, this_weight)
                    histograms[i]['response_only_fakes'].Fill(
                        reco, gen_particle, this_weight)
                    if gen_parton:
                        histograms[i]['response_only_fakes_parton'].Fill(
                            reco, gen_parton, this_weight)

                if passes_gen_selection_vis:  # signal
                    histograms[i]['responseVis_without_fakes'].Fill(
                        reco, gen_particle, this_weight_vis)
                else:  # fake
                    histograms[i]['fakeVis'].Fill(
                        reco, this_weight_vis)
                    histograms[i]['responseVis_only_fakes'].Fill(
                        reco, gen_particle, this_weight_vis)

    def write(self):
        self.f_out.cd()
        self.output_dir.cd()
        for hists, folder in zip(self.histograms, self.folders):
            folder.cd()
            for _, h in hists.items():
                h.Write()
#         self.output_dir.Write()
#         self.f_out.Write()


def main(argv=None):
    '''Command line options.'''

    program_name = os.path.basename(sys.argv[0])
    program_version = "v{0}".format(__version__)
    program_build_date = "{0}".format(__updated__)

    program_version_string = '%%prog %s (%s)' % (
        program_version, program_build_date)
    # program_usage = '''usage: spam two eggs''' # optional - will be
    # autogenerated by optparse
    program_longdesc = ''''''  # optional - give further explanation about what the program does
    program_license = "Copyright 2015 user_name (organization_name)                                            \
                Licensed under the Apache License 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0"

    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = OptionParser(
            version=program_version_string, epilog=program_longdesc, description=program_license)
        parser.add_option("-n", "--n_toy_mc", dest="n_toy_mc",
                          help="number of toy MC to create", type=int)
        parser.add_option("-i", "--n_input_mc", dest="n_input_mc",
                          help="number of toy MC use as input", type=int)
        parser.add_option("-o", "--output", dest="output_folder",
                          help="output folder for toy MC")
        parser.add_option("-c", "--centre-of-mass-energy", dest="CoM",
                          help="Centre of mass energy. Default = %default[TeV]",
                          type=int)
        parser.add_option('-v', '--verbose', dest="verbose", action="store_true",
                          help="set verbosity level [default: %default]")

        # set defaults
        parser.set_defaults(
            CoM=13, variable="MET", output_folder='data/toy_mc/', n_toy_mc=300,
            n_input_mc=50000)

        # process options
        (opts, _) = parser.parse_args(argv)

        if opts.verbose > 0:
            print("verbosity level = %d" % opts.verbose)

        # MAIN BODY #
        config = XSectionConfig(opts.CoM)
        generate_toy(
            opts.n_toy_mc, opts.n_input_mc, config, opts.output_folder)

    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help" + "\n")
        return 2


def generate_toy(n_toy, n_input_mc, config, output_folder, start_at=0, split=1):
    from progressbar import Percentage, Bar, ProgressBar, ETA
    set_root_defaults()
    genWeight = '( EventWeight * {0})'.format(config.luminosity_scale)
    file_name = config.ttbar_category_templates_trees['central']
    make_folder_if_not_exists(output_folder)
    outfile = get_output_file_name(
        output_folder, n_toy, start_at, n_input_mc, config.centre_of_mass_energy)

    variable_bins = bin_edges.copy()
    
    widgets = ['Progress: ', Percentage(), ' ', Bar(),
           ' ', ETA()]
    
    with root_open(file_name, 'read') as f_in, root_open(outfile, 'recreate') as f_out:
        tree = f_in.Get("TTbar_plus_X_analysis/Unfolding/Unfolding")
        n_events = tree.GetEntries()
        print("Number of entries in tree : ", n_events)
        for channel in ['electron', 'muon']:
            print('Channel :', channel)
            gen_selection, gen_selection_vis = '', ''
            if channel is 'muon':
                gen_selection = '( isSemiLeptonicMuon == 1 )'
                gen_selection_vis = '( isSemiLeptonicMuon == 1 && passesGenEventSelection )'
            else:
                gen_selection = '( isSemiLeptonicElectron == 1 )'
                gen_selection_vis = '( isSemiLeptonicElectron == 1 && passesGenEventSelection )'

            selection = '( {0} ) * ( {1} )'.format(genWeight, gen_selection)
            selection_vis = '( {0} ) * ( {1} )'.format(genWeight,
                                                       gen_selection_vis)
            weighted_entries = get_weighted_entries(tree, selection)
            weighted_entries_vis = get_weighted_entries(tree, selection_vis)
            pbar = ProgressBar(widgets=widgets, maxval=n_input_mc).start()

            toy_mc_sets = []
            for variable in ['MET', 'HT', 'ST', 'WPT']:  # variable_bins:
                toy_mc = ToySet(f_out, variable, channel, n_toy)
                toy_mc_sets.append(toy_mc)
            count = 0
            for event in tree:
                # generate 300 weights for each event
                mc_weights = get_mc_weight(weighted_entries, n_toy)
                mc_weights_vis = get_mc_weight(weighted_entries_vis, n_toy)

                if count >= n_input_mc:
                    break
                count += 1
                if count < start_at:
                    continue
#                 weight = event.EventWeight * config.luminosity_scale
#                 # rescale to N input events
#                 weight *= n_events / n_input_mc / split
                weight = 1

                for toy_mc in toy_mc_sets:
                    toy_mc.fill(event, weight, mc_weights, mc_weights_vis)
                if count % 1000 == 1:
                    pbar.update(count)
                    print('Processed {0} events'.format(count))
            pbar.finish()
            for toy_mc in toy_mc_sets:
                toy_mc.write()
    print('Toy MC was saved to file:', outfile)


def get_weighted_entries(tree, selection):
    h = tree.Draw('EventWeight', selection=selection)
    return h.Integral()


def get_mc_weight(weighted_entries, n_toy=1):
#     sqrt_error = math.sqrt(weighted_entries)
    mc_weight = np.random.poisson(
        weighted_entries, n_toy) / weighted_entries
    return mc_weight


def get_output_file_name(output_folder, n_toy, start_at, n_input_mc, centre_of_mass):
    # define output file
    out_file_template = '{0}/toy_mc_N_{1}_from_{2}_to_{3}_{4}TeV.root'
    output_file_name = out_file_template.format(
        output_folder, n_toy, start_at, start_at + n_input_mc, centre_of_mass)
    return output_file_name


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        from guppy import hpy
        profile_filename = 'dps.analysis.unfolding_tests.create_toy_mc_from_tree_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        h = hpy().heap()
        statsfile.write(str(h))
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
