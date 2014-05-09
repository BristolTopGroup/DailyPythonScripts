##
## This run script is used to fit RelIso using exponential (or linear) function
## in various jet bins, using fit_data_Njet.C
##
###############################################################################


##=======================
##
##  Inclusive jet bin
##
##=======================

##-----------------
##  Fit Njet >= 0
##-----------------
echo "Alljet Gaus" >> MyEstimates.txt
# (1) fit allj, norm mc to luminosity
root -q -n 'fit_data_Njet.C("all",1)' >& res_allj_normToLumi.txt
# (2) fit allj, norm mc to data
##root -q -n 'fit_data_Njet.C("allj",2)' >& res_allj_normToData.txt



echo "1m-jet Gaus" >> MyEstimates.txt
##-----------------
##  Fit Njet >= 1 ('1mj' means 1 or more jet)
##-----------------
# (1) norm mc to luminosity
root -q -n 'fit_data_Njet.C("1mj",1)' >& res_1mj_normToLumi.txt
# (2) norm mc to data
##root -q -n 'fit_data_Njet.C("1mj",2)' >& res_1mj_normToData.txt

echo "2m-jet Gaus" >> MyEstimates.txt
##-----------------
##  Fit Njet >= 2
##-----------------
# (1) norm mc to luminosity
root -q -n 'fit_data_Njet.C("2mj",1)' >& res_2mj_normToLumi.txt
# (2) norm mc to data
##root -q -n 'fit_data_Njet.C("2mj",2)' >& res_2mj_normToData.txt

echo "3m-jet Gaus" >> MyEstimates.txt
##-----------------
##  Fit Njet >= 3
##-----------------
# (1) norm mc to luminosity
root -q -n 'fit_data_Njet.C("3mj",1)' >& res_3mj_normToLumi.txt
# (2) norm mc to data
##root -q -n 'fit_data_Njet.C("3mj",2)' >& res_3mj_normToData.txt

echo "4m-jet Gaus" >> MyEstimates.txt
##-----------------
##  Fit Njet >= 4
##-----------------
# (1) norm mc to luminosity
root -q -n 'fit_data_Njet.C("4orMoreJets",1)' >& res_4mj_normToLumi.txt
# (2) norm mc to data
#root -q -n 'fit_data_Njet.C("4orMoreJets",2)' >& res_4mj_normToData.txt







##=======================
##
##  Exclusive jet bin
##
##=======================

echo "0 jet Gaus" >> MyEstimates.txt
##----------------
##  Fit Njet = 0
##----------------
# (1) norm mc to luminosity
root -q -n 'fit_data_Njet.C("0jet",1)' >& res_0j_normToLumi.txt
# (2) norm mc to data
#root -q -n 'fit_data_Njet.C("0jet",2)' >& res_0j_normToData.txt

echo "1 jet Gaus" >> MyEstimates.txt
##----------------
##  Fit Njet = 1
##----------------
# (1) norm mc to luminosity
root -q -n 'fit_data_Njet.C("1jet",1)' >& res_1j_normToLumi.txt
# (2) norm mc to data
#root -q -n 'fit_data_Njet.C("1jet",2)' >& res_1j_normToData.txt

echo "2 jet Gaus" >> MyEstimates.txt
##----------------
##  Fit Njet = 2
##----------------
# (1) norm mc to luminosity
root -q -n 'fit_data_Njet.C("2jets",1)' >& res_2j_normToLumi.txt
# (2) norm mc to data
#root -q -n 'fit_data_Njet.C("2jets",2)' >& res_2j_normToData.txt

echo "3 jet Gaus" >> MyEstimates.txt
root -q -n 'fit_data_Njet.C("3jets",1)' >& res_3j_normToLumi.txt
echo "4 jet Gaus" >> MyEstimates.txt
root -q -n 'fit_data_Njet.C("4j",1)' >& res_4j_normToLumi.txt
