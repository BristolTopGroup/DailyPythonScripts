##
## 15 Jul 2010
## 
## * This is the run script to plot/fit RelIso using only MC events.
## * It calls fit_new.C and perform gaussian fit over all permutations of fit ranges,
##   and make 2 version of plots: one zoomed-in on y-axis and the other not.
##
## * plot_qcd_estimate.C
##
## * It creates the following directories to store the output:
##       mc_only_[DT]/nofit
##       mc_only_[DT]/gaus_free12j_fix34j
##       mc_only_[DT]/gaus_mean_0.3to0.6_12j_fix34j
##       mc_only_[DT]/gaus_mean_0.4to0.6_12j_fix34j
##   [DT] above means Date and Time, ie the time stamp of when the dir is created.
##
## * The time stamp format can be changed below by adapting the mytime variable.
##
#####################################################################################

# main dir
dir=mc_only

# To add time stamp to "mc_only"
#mytime=`date "+%d%m%y_%Hh%Mm"` ## produces eg '150710_13h55m' for 13 July 2010, 1.55pm
mytime=`date "+%d%h%y_%Hh%Mm"` ## produces eg '15Jul10_13h55m' for 13 July 2010, 1.55pm
dir=${dir}_$mytime

# subdirectories
sd1=nofit
sd2=gaus_free12j_fix34j
sd3=gaus_mean_0.3to0.6_12j_fix34j
sd4=gaus_mean_0.4to0.6_12j_fix34j

# create directories
mkdir -p $dir/$sd1
mkdir -p $dir/$sd2
mkdir -p $dir/$sd3
mkdir -p $dir/$sd4


# plot without fit
echo "plot without fit"
echo " op: $dir/$sd1"
root -q -b 'run_fit_none.cc(1,0)' >& fit_none.txt
mv -f *QCD_reliso*.pdf fit_none.txt $dir/$sd1



# Fit: gaus, no constrain in 1,2j, constrain in 3,4j
echo "Fit gaus"
echo " op: $dir/$sd2"
root -q -b 'run_fit.cc(1,0)' >& fit_res_gaus.txt
so animate_gaus.sh
mv -f *pdf *txt *gif $dir/$sd2


# Fit gaus, constrain mean in 1,2j mean:0.3-1.6, fix 3,4j
#echo "Fit gaus, constrain mean in 1,2j (0.3-1.6)"
#echo " op: $dir/$sd3"
#root -q -b 'run_fit_mean12j_geq03.cc(1,0)' >& fit_res_mean12j_geq03.txt
#so animate_gaus.sh
#mv -f *pdf *txt *gif $dir/$sd3


# Fit gaus, constrain mean in 1,2j mean:0.4-1.6, fix 3,4j
#echo "Fit gaus, constrain mean in 1,2j (0.4-1.6)"
#echo " op: $dir/$sd4"
#root -q -b 'run_fit_mean12j_geq04.cc(1,0)' >& fit_res_mean12j_geq04.txt
#so animate_gaus.sh
#mv -f *pdf *txt *gif $dir/$sd4

rm -f *eps
echo done



###############################
#                             #
# Some notes on the workflow  #
#                             #
#                             #
###############################
#
# run_fit.cc calls fit_new.C, and runs the "fit" function for each fit range. For each case,
# it plots 6 histograms for alljet, 0 jet, 1 jet...4mjets. 
# In doing so, it calculates estimates of the QCD in the signal region, and outputs the estimates  
# to fit_res_gaus.txt, and the relative deviations ([est-true]/true) to est_free_gaus.txt.
# plot_qcd_estimate.C is then called, which reads in the values from est_free_gaus.txt, and plots these. 
# It does this for unconstrained fits, or for constrained fits. 
#
#
#
#
