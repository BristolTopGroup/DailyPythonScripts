// The Bristol Log_IPchi^2 Adaptively_Binned Mass Background Subtraction (LAMBS) Fitter
// Paras Naik, et al.

#include "LAMBSFitter.h"
#include "LHCbStyle.h"

#include "NormalizedIntegral.h"
#include "GetRooDataSet.h"
#include "CreateVariables_roofit.h"

#include "mcAssoc.h"
#include "CDS.h"

void LAMBSFitter::roofit_LogIPCHI2(const char * mcTreeName = "mc_k3pi",
                                   const char * dataTreeName = "data_k3pi", 
                                   const char * inMC = "./mc_k3pi.root", 
                                   const char * inData = "./data_k3pi.root", 
                                   const char * outDir = "./testLAMBSFitter", 
                                   const char * cuts = "(1 == 1)",   
                                   const int aCase = 2,
                                   const int regenerate = 1)
{

  std::cout << "In LAMBSFitter::roofit_LogIPCHI2." << std::endl ;

  LHCbStyle();

  // Create variables to load from the ntuple. (just add more here if you need them)
 
  //MODE_PHILIP_D0 
  RooRealVar m("m","m",1790,1940); // 1790 to 1940
  RooRealVar ptcm("ptcm","ptcm",-998,20000); // 0 to 8000
  RooRealVar ycm("ycm","ycm",1.0,5.5); // 2.0 to 4.5
  RooRealVar lnIPchi2("lnIPchi2","lnIPchi2",-9995,1000000); // ipmin to 5
  RooRealVar lnFLchi2("lnFLchi2","lnFLchi2",-9995,1000000); // less than or equal to 10
  RooRealVar ubv("ubv","ubv",-9995,10000); // 
  RooRealVar ubt("ubt","ubt",-9995,10000); // 
  RooRealVar ubvlim("ubvlim","ubvlim",-9995,10000); //
  RooRealVar ubtlim("ubtlim","ubtlim",-9995,10000); //
  RooRealVar prompt("prompt","prompt",-9995,10000); //
  RooRealVar K_cloneDist("K_cloneDist","K_cloneDist",-9995,100000); //
  RooRealVar Pi0_cloneDist("Pi0_cloneDist","Pi0_cloneDist",-9995,100000); //
  RooRealVar Pi1_cloneDist("Pi1_cloneDist","Pi1_cloneDist",-9995,100000); //
  RooRealVar Pi2_cloneDist("Pi2_cloneDist","Pi2_cloneDist",-9995,100000); //
  RooRealVar K_dllkpi("K_dllkpi","K_dllkpi",-9995,100000); //
  RooRealVar Pi0_dllkpi("Pi0_dllkpi","Pi0_dllkpi",-9995,100000); //
  RooRealVar Pi1_dllkpi("Pi1_dllkpi","Pi1_dllkpi",-9995,100000); //
  RooRealVar Pi2_dllkpi("Pi2_dllkpi","Pi2_dllkpi",-9995,100000); //
  
  RooArgSet *ntupleVarSet = 0;
  
  switch (aCase)
  {
  default:
    ntupleVarSet = new RooArgSet(m);
    (*ntupleVarSet).add(ptcm); 
    (*ntupleVarSet).add(ycm); 
    (*ntupleVarSet).add(lnIPchi2); 
    (*ntupleVarSet).add(lnFLchi2); 
    (*ntupleVarSet).add(ubv); 
    (*ntupleVarSet).add(ubt); 
    (*ntupleVarSet).add(ubvlim); 
    (*ntupleVarSet).add(ubtlim); 
    (*ntupleVarSet).add(prompt); 
    (*ntupleVarSet).add(K_cloneDist); 
    (*ntupleVarSet).add(Pi0_cloneDist); 
    (*ntupleVarSet).add(Pi1_cloneDist); 
    (*ntupleVarSet).add(Pi2_cloneDist); 
    (*ntupleVarSet).add(K_dllkpi);
    (*ntupleVarSet).add(Pi0_dllkpi);
    (*ntupleVarSet).add(Pi1_dllkpi);
    (*ntupleVarSet).add(Pi2_dllkpi);
    break;
  }
  
  // Cuts (using include above)
  
  TCut ALL = cuts;
  TCut PRO = "(prompt == 1)";
  TCut SEC = "(prompt == 2)";
  TCut BKG = "(prompt == 0)";
  TCut PS = "( (prompt == 1 ) || (prompt == 2 ) ) ";
  
  // load data into dataSet
	
  RooDataSet* mcDataSet = 0;
  mcDataSet = GetRooDataSet("mcDataSet", mcTreeName, *ntupleVarSet, inMC);
  mcDataSet->Print(); 
  RooDataSet* dataDataSet = 0;
  dataDataSet = GetRooDataSet("dataDataSet", dataTreeName, *ntupleVarSet, inData);
  dataDataSet->Print(); 
  
  // Log IP
  //  RooFormulaVar* LogIP_func = 0;
  RooRealVar* LogIP = 0;
  switch (aCase)
  {
  default:
    LogIP = new RooRealVar("LogIP", "Log of IP", -28, 22, "log mm");
    // We don't use log IP
    break;
  }
  // Log IP chi2
  RooFormulaVar* LogIPCHI2_func = 0; 
  switch (aCase)
  {
  default: // MODE_PHILIP_D0
    // convert to log base 10 for michael-ntuple... apparently lnIPchi2 at least for the K3pi analysis nTuple right now is in base e
    LogIPCHI2_func = new RooFormulaVar("LogIPCHI2", "LogIPCHI2", "log10(exp(@0))" , RooArgList(lnIPchi2) );
    break;
  }
  RooRealVar *LogIPCHI2 = 0;
  switch (aCase)
  {
  default: // MODE_PHILIP_D0
    // log base 10 for michael-ntuple
    LogIPCHI2 = new RooRealVar("LogIPCHI2", "Log of IPCHI2", ipmin, ipmax, "log 10");
    break;
  }
  LogIPCHI2 = (RooRealVar*) mcDataSet->addColumn(*LogIPCHI2_func);
  mcDataSet->Print();
  LogIPCHI2 = (RooRealVar*) dataDataSet->addColumn(*LogIPCHI2_func);
  dataDataSet->Print();
  
  std::cout << "Cuts: " << (const char*)ALL << std::endl;

  RooDataSet* ReducedMCDataSetALL = (RooDataSet*)mcDataSet->reduce( (ALL) );
  ReducedMCDataSetALL->Print();
  RooDataSet* ReducedMCDataSetPro = (RooDataSet*)mcDataSet->reduce( (ALL && PRO) );
  ReducedMCDataSetPro->Print();
  RooDataSet* ReducedMCDataSetSec = (RooDataSet*)mcDataSet->reduce( (ALL && SEC) );
  ReducedMCDataSetSec->Print();
  RooDataSet* ReducedMCDataSetPS = (RooDataSet*)mcDataSet->reduce( (ALL && PS) );
  ReducedMCDataSetPS->Print();

  RooDataSet* ReducedDataSet_m = (RooDataSet*)dataDataSet->reduce( (ALL) );
  ReducedDataSet_m->Print();

  // NOTE, it's possible to run these one at a time, so long as outDir is the same for all.

  if (regenerate == 1)
  {
    roofit_prompt_LogIPCHI2(ReducedMCDataSetPro, outDir, aCase, "");
    roofit_secondary_LogIPCHI2(ReducedMCDataSetSec, outDir, aCase, "");
//    roofit_refit_LogIPCHI2(ReducedMCDataSetPS, outDir, aCase, "");

    roofit_data_D0_M(ReducedDataSet_m, outDir, aCase, "");
  }
  standard_LogIPCHI2(outDir, aCase, "");
  roofit_datafit_standard_LogIPCHI2(outDir, aCase, "", "", 0);

  // the big bin y and pt loop (Define big bins here!!)
  std::vector<double> yBin_s;
  std::vector<double> yBin_e;
  std::vector<double> ptBin_s;
  std::vector<double> ptBin_e;
  std::vector<double> bigBin;
  int bigBin_i;


  switch (aCase)
  {
  default:
    bigBin.push_back(1);  yBin_s.push_back(2);  yBin_e.push_back(3);  ptBin_s.push_back(0);  ptBin_e.push_back(2000);
    bigBin.push_back(2);  yBin_s.push_back(2);  yBin_e.push_back(3);  ptBin_s.push_back(2000);  ptBin_e.push_back(4000);
    bigBin.push_back(3);  yBin_s.push_back(2);  yBin_e.push_back(3);  ptBin_s.push_back(4000);  ptBin_e.push_back(8000);
    bigBin.push_back(4);  yBin_s.push_back(3);  yBin_e.push_back(3.5);  ptBin_s.push_back(0);  ptBin_e.push_back(2000);
    bigBin.push_back(5);  yBin_s.push_back(3);  yBin_e.push_back(3.5);  ptBin_s.push_back(2000);  ptBin_e.push_back(4000);
    bigBin.push_back(6);  yBin_s.push_back(3);  yBin_e.push_back(3.5);  ptBin_s.push_back(4000);  ptBin_e.push_back(8000);
    bigBin.push_back(7);  yBin_s.push_back(3.5);  yBin_e.push_back(4.5);  ptBin_s.push_back(0);  ptBin_e.push_back(2000);
    bigBin.push_back(8);  yBin_s.push_back(3.5);  yBin_e.push_back(4.5);  ptBin_s.push_back(2000);  ptBin_e.push_back(4000);
    bigBin.push_back(9);  yBin_s.push_back(3.5);  yBin_e.push_back(4.5);  ptBin_s.push_back(4000);  ptBin_e.push_back(8000);
    break;
  case 21:
    bigBin.push_back(1);  yBin_s.push_back(2.0);  yBin_e.push_back(4.5);  ptBin_s.push_back(0);  ptBin_e.push_back(1000);
    bigBin.push_back(2);  yBin_s.push_back(2.0);  yBin_e.push_back(4.5);  ptBin_s.push_back(1000);  ptBin_e.push_back(2000);
    bigBin.push_back(3);  yBin_s.push_back(2.0);  yBin_e.push_back(4.5);  ptBin_s.push_back(2000);  ptBin_e.push_back(3000);
    bigBin.push_back(4);  yBin_s.push_back(2.0);  yBin_e.push_back(4.5);  ptBin_s.push_back(3000);  ptBin_e.push_back(4000);
    bigBin.push_back(5);  yBin_s.push_back(2.0);  yBin_e.push_back(4.5);  ptBin_s.push_back(4000);  ptBin_e.push_back(5000);
    bigBin.push_back(6);  yBin_s.push_back(2.0);  yBin_e.push_back(4.5);  ptBin_s.push_back(5000);  ptBin_e.push_back(6000);
    bigBin.push_back(7);  yBin_s.push_back(2.0);  yBin_e.push_back(4.5);  ptBin_s.push_back(6000);  ptBin_e.push_back(7000);
    bigBin.push_back(8);  yBin_s.push_back(2.0);  yBin_e.push_back(4.5);  ptBin_s.push_back(7000);  ptBin_e.push_back(8000);
    break;
  case 22:
    bigBin.push_back(1);  yBin_s.push_back(2.0);  yBin_e.push_back(2.5);  ptBin_s.push_back(0);  ptBin_e.push_back(8000);
    bigBin.push_back(2);  yBin_s.push_back(2.5);  yBin_e.push_back(3.0);  ptBin_s.push_back(0);  ptBin_e.push_back(8000);
    bigBin.push_back(3);  yBin_s.push_back(3.0);  yBin_e.push_back(3.5);  ptBin_s.push_back(0);  ptBin_e.push_back(8000);
    bigBin.push_back(4);  yBin_s.push_back(3.5);  yBin_e.push_back(4.0);  ptBin_s.push_back(0);  ptBin_e.push_back(8000);
    bigBin.push_back(5);  yBin_s.push_back(4.0);  yBin_e.push_back(4.5);  ptBin_s.push_back(0);  ptBin_e.push_back(8000);
    break;
  }
  
  std::cout << "bigBin.size() = " << bigBin.size() << std::endl;

  SecFracsBig->SetBins(  bigBin.size() , 0.5 , (double)bigBin.size() + 0.5);
  SecFracsMCBig->SetBins(  bigBin.size() , 0.5 , (double)bigBin.size() + 0.5);

  for ( bigBin_i = 1; bigBin_i <= (int) bigBin.size(); ++bigBin_i )
  {
    bigCount++;

    int bm1 = bigBin_i - 1 ;
    double pts = ptBin_s[bm1] ;
    double pte = ptBin_e[bm1] ;
    double ys = yBin_s[bm1] ;
    double ye = yBin_e[bm1] ;

    std::cout << "ys " << ys << " pts " << pts << " bigBin_i " << bigBin_i << std::endl;

    std::ostringstream y_pt_str; 
    char loop_y_str[20];
    char loop_pt_str[20];
    int ret;
    ret = sprintf(loop_y_str,"%4.2f", ( (ys + ye)/2 ) );
    ret = sprintf(loop_pt_str,"%4.2f", ( (pts + pte)/2 ) / 1000 );
    y_pt_str << "_big_y" << loop_y_str << "_pt" << loop_pt_str;
    std::cout << "y_pt_str: " << y_pt_str.str().c_str() << std::endl; 

    std::ostringstream y_bin_ss;
    std::ostringstream pt_bin_ss;
    y_bin_ss << "( ycm > "<< ys << ") && ( ycm <= " << ye << ")";
    pt_bin_ss << "( ptcm > "<< pts << ") && ( ptcm <= " << pte << ")";

    TCut y_bin = y_bin_ss.str().c_str();
    TCut pt_bin = pt_bin_ss.str().c_str();
    TCut y_pt_bin = y_bin && pt_bin;

    std::cout << "Bin Cut: " << (const char*)y_pt_bin << std::endl;

    RooDataSet* loop_ReducedMCDataSetALL = (RooDataSet*)mcDataSet->reduce( (ALL && y_pt_bin) );
    loop_ReducedMCDataSetALL->Print();
    RooDataSet* loop_ReducedMCDataSetPro = (RooDataSet*)mcDataSet->reduce( (ALL && PRO && y_pt_bin) );
    loop_ReducedMCDataSetPro->Print();
    RooDataSet* loop_ReducedMCDataSetSec = (RooDataSet*)mcDataSet->reduce( (ALL && SEC && y_pt_bin) );
    loop_ReducedMCDataSetSec->Print();
    RooDataSet* loop_ReducedMCDataSetPS = (RooDataSet*)mcDataSet->reduce( (ALL && PS && y_pt_bin) );
    loop_ReducedMCDataSetPS->Print();

    double loop_SecFracFromMC = 0;
    double loop_SecFracErrFromMC = 0;
    if(loop_ReducedMCDataSetPS->numEntries() > 0) 
    {
      double numSec = (double)loop_ReducedMCDataSetSec->numEntries();
      double numPro = (double)loop_ReducedMCDataSetPro->numEntries();
      double numTot = (double)loop_ReducedMCDataSetPS->numEntries();
      loop_SecFracFromMC = numSec / numTot;
      loop_SecFracErrFromMC = sqrt( ((numSec * numPro * numPro)+(numSec * numSec * numPro)) / (numTot*numTot*numTot*numTot) );      
    }
    int binX = 1 + ((allCount - 1) % ptNBins);
    int binY = yNBins - floor((allCount - 1) / ptNBins); 
    SecFracsMCBig->SetBinContent(bigCount, loop_SecFracFromMC);
    SecFracsMCBig->SetBinError(bigCount, loop_SecFracErrFromMC);
    std::cout << "bigCount: " << bigCount ;
    std::cout << " binX: " << binX ;
    std::cout << " binY: " << binY ;
    std::cout << " loop_SecFracFromMC: " << loop_SecFracFromMC  ;
    std::cout << " loop_SecFracErrFromMC: " << loop_SecFracErrFromMC << std::endl ;

    RooDataSet* loop_ReducedDataSet_m = (RooDataSet*)dataDataSet->reduce( (ALL && y_pt_bin) );
    loop_ReducedDataSet_m->Print();

// We assume our big bins are populated
/*
    if ((loop_ReducedMCDataSetPro->numEntries() == 0)||
        (loop_ReducedMCDataSetSec->numEntries() == 0)||
        (loop_ReducedDataSet_m->numEntries() == 0)) 
    {
      std::cout << "This big bin has been skipped! No plots for this big bin!" << std::endl;
      continue;
    }
*/

    if (regenerate == 1)
    {
      roofit_prompt_LogIPCHI2(loop_ReducedMCDataSetPro, outDir, aCase, y_pt_str.str().c_str());
      roofit_secondary_LogIPCHI2(loop_ReducedMCDataSetSec, outDir, aCase, y_pt_str.str().c_str());
//      roofit_refit_LogIPCHI2(loop_ReducedMCDataSetPS, outDir, aCase, y_pt_str.str().c_str());

      roofit_data_D0_M(loop_ReducedDataSet_m, outDir, aCase, y_pt_str.str().c_str());
    }
    standard_LogIPCHI2(outDir, aCase, y_pt_str.str().c_str() );
    roofit_datafit_standard_LogIPCHI2(outDir, aCase, y_pt_str.str().c_str(), y_pt_str.str().c_str(), 0);

  }

  // the y and pt loop

  allCount = 0; // now we'll put the plots on the canvas with all plots
  bigCount = 0; // Stop setting bin contents for the secondary fractions 1D histogram

  double loop_y;
  double loop_pt;
  double inc_y = 0.5;
  double inc_pt = 1000;

  for(loop_y = 4.0; loop_y >= 2.0; loop_y -= inc_y) 
  {
    for(loop_pt = 0; loop_pt < 8000; loop_pt += inc_pt) 
    {
      allCount++;

      std::cout << "loop_y " << loop_y << " loop_pt " << loop_pt << " allCount " << allCount << std::endl;

      std::ostringstream y_pt_str; 
      char loop_y_str[20];
      char loop_pt_str[20];
      int ret;
      ret = sprintf(loop_y_str,"%4.2f", ( loop_y + (inc_y/2) ) );
      ret = sprintf(loop_pt_str,"%4.2f", ( ( loop_pt + (inc_pt/2) ) / 1000 ) );
      y_pt_str << "_y" << loop_y_str << "_pt" << loop_pt_str;
      std::cout << "y_pt_str: " << y_pt_str.str().c_str() << std::endl; 

      std::ostringstream y_bin_ss;
      std::ostringstream pt_bin_ss;
      y_bin_ss << "( ycm > "<< loop_y << ") && ( ycm < " << (loop_y + inc_y) << ")";
      pt_bin_ss << "( ptcm > "<< loop_pt << ") && ( ptcm < " << (loop_pt + inc_pt) << ")";

      TCut y_bin = y_bin_ss.str().c_str();
      TCut pt_bin = pt_bin_ss.str().c_str();
      TCut y_pt_bin = y_bin && pt_bin;

      std::cout << "Bin Cut: " << (const char*)y_pt_bin << std::endl;

      RooDataSet* loop_ReducedMCDataSetALL = (RooDataSet*)mcDataSet->reduce( (ALL && y_pt_bin) );
      loop_ReducedMCDataSetALL->Print();
      RooDataSet* loop_ReducedMCDataSetPro = (RooDataSet*)mcDataSet->reduce( (ALL && PRO && y_pt_bin) );
      loop_ReducedMCDataSetPro->Print();
      RooDataSet* loop_ReducedMCDataSetSec = (RooDataSet*)mcDataSet->reduce( (ALL && SEC && y_pt_bin) );
      loop_ReducedMCDataSetSec->Print();
      RooDataSet* loop_ReducedMCDataSetPS = (RooDataSet*)mcDataSet->reduce( (ALL && PS && y_pt_bin) );
      loop_ReducedMCDataSetPS->Print();

      double loop_SecFracFromMC = 0;
      double loop_SecFracErrFromMC = 0;
      if(loop_ReducedMCDataSetPS->numEntries() > 0) 
      {
        double numSec = (double)loop_ReducedMCDataSetSec->numEntries();
        double numPro = (double)loop_ReducedMCDataSetPro->numEntries();
        double numTot = (double)loop_ReducedMCDataSetPS->numEntries();
        loop_SecFracFromMC = numSec / numTot;
        loop_SecFracErrFromMC = sqrt( ((numSec * numPro * numPro)+(numSec * numSec * numPro)) / (numTot*numTot*numTot*numTot) );      
      }
      int binX = 1 + ((allCount - 1) % ptNBins);
      int binY = yNBins - floor((allCount - 1) / ptNBins); 
      SecFracsMC->SetBinContent(binX, binY, loop_SecFracFromMC);
      SecFracsMC->SetBinError(binX, binY, loop_SecFracErrFromMC);
      ProYieldsMC->SetBinContent(binX, binY, (double)loop_ReducedMCDataSetPro->numEntries() );
      ProYieldsMC->SetBinError(binX, binY, sqrt( (double)loop_ReducedMCDataSetPro->numEntries() ) );
      SecYieldsMC->SetBinContent(binX, binY, (double)loop_ReducedMCDataSetSec->numEntries());
      SecYieldsMC->SetBinError(binX, binY, sqrt( (double)loop_ReducedMCDataSetSec->numEntries() ) );
      std::cout << "allCount: " << allCount ;
      std::cout << " binX: " << binX ;
      std::cout << " binY: " << binY ;
      std::cout << " loop_SecFracFromMC: " << loop_SecFracFromMC  ;
      std::cout << " loop_SecFracErrFromMC: " << loop_SecFracErrFromMC  ;
      std::cout << " loop_ProYieldFromMC: " << loop_ReducedMCDataSetPro->numEntries()  ;
      std::cout << " loop_SecYieldFromMC: " << loop_ReducedMCDataSetSec->numEntries() << std::endl ;

      RooDataSet* loop_ReducedDataSet_m = (RooDataSet*)dataDataSet->reduce( (ALL && y_pt_bin) );
      loop_ReducedDataSet_m->Print();

// Since we are using shapes from the big bins, no reason not to use all the little bins
/*
      if ((loop_ReducedMCDataSetPro->numEntries() == 0)||
          (loop_ReducedMCDataSetSec->numEntries() == 0)||
          (loop_ReducedDataSet_m->numEntries() == 0)) 
      {
        std::cout << "This bin has been skipped! No plots for this bin!" << std::endl;
        continue;
      }

      if (regenerate == 1)
      {
        roofit_prompt_LogIPCHI2(loop_ReducedMCDataSetPro, outDir, aCase, y_pt_str.str().c_str());
        roofit_secondary_LogIPCHI2(loop_ReducedMCDataSetSec, outDir, aCase, y_pt_str.str().c_str());
        roofit_refit_LogIPCHI2(loop_ReducedMCDataSetPS, outDir, aCase, y_pt_str.str().c_str());
      }
*/
      if (regenerate == 1)
      {
        roofit_data_D0_M(loop_ReducedDataSet_m, outDir, aCase, y_pt_str.str().c_str());
      }
      standard_LogIPCHI2(outDir, aCase, y_pt_str.str().c_str());

      // Search Through the Big Bins to see which big bin this small bin is in
      double ptst = 0;
      double pten = 0;
      double yst = 0;
      double yen = 0;
      int bB_i;

      for ( bB_i = 1; bB_i <= (int) bigBin.size(); ++bB_i )
      {
        int bm1 = bB_i - 1 ;
        ptst = ptBin_s[bm1] ;
        pten = ptBin_e[bm1] ;
        yst = yBin_s[bm1] ;
        yen = yBin_e[bm1] ;

//        std::cout << "TESTING BIG BIN: " << " yst " << yst << " ptst " << ptst << " bB_i " << bB_i << std::endl;

        if ( 
             (( loop_y + (inc_y/2) ) > yst) &&
             (( loop_y + (inc_y/2) ) < yen) &&
             (( loop_pt + (inc_pt/2) ) > ptst) &&
             (( loop_pt + (inc_pt/2) ) < pten)
           )
        {
          break;
        }

      }

      std::cout << "FOUND BIG BIN: " << " yst " << yst << " ptst " << ptst << " bB_i " << bB_i << std::endl;

      std::ostringstream big_y_pt_str; 
      char big_loop_y_str[20];
      char big_loop_pt_str[20];
      int big_ret;
      big_ret = sprintf(big_loop_y_str,"%4.2f", ( (yst + yen)/2 ) );
      big_ret = sprintf(big_loop_pt_str,"%4.2f", ( (ptst + pten)/2 ) / 1000 );
      big_y_pt_str << "_big_y" << big_loop_y_str << "_pt" << big_loop_pt_str;
      std::cout << "big_y_pt_str: " << big_y_pt_str.str().c_str() << std::endl; 

      std::ostringstream big_y_bin_ss;
      std::ostringstream big_pt_bin_ss;
      big_y_bin_ss << "( ycm > "<< yst << ") && ( ycm <= " << yen << ")";
      big_pt_bin_ss << "( ptcm > "<< ptst << ") && ( ptcm <= " << pten << ")";

      TCut big_y_bin = big_y_bin_ss.str().c_str();
      TCut big_pt_bin = big_pt_bin_ss.str().c_str();
      TCut big_y_pt_bin = big_y_bin && big_pt_bin;

      std::cout << "Big Bin Label: " << (const char*)big_y_pt_bin << std::endl;

      roofit_datafit_standard_LogIPCHI2(outDir, aCase, y_pt_str.str().c_str(), big_y_pt_str.str().c_str(), bB_i);
    }      
  }

  if (regenerate == 1)
  {
    std::ostringstream M_EPS;
    M_EPS << outDir << "/" << "all_M" << ".eps";
    AllPlotsM->Print(M_EPS.str().c_str()); // Encapsulated PostScript format
    Histos->Add(AllPlotsM);
 }
  std::ostringstream IP_EPS;
  IP_EPS << outDir << "/" << "all_IP" << ".eps";
  AllPlotsI->Print(IP_EPS.str().c_str()); // Encapsulated PostScript format
  Histos->Add(AllPlotsI);
  std::ostringstream IPd_EPS;
  IPd_EPS << outDir << "/" << "all_IPd" << ".eps";
//  AllPlotsId->Print(IPd_EPS.str().c_str()); // Encapsulated PostScript format
//  Histos->Add(AllPlotsId);

  std::cout << "Just printed the plots." << endl ;

  LHCbStyle(kTRUE,25);

  TCanvas* Pro = new TCanvas("Pro", "Prompt Yields"); // make new canvas 
//  ProYields->SetMaximum(460);
  ProYields->SetMinimum(-10); // allow us to plot zero bins (along with the extra line in LHCbStyle.h)
  ProYields->SetMarkerSize(1.5);
  ProYields->SetMarkerColor(kBlack);
  ProYields->Draw("COLZTEXTE"); // Put our plot on the canvas.
  std::ostringstream PRO_EPS;
  PRO_EPS << outDir << "/" << "all_ProYields" << ".eps";
  Pro->Print(PRO_EPS.str().c_str()); // Encapsulated PostScript format
  Histos->Add(ProYields);

  TCanvas* Sec = new TCanvas("Sec", "Secondary Fractions"); // make new canvas 
//  SecFracs->SetMaximum(0.162);
  SecFracs->SetMinimum(-0.0001);
  SecFracs->SetMarkerSize(1.5);
  SecFracs->SetMarkerColor(kBlack);
  SecFracs->Sumw2();
  SecFracs->Scale(100.0);
  SecFracs->Draw("COLZTEXTE"); // Put our plot on the canvas.
  std::ostringstream SEC_EPS;
  SEC_EPS << outDir << "/" << "all_SecFracs" << ".eps";
  Sec->Print(SEC_EPS.str().c_str()); // Encapsulated PostScript format
  Histos->Add(SecFracs);

  TCanvas* SecMC = new TCanvas("SecMC", "Secondary Fractions"); // make new canvas 
//  SecFracsMC->SetMaximum(0.162);
  SecFracsMC->SetMinimum(-0.0001);
  SecFracsMC->SetMarkerSize(1.5);
  SecFracsMC->SetMarkerColor(kBlack);
  SecFracsMC->Sumw2();
  SecFracsMC->Scale(100.0);
  SecFracsMC->Draw("COLZTEXTE"); // Put our plot on the canvas.
  std::ostringstream SecMC_EPS;
  SecMC_EPS << outDir << "/" << "all_SecFracsMC" << ".eps";
  SecMC->Print(SecMC_EPS.str().c_str()); // Encapsulated PostScript format
  Histos->Add(SecFracsMC);

  LHCbStyle();

  TCanvas* SecBig = new TCanvas("SecBig", "Secondary Fractions"); // make new canvas 
  SecFracsBig->SetMinimum(-0.0001);
  SecFracsBig->SetMarkerSize(1.5);
  SecFracsBig->SetMarkerColor(kBlack);
  SecFracsBig->Sumw2();
  SecFracsBig->Scale(100.0);
  SecFracsBig->Draw(); // Put our plot on the canvas.
  std::ostringstream SECBIG_EPS;
  SECBIG_EPS << outDir << "/" << "all_SecFracs_BigBins" << ".eps";
  SecBig->Print(SECBIG_EPS.str().c_str()); // Encapsulated PostScript format
  Histos->Add(SecFracsBig);

  TCanvas* SecMCBig = new TCanvas("SecMCBig", "Secondary Fractions"); // make new canvas 
  SecFracsMCBig->SetMinimum(-0.0001);
  SecFracsMCBig->SetMarkerSize(1.5);
  SecFracsMCBig->SetMarkerColor(kBlack);
  SecFracsMCBig->Sumw2();
  SecFracsMCBig->Scale(100.0);
  SecFracsMCBig->Draw(); // Put our plot on the canvas.
  std::ostringstream SecMCBig_EPS;
  SecMCBig_EPS << outDir << "/" << "all_SecFracsMC_BigBins" << ".eps";
  SecMCBig->Print(SecMCBig_EPS.str().c_str()); // Encapsulated PostScript format
  Histos->Add(SecFracsMCBig);

  TCanvas* SecMCpt = new TCanvas("SecMCpt", "Secondary Fractions"); // make new canvas 
  TH1D* SecMCproj_pt = SecYieldsMC->ProjectionX();
  TH1D* TotMCproj_pt = ProYieldsMC->ProjectionX();
  SecMCproj_pt->Sumw2();
  TotMCproj_pt->Sumw2();
  TotMCproj_pt->Add(SecMCproj_pt);
  SecMCproj_pt->Divide(TotMCproj_pt);
  SecMCproj_pt->Scale(100.0);
  SecMCproj_pt->SetMinimum(-0.0001);
  SecMCproj_pt->SetMarkerSize(1.5);
  SecMCproj_pt->SetMarkerColor(kBlack);
  SecMCproj_pt->Draw(); // Put our plot on the canvas.
  std::ostringstream SecMCpt_EPS;
  SecMCpt_EPS << outDir << "/" << "all_SecFracsMC_ptBins" << ".eps";
  SecMCpt->Print(SecMCpt_EPS.str().c_str()); // Encapsulated PostScript format
  Histos->Add(SecMCproj_pt);

  TCanvas* SecMCy = new TCanvas("SecMCy", "Secondary Fractions"); // make new canvas 
  TH1D* SecMCproj_y = SecYieldsMC->ProjectionY();
  TH1D* TotMCproj_y = ProYieldsMC->ProjectionY();
  SecMCproj_y->Sumw2();
  TotMCproj_y->Sumw2();
  TotMCproj_y->Add(SecMCproj_y);
  SecMCproj_y->Divide(TotMCproj_y);
  SecMCproj_y->Scale(100.0);
  SecMCproj_y->SetMinimum(-0.0001);
  SecMCproj_y->SetMarkerSize(1.5);
  SecMCproj_y->SetMarkerColor(kBlack);
  SecMCproj_y->Draw(); // Put our plot on the canvas.
  std::ostringstream SecMCy_EPS;
  SecMCy_EPS << outDir << "/" << "all_SecFracsMC_yBins" << ".eps";
  SecMCy->Print(SecMCy_EPS.str().c_str()); // Encapsulated PostScript format
  Histos->Add(SecMCproj_y);

  std::cout << "Just printed more plots." << endl ;

  // Store Histos to a .root file
  std::ostringstream rootName;
  rootName << outDir << "/" << "Histos_" << aCase << ".root";
  TFile *MyFile = new TFile(rootName.str().c_str(),"RECREATE");
  Histos->Write();
  MyFile->Close();
  delete MyFile;

  // Everything is completed
  
  delete SecMCy;
  delete SecMCpt;
  delete SecMCBig;
  delete SecBig;
  delete SecMC;
  delete Sec;
  delete Pro;
//  delete dataDataSet;
//  delete mcDataSet;
  delete LogIPCHI2 ;
  delete LogIPCHI2_func;
  delete LogIP ;
  delete ntupleVarSet;

  std::cout << "return" << endl ;
  return;
  
}
    

void LAMBSFitter::roofit_prompt_LogIPCHI2(RooDataSet* ReducedDataSetALL,
                             const char* outDir = "./test", 
                             const int aCase = 1, const char* label = "")
{
  std::cout << "in LAMBSFitter::roofit_prompt_LogIPCHI2()" << std::endl << std::endl;
  RooRealVar *LogIPCHI2 = 0;
  switch (aCase)
  {
  default:
    LogIPCHI2 = new RooRealVar("LogIPCHI2", "Log_10 of IP chi^2", ipmin, ipmax, "log_10 chi^2");
    (*LogIPCHI2).setVal(0.5); 
    break;
  }

  //  std::cout << "Choose Signal"<< std::endl; // Choose Signal
  // BUKIN PDF
  RooBukinPdf sigProPdfALL("sigProPdfALL", "sigProPdfALL Bukin", (*LogIPCHI2), 
                           peakBukin, widthBukin, asymBukin, leftTailBukin, rightTailBukin);
  
  //  std::cout << "Choose Background"<< std::endl; // Choose Background
  c0ALL.setConstant(kTRUE); // assume background is zero for background subtraction
  RooChebychev bkgProPdfALL("bkgCheby0ALL", "Fe Cheby Order 1 background", (*LogIPCHI2), RooArgList(c0ALL));
  
  //  std::cout << "Make Total PDF"<< std::endl;
  // Make the totalPDFALL
  RooArgList shapesALL;
  RooArgList yieldsALL;
  shapesALL.add(sigProPdfALL);
  yieldsALL.add(sigPro_yieldALL);
  shapesALL.add(bkgProPdfALL);
  yieldsALL.add(bkgPro_yieldALL);
  RooAddPdf totalPdfALL("totalPdfALL", "sum of signal and background PDF's", shapesALL, yieldsALL);
  
  //  std::cout << "Fit"<< std::endl; // Fit
  int nBins = 25;
  switch(aCase)
  {
  default:
    (*LogIPCHI2).setRange("R1", ipmin, ipmax) ;
    (*LogIPCHI2).setRange("R2", -28, -27) ;
    (*LogIPCHI2).setRange("R3", 21, 22) ;
    break;
  }
  //        bkgProPdfALL.fitTo(*ReducedDataSetALL, Range("R2,R3"), Minos(kTRUE)) ;
  //totalPdfALL.fitTo(*ReducedDataSetALL, Extended(), Minos(kTRUE), Range("R1") , 
  totalPdfALL.fitTo(*ReducedDataSetALL, Minos(kTRUE), Range("R1") , NumCPU(6),
                    Verbose(kV), Warnings(kW), PrintLevel(iPL), PrintEvalErrors(iPE) );
  
  //  std::cout << "Plot"<< std::endl;
  // Plot ALL
  std::ostringstream RPn_ss;
  RPn_ss << "LogIPCHI2ALLpro" << label;
  // Create RooPlot object with M on the axis.
  RooPlot* LogIPCHI2frameALL=(*LogIPCHI2).frame(Bins(nBins), Name(RPn_ss.str().c_str()), Title("LogIPCHI2 of D candidates") ); 
  LogIPCHI2frameALL->SetXTitle("Log_{10} IP#chi^{2}");
  totalPdfALL.paramOn(LogIPCHI2frameALL, ShowConstants(kFALSE), Format("NELU", AutoPrecision(2)), 
                      Parameters((RooArgSet&) *(totalPdfALL.getParameters(*ReducedDataSetALL)->selectByAttrib("Constant",kFALSE))),
                      Layout(0.65, 0.95, 0.95) )->getAttText()->SetTextSize(0.030); // display fit parameters
  ReducedDataSetALL->plotOn(LogIPCHI2frameALL, MarkerSize(0.9) ); // plot histogram

  // Plot function sums
  // Simple way:
  totalPdfALL.plotOn( LogIPCHI2frameALL, Components(bkgProPdfALL) , LineColor(kGreen) );
  
  // Plot total PDF
  totalPdfALL.plotOn( LogIPCHI2frameALL, LineColor(kRed)); // plot fit pdf
  // The plot is not on the screen yet -- we have only created a RooPlot object.
  
  // Put the plot on the screen.
  TCanvas* LogIPCHI2CanvasALL = new TCanvas("LogIPCHI2CanvasALL", "Fit of LogIPCHI2"); // make new canvas
  LogIPCHI2frameALL->Draw(); // Put our plot on the canvas.
  
  // BUKIN
  // Save output plot
  std::ostringstream outEPS;
  outEPS << outDir << "/" << "prompt_LogIPCHI2_Bukin" << label << ".eps";
  LogIPCHI2CanvasALL->Print(outEPS.str().c_str()); // Encapsulated PostScript format

  // Freeze Parameters of FITTED PDF
  c0ALL.setConstant(kTRUE);
  bkgPro_yieldALL.setConstant(kTRUE);
  widthBukin.setConstant(kTRUE);
  //        peakBukin.setConstant(kTRUE);
  asymBukin.setConstant(kTRUE);
  leftTailBukin.setConstant(kTRUE);
  rightTailBukin.setConstant(kTRUE);
  //        sigPro_yieldALL.setConstant(kTRUE);
  
  // Store the FITTED SIGNAL PDF
  RooWorkspace *rws = new RooWorkspace("rws","workspace") ;
  rws->import(sigProPdfALL) ;
  rws->Print();
  std::ostringstream outName;
  outName << outDir << "/" << "PDF_prompt_LogIPCHI2_Bukin" << label << ".root";
  rws->writeToFile(outName.str().c_str());
  
  // Zoom Plot
  switch (aCase)
  {
  default:
    LogIPCHI2frameALL->SetAxisRange(ipmin , ipmax - 0.01); // Put our plot on the canvas.
    break;
  }
  LogIPCHI2frameALL->Draw(); // Put our plot on the canvas.
  std::ostringstream outEPSz;
  outEPSz << outDir << "/" << "prompt_LogIPCHI2_Bukin_ZOOM" << label << ".eps";
//  LogIPCHI2CanvasALL->Print(outEPSz.str().c_str()); // Encapsulated PostScript format
        
  // Free Parameters of FITTED PDF
  c0ALL.setConstant(kFALSE);
  bkgPro_yieldALL.setConstant(kFALSE);
  widthBukin.setConstant(kFALSE);
  peakBukin.setConstant(kFALSE);
  asymBukin.setConstant(kFALSE);
  leftTailBukin.setConstant(kFALSE);
  rightTailBukin.setConstant(kFALSE);
  sigPro_yieldALL.setConstant(kFALSE);

  delete rws;
  delete LogIPCHI2CanvasALL;
  delete LogIPCHI2;

  return;
}


void LAMBSFitter::roofit_secondary_LogIPCHI2(RooDataSet* ReducedDataSetALL,
                                const char* outDir = "./test",
                                const int aCase = 1, const char* label = "")
{
  std::cout << "in LAMBSFitter::roofit_secondary_LogIPCHI2()" << std::endl << std::endl;
  RooRealVar *LogIPCHI2 = 0;                                   
  switch (aCase)
  {
  default:
    LogIPCHI2 = new RooRealVar("LogIPCHI2", "Log_10 of IP chi^2", ipmin, ipmax, "log_10 chi^2");
    (*LogIPCHI2).setVal(1.5);    
    break;
  }
  
  //  std::cout << "Choose Signal"<< std::endl;  // Choose Signal
  // BUKIN PDF
  RooBukinPdf sigSecPdfALL("sigSecPdfALL", "sigSecPdfALL Bukin", (*LogIPCHI2), 
                           peakBukinSec, widthBukinSec, asymBukinSec, leftTailBukinSec, rightTailBukinSec);
  
  //  std::cout << "Choose Background"<< std::endl;
  // Choose Background
  c0ALL.setConstant(kTRUE);
  RooChebychev bkgSecPdfALL("bkgCheby0ALL", "Fe Cheby Order 1 background", (*LogIPCHI2), RooArgList(c0ALL));
  
  //  std::cout << "Make Total PDF"<< std::endl;
  // Make the totalPDFALL
  RooArgList shapesALL;
  RooArgList yieldsALL;
  shapesALL.add(sigSecPdfALL);
  yieldsALL.add(sigSec_yieldALL);
  shapesALL.add(bkgSecPdfALL);
  yieldsALL.add(bkgSec_yieldALL);
  RooAddPdf totalPdfALL("totalPdfALL", "sum of signal and background PDF's", shapesALL, yieldsALL);

  //  std::cout << "Fit"<< std::endl; // Fit
  int nBins = 25;
  switch(aCase)
  {
  default:
    (*LogIPCHI2).setRange("R1", ipmin, ipmax) ;
    (*LogIPCHI2).setRange("R2", -28, -27) ;
    (*LogIPCHI2).setRange("R3", 21, 22) ;
    break;
        }
  //        bkgSecPdfALL.fitTo(*ReducedDataSetALL, Range("R2,R3"), Minos(kTRUE)) ;
  //totalPdfALL.fitTo(*ReducedDataSetALL, Extended(), Minos(kTRUE), Range("R1"),
  totalPdfALL.fitTo(*ReducedDataSetALL, Minos(kTRUE), Range("R1"), NumCPU(6),
                    Verbose(kV), Warnings(kW), PrintLevel(iPL), PrintEvalErrors(iPE) );
  
  //  std::cout << "Plot"<< std::endl;
  // Plot ALL
  std::ostringstream RPn_ss;
  RPn_ss << "LogIPCHI2ALLsec" << label;
  // Create RooPlot object with M on the axis.
  RooPlot* LogIPCHI2frameALL=(*LogIPCHI2).frame(Bins(nBins), Name(RPn_ss.str().c_str()), Title("LogIPCHI2 of D candidates") ); 
  LogIPCHI2frameALL->SetXTitle("Log_{10} IP#chi^{2}");
  totalPdfALL.paramOn(LogIPCHI2frameALL, ShowConstants(kFALSE), Format("NELU", AutoPrecision(2)), 
                      Parameters((RooArgSet&) *(totalPdfALL.getParameters(*ReducedDataSetALL)->selectByAttrib("Constant",kFALSE))),
                      Layout(0.65, 0.95, 0.95) )->getAttText()->SetTextSize(0.030); // display fit parameters
  ReducedDataSetALL->plotOn(LogIPCHI2frameALL, MarkerSize(0.9) ); // plot histogram
 
  // Plot function sums
  // Simple way:
  totalPdfALL.plotOn( LogIPCHI2frameALL, Components(bkgSecPdfALL) , LineColor(kGreen) );
 
  // Plot total PDF
  totalPdfALL.plotOn( LogIPCHI2frameALL, LineColor(kRed)); // plot fit pdf
  // The plot is not on the screen yet -- we have only created a RooPlot object.
 
  // Put the plot on the screen.
  TCanvas* LogIPCHI2CanvasALL = new TCanvas("LogIPCHI2CanvasALL", "Fit of LogIPCHI2"); // make new canvas
  LogIPCHI2frameALL->Draw(); // Put our plot on the canvas.
 
  // BUKIN
 
  // Save output plot
  std::ostringstream outEPS;
  outEPS << outDir << "/" << "secondary_LogIPCHI2_Bukin" << label << ".eps";
  LogIPCHI2CanvasALL->Print(outEPS.str().c_str()); // Encapsulated PostScript format
 
  // Freeze Parameters of FITTED PDF
  c0ALL.setConstant(kTRUE);
  bkgSec_yieldALL.setConstant(kTRUE);
  widthBukinSec.setConstant(kTRUE);
  peakBukinSec.setConstant(kTRUE); // THIS IS NOW FIXED!
  asymBukinSec.setConstant(kTRUE);
  leftTailBukinSec.setConstant(kTRUE);
  rightTailBukinSec.setConstant(kTRUE);
  //        sigSec_yieldALL.setConstant(kTRUE);
 
  // Store the FITTED SIGNAL PDF
  RooWorkspace *rws = new RooWorkspace("rws","workspace") ;
  rws->import(sigSecPdfALL) ;
  rws->Print();
  std::ostringstream outName;
  outName << outDir << "/" << "PDF_secondary_LogIPCHI2_Bukin" << label << ".root";
  rws->writeToFile(outName.str().c_str());
 
  // Zoom Plot
  switch (aCase)
  {
  default:
    LogIPCHI2frameALL->SetAxisRange(ipmin , ipmax - 0.01); // Put our plot on the canvas.
    break;
  }
  LogIPCHI2frameALL->Draw(); // Put our plot on the canvas.
  std::ostringstream outEPSz;
  outEPSz << outDir << "/" << "secondary_LogIPCHI2_Bukin_ZOOM" << label << ".eps";
//  LogIPCHI2CanvasALL->Print(outEPSz.str().c_str()); // Encapsulated PostScript format
 
  delete rws;
  delete LogIPCHI2CanvasALL;
  delete LogIPCHI2;

  // Free Parameters of FITTED PDF
  c0ALL.setConstant(kFALSE);
  bkgSec_yieldALL.setConstant(kFALSE);
  widthBukinSec.setConstant(kFALSE);
  peakBukinSec.setConstant(kFALSE); 
  asymBukinSec.setConstant(kFALSE);
  leftTailBukinSec.setConstant(kFALSE);
  rightTailBukinSec.setConstant(kFALSE);
  sigSec_yieldALL.setConstant(kFALSE);

  return;
}

void LAMBSFitter::roofit_refit_LogIPCHI2(RooDataSet* ReducedDataSetALL,
                            const char* outDir = "./test", 
                            const int aCase = 1, const char* label="")
{
  std::cout << "in LAMBSFitter::roofit_refit_LogIPCHI2()" << std::endl << std::endl;
  RooRealVar *LogIPCHI2 = 0;                                   
  switch (aCase)
  {
  default:
    LogIPCHI2 = new RooRealVar("LogIPCHI2", "Log_10 of IP chi^2", ipmin, ipmax, "log_10 chi^2");
    (*LogIPCHI2).setVal(0.5);    
    break;
  }
  
  std::ostringstream in_ss_Pro;
  std::ostringstream in_ss_Sec;
  in_ss_Pro << outDir << "/" << "PDF_prompt_LogIPCHI2_Bukin" << label << ".root";
  in_ss_Sec << outDir << "/" << "PDF_secondary_LogIPCHI2_Bukin" << label << ".root";
  char *inPro;
  inPro = new char [in_ss_Pro.str().size()+1];
  strcpy (inPro, in_ss_Pro.str().c_str());  // inPro now contains a c-string copy of in_ss_Pro.str()
  char *inSec;
  inSec = new char [in_ss_Sec.str().size()+1];
  strcpy (inSec, in_ss_Sec.str().c_str());  // inSec now contains a c-string copy of in_ss_Sec.str()


  //  std::cout << "Make Signal"<< std::endl;
  TFile *prompt_w_filein = new TFile(inPro) ; 
  RooWorkspace* prompt_w_in = (RooWorkspace*) prompt_w_filein->Get("rws") ; 
  //  prompt_w_in->Print();
  RooAbsPdf *promptPdfALL = prompt_w_in->pdf("sigProPdfALL") ; 
  promptPdfALL->Print("t") ;
  
  TFile *secondary_w_filein = new TFile(inSec) ; 
  RooWorkspace* secondary_w_in = (RooWorkspace*) secondary_w_filein->Get("rws") ; 
  //  secondary_w_in->Print();
  RooAbsPdf *secondaryPdfALL = secondary_w_in->pdf("sigSecPdfALL") ; 
  secondaryPdfALL->Print("t") ;
  
  RooRealVar PromptFracALL("PromptFracALL","Prompt Fraction", 0.70, 0.50, 1.00);
  RooRealVar sig_yieldALL("sig_yieldALL", "Signal yield", 5000.0, 0.0, 300000.0);
  
  //  std::cout << "Convolve Signals" << std::endl;
  //        RooRealVar sigConv("sigConv", "#sigma Conv", 0.2, 0.0, 2.0, "log mm");
  //        RooRealVar meanConv("meanConv", "mean Conv", 0.00, -1.00, 3.00, "log mm");
  //        RooGaussian GaussConvPdf("GaussConvPdf", "GaussConvPdf", (*LogIPCHI2), meanConv, sigConv); 
  
  //      RooFFTConvPdf convPromptPdfALL("convPromptPdfALL", "convPromptPdfALL", (*LogIPCHI2), *promptPdfALL, GaussConvPdf, 2);
  //      RooFFTConvPdf convSecondaryPdfALL("convSecondaryPdfALL", "convSecondaryPdfALL", (*LogIPCHI2), 
  //                                        *secondaryPdfALL, GaussConvPdf, 2);        
  
  //  std::cout << "Choose Signal"<< std::endl;
  // Choose Signal
  RooAddPdf sigPdfALL("Total", "Prompt+Secondary", RooArgList(*promptPdfALL,*secondaryPdfALL), PromptFracALL);
  //        RooAddPdf sigPdfALL("Total", "Prompt+Secondary", RooArgList(convPromptPdfALL,convSecondaryPdfALL), PromptFracALL);

  //  std::cout << "Make Background"<< std::endl;
  // Make Background
  RooRealVar bkg_yieldALL("bkg_yieldALL", "ALL Background yield", 0, 0, 0, "");          //ZERO BACKGROUND
  
  // Make Chebyshev (order 0)
  RooRealVar c0ALL("c0ALL","Fe coef #0", 0, 0, 0, ""); //ZERO BACKGROUND
  //        RooRealVar c0ALL("c0ALL","Fe coef #0", 0, -1, 1);
  
  //  std::cout << "Choose Background"<< std::endl;
  // Choose Background
  RooChebychev bkgPdfALL("bkgCheby0ALL", "Fe Cheby Order 0 background", (*LogIPCHI2), RooArgList(c0ALL));
  
  // Make the totalPDFALL
  RooArgList shapesALL;
  RooArgList yieldsALL;
  shapesALL.add(sigPdfALL);
  yieldsALL.add(sig_yieldALL);
  shapesALL.add(bkgPdfALL);
  yieldsALL.add(bkg_yieldALL);
  RooAddPdf  totalPdfALL("totalPdfALL", "sum of signal and background PDF's", shapesALL, yieldsALL);
  
  //  std::cout << "Fit"<< std::endl;
  // Fit
  // (*LogIPCHI2).setRange("R1", -19.0, 21.0) ;
  //NO BACKGROUND        
  //        bkgPdfALL.fitTo(*ReducedDataSetALL, Range("R1"), Verbose(kV), Warnings(kW), 
  //                        PrintLevel(iPL), PrintEvalErrors(iPE), Minos(kTRUE)) ;
  //        c0ALL.setConstant(kTRUE);
  //        totalPdfALL.fitTo(*ReducedDataSetALL, Range("R1"), Extended(), Minos(kTRUE)); // fit the whole spectrum
  totalPdfALL.fitTo(*ReducedDataSetALL, Minos(kFALSE), Verbose(kV), Warnings(kW), PrintLevel(iPL), PrintEvalErrors(iPE), NumCPU(6) );
  
  //  std::cout << "Plot"<< std::endl;
  // Plot ALL
  std::ostringstream RPn_ss;
  RPn_ss << "LogIPCHI2ALLre" << label;
  // Create RooPlot object with M on the axis.
  RooPlot* LogIPCHI2frameALL = (*LogIPCHI2).frame(Bins(25), Name(RPn_ss.str().c_str()), Title("LogIPCHI2 of D candidates") ); 
  LogIPCHI2frameALL->SetXTitle("Log_{10} IP#chi^{2}");
  totalPdfALL.paramOn( LogIPCHI2frameALL, ShowConstants(kFALSE), Format("NELU", AutoPrecision(2)), 
                       Parameters((RooArgSet&) *(totalPdfALL.getParameters(*ReducedDataSetALL)->selectByAttrib("Constant",kFALSE))),
                       Layout(0.65, 0.95, 0.95) )->getAttText()->SetTextSize(0.030); // display fit parameters
  ReducedDataSetALL->plotOn(LogIPCHI2frameALL, MarkerSize(0.9) ); // plot histogram
  
  // Plot function sums
  // Simple way:
  totalPdfALL.plotOn( LogIPCHI2frameALL, Components(bkgPdfALL) , LineColor(kGreen) );
  totalPdfALL.plotOn( LogIPCHI2frameALL, Components(*promptPdfALL) , LineColor(kBlue) );
  totalPdfALL.plotOn( LogIPCHI2frameALL, Components(*secondaryPdfALL) , LineColor(kCyan) );
  //        totalPdfALL.plotOn( LogIPCHI2frameALL, Components(convPromptPdfALL) , LineColor(kBlue) );
  //        totalPdfALL.plotOn( LogIPCHI2frameALL, Components(convSecondaryPdfALL) , LineColor(kCyan) );
  
  // Plot total PDF
  totalPdfALL.plotOn( LogIPCHI2frameALL, LineColor(kRed)); // plot fit pdf
  // The plot is not on the screen yet -- we have only created a RooPlot object.
  
	// Put the plot on the screen.
	TCanvas* LogIPCHI2CanvasALL = new TCanvas("LogIPCHI2CanvasALL", "Fit of LogIPCHI2"); // make new canvas
	LogIPCHI2frameALL->Draw(); // Put our plot on the canvas.
  
	// Save output plot
  std::ostringstream outEPS;
  outEPS << outDir << "/" << "LogIPCHI2_Refit_Bukin" << label << ".eps";
  LogIPCHI2CanvasALL->Print(outEPS.str().c_str()); // Encapsulated PostScript format
  
  // Zoom Plot
  switch (aCase)
  {
  default:
    LogIPCHI2frameALL->SetAxisRange(ipmin , ipmax - 0.01); // Put our plot on the canvas.
    break;
  }
  LogIPCHI2frameALL->Draw(); // Put our plot on the canvas.
  std::ostringstream outEPSz;
  outEPSz << outDir << "/" << "LogIPCHI2_Refit_Bukin_ZOOM" << label << ".eps";
//  LogIPCHI2CanvasALL->Print(outEPSz.str().c_str()); // Encapsulated PostScript format

  delete LogIPCHI2CanvasALL;
  delete secondary_w_filein;
  delete prompt_w_filein;
  delete inSec;
  delete inPro;
  delete LogIPCHI2;
  
  return;
}







void LAMBSFitter::roofit_data_D0_M(RooDataSet* ReducedDataSet_m,
                      const char* outDir = "./test",
                      const int aCase = 1, const char* label = "")
{
  std::cout << "In LAMBSFitter::roofit_data_D0_M " << std::endl;

  // Add Mass and massdiff
  RooRealVar *D0_M = 0;
  
  switch (aCase)
  {
  default:
    D0_M = new RooRealVar("m", "m", 1790, 1940, "MeV");
    break;
  }
  
  //  std::cout << "Make Signal"<< std::endl;  
  // Make Signal
  RooRealVar sig_yield_m("sig_yield_m", "_m Signal yield", ReducedDataSet_m->sumEntries(), 
                         (ReducedDataSet_m->sumEntries()-fabs(ReducedDataSet_m->sumEntries())) > 0 ? 
                         (ReducedDataSet_m->sumEntries()-fabs(ReducedDataSet_m->sumEntries())) : 0 , 
                         ReducedDataSet_m->sumEntries()+fabs(ReducedDataSet_m->sumEntries()));         
  
  // Make Gauss
  RooRealVar mean_m("mean_m", "mean", 1864.84, 1860, 1870, "MeV");
  RooRealVar sig_m("sig_m", "#sigma", 7, 4, 10, "MeV"); // This also replaces sigA1_m
  
  // Make 2BifurGauss
  RooRealVar sigB1_m("sigB1_m", "#sigma B1", 8, 6, 12, "MeV");
  RooRealVar sigA1minusA2_m("sigA1minusA2_m", "#sigma A1 - #sigma A2", 3.9, 0, 4.9, "MeV");
  RooFormulaVar sigA2_m("sigA2_m", "#sigma A2", "-sigA1minusA2_m + sig_m", RooArgList(sig_m,sigA1minusA2_m));
  RooFormulaVar sigB2_m("sigB2_m", "#sigma B2",
                         "(sigA2_m/sig_m)*sigB1_m", RooArgList(sig_m,sigA2_m,sigB1_m));
  RooBifurGauss G1_m("G1_m", "Fe BifurGauss Signal 1", (*D0_M), mean_m, sig_m, sigB1_m);
  RooBifurGauss G2_m("G2_m", "Fe BifurGauss Signal 2", (*D0_M), mean_m, sigA2_m, sigB2_m);
  RooRealVar G1Frac_m("G1Frac_m","Fe G1 Fraction",0.99,0.00,1.00);
  
  //  std::cout << "Choose Signal"<< std::endl;
  
  // Choose Signal
  RooGaussian sigPdf_m("sigPdf_m", "Gaussian Signal 1", (*D0_M), mean_m, sig_m);
  //         RooAddPdf sigPdf_m("sigPdf_m", "Fe Two BifurGauss Signal", RooArgList(G1_m,G2_m), G1Frac_m);
  
  //  std::cout << "Make Background"<< std::endl;
  
  // Make Background
  //        RooRealVar bkg_yield_m("bkg_yield_m", "_m Background yield", 0, 0, 0);          //ZERO BACKGROUND
  RooRealVar bkg_yield_m("bkg_yield_m", "_m Background yield", 50, 0, 5000000);        
  
  // Make Chebyshev (order 0)
  RooRealVar c0_m("c0_m","Fe coef #0", 0, -1, 1);
  
  // Make polynomial (order 3)
  RooRealVar kBg_m("kBg_m","Bg coef #3", -0.000000001, -0.01, 0.01);
  RooRealVar aBg_m("aBg_m","Bg coef #2", -0.000000001, -0.1, 0.1);
  RooRealVar bBg_m("bBg_m","Bg coef #1", -0.000000001, -0.1, 0.1);
  RooRealVar cBg_m("cBg_m","Bg coef #0", 1, 1, 1);
  
  //  std::cout << "Choose Background"<< std::endl;
  // Choose Background
  RooChebychev bkgPdf_m("bkgPdf_m", "Fe Cheby Order 0 background", (*D0_M), RooArgList(c0_m));
  //        RooGenericPdf bkgPdf_m("bkgPdf_m", "Polynomial Order 3 background centered at the mean",
  //                               "(kBg_m*pow(((D0_M)-mean_m),3) + aBg_m*pow(((D0_M)-mean_m),2) + bBg_m*((D0_M)-mean_m) + cBg_m)",
  //                                RooArgList((*D0_M),kBg_m,aBg_m,bBg_m,cBg_m,mean_m));
  
  //  std::cout << "Choose Total _m"<< std::endl;
  // Make the totalPDF_m
  RooArgList shapes_m;
  RooArgList yields_m;
  shapes_m.add(sigPdf_m);
  yields_m.add(sig_yield_m);
  shapes_m.add(bkgPdf_m);
  yields_m.add(bkg_yield_m);
  RooAddPdf  totalPdf_m("totalPdf_m", "sum of signal and background PDF's", shapes_m, yields_m);
  
  //  std::cout << "Fit _m"<< std::endl;
  // Fit _m
  (*D0_M).setRange("R1", 1790, 1940) ;
  //        (*D0_M).setRange("R2", 1800, 1810) ;
  //        (*D0_M).setRange("R3", 1910, 1920) ;
  //        bkgPdf_m.fitTo(*ReducedDataSet_m, Range("R2,R3"), Minos(kTRUE)) ;
  //        c0_m.setConstant(kTRUE);
  totalPdf_m.fitTo(*ReducedDataSet_m, Minos(kTRUE), Range("R1"), NumCPU(6),
                   Verbose(kV), Warnings(kW), PrintLevel(iPL), PrintEvalErrors(iPE));
  //        totalPdf_m.fitTo(*ReducedDataSet_m, Extended(), Minos(kTRUE), Range("R1"), 
  //                         Verbose(kV), Warnings(kW), PrintLevel(iPL), PrintEvalErrors(iPE) );
  
  //  std::cout << "Plot _m"<< std::endl;
  // Plot _m
  std::ostringstream RPn_ss;
  RPn_ss << "D0_M_m" << label;
  // Create RooPlot object with M on the axis.
  RooPlot* D0_Mframe_m = (*D0_M).frame(Bins(25), Name(RPn_ss.str().c_str()), Title("D0_M of D candidates") ); 
  D0_Mframe_m->SetXTitle("m_{K3#pi} (MeV)");
  totalPdf_m.paramOn( D0_Mframe_m, 
                      Parameters((RooArgSet&) *(totalPdf_m.getParameters(*ReducedDataSet_m)->selectByAttrib("Constant",kFALSE))),
                      ShowConstants(kFALSE), Format("NELU", AutoPrecision(2)), Layout(0.65, 0.95, 0.95) 
                    )->getAttText()->SetTextSize(0.030); 
  // display fit parameters
  ReducedDataSet_m->plotOn(D0_Mframe_m, MarkerSize(0.9) ); // plot histogram
  
  // Plot function sums
  // Simple way:
  //        totalPdf_m.plotOn( D0_Mframe_m, Components(sigPdf_m) , LineColor(kGreen) );
  totalPdf_m.plotOn( D0_Mframe_m, Components(bkgPdf_m) , LineColor(kCyan) );
  
  // Plot total PDF
  totalPdf_m.plotOn( D0_Mframe_m, LineColor(kRed)); // plot fit pdf
  // The plot is not on the screen yet -- we have only created a RooPlot object.
  
	// Put the plot on the screen.
	TCanvas* D0_MCanvas_m = new TCanvas("D0_MCanvas_m", "Fit of D0_M"); // make new canvas
	D0_Mframe_m->Draw(); // Put our plot on the canvas.
  
  Double_t framemaxvalue_m=D0_Mframe_m->GetMaximum();
  //  std::cout << "Frame max is: " << framemaxvalue_m << std::endl ;
  TLine* lLine_m= new TLine(mean_m.getVal()-3*sig_m.getVal(),0,mean_m.getVal()-3*sig_m.getVal(),framemaxvalue_m);
  TLine* rLine_m= new TLine(mean_m.getVal()+3*sig_m.getVal(),0,mean_m.getVal()+3*sig_m.getVal(),framemaxvalue_m);
  //        rLine_m= new TLine(mean_m.getVal()+3*sigB1_m.getVal(),0,mean_m.getVal()+3*sigB1_m.getVal(),framemaxvalue_m);
  lLine_m->SetLineColor(38);
  rLine_m->SetLineColor(38);
  lLine_m->Draw();
  rLine_m->Draw();
  
  Double_t CHI2PERBIN_m = D0_Mframe_m->chiSquare();
  Int_t NBINS_m = D0_Mframe_m->GetNbinsX();
  Double_t CHI2_m = CHI2PERBIN_m * NBINS_m;
  Int_t NFREEPARAMS_m = totalPdf_m.getParameters(ReducedDataSet_m)->selectByAttrib("Constant",kFALSE)->getSize();
  Int_t NDOF_m = NBINS_m - NFREEPARAMS_m;
  Double_t PVAL_m = TMath::Prob(CHI2_m,NDOF_m);
  
  std::cout << "Fe: For the fit, the number of bins is " << NBINS_m << std::endl;
  std::cout << "Fe: For the fit, the number of free parameters is " << NFREEPARAMS_m << std::endl;
  std::cout << "Fe: For the fit, the number of degrees of freedom is " << NDOF_m << std::endl;
  std::cout << std::endl;
  std::cout << "Fe: For the fit, the Chi-squared value is " << CHI2_m << std::endl;
  std::cout << "Fe: For the fit, the average Chi-squared value per bin is " << CHI2PERBIN_m << std::endl;
  std::cout << "Fe: For the fit, the P-value (Probability) is " << PVAL_m << std::endl;
  std::cout << std::endl;
  
  TString Chisqe = "#scale[0.5]{Fit P-value = " + to_string( PVAL_m ) + "}";
  TString Bc = "";
  if (strcmp(label,"") != 0)
  {
  Bc = "#scale[0.375]{Bin Name: " + to_string( label ) + "}";
  }

  TLatex *t = new TLatex( .04, .01, Chisqe );
  t->SetNDC(kTRUE);
  t->Draw();
  TLatex *t2 = new TLatex( .25, .97, Bc);
  t2->SetNDC(kTRUE);
  t2->Draw();
  
  // Save output plot
  std::ostringstream outEPS;
  outEPS << outDir << "/" << "D0_M_MassFit__m" << label << ".eps";
  D0_MCanvas_m->Print(outEPS.str().c_str()); // Encapsulated PostScript format
  
  // Store the FITTED SIGNAL PDF
  RooWorkspace *rwsSet1 = new RooWorkspace("rwsSet1","workspace") ;
  rwsSet1->import( sigPdf_m ) ;
  rwsSet1->import( bkgPdf_m ) ;
  rwsSet1->import( *ReducedDataSet_m, Rename("data") ) ;
  rwsSet1->Print();
  std::ostringstream outName;
  outName << outDir << "/" << "WS_data_m_D0_M" << label << ".root";
  rwsSet1->writeToFile(outName.str().c_str());
  
  //  std::cout << "M plot Count = " << allCount << std::endl;
  AllPlotsM->cd(allCount);
  D0_Mframe_m->Draw(); // Put our plot on the canvas.
  TLine *lLine_m_APM = new TLine(mean_m.getVal()-3*sig_m.getVal(),0,mean_m.getVal()-3*sig_m.getVal(),framemaxvalue_m);
  TLine *rLine_m_APM = new TLine(mean_m.getVal()+3*sig_m.getVal(),0,mean_m.getVal()+3*sig_m.getVal(),framemaxvalue_m);
  // TLine* rLine_m_APM= new TLine(mean_m.getVal()+3*sigB1_m.getVal(),0,mean_m.getVal()+3*sigB1_m.getVal(),framemaxvalue_m);
  lLine_m_APM->SetLineColor(38);
  rLine_m_APM->SetLineColor(38);
  lLine_m_APM->Draw();
  rLine_m_APM->Draw();
  TLatex *t_APM = new TLatex( .04, .01, Chisqe );
  t_APM->SetNDC(kTRUE);
  t_APM->Draw();
  TLatex *t2_APM = new TLatex( .25, .97, Bc);
  t2_APM->SetNDC(kTRUE);
  t2_APM->Draw();
  //  AllPlotsM->Print("./test/all_help_M.eps") ;
 
  //  delete t2_APM;
  //  delete t_APM;
  //  delete rLine_m_APM;
  //  delete lLine_m_APM;
  delete rwsSet1;
  delete t2;
  delete t;
  delete rLine_m;
  delete lLine_m;
  delete D0_MCanvas_m;
  delete D0_M; 

  return;
  
}


/////////////////////////////////////////////////////////////////////////
//
// Standard Background Subtraction by Paras Naik, et al. Oct. 2010
//
// This tutorial shows an example of using Standard Background Subtraction to unfold two distributions.
// The physics context for the example is that we want to know 
// the LogIPCHI2 distribution for real NeutralDs from D0 events 
// and fake NeutralDs from BACKGROUND.  LogIPCHI2 is our 'control' variable
// To unfold them, we need a model for an uncorrelated variable that
// discriminates between D0 and BACKGROUND.  To do this, we use the invariant 
// mass of NeutralDs.  We model the D0 with a Gaussian and the BACKGROUND
// with a Chebyshev polynomial.
//
// If we didn't have real data in this tutorial, we'd need to generate
// toy data.  To do that we'd need a model for the LogIPCHI2 variable for
// both D0 and BACKGROUND.  This would only be used to generate the toy data, and is
// not needed since we have real data.
/////////////////////////////////////////////////////////////////////////

void LAMBSFitter::standard_LogIPCHI2(const char* outDir = "./test",
                        const int aCase = 1, const char* label = "")
{
  std::cout << "In LAMBSFitter::standard_LogIPCHI2" << std::endl;

  std::ostringstream inFile_ss;
  inFile_ss << outDir << "/" << "WS_data_m_D0_M" << label << ".root";
  char *inFileName = 0;
  inFileName = new char [inFile_ss.str().size()+1];
  strcpy (inFileName, inFile_ss.str().c_str());  // inFileName now contains a c-string copy of inFile_ss.str()

  switch (aCase)
  {
  default:
    LeftSB_low = (1865 - 75);
    LeftSB_high = (1865 - 30);
    RightSB_low = (1865 + 30);
    RightSB_high = (1865 + 75);
    break;
  }
  TString Ll = to_string(LeftSB_low);
  TString Lh = to_string(LeftSB_high);
  TString Rl = to_string(RightSB_low);
  TString Rh = to_string(RightSB_high);
  switch (aCase)
  {
  default:
    BkgReg = "( (( m > "+Ll+") && (m < "+Lh+")) || (( m >"+Rl+" ) && (m < "+Rh+")) )";
    break;
  }
  
  // Create a new workspace to manage the project.
  RooWorkspace* wspace = new RooWorkspace("myWS");
  
  // add the signal and background models to the workspace from a ROOT file.
  //
  AddModel(wspace, inFileName, outDir, label);
  
  // inspect the workspace after AddModel
  //  wspace->Print();
  
  // add real data to the workspace from a ROOT file.
  AddData(wspace, inFileName);
  
  // inspect the workspace after AddData
  //  wspace->Print();
  
  // do Standard. Function gives W a value. 
  double Wx = 1;
  double *Weight = &Wx;
  DoStandard(wspace,Weight,outDir,aCase, label);
  
  //  std::cout << "Weight is now: " << *Weight << std::endl;
  
  // Uncomment to make some plots showing the discriminating variable and 
  // the control variable after unfolding.
  //  MakePlots(wspace,Weight,outDir,aCase, label);
  
  // cleanup
  delete wspace;
  delete inFileName;  
}

 
//____________________________________
void LAMBSFitter::AddModel(RooWorkspace* ws, char * inFileName , const char * outDir = "./test", const char * label = ""){

  // Make models for signal and background (D0 and BACKGROUND)

  // set range of observable
  //  Double_t lowRange = 1800, highRange = 1920;
  Double_t lowRange = LeftSB_low, highRange = RightSB_high;

  // make a RooRealVar for the observables
  RooRealVar D0_M("D0_M", "M_{inv}", lowRange, highRange,"MeV");
  RooRealVar LogIPCHI2("LogIPCHI2", "LogIPCHI2", ipmin, ipmax, "");

  /////////////////////////////////////////////
  // load mass model for D0 and BACKGROUND
  //
  //
  //  std::cout << "load D0 model" << std::endl; 

  TFile *w_filein = new TFile(inFileName) ;
  RooWorkspace* w_in = (RooWorkspace*) w_filein->Get("rwsSet1") ;
  //  std::cout << "Workspace In" << std::endl;
  //  w_in->Print();

  // mass model for D0
  RooAbsPdf *D0Model = w_in->pdf("sigPdf_m") ;
  D0Model->SetName("D0Model");
  //  std::cout << "Signal Model In" << std::endl;
  D0Model->Print("t") ;









  //////////////////////////////////////////////
  // make BACKGROUND model

  //  std::cout << "make BACKGROUND model" << std::endl;

  RooAbsPdf *BACKGROUNDModel = w_in->pdf("bkgPdf_m") ;
  BACKGROUNDModel->SetName("BACKGROUNDModel");
  //  std::cout << "Background Model In" << std::endl;
  BACKGROUNDModel->Print("t") ;












  //////////////////////////////////////////////
  // combined model  

  // These variables represent the number of D0 or BACKGROUND events
  // They will be fitted.
  RooRealVar D0Yield("D0Yield","fitted yield for D0",1000.,0.,1000000.) ; 
  RooRealVar BACKGROUNDYield("BACKGROUNDYield","fitted yield for BACKGROUND", 3000. ,0.,100000.) ; 

  // now make the combined model
  //  std::cout << "make full model" << std::endl;
  RooAddPdf model("model","D0+BACKGROUND background models",
                  RooArgList(*D0Model, *BACKGROUNDModel), 
                  RooArgList(D0Yield, BACKGROUNDYield));
  
  // interesting for debugging and visualizing the model
  std::ostringstream dotFile_ss;
  dotFile_ss << outDir << "/" << "fullModeldata_standard_LogIPCHI2" << label << ".dot";
  model.graphVizTree(dotFile_ss.str().c_str());
  
  //  std::cout << "import model" << std::endl;

  ws->import(model);

  delete w_filein;
}

//____________________________________
void LAMBSFitter::AddData(RooWorkspace* ws, char * inFileName){

  TFile *w_filein = new TFile(inFileName) ;
  RooWorkspace* w_in = (RooWorkspace*) w_filein->Get("rwsSet1") ;
  //  std::cout << "Workspace In" << std::endl;
  //  w_in->Print();
  RooDataSet *data = (RooDataSet*) w_in->data("data") ;
  //  std::cout << "Data In" << std::endl;
  //  data->Print() ;
  
  ws->import(*data, Rename("data"));

  delete w_filein;
}





























//____________________________________
void LAMBSFitter::DoStandard(RooWorkspace* ws, double* W, const char * outDir, int bCase, const char * label){
  //  std::cout << "Calculate sWeights" << std::endl;

  // get what we need out of the workspace to do the fit
  //  RooAbsPdf* model = ws->pdf("model");
  RooAbsPdf* D0Model = ws->pdf("D0Model");
  RooAbsPdf* BACKGROUNDModel = ws->pdf("BACKGROUNDModel");
  RooRealVar* D0Yield = ws->var("D0Yield");
  RooRealVar* BACKGROUNDYield = ws->var("BACKGROUNDYield");
  RooDataSet* data = (RooDataSet*) ws->data("data");
  RooRealVar* D0_M; 
  switch (bCase)
  {
  default:

    D0_M = ws->var("m");
    break;
  }
  RooRealVar* LogIPCHI2 = ws->var("LogIPCHI2");
  
  //  std::cout << "DoStandard() fitTo" << std::endl;

  // fit the model to the data.
  //  model->fitTo(*data, Extended() );
  //  std::cout << "DoStandard() fitTo done" << std::endl;
  
  // The Standard technique requires that we fix the parameters
  // of the model that are not yields after doing the fit. (actually, does it really? I don't think so)
  RooRealVar* mean_m = ws->var("mean_m");
  RooRealVar* sig_m = ws->var("sig_m");
  //  RooRealVar* c0_m = ws->var("c0_m");  
  mean_m->setConstant();
  sig_m->setConstant();
  //  c0_m->setConstant();
  
  RooMsgService::instance().setSilentMode(true);
  
  
  // Now we determine the weight W = ( S_B / (B_L + B_R) )
  double SigR_low = mean_m->getVal() - 3 * sig_m->getVal() ;
  double SigR_high = mean_m->getVal()  + 3 * sig_m->getVal() ;
  //  std::cout << SigR_low << " " << SigR_high << std::endl;
  
  // How many background events are there in the signal region?
  //  std::cout << "before first NormalizedIntegral" << std::endl;
  double bkgfrac = NormalizedIntegral(BACKGROUNDModel, *D0_M, SigR_low, SigR_high);
  //  std::cout << "after first NormalizedIntegral" << std::endl;
  double S_B = bkgfrac*BACKGROUNDYield->getVal();
  printf("\n model: The number of background events between (%f-%f) and (%f+%f) is %f.\n", 
         mean_m->getVal(), 3 * sig_m->getVal(), mean_m->getVal(), 3 * sig_m->getVal(),  S_B);
  
  // How many background events are there in the background regions?
  double bkgfracL = NormalizedIntegral(BACKGROUNDModel, *D0_M, LeftSB_low, LeftSB_high);
  double bkgfracR = NormalizedIntegral(BACKGROUNDModel, *D0_M, RightSB_low, RightSB_high);
  double B_L = (bkgfracL)*BACKGROUNDYield->getVal();
  double B_R = (bkgfracR)*BACKGROUNDYield->getVal();
  printf("\n model: The number of background events between (%f) and (%f) is %f.\n", LeftSB_low, LeftSB_high, B_L );
  printf("\n model: The number of background events between (%f) and (%f) is %f.\n", RightSB_low, RightSB_high, B_R );
  
  printf("\n model: The weight was %f.\n", *W );
  *W = S_B / (B_L + B_R);
  printf("\n model: The weight is %f.\n", *W );
  
  // How many Signal events are there in the signal region??
  double sigfrac = NormalizedIntegral(D0Model, *D0_M, SigR_low, SigR_high);
  printf("\n model: The number of Signal events between  (%f-%f) and (%f+%f) is %f.\n", 
         mean_m->getVal(), 3 * sig_m->getVal(), mean_m->getVal(), 3 * sig_m->getVal(), sigfrac*D0Yield->getVal() );
  
  TString Sl = to_string((mean_m->getVal() - 3 * sig_m->getVal() )) ;
  TString Sh = to_string((mean_m->getVal() + 3 * sig_m->getVal() )) ;
  switch (bCase)
  {
  default:
    SigReg = "(m > " + Sl +") && (m < " + Sh + ")";
    break;
  }
  
  LogIPCHI2->setRange(ipmin,ipmax);

  int nBins = 25;
  //  LogIPCHI2->setBins(nBins); 
  double currentMin = ipmin; 
  double currentBL = ipmin; 
  double incr = (ipmax-ipmin)/nBins; 
  std::vector<double> boundaries;
  vector<double>::iterator iB;
  while (currentBL <= (ipmax + 0.000001))
  {
    char testBinChar[100];
    sprintf(testBinChar,"(LogIPCHI2 > %4.2f) && (LogIPCHI2 < %4.2f)",currentMin,currentBL);
    TCut testBin = testBinChar;
    RooDataSet *current = (RooDataSet*)data->reduce( testBin );
    int Entries = current->numEntries();
    if (Entries < 2) 
    {
      if ( (currentBL > (ipmax - 0.000001)) && (currentMin != ipmin))
      {
        boundaries.pop_back();
      }
      currentBL += incr;
      continue;
    }
    if (currentBL < (ipmax - 0.000001)) 
    {
      currentMin = currentBL;
      boundaries.push_back(currentMin);
    }
    currentBL += incr;
  }

  RooBinning* AdaptiveBinning = new RooBinning(ipmin,ipmax,0);
  for ( iB = boundaries.begin(); iB != boundaries.end(); ++iB )
  {
    AdaptiveBinning->addBoundary(*iB);
  }
  LogIPCHI2->setBinning(*AdaptiveBinning,0);
 
  std::vector<double> density;
  double nominalBinSize = (ipmax-ipmin)/LogIPCHI2->getBins();
  if (boundaries.size() == 0)
  {
    density.push_back( ( ipmax - ipmin ) / nominalBinSize);
  }
  if (boundaries.size() == 1)
  {
    density.push_back( ( *(boundaries.begin()) - ipmin ) / nominalBinSize);
    density.push_back( ( ipmax - *((boundaries.end() - 1)) ) / nominalBinSize);
  }
  if (boundaries.size() >= 2)
  {
    density.push_back( ( *(boundaries.begin()) - ipmin ) / nominalBinSize);
  //    cout << "first" << ((*boundaries.begin()) - ipmin) / nominalBinSize  << endl;
    for ( iB = boundaries.begin(); iB != (boundaries.end() - 1) ; ++iB )
    {
      density.push_back( (*(iB+1) - *iB ) / nominalBinSize);
  //      cout << (*(iB+1) - *iB) / nominalBinSize << endl;
    }
    density.push_back( ( ipmax - *((boundaries.end() - 1)) ) / nominalBinSize);
  //    cout << (ipmax - *((boundaries.end() - 1))) / nominalBinSize << endl;
  }


  RooDataSet *data_backreg = (RooDataSet*)data->reduce( (BkgReg) );
  data_backreg->Print();
  RooDataSet *data_sigreg  = (RooDataSet*)data->reduce( (SigReg) );
  data_sigreg->Print();

  RooDataHist *whist_backreg = new RooDataHist("LogIPCHI2_histback", "Log10 of IP chi^2", RooArgSet(*LogIPCHI2), *data_backreg);
  whist_backreg->Print();

  TCanvas* ahb = new TCanvas("StandardB","Standard data (b)", 1200, 800);
  RooPlot* ahbf = LogIPCHI2->frame()  ; // same way you made 'frame'
  whist_backreg->plotOn(ahbf) ;
  std::ostringstream ahbf_ss;
  ahbf_ss << "ahbf" << label; 
  ahbf->SetName(ahbf_ss.str().c_str());
  ahbf->SetTitle("Unweighted Background LogIPCHI2 in Bins");
  ahbf->Draw() ;
  std::ostringstream ahbFile_ss;
  ahbFile_ss << outDir << "/" << "hstandard_back_LogIPCHI2" << label << ".eps";
  //  ahb->SaveAs(ahbFile_ss.str().c_str());

  RooDataHist *whist_sigreg = new RooDataHist("LogIPCHI2_histsig", "Log10 of IP chi^2", RooArgSet(*LogIPCHI2), *data_sigreg);
  whist_sigreg->Print();

  TCanvas* ahs = new TCanvas("StandardS","Standard data (s)", 1200, 800);
  RooPlot* ahsf = LogIPCHI2->frame()  ; // same way you made 'frame'
  whist_sigreg->plotOn(ahsf) ;
  std::ostringstream ahsf_ss;
  ahsf_ss << "ahsf" << label; 
  ahsf->SetName(ahsf_ss.str().c_str()); 
  ahsf->SetTitle("Unweighted Signal LogIPCHI2 in Bins");
  ahsf->Draw() ;
  std::ostringstream ahsFile_ss;
  ahsFile_ss << outDir << "/" << "hstandard_sig_LogIPCHI2" << label << ".eps";
  //  ahs->SaveAs(ahsFile_ss.str().c_str());

  // calculate bin errors first
  std::vector<double> backHistErrors;
  std::vector<double> sigHistErrors;
  std::vector<double> totalHistErrors;
  std::vector<double> backHistContent;
  std::vector<double> sigHistContent;
  std::vector<double> totalHistContent;
  double gB = LogIPCHI2->getBins();
  std::ostringstream nameStringB_ss;
  nameStringB_ss << "th1b" << label;
  TH1F *cHB = (TH1F*) whist_backreg->createHistogram(nameStringB_ss.str().c_str(),*LogIPCHI2,Binning(*AdaptiveBinning));
  std::ostringstream nameStringS_ss;
  nameStringS_ss << "th1s" << label;
  TH1F *cHS = (TH1F*) whist_sigreg->createHistogram(nameStringS_ss.str().c_str(),*LogIPCHI2,Binning(*AdaptiveBinning));
  for (int iGB = 1; iGB <= gB ; ++iGB)
  { 
    backHistContent.push_back(cHB->GetBinContent(iGB));
  //    backHistErrors.push_back(cHB->GetBinError(iGB)); // THIS DOESN'T WORK FOR FIRST BIN (must be a bug)
    backHistErrors.push_back(sqrt(cHB->GetBinContent(iGB)));
    sigHistContent.push_back(cHS->GetBinContent(iGB));
  //    sigHistErrors.push_back(cHS->GetBinError(iGB)); // THIS DOESN'T WORK FOR FIRST BIN (must be a bug)
    sigHistErrors.push_back(sqrt(cHS->GetBinContent(iGB)));
  // fix the errors
    double theError = 
        sqrt( sigHistErrors[iGB-1] * sigHistErrors[iGB-1] + (0 - *W) * (0 - *W) * backHistErrors[iGB-1] * backHistErrors[iGB-1]);
    if (theError < sqrt( 1 * 1 + (0 - *W) * (0 - *W) * 1 * 1 ) ) 
    {
      theError = sqrt( 1 * 1 + (0 - *W) * (0 - *W) * 1 * 1 ) ;
    }
    totalHistErrors.push_back(theError);
    totalHistContent.push_back( ( sigHistContent[iGB-1] - *W * backHistContent[iGB-1] ) );
  }
  // Print out details of the content
  /* 
       std::cout << std::endl << "sigContent: " ;
        for ( iB = sigHistContent.begin(); iB != sigHistContent.end(); ++iB )
        {
          std::cout << *iB << " ";
        }
        std::cout << "" << std::endl;
 
        std::cout << "sigErrors: " ;
        for ( iB = sigHistErrors.begin(); iB != sigHistErrors.end(); ++iB )
        {
          std::cout << *iB << " ";
        }
        std::cout << "" << std::endl << std::endl;

        std::cout << "backContent: " ;
        for ( iB = backHistContent.begin(); iB != backHistContent.end(); ++iB )
        {
          std::cout << *iB << " ";
        }
        std::cout << "" << std::endl;

        std::cout << "backErrors: " ;
        for ( iB = backHistErrors.begin(); iB != backHistErrors.end(); ++iB )
        {
          std::cout << *iB << " ";
        }
        std::cout << "" << std::endl << std::endl;

        std::cout << "totalContent: " ;
        for ( iB = totalHistContent.begin(); iB != totalHistContent.end(); ++iB )
        {
          std::cout << *iB << " ";
        }
        std::cout << "" << std::endl;

        std::cout << "totalErrors: " ;
        for ( iB = totalHistErrors.begin(); iB != totalHistErrors.end(); ++iB )
        {
          std::cout << *iB << " ";
        }
        std::cout << "" << std::endl << std::endl;
  */

  // do the background subtraction
  whist_sigreg->add(*whist_backreg, "(1 == 1)", (0 - *W)) ;
  whist_sigreg->Print();

  RooDataHist *DcHS = new RooDataHist("LogIPCHI2_histback", "Log10 of IP chi^2", RooArgSet(*LogIPCHI2));
  std::ostringstream nameStringT_ss;
  nameStringT_ss << "th1t" << label;
  TH1F *cHT = (TH1F*) DcHS->createHistogram(nameStringT_ss.str().c_str(),*LogIPCHI2,Binning(*AdaptiveBinning));
  //  TH1F *cHT = whist_sigreg->createHistogram("th1t",*LogIPCHI2,Binning(*AdaptiveBinning));
  int iCHT = 0;
  for ( iB = totalHistContent.begin(); iB != totalHistContent.end(); ++iB )
  {
    iCHT++;
    cHT->SetBinContent(iCHT,*iB); // if using content
  //    cHT->SetBinContent(iCHT,*iB / density[iCHT-1]); // if using density
  }
  iCHT = 0; 
  for ( iB = totalHistErrors.begin(); iB != totalHistErrors.end(); ++iB )
  {
    iCHT++;
    cHT->SetBinError(iCHT,*iB); // if using content
  //    cHT->SetBinError(iCHT,*iB / density[iCHT-1]); // if using density  ?
  }

  cout << "after setbin" << endl;
  cHT->Print();
  // if using content
  RooDataHist *whist_sigreg2 = new RooDataHist("LogIPCHI2_histnewerrors", "Log10 of IP chi^2", 
                                               RooArgSet(*LogIPCHI2), Import(*cHT,kFALSE));
  // if using density
  //  RooDataHist *whist_sigreg2 = new RooDataHist("LogIPCHI2_histnewerrors", 
  //                                               "Log10 of IP chi^2", RooArgSet(*LogIPCHI2), Import(*cHT,kTRUE));
  whist_sigreg2->Print();

  RooRealVar D0_w("D0_w","D0_w",-1,1) ; 
  D0_w.setVal(1) ; data_sigreg->addColumn(D0_w,kFALSE) ; 
  D0_w.setVal(0 - *W) ; data_backreg->addColumn(D0_w,kFALSE) ; 
  data_sigreg->append(*data_backreg); 
  data_sigreg->Print();
  RooDataSet* wdata_sigreg = new RooDataSet(data_sigreg->GetName(),
                                            data_sigreg->GetTitle(),
                                            data_sigreg,
                                            *data_sigreg->get(),
                                            0,
                                            D0_w.GetName()) ;
  wdata_sigreg->Print();

  TCanvas* adata = new TCanvas("Standard","Standard data", 1200, 800);
  adata->Divide(1,1);
  adata->cd(1);
  RooPlot* framex = LogIPCHI2->frame()  ; // same way you made 'frame'
  wdata_sigreg->plotOn(framex,DataError(RooAbsData::SumW2)) ;
  std::ostringstream framex_ss;
  framex_ss << "framex" << label; 
  framex->SetName(framex_ss.str().c_str());  
  framex->SetTitle("Weighted LogIPCHI2");
  framex->Draw() ;
  std::ostringstream adataFile_ss;
  adataFile_ss << outDir << "/" << "standard_w_LogIPCHI2" << label << ".eps";
  //  adata->SaveAs(adataFile_ss.str().c_str());

  TCanvas* hadata = new TCanvas("StandardHist","Standard dataHist", 1200, 800);
  hadata->Divide(1,1);
  hadata->cd(1);
  RooPlot* hframex = LogIPCHI2->frame()  ; // same way you made 'frame'
  whist_sigreg->plotOn(hframex,DataError(RooAbsData::SumW2)) ; 
  std::ostringstream hframex_ss;
  hframex_ss << "hframex" << label; 
  hframex->SetName(hframex_ss.str().c_str());  
  hframex->SetTitle("Weighted LogIPCHI2 in Bins");
  hframex->Draw() ;
  std::ostringstream hadataFile_ss;
  hadataFile_ss << outDir << "/" << "hstandard_w_LogIPCHI2" << label << ".eps";
  //  hadata->SaveAs(hadataFile_ss.str().c_str());

  TCanvas* qhadata = new TCanvas("StandardHist2","Standard dataHist", 1200, 800);
  qhadata->Divide(1,1);
  qhadata->cd(1);
  RooPlot* qhframex = LogIPCHI2->frame()  ; // same way you made 'frame'
  whist_sigreg2->plotOn(qhframex,DataError(RooAbsData::SumW2)) ; 
  std::ostringstream qhframex_ss;
  qhframex_ss << "qhframex" << label; 
  qhframex->SetName(qhframex_ss.str().c_str());  
  qhframex->SetTitle("Weighted LogIPCHI2 in Bins");
  qhframex->Draw() ;
  std::ostringstream qhadataFile_ss;
  qhadataFile_ss << outDir << "/" << "qhstandard_w_LogIPCHI2" << label << ".eps";
  //  qhadata->SaveAs(qhadataFile_ss.str().c_str());

  // import this new dataset with Weights
  std::cout << "import new dataset with Weights" << std::endl;
  ws->import(*data_sigreg, Rename("dataWithWeights"));
  //  ws->Print();
  // import this new dataHist with Weights
  std::cout << "import new dataHist with Weights" << std::endl;
  ws->import(*whist_sigreg, Rename("histWithWeights"));
  //  ws->Print();
  // import this new dataHist with Weights
  std::cout << "import new dataHist with Content and Errors defined by me" << std::endl;
  ws->import(*whist_sigreg2, Rename("histWithMyErrors"));
  //  ws->Print();
  std::ostringstream wsFile_ss;
  wsFile_ss << outDir << "/" << "dataWithWeights_LogIPCHI2" << label << ".root";
  ws->writeToFile(wsFile_ss.str().c_str());

  delete qhadata;
  delete hadata;
  delete adata;
  delete wdata_sigreg;
  delete whist_sigreg2;
  delete DcHS;
  delete ahs;
  delete whist_sigreg;
  delete ahb;
  delete whist_backreg;
  delete AdaptiveBinning;
}

void LAMBSFitter::MakePlots(RooWorkspace* ws, double* W, const char * outDir = "./test", int cCase = 2, const char * label = "")
{
  
  // Here we make plots of the discriminating variable (D0_M) after the fit
  // and of the control variable (LogIPCHI2) after unfolding with Standard.
  std::cout << "make plots" << std::endl;
  
  // make our canvas
  TCanvas* cdata = new TCanvas("Standard","Standard data", 1200, 800);
  cdata->Divide(3,2);
  std::cout << "canvas made" << std::endl;
  
  // get what we need out of the workspace
  RooAbsPdf* model = ws->pdf("model");
  RooAbsPdf* D0Model = ws->pdf("D0Model");
  RooAbsPdf* BACKGROUNDModel = ws->pdf("BACKGROUNDModel");
  std::cout << "got models" << std::endl;

  RooRealVar* D0_M;
  RooRealVar* LogIPCHI2 = ws->var("LogIPCHI2");
  LogIPCHI2->setRange(ipmin,ipmax);
  switch (cCase)
  {
  default:
    D0_M = ws->var("m");
    break;
  }
  std::cout << "got vars" << std::endl;
  
  // note, we get the dataset 
  RooDataSet* data = (RooDataSet*) ws->data("data");
  std::cout << "got data" << std::endl;
  
  // this shouldn't be necessary, need to fix something with workspace
  // do this to set parameters back to their fitted values.
  std::cout << "MakePlots() fitTo" << std::endl;
  model->fitTo(*data, Extended(), NumCPU(6) );
  std::cout << "MakePlots() fitTo done" << std::endl;
  
  //plot D0_M for data with full model and individual componenets overlayed
  //  TCanvas* cdata = new TCanvas();
  cdata->cd(1);
  RooPlot* frame = D0_M->frame() ; 
  // display fit parameters
  //  model->paramOn(frame, ShowConstants(kFALSE), Format("NELU", AutoPrecision(2)), Layout(0.65, 0.95, 0.95) )->getAttText()->SetTextSize(0.030); 
  model->paramOn(frame, ShowConstants(kFALSE), Format("NELU", AutoPrecision(2)) ); // display fit parameters
  model->plotOn(frame,Name("modelname")) ;
  model->plotOn(frame,Components(*D0Model),LineStyle(kDashed), LineColor(kRed)) ;     
  model->plotOn(frame,Components(*BACKGROUNDModel),LineStyle(kDashed),LineColor(kGreen)) ;    
  //  data->statOn(frame);
  data->plotOn(frame,Name("dataname")) ;
  std::cout << "after model paramOn" << std::endl;
  
  std::ostringstream frame_ss;
  frame_ss << "frame" << label; 
  frame->SetName(frame_ss.str().c_str());  
  frame->SetTitle("Fit of model to discriminating variable");
  frame->Draw() ;
  std::cout << "frame->Draw" << std::endl;
  
  std::cout << "frame->chiSquare: " <<  frame->chiSquare("modelname","dataname") << std::endl;
  
  cdata->cd(4);
  RooPlot* frame1a = D0_M->frame()  ; // same way you made 'frame'
  frame1a->addObject(frame->pullHist("dataname","modelname")) ;
  //  frame1a->SetMinimum(-5) ;
  //  frame1a->SetMaximum(+5) ;
  std::ostringstream frame1a_ss;
  frame1a_ss << "frame1a" << label; 
  frame1a->SetName(frame1a_ss.str().c_str());  
  frame1a->SetTitle("pull histogram -- and the chi squared is...");
  frame1a->Draw() ;
  
  TString Chisqe = to_string( frame->chiSquare("modelname","dataname") );  

  TLatex *t = new TLatex( .04, .01, Chisqe );
  t->SetNDC(kTRUE);
  t->Draw();
  
  cdata->cd(5);
  RooPlot* frame1b = D0_M->frame()  ; // same way you made 'frame'
  frame1b->addObject(frame->residHist("dataname","modelname")) ;
  //frame1b->SetMinimum(-30) ;
  //frame1b->SetMaximum(+30) ;
  std::ostringstream frame1b_ss;
  frame1b_ss << "frame1b" << label; 
  frame1b->SetName(frame1b_ss.str().c_str());  
  frame1b->SetTitle("residual Histogram");
  frame1b->Draw() ;

  // Plot LogIPCHI2 for D0 component.  
  // Do this by plotting all events weighted by the sWeight for the D0 component.
  // The Standard class adds a new variable that has the name of the corresponding
  // yield + "_sw".
  cdata->cd(2);

  // create weightfed data set 
  RooDataSet *dataw_back_pre = new RooDataSet(data->GetName(),data->GetTitle(),data,*data->get(),0,0) ;
  //  RooDataSet *dataw_back_pre = new RooDataSet(data->GetName(),data->GetTitle(),data,*data->get(),0,"D0Yield_sw") ;
  RooDataSet *dataw_back = (RooDataSet*)dataw_back_pre->reduce( (BkgReg) );
  
  //  RooPlot* frame2 = LogIPCHI2->frame() ; 
  //  dataw_back->plotOn(frame2, DataError(RooAbsData::SumW2) ) ; 
  //  dataw_back->statOn(frame2); 
  
  //std::ostringstream frame2_ss;
  //frame2_ss << "frame2" << label; 
  //frame2->SetName(frame2_ss.str().c_str());  
  //  frame2->SetTitle("LogIPCHI2 distribution");
  //  frame2->Draw() ;
  //  std::cout << "frame2->Draw" << std::endl;
  
  std::ostringstream nS_b_ss;
  nS_b_ss << "LogIPCHI2back" << label;
  TH1F *back1 = (TH1F*) dataw_back->createHistogram(nS_b_ss.str().c_str(),*LogIPCHI2);
  //  back1->Sumw2();
  back1->GetXaxis()->SetTitle("");
  std::cout << "Weight: " << *W << std::endl;
  back1->Scale(*W);
  back1->Draw();
  //back1->Draw("esame");
  
  
  // Plot LogIPCHI2 for BACKGROUND component.  
  // Eg. plot all events weighted by the sWeight for the BACKGROUND component.
  // The Standard class adds a new variable that has the name of the corresponding
  // yield + "_sw".
  cdata->cd(3);
  RooDataSet *dataw_D0_pre = new RooDataSet(data->GetName(),data->GetTitle(),data,*data->get(),0,0) ;
  //  RooDataSet *dataw_D0_pre = new RooDataSet(data->GetName(),data->GetTitle(),data,*data->get(),0,"BACKGROUNDYield_sw") ;
  RooDataSet *dataw_D0 = (RooDataSet*)dataw_D0_pre->reduce( (SigReg) );
  
  RooPlot* frame3 = LogIPCHI2->frame() ; 
  dataw_D0->plotOn(frame3,DataError(RooAbsData::SumW2)) ; 
  dataw_D0->statOn(frame3);  
  std::ostringstream frame3_ss;
  frame3_ss << "frame3" << label; 
  frame3->SetName(frame3_ss.str().c_str());  
  frame3->SetTitle("LogIPCHI2 distribution for Signal");
  frame3->Draw() ;
  std::cout << "frame3->Draw" << std::endl;
  
  // Plot Background subtracted signal
  cdata->cd(5);
  std::ostringstream nS_s_ss;
  nS_s_ss << "LogIPCHI2sig" << label;
  TH1F *sig1 = (TH1F*) dataw_D0->createHistogram(nS_s_ss.str().c_str(),*LogIPCHI2);
  //sig1->Sumw2();
  sig1->GetXaxis()->SetTitle("");
  sig1->Add(back1,-1);
  sig1->Draw();
  //sig1->Draw("esame");
  std::cout << "sig1->Draw" << std::endl;  
  
  // Plot Mass vs LogIPCHI2 all.
  cdata->cd(6);
  RooPlot* frame4 = new RooPlot(*D0_M, *LogIPCHI2) ;
  TH2F* histo6 = data->createHistogram(*D0_M,*LogIPCHI2) ;
  
  
  
  
  //  data->plotOn(frame4) ;
  //  data->statOn(frame4);
  
  frame4->SetTitle("discriminating variable and isolation variable");
  //  frame4->Draw() ;
  histo6->Draw();

  
  
  
  






  std::cout << "frame4->Draw" << std::endl;

  
  std::ostringstream cdataFile_ss;
  cdataFile_ss << outDir << "/" << "standard_LogIPCHI2" << label << ".eps";
  cdata->SaveAs(cdataFile_ss.str().c_str());

  delete frame4;
  delete dataw_D0_pre;
  delete dataw_back_pre;
  delete t;
  delete cdata;
  
}


void LAMBSFitter::roofit_datafit_standard_LogIPCHI2(const char* outDir = "./test", const int aCase = 1, const char * label = "", 
                                                    const char* biglabel = "", const int bB = 0)
{
  std::cout << "In LAMBSFitter::roofit_datafit_standard_LogIPCHI2" << std::endl;

  std::cout << "Make Log IP"<< std::endl;
  // Log IP
	RooRealVar LogIP("LogIP", "Log of IP", -8, 2, "log mm");
  std::cout << "Make Log IP CHI2"<< std::endl;
  // Log IPCHI2
	RooRealVar *LogIPCHI2 = 0;
  switch (aCase)
  {
  default:
    LogIPCHI2 = new RooRealVar("LogIPCHI2", "Log_10 of IP chi^2", ipmin, ipmax, "log_10 chi^2");
    (*LogIPCHI2).setVal(0.5); 
    break;
  }
  int nBins = 25;

	// Cuts
  
  TCut NC = "(1 == 1)"; // No Cuts Needed
  
	// load data into dataSet
	
  std::ostringstream inFile_ss;
  inFile_ss << outDir << "/" << "dataWithWeights_LogIPCHI2" << label << ".root";
  char *inFileName = 0;
  inFileName = new char [inFile_ss.str().size()+1];
  strcpy (inFileName, inFile_ss.str().c_str());  // inFileName now contains a c-string copy of inFile_ss.str()

  TFile *data_w_filein = new TFile(inFileName) ; 
  //  data_w_filein->Print();
  RooWorkspace* data_w_in = (RooWorkspace*) data_w_filein->Get("myWS") ; 
  //  data_w_in->Print();
  RooDataSet *data = (RooDataSet*) data_w_in->data("dataWithWeights") ; 
  data->Print("") ;
  RooDataSet *dataSet = new RooDataSet(data->GetName(),data->GetTitle(),data,*data->get(),0,"D0_w") ;
  dataSet->Print("") ;
  //  RooDataHist *dataHist = data_w_in->data("histWithWeights") ; 
  RooDataHist *dataHist = (RooDataHist*) data_w_in->data("histWithMyErrors") ; 
  dataHist->Print("") ;
  
  std::cout << "Make Cuts"<< std::endl;
  //	// Perform Reduce Dataset
  //	RooDataSet* ReducedDataSetNC = (RooDataSet*)dataSet->reduce( (NC) );
  //  ReducedDataSetNC->Print();
  
  std::cout << "Make inPro and inSec"<< std::endl;

  std::ostringstream in_ss_Pro;
  std::ostringstream in_ss_Sec;
  in_ss_Pro << outDir << "/" << "PDF_prompt_LogIPCHI2_Bukin" << biglabel << ".root";
  in_ss_Sec << outDir << "/" << "PDF_secondary_LogIPCHI2_Bukin" << biglabel << ".root";
  char *inPro = 0;
  inPro = new char [in_ss_Pro.str().size()+1];
  strcpy (inPro, in_ss_Pro.str().c_str());  // inPro now contains a c-string copy of in_ss_Pro.str()
  char *inSec = 0;
  inSec = new char [in_ss_Sec.str().size()+1];
  strcpy (inSec, in_ss_Sec.str().c_str());  // inSec now contains a c-string copy of in_ss_Sec.str()

  std::cout << "Make Signal"<< std::endl;

  TFile *prompt_w_filein = new TFile(inPro) ; 
  RooWorkspace* prompt_w_in = (RooWorkspace*) prompt_w_filein->Get("rws") ; 
  //  prompt_w_in->Print();
  RooAbsPdf *promptPdfNC = prompt_w_in->pdf("sigProPdfALL") ; 
  promptPdfNC->Print("t") ;
  
  // Make Signal
  TFile *secondary_w_filein = new TFile(inSec) ; 
  RooWorkspace* secondary_w_in = (RooWorkspace*) secondary_w_filein->Get("rws") ; 
  //  secondary_w_in->Print();
  RooAbsPdf *secondaryPdfNC = secondary_w_in->pdf("sigSecPdfALL") ; 
  secondaryPdfNC->Print("t") ;
  
  RooRealVar sig_yieldNC("sig_yieldNC", "Signal yield", dataHist->sumEntries(), 
//                                        (dataHist->sumEntries()-fabs(dataHist->sumEntries())) > 0 ? 
//                                        (dataHist->sumEntries()-fabs(dataHist->sumEntries())) : 0 , 
                                        (dataHist->sumEntries()-fabs(dataHist->sumEntries()))  , 
                                        dataHist->sumEntries()+fabs(dataHist->sumEntries()));         

  RooRealVar PromptFracNC("PromptFracNC","Prompt Fraction", 0.900, 0.750, 1.000);
  RooRealVar alpha("alpha","Prompt Fraction Value from big bin", 0.900, 0.750, 1.000);
  RooRealVar ealpha("ealpha","Prompt Fraction Error from big bin", 0.900, 0.000, 1.000);
  if (bB != 0)
  { 
    alpha.setVal( 1 - SecFracsBig->GetBinContent(bB) );
    ealpha.setVal( SecFracsBig->GetBinError(bB) );
    alpha.setConstant();
    ealpha.setConstant();
//    PromptFracNC.setVal( 1 - SecFracsBig->GetBinContent(bB) );
//    PromptFracNC.setError( SecFracsBig->GetBinError(bB) );
//    PromptFracNC.setConstant();
    std::cout << "Changing alpha (central val.) and ealpha (error) to: " 
              <<  (1 - SecFracsBig->GetBinContent(bB)) << "+/-" << (SecFracsBig->GetBinError(bB)) << std::endl; 
  }  
  std::cout << "Convolve Signals" << std::endl;
  RooRealVar sigConv("sigConv", "#sigma Conv", 0.01, 0.005, 0.05, "log mm");
  //        RooRealVar sigConv("sigConv", "#sigma Conv", 0.0200, 0.0013, 0.5000, "log mm");
  RooRealVar meanConv("meanConv", "mean Conv", 0.5000, 0.0000, 1.750, "log mm");
  //        RooRealVar meanConv("meanConv", "mean Conv", 0.4000, 0.0000, 4.0000, "log mm");
  RooGaussian GaussConvPdf("GaussConvPdf", "GaussConvPdf", (*LogIPCHI2), meanConv, sigConv); 
  RooGaussian GaussConvPdf2("GaussConvPdf2", "GaussConvPdf2", (*LogIPCHI2), meanConv, sigConv); 
  //        RooRealVar sigConv2("sigConv2", "#sigma Conv2", 4.0000, 0.0091, 7.0000, "log");
  //        RooRealVar meanConv2("meanConv2", "mean Conv2", 2.0000, 1.0000, 5.0000, "log");
  //        RooGaussian GaussConvPdf2("GaussConvPdf2", "GaussConvPdf2", (*LogIPCHI2), meanConv2, sigConv2); 
  
  RooFFTConvPdf convPromptPdfNC("convPromptPdfNC", "convPromptPdfNC", (*LogIPCHI2), *promptPdfNC, GaussConvPdf, 2);
  RooFFTConvPdf convSecondaryPdfNC("convSecondaryPdfNC", "convSecondaryPdfNC", (*LogIPCHI2), *secondaryPdfNC, GaussConvPdf2, 2);        
  
  std::cout << "Choose Signal"<< std::endl;
  // Choose Signal
  RooAddPdf sigPdfNC("Total", "Prompt+Secondary", RooArgList(*promptPdfNC,*secondaryPdfNC), PromptFracNC);
  //        RooAddPdf sigPdfNC("Total", "Prompt+Secondary", RooArgList(convPromptPdfNC,convSecondaryPdfNC), PromptFracNC);
  
  std::cout << "Make Background"<< std::endl;
  // Make Background
  RooRealVar bkg_yieldNC("bkg_yieldNC", "NC Background yield", 0, 0, 0, "");          //ZERO BACKGROUND
  bkg_yieldNC.setConstant();
  //        RooRealVar bkg_yieldNC("bkg_yieldNC", "NC Background yield", 50, 0, 1000000);        
  
  // Make Chebyshev (order 0)
  RooRealVar c0NC("c0NC","Fe coef #0", 0, 0, 0, "");     // Fixed c0NC
  c0NC.setConstant();
  //        RooRealVar c0NC("c0NC","Fe coef #0", 0, -1, 1);
  
  std::cout << "Choose Background"<< std::endl;
  // Choose Background
  RooChebychev bkgPdfNC("bkgCheby0NC", "Fe Cheby Order 0 background", (*LogIPCHI2), RooArgList(c0NC));
  
  std::cout << "Choose Total NC"<< std::endl;
  // Make the totalPDFNC
  RooArgList shapesNC;
  RooArgList yieldsNC;
  shapesNC.add(sigPdfNC);
  yieldsNC.add(sig_yieldNC);
  shapesNC.add(bkgPdfNC);
  yieldsNC.add(bkg_yieldNC);
  RooAddPdf  totalPdfNC("totalPdfNC", "sum of signal and background PDF's", shapesNC, yieldsNC);
  
////////// HIST FIT

  std::cout << "Fit NC HIST" << std::endl;
  // Fit NC
  (*LogIPCHI2).setRange("R1", ipmin, ipmax) ;

  // We do not use chi2FitTo, as I don't think it has an option to use SumW2Errors, so instead we use RooChi2Var
  /*
  totalPdfNC.chi2FitTo(*dataHist, Minos(kTRUE), //Range("R1"), NumCPU(6), 
  //    totalPdfNC.fitTo(*dataHist, Minos(kTRUE), SumW2Error(kTRUE), //Range("R1"), 
                   Verbose(kV), Warnings(kW), PrintLevel(iPL), PrintEvalErrors(iPE) );
  */

  // Instead we use RooMinuit directly, and give it a RooChi2Var that gives the correct error
  RooChi2Var chi2("chi2","chi2", (RooAbsPdf&) totalPdfNC, *dataHist, kTRUE, 0, 0, 4, kFALSE, kTRUE, kTRUE, RooDataHist::SumW2) ; 
  // Add a chi^2 penalty term for the signal fraction
  RooFormulaVar chi2p("chi2p","penalized chi2","chi2 + ( ((PromptFracNC-alpha)/ealpha) * ((PromptFracNC-alpha)/ealpha) )", 
                      RooArgList(chi2,PromptFracNC,alpha,ealpha));
  // Minimize
  RooMinuit *m = 0;
  if (bB != 0)
  {  
    m = new RooMinuit(chi2p) ;
  }
  else
  {
    m = new RooMinuit(chi2) ;
  }
  m->setStrategy(2); // use the intensive strategy 
  m->setVerbose(kV);
  m->setPrintLevel(iPL);
  m->setPrintEvalErrors(iPE);
  if (kW == kFALSE)
  { 
    m->setNoWarn();
  }
  m->fit("smhr") ;
  m->minos() ;
  RooFitResult *fr = m->save();
  RooArgList fp = fr->floatParsFinal();

  double nBinsMerged = dataHist->numEntries(); // since you can't divide an int by an int in c++
  double normalizeFactor = (nBinsMerged / nBins);
  cout << "PDF normalization correction factor: " << normalizeFactor << endl;

  std::cout << "Plot NC HIST" << std::endl;
  // Plot NC
  std::ostringstream RPn2_ss;
  RPn2_ss << "LogIPCHI2NChist" << label;
  // Create RooPlot object with M on the axis.
  RooPlot* LogIPCHI2frameNChist = (*LogIPCHI2).frame(Bins(nBins),Range(ipmin, ipmax), 
                                                    Name(RPn2_ss.str().c_str()), 
                                                    Title("LogIPCHI2 of D candidates") ); 
  LogIPCHI2frameNChist->SetXTitle("Log_{10} IP#chi^{2}");
  // display fit parameters
  totalPdfNC.paramOn( LogIPCHI2frameNChist, 
                      Parameters((RooArgSet&) *(totalPdfNC.getParameters(*dataHist)->selectByAttrib("Constant",kFALSE))),
                      ShowConstants(kFALSE), Format("NELU", AutoPrecision(2)), Layout(0.65, 0.95, 0.95) )->getAttText()->SetTextSize(0.030); 
  //                      ShowConstants(kFALSE), Format("NELU", AutoPrecision(2)), Layout(0.65, 0.95, 0.95) )->getAttText()->SetTextSize(0.030); 
  //  ReducedDataSetNChist->plotOn(LogIPCHI2frameNChist, MarkerSize(0.9), DataError(RooAbsData::SumW2) ); // plot histogram
  dataHist->plotOn(LogIPCHI2frameNChist, MarkerSize(0.9) , DataError(RooAbsData::SumW2) , DrawOption("E2") ); // plot histogram

  
  // Plot function sums
  // Simple way:
  totalPdfNC.plotOn( LogIPCHI2frameNChist, Components(bkgPdfNC) , 
                     LineColor(kGreen), Normalization( normalizeFactor , 
                     RooAbsReal::Relative) );
  totalPdfNC.plotOn( LogIPCHI2frameNChist, Components(*promptPdfNC) , LineColor(kBlue), Normalization( normalizeFactor , 
                     RooAbsReal::Relative) );
  totalPdfNC.plotOn( LogIPCHI2frameNChist, Components(*secondaryPdfNC) , LineColor(kCyan), Normalization( normalizeFactor , 
                     RooAbsReal::Relative) );
  //        totalPdfNC.plotOn( LogIPCHI2frameNChist, Components(convPromptPdfNC) , LineColor(kBlue) );
  //        totalPdfNC.plotOn( LogIPCHI2frameNChist, Components(convSecondaryPdfNC) , LineColor(kCyan) );
  
  // Plot total PDF
  // plot fit pdf
  totalPdfNC.plotOn( LogIPCHI2frameNChist, LineColor(kRed), Normalization( normalizeFactor , RooAbsReal::Relative) ); 
  // The plot is not on the screen yet -- we have only created a RooPlot object.
    
  // Put the plot on the screen.
  TCanvas* LogIPCHI2CanvasNChist = new TCanvas("LogIPCHI2CanvasNChist", "Fit of LogIPCHI2"); // make new canvas
  LogIPCHI2frameNChist->Draw(); // Put our plot on the canvas.
  
  Double_t chi2_val = chi2.getVal(); 
  Double_t chi2p_val = chi2p.getVal(); 
  Double_t chi2_perbin = chi2_val/(nBinsMerged);
  Double_t chi2p_perbin = chi2p_val/(nBinsMerged);
  Int_t NFREEPARAMS = totalPdfNC.getParameters(dataHist)->selectByAttrib("Constant",kFALSE)->getSize();
  Int_t NDOF = nBinsMerged - NFREEPARAMS;
  Double_t PVAL = TMath::Prob(chi2_val,NDOF);
  Double_t PVALp = TMath::Prob(chi2p_val,NDOF);
  std::cout << "Final: For the fit, the number of free parameters is " << NFREEPARAMS << std::endl;
  std::cout << "Final: For the fit, the number of degrees of freedom is " << NDOF << std::endl;
  if (bB != 0)
  {  
  std::cout << "Final: chi2p from RooChi2Var = " << chi2p_val << std::endl;
  std::cout << "Final: chi2p per bin from RooChi2Var = " << chi2p_perbin << std::endl;
  std::cout << "Final: chi2p/d.o.f = " << chi2p_val / NDOF << std::endl;
  std::cout << "Final: For the fit, the P-value (Probability) of chi2p is " << PVALp << std::endl;
  }
  std::cout << std::endl;
  std::cout << "Final: chi2 from RooChi2Var = " << chi2_val << std::endl;
  std::cout << "Final: chi2 per bin from RooChi2Var = " << chi2_perbin << std::endl;
  std::cout << "Final: chi2/d.o.f = " << chi2_val / NDOF << std::endl;
  std::cout << "Final: For the fit, the P-value (Probability) of chi2 is " << PVAL << std::endl;
  std::cout << std::endl;

  int binX = 1 + ((allCount - 1) % ptNBins);
  int binY = yNBins - floor((allCount - 1) / ptNBins);

  RooRealVar* par1 = (RooRealVar*) fp.find("PromptFracNC");
  RooRealVar par1c = *par1; 
  Double_t proF = par1c.getVal();
  Double_t proFE = par1c.getError();

  RooRealVar* par2 = (RooRealVar*) fp.find("sig_yieldNC") ;
  Double_t totY = par2->getVal();
  Double_t totYE = par2->getError();

  Double_t secF = 1 - proF;  
  Double_t proY = proF * totY;
  Double_t proYE = sqrt(proFE*totY*proFE*totY  +  totYE*proF*totYE*proF);

  if (bigCount != 0)
  {
    SecFracsBig->SetBinContent(bigCount, secF);
    SecFracsBig->SetBinError(bigCount, proFE);
  }

  if ( (allCount > 0) && ( allCount <= (ptNBins*yNBins) ) )
  {

    SecFracs->SetBinContent(binX, binY, secF);
    SecFracs->SetBinError(binX, binY, proFE);
    ProYields->SetBinContent(binX, binY, proY);
    ProYields->SetBinError(binX, binY, proYE);

//    Double_t bigProF = 1 - SecFracsBig->GetBinContent(bB);
//    Double_t bigProFE = SecFracsBig->GetBinError(bB);
//    SecFracs->SetBinContent(binX, binY, 1 - bigProF);
//    SecFracs->SetBinError(binX, binY, bigProFE);
//    ProYields->SetBinContent(binX, binY, bigProF * totY);
//    ProYields->SetBinError(binX, binY, sqrt(bigProFE*totY*bigProFE*totY  +  totYE*bigProF*totYE*bigProF) );

  }

  TString Chisqe = "#scale[0.5]{Fit P-value (pdf only) = " + to_string( PVAL ) + "}";
  TString Chisqep = "" ;
  if (bB != 0)
  {  
  Chisqep = "#scale[0.5]{Fit P-value  = " + to_string( PVALp ) + "}";
  }
  TString Bc = "";
  if (strcmp(label,"") != 0)
  {
  Bc = "#scale[0.375]{Bin Name: " + to_string( label ) + "}";
  }
  char buffer [50];
  char buffer2 [50];
  sprintf(buffer, "%3.1f +/- %3.1f", ( proY ), ( proYE ));
  sprintf(buffer2, "(%3.1f +/- %3.1f)", (secF * 100), ( proFE * 100 ));
  TString SecFLine = "#scale[0.5]{n_{prompt} = " + to_string( buffer ) + "}" ;
  TString ProYLine = "#scale[0.5]{#alpha_{sec} = " + to_string( buffer2 ) + "%}" ;
  
  TLatex *t = new TLatex( .04, .01, Chisqe );
  t->SetNDC(kTRUE);
  t->Draw();
  TLatex *t2 = new TLatex( .04, .05, Chisqep );
  t2->SetNDC(kTRUE);
  t2->Draw();
  TLatex *t3 = new TLatex( .25, .97, Bc);
  t3->SetNDC(kTRUE);
  t3->Draw();
  TLatex *t4 = new TLatex( .17, .80, SecFLine);
  t4->SetNDC(kTRUE);
  t4->Draw();
  TLatex *t5 = new TLatex( .17, .76, ProYLine);
  t5->SetNDC(kTRUE);
  t5->Draw();

  // Save output plot
  std::ostringstream outFile_ss;
  outFile_ss << outDir << "/" << "LogIPCHI2_Histfit_Bukin_standard" << label << ".eps";
  LogIPCHI2CanvasNChist->Print(outFile_ss.str().c_str());

  std::cout << "IP Plot Count = " << allCount << std::endl;
  AllPlotsI->cd(allCount);
  LogIPCHI2frameNChist->Draw(); // Put our plot on the canvas.
  TLatex *t_ip = new TLatex( .04, .01, Chisqe );
  t_ip->SetNDC(kTRUE);
  t_ip->Draw();
  TLatex *t2_ip = new TLatex( .04, .05, Chisqep );
  t2_ip->SetNDC(kTRUE);
  t2_ip->Draw();
  TLatex *t3_ip = new TLatex( .25, .97, Bc);
  t3_ip->SetNDC(kTRUE);
  t3_ip->Draw();
  TLatex *t4_ip = new TLatex( .17, .80, SecFLine);
  t4_ip->SetNDC(kTRUE);
  t4_ip->Draw();
  TLatex *t5_ip = new TLatex( .17, .76, ProYLine);
  t5_ip->SetNDC(kTRUE);
  t5_ip->Draw();
  //  AllPlotsI->Print("./test/all_help_IP.eps") ; 

  std::cout << "before delete NChist Canvas" << std::endl;
//  delete t3_ip;
//  delete t2_ip;
//  delete t_ip;
  delete t3;
  delete t2;
  delete t;
  delete LogIPCHI2CanvasNChist;
  delete m;
  std::cout << "after delete NChist Canvas" << std::endl;

// Let's just not do the unbinned subtraction fit anymore (this whole section commented out)
/*
////////// DATA FIT

  std::cout << "Fit NC DATA" << std::endl;
  // Fit NC
  totalPdfNC.fitTo(*dataSet, Minos(kTRUE), SumW2Error(kTRUE), NumCPU(6),
                   Verbose(kV), Warnings(kW), PrintLevel(iPL), PrintEvalErrors(iPE) );
  
  std::cout << "Plot NC DATA" << std::endl;
  // Plot NC
  std::ostringstream RPn_ss;
  RPn_ss << "LogIPCHI2NC" << label;
  // Create RooPlot object with M on the axis.
  RooPlot* LogIPCHI2frameNC= (*LogIPCHI2).frame(Bins(nBins), 
                                                   Name(RPn_ss.str().c_str()), 
                                                   Title("LogIPCHI2 of D candidates") ); 
  LogIPCHI2frameNC->SetXTitle("Log_{10} IP#chi^{2}");
  // display fit parameters
  totalPdfNC.paramOn( LogIPCHI2frameNC, 
                      Parameters((RooArgSet&) *(totalPdfNC.getParameters(*dataSet)->selectByAttrib("Constant",kFALSE))),
                      ShowConstants(kFALSE), Format("NELU", AutoPrecision(2)), Layout(0.65, 0.95, 0.95) )->getAttText()->SetTextSize(0.030); 
  //  ReducedDataSetNC->plotOn(LogIPCHI2frameNC, MarkerSize(0.9), DataError(RooAbsData::SumW2) ); // plot histogram
  dataSet->plotOn(LogIPCHI2frameNC, MarkerSize(0.9), DataError(RooAbsData::SumW2) ); // plot histogram
  
  // Plot function sums
  // Simple way:
  totalPdfNC.plotOn( LogIPCHI2frameNC, Components(bkgPdfNC) , LineColor(kGreen) );
  totalPdfNC.plotOn( LogIPCHI2frameNC, Components(*promptPdfNC) , LineColor(kBlue) );
  totalPdfNC.plotOn( LogIPCHI2frameNC, Components(*secondaryPdfNC) , LineColor(kCyan) );
  //        totalPdfNC.plotOn( LogIPCHI2frameNC, Components(convPromptPdfNC) , LineColor(kBlue) );
  //        totalPdfNC.plotOn( LogIPCHI2frameNC, Components(convSecondaryPdfNC) , LineColor(kCyan) );
  
  // Plot total PDF
  totalPdfNC.plotOn( LogIPCHI2frameNC, LineColor(kRed)); // plot fit pdf
  // The plot is not on the screen yet -- we have only created a RooPlot object.
  
	// Put the plot on the screen.
	TCanvas* LogIPCHI2CanvasNC = new TCanvas("LogIPCHI2CanvasNC", "Fit of LogIPCHI2"); // make new canvas
	LogIPCHI2frameNC->Draw(); // Put our plot on the canvas.
  
	// Save output plot
  std::ostringstream outFiled_ss;
  outFiled_ss << outDir << "/" << "LogIPCHI2_Datafit_Bukin_standard" << label << ".eps";
  LogIPCHI2CanvasNC->Print(outFiled_ss.str().c_str());

  //  std::cout << "IPd Plot Count = " << allCount << std::endl;
  AllPlotsId->cd(allCount);
  LogIPCHI2frameNC->Draw(); // Put our plot on the canvas.
  //  AllPlotsId->Print("./test/all_help_IPd.eps") ;

  delete LogIPCHI2CanvasNC;
*/

//////////

  delete secondary_w_filein;
  delete prompt_w_filein;
  delete inSec ;
  delete inPro ;
  delete dataSet ;
  delete data_w_filein;
  delete inFileName;
  delete LogIPCHI2 ; 
  
  return;
}

void LAMBSFitter::Print() const
{
  cout << "fX = " << fX << endl; // justs prints the ID, which is useless
}
