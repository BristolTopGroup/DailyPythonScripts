cd src
cmsenv
rm -r DailyPythonScripts

git clone https://github.com/BristolTopGroup/DailyPythonScripts

cd DailyPythonScripts
git submodule init && git submodule update
./setup_standalone.sh
source environment.sh
python experimental/BLTUnfold/produceUnfoldingHistograms.py
mv unfolding_TTJets_8TeV_asymmetric.root ../
