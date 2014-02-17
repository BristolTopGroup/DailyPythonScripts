#ifndef TOPSVDUNFOLD_H
#define TOPSVDUNFOLD_H

#include "BaseSVDUnfold.h"

class TopSVDUnfold : public BaseSVDUnfold {

public:

    // Special Constructure that creates "empty" objects
    // This is needed create arrays of TopSVDUnfold on the heap
    TopSVDUnfold(); // Needed for the construction of arrays 


    // Constructors and Destructor
    TopSVDUnfold( const TH1D* bdat, const TH1D* bini, const TH1D* xini, const TH2D* Adet );
    TopSVDUnfold( const TH1D* bdat, TH2D* Bcov, const TH1D* bini, const TH1D* xini, const TH2D* Adet );
    TopSVDUnfold( const TopSVDUnfold& other ); 
    virtual ~TopSVDUnfold(); 
   
   
   
    // Steer Regularization
    void SetTau(double tau) { fTau = tau; }
    double GetTau() { return fTau;}
    void SetKReg(int kreg) { fKReg = kreg;}
   
    // Get Curvature of last unfolding run
    double GetCurv() { return fCurv; }
   
    
    // Get Histo of Weights of LAST Unfolding run
    TH1D* GetWeights(); 
   
   
    // UNFOLDING
    // Here, we overwrite the Unfold-Function from BaseSVDUnfold!
    // A litte HowTo:
    // If you want to steer the unfolding via k
    // --- just use the function as you are used to.
    // If you want to steer the unfolding via tau
    // --- Set tau via the "SetTau" setter function
    // --- Use UnfoldTau with k = -1.
    virtual TH1D* Unfold(Int_t kreg); 
    
    // Joern
    // Determine for given input error matrix covariance matrix of unfolded 
   // spectrum from toy simulation
   // "cov"    - covariance matrix on the measured spectrum, to be propagated
   // "ntoys"  - number of pseudo experiments used for the propagation
   // "seed"   - seed for pseudo experiments
    TH2D* GetUnfoldCovMatrixNorm( const TH2D* cov, Int_t ntoys, Int_t seed =1, Int_t normType=2, Int_t verbose=0 );
    static TH1D* IntNormalizeSVDDistribution(TH1D* inputHist);

protected:
    double fTau;
    double fCurv;
    bool fReturnWeights;
    TH1D* fWeights;

    ClassDef( TopSVDUnfold, 0 );
   
};

#endif

