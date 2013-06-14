
from copy import copy
b_tag_bins_inclusive = ['0orMoreBtag', '1orMoreBtag', '2orMoreBtags', '3orMoreBtags']
b_tag_bins_exclusive = ['0btag', '1btag', '2btags', '3btags', '4orMoreBtags']
all_b_tag_bins = copy(b_tag_bins_inclusive)
all_b_tag_bins.extend(b_tag_bins_exclusive)

b_tag_summations = {
             '0orMoreBtag':['0btag', '1btag', '2btags', '3btags', '4orMoreBtags'],
             '1orMoreBtag':['1btag', '2btags', '3btags', '4orMoreBtags'],
             '2orMoreBtags':['2btags', '3btags', '4orMoreBtags'],
             '3orMoreBtags':['3btags', '4orMoreBtags']
             }

jet_bins_inclusive = ["0orMoreJets", "1orMoreJets", "2orMoreJets", "3orMoreJets" , "4orMoreJets"]
jet_bins_exclusive = ["0jet", "1jet", "2jets", "3jets"]
all_jet_bins = copy(b_tag_bins_inclusive)
all_jet_bins.extend(b_tag_bins_exclusive)
