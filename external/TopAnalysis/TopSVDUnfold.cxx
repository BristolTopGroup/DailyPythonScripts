#include "TopSVDUnfold.h"
#include "TDecompSVD.h"
#include <TH1.h>
#include <TH2.h>
#include <TMath.h>
#include <TRandom3.h>
#include <iostream>

using namespace std;

ClassImp (TopSVDUnfold);
// Special Constructure that creates "empty" objects
// This is needed create arrays of TopSVDUnfold on the heap 
TopSVDUnfold::TopSVDUnfold() :
		BaseSVDUnfold() {
	fTau = 0.;
	fCurv = -1.;
	fWeights = NULL;
//  : TObject     (),
//    fNdim       (0),
//    fDdim       (2),
//    fNormalize  (kFALSE),
//    fKReg       (-1),
//    fDHist      (NULL),
//    fSVHist     (NULL),
//    fXtau       (NULL),
//    fXinv       (NULL),
//    fBdat       (NULL),
//    fBini       (NULL),
//    fXini       (NULL),
//    fAdet       (NULL),
//    fToyhisto   (NULL),
//    fToymat     (NULL),
//    fToyMode    (kFALSE),
//    fMatToyMode (kFALSE)
}

TopSVDUnfold::TopSVDUnfold(const TH1D* bdat, const TH1D* bini, const TH1D* xini, const TH2D* Adet) :
		BaseSVDUnfold(bdat, bini, xini, Adet) {
	fTau = 0.;
	fCurv = -1.;
	fWeights = NULL;
}

TopSVDUnfold::TopSVDUnfold(const TH1D *bdat, TH2D* Bcov, const TH1D *bini, const TH1D *xini, const TH2D *Adet) :
		BaseSVDUnfold(bdat, Bcov, bini, xini, Adet) {
	fTau = 0.;
	fCurv = -1.;
	fWeights = NULL;
}

TopSVDUnfold::TopSVDUnfold(const TopSVDUnfold& other) :
		BaseSVDUnfold(other) {
	fTau = other.fTau;
	fCurv = other.fCurv;
	fWeights = other.fWeights;
}

TopSVDUnfold::~TopSVDUnfold() {
	if (fWeights != NULL)
		delete fWeights;
}

// DAVID
// This is your stuff here
TH1D* TopSVDUnfold::GetWeights() {
	if (fWeights == NULL)
		return NULL;

	for (int i = 0; i < fWeights->GetNbinsX() + 2; i++) {
		fWeights->SetBinError(i, 0.);
	}
	return fWeights;
}

// Unfold via tau
TH1D* TopSVDUnfold::Unfold(Int_t kreg) {
	fKReg = kreg;

	// Make the histos
	if (!fToyMode && !fMatToyMode)
		InitHistos();

	// Create vectors and matrices
	TVectorD vb(fNdim), vbini(fNdim), vxini(fNdim), vberr(fNdim);
	TMatrixD mB(fNdim, fNdim), mA(fNdim, fNdim), mCurv(fNdim, fNdim), mC(fNdim, fNdim);

	Double_t eps = 1e-12;
	Double_t sreg;

	// Copy histogams entries into vector
	if (fToyMode) {
		H2V(fToyhisto, vb);
		H2Verr(fToyhisto, vberr);
	} else {
		H2V(fBdat, vb);
		H2Verr(fBdat, vberr);
	}

	H2M(fBcov, mB);
	H2V(fBini, vbini);
	H2V(fXini, vxini);
	if (fMatToyMode)
		H2M(fToymat, mA);
	else
		H2M(fAdet, mA);

	// Fill and invert the second derivative matrix
	FillCurvatureMatrix(mCurv, mC);

	// Inversion of mC by help of SVD
	TDecompSVD CSVD(mC);
	TMatrixD CUort = CSVD.GetU();
	TMatrixD CVort = CSVD.GetV();
	TVectorD CSV = CSVD.GetSig();

	TMatrixD CSVM(fNdim, fNdim);
	for (Int_t i = 0; i < fNdim; i++)
		CSVM(i, i) = 1 / CSV(i);

	CUort.Transpose(CUort);
	TMatrixD mCinv = (CVort * CSVM) * CUort;

//    // Rescale matrix and vectors by error of data vector. Replaced by using full covmat now
//    vbini = VecDiv   ( vbini, vberr );
//    vb    = VecDiv   ( vb,    vberr, 1 );
//    mA    = MatDivVec( mA,    vberr, 1 );
//    vberr = VecDiv   ( vberr, vberr, 1 );

//Rescale using the data covariance matrix
	TDecompSVD BSVD(mB);
	TMatrixD QT = BSVD.GetU();
	QT.Transpose(QT);
	TVectorD B2SV = BSVD.GetSig();
	TVectorD BSV(B2SV);

	for (int i = 0; i < fNdim; i++) {
		BSV(i) = TMath::Sqrt(B2SV(i));
	}
	TMatrixD mAtmp(fNdim, fNdim);
	TVectorD vbtmp(fNdim);
	mAtmp *= 0;
	vbtmp *= 0;
	for (int i = 0; i < fNdim; i++) {
		for (int j = 0; j < fNdim; j++) {
			if (BSV(i)) {
				vbtmp(i) += QT(i, j) * vb(j) / BSV(i);
			}
			for (int m = 0; m < fNdim; m++) {
				if (BSV(i)) {
					mAtmp(i, j) += QT(i, m) * mA(m, j) / BSV(i);
				}
			}
		}
	}
	mA = mAtmp;
	vb = vbtmp;

	// Singular value decomposition and matrix operations
	TDecompSVD ASVD(mA * mCinv);
	TMatrixD Uort = ASVD.GetU();
	TMatrixD Vort = ASVD.GetV();
	TVectorD ASV = ASVD.GetSig();

	if (!fToyMode && !fMatToyMode) {
		V2H(ASV, *fSVHist);
	}

	TMatrixD Vreg = mCinv * Vort;

	Uort.Transpose(Uort);
	TVectorD vd = Uort * vb;

	if (!fToyMode && !fMatToyMode) {
		V2H(vd, *fDHist);
	}

	Int_t k = GetKReg() - 1;

	TVectorD vx(fNdim); // Return variable

	// Damping factors
	TVectorD vdz(fNdim);
	TMatrixD Z(fNdim, fNdim);
	for (Int_t i = 0; i < fNdim; i++) {
		if (ASV(i) < ASV(0) * eps)
			sreg = ASV(0) * eps;
		else
			sreg = ASV(i);

		// DAVID
		// Here is the point where you made changes!
		if (kreg == -1) { // tau steered damping
			vdz(i) = sreg / (sreg * sreg + fTau * fTau);
		} else { // k steered damping
			vdz(i) = sreg / (sreg * sreg + ASV(k) * ASV(k));
		}

		Z(i, i) = vdz(i) * vdz(i);
	}

	TVectorD vz = CompProd(vd, vdz);

	TMatrixD VortT(Vort);
	VortT.Transpose(VortT);
	TMatrixD W = mCinv * Vort * Z * VortT * mCinv;

	TMatrixD Xtau(fNdim, fNdim);
	TMatrixD Xinv(fNdim, fNdim);
	Xtau *= 0;
	Xinv *= 0;
	for (Int_t i = 0; i < fNdim; i++) {
		for (Int_t j = 0; j < fNdim; j++) {
			Xtau(i, j) = vxini(i) * vxini(j) * W(i, j);

			double a = 0;
			for (Int_t m = 0; m < fNdim; m++) {
				a += mA(m, i) * mA(m, j);
			}
			if (vxini(i) * vxini(j))
				Xinv(i, j) = a / vxini(i) / vxini(j);
		}
	}

	// Compute the weights
	TVectorD vw = Vreg * vz;

	// DAVID
	vx = CompProd(vw, vxini);

	if (fNormalize) { // Scale result to unit area
		Double_t scale = vx.Sum();
		if (scale > 0) {
			vx *= 1.0 / scale;
			Xtau *= 1. / scale / scale;
			Xinv *= scale * scale;
		}
	}

	if (!fToyMode && !fMatToyMode) {
		M2H(Xtau, *fXtau);
		M2H(Xinv, *fXinv);
	}

	// DAVID
	// Speichere die Kruemmung ab!
	fCurv = GetCurvature(vw, mCurv);

	// Get Curvature and also chi2 in case of MC unfolding
	if (!fToyMode && !fMatToyMode) {
		Info("Unfold", "Unfolding param: %i", k + 1);
		Info("Unfold", "Curvature of weight distribution: %f", fCurv);
	}

	TH1D* h = (TH1D*) fBdat->Clone("unfoldingresult");
	for (int i = 1; i <= fNdim; i++) {
		h->SetBinContent(i, 0.);
		h->SetBinError(i, 0.);
	}
	V2H(vx, *h);

	// DAVID
	// Save the weights
	// but only if this is not a "Toy"-Run
	if (!fToyMode && !fMatToyMode) {
		if (fWeights != NULL) {
			delete fWeights;
			fWeights = NULL;
		}
		fWeights = (TH1D*) fBdat->Clone("Weights");
		V2H(vw, *fWeights);
	}

	return h;
}

//_______________________________________________________________________
TH2D* TopSVDUnfold::GetUnfoldCovMatrixNorm(const TH2D* cov, Int_t ntoys, Int_t seed, Int_t normType, Int_t verbose) {

	// Added by Joern: adapted from TSVDUnfold::GetUnfoldCovMatrix
	//                 to include the normalisation in the procedure
	//
	// Determine for given input error matrix covariance matrix of unfolded
	// spectrum from toy simulation given the passed covariance matrix on measured spectrum
	// "cov"    - covariance matrix on the measured spectrum, to be propagated
	// "ntoys"  - number of pseudo experiments used for the propagation
	// "seed"   - seed for pseudo experiments
	// "normType" - set type of normalisation (1=extrinsic, 2=intrinsic)
	// Note that this covariance matrix will contain effects of forced normalisation if spectrum is normalised to unit area.
	if (verbose > 2) {
		cout
				<< "TopSVDUnfold::GetUnfoldCovMatrixNorm -> calculates the covariance matrix for the unfolded results after normalisation"
				<< endl;
		if (normType == 1)
			cout << "Extrinsic Normalisation (at the moment NOT WORKING!!!) normType = " << normType << endl;
		else if (normType == 2)
			cout << "Intrinsic Normalisation! normType = " << normType << endl;
	}
	fToyMode = true;
	TH1D* unfres = 0;
	TH1D* unfresNorm = 0;
	TH2D* unfcov = (TH2D*) fAdet->Clone("unfcovmat");
	unfcov->SetTitle("Toy covariance matrix");
	for (int i = 1; i <= fNdim; i++)
		for (int j = 1; j <= fNdim; j++)
			unfcov->SetBinContent(i, j, 0.);
	TH2D* unfcovNorm = (TH2D*) unfcov->Clone("unfcovmatnorm");
	unfcovNorm->SetTitle("Toy covariance matrix (normalised)");

	// Code for generation of toys (taken from RooResult and modified)
	// Calculate the elements of the upper-triangular matrix L that
	// gives Lt*L = C, where Lt is the transpose of L (the "square-root method")
	TMatrixD L(fNdim, fNdim);
	L *= 0;

	for (Int_t iPar = 0; iPar < fNdim; iPar++) {

		// Calculate the diagonal term first
		L(iPar, iPar) = cov->GetBinContent(iPar + 1, iPar + 1);
		for (Int_t k = 0; k < iPar; k++)
			L(iPar, iPar) -= TMath::Power(L(k, iPar), 2);
		if (L(iPar, iPar) > 0.0)
			L(iPar, iPar) = TMath::Sqrt(L(iPar, iPar));
		else
			L(iPar, iPar) = 0.0;

		// ...then the off-diagonal terms
		for (Int_t jPar = iPar + 1; jPar < fNdim; jPar++) {
			L(iPar, jPar) = cov->GetBinContent(iPar + 1, jPar + 1);
			for (Int_t k = 0; k < iPar; k++)
				L(iPar, jPar) -= L(k, iPar) * L(k, jPar);
			if (L(iPar, iPar) != 0.)
				L(iPar, jPar) /= L(iPar, iPar);
			else
				L(iPar, jPar) = 0;
		}
	}

	// Remember it
	TMatrixD *Lt = new TMatrixD(TMatrixD::kTransposed, L);
	TRandom3 random(seed);

	fToyhisto = (TH1D*) fBdat->Clone("toyhisto");
	TH1D *toymean = (TH1D*) fBdat->Clone("toymean");
	for (Int_t j = 1; j <= fNdim; j++)
		toymean->SetBinContent(j, 0.);
	TH1D *toymeanNorm = (TH1D*) toymean->Clone("toymeanNorm");

	// Get the mean of the toys first
	for (int i = 1; i <= ntoys; i++) {

		// create a vector of unit Gaussian variables
		TVectorD g(fNdim);
		for (Int_t k = 0; k < fNdim; k++)
			g(k) = random.Gaus(0., 1.);

		// Multiply this vector by Lt to introduce the appropriate correlations
		g *= (*Lt);

		// Add the mean value offsets and store the results
		for (int j = 1; j <= fNdim; j++) {
			fToyhisto->SetBinContent(j, fBdat->GetBinContent(j) + g(j - 1));
			fToyhisto->SetBinError(j, fBdat->GetBinError(j));
		}

		unfres = Unfold(GetKReg());
		// change by Joern
		if (normType == 3)
			unfresNorm = IntNormalizeSVDDistribution(unfres);
		// for other normalisation types return empty histo
		else {
			delete unfres;
			delete unfresNorm;
			return unfcovNorm;
		}

		for (Int_t j = 1; j <= fNdim; j++) {
			toymean->SetBinContent(j, toymean->GetBinContent(j) + unfres->GetBinContent(j) / ntoys);
			toymeanNorm->SetBinContent(j, toymeanNorm->GetBinContent(j) + unfresNorm->GetBinContent(j) / ntoys);
			if (verbose > 2 && i == ntoys)
				cout << "bin " << j << "; toymean = " << toymean->GetBinContent(j) << "; toymeanNorm = "
						<< toymeanNorm->GetBinContent(j) << endl;
		}
		delete unfres;
		delete unfresNorm;
		unfres = 0;
		unfresNorm = 0;
	}

	// Reset the random seed
	random.SetSeed(seed);
	//Now the toys for the covariance matrix
	for (int i = 1; i <= ntoys; i++) {
		// Create a vector of unit Gaussian variables
		TVectorD g(fNdim);
		for (Int_t k = 0; k < fNdim; k++)
			g(k) = random.Gaus(0., 1.);

		// Multiply this vector by Lt to introduce the appropriate correlations
		g *= (*Lt);

		// Add the mean value offsets and store the results
		for (int j = 1; j <= fNdim; j++) {
			fToyhisto->SetBinContent(j, fBdat->GetBinContent(j) + g(j - 1));
			fToyhisto->SetBinError(j, fBdat->GetBinError(j));
		}
		unfres = Unfold(GetKReg());
		// change by Joern
		if (normType == 3)
			unfresNorm = IntNormalizeSVDDistribution(unfres);

		for (Int_t j = 1; j <= fNdim; j++) {
			for (Int_t k = 1; k <= fNdim; k++) {
				unfcov->SetBinContent(j, k,
						unfcov->GetBinContent(j, k)
								+ ((unfres->GetBinContent(j) - toymean->GetBinContent(j))
										* (unfres->GetBinContent(k) - toymean->GetBinContent(k)) / (ntoys - 1)));
				unfcovNorm->SetBinContent(j, k,
						unfcovNorm->GetBinContent(j, k)
								+ ((unfresNorm->GetBinContent(j) - toymeanNorm->GetBinContent(j))
										* (unfresNorm->GetBinContent(k) - toymeanNorm->GetBinContent(k)) / (ntoys - 1)));

				if (verbose > 2 && i == ntoys) {
					//cout << "(j,k) = (" << j <<", " << k << "); unfcov = " << unfcov->GetBinContent(j,k) << "; unfcovNorm = " << unfcovNorm->GetBinContent(j,k) <<endl;
					double unfcovCorrDenom = TMath::Sqrt(unfcov->GetBinContent(j, j) * unfcov->GetBinContent(k, k));
					if (unfcovCorrDenom == 0)
						unfcovCorrDenom = 1e10;
					double unfcovNormCorrDenom = TMath::Sqrt(
							unfcovNorm->GetBinContent(j, j) * unfcovNorm->GetBinContent(k, k));
					if (unfcovNormCorrDenom == 0)
						unfcovNormCorrDenom = 1e10;
					cout << "(j,k) = (" << j << ", " << k << "); unfcorr = "
							<< unfcov->GetBinContent(j, k) / unfcovCorrDenom << "; unfcorrNorm = "
							<< unfcovNorm->GetBinContent(j, k) / unfcovNormCorrDenom << endl;
					double unfcovUncDenom = toymean->GetBinContent(k);
					if (unfcovUncDenom == 0)
						unfcovUncDenom = 1e10;
					double unfcovNormUncDenom = toymeanNorm->GetBinContent(k);
					if (unfcovNormUncDenom == 0)
						unfcovNormUncDenom = 1e10;
					if (j == k)
						cout << "UNCERTAINTY [%], bin " << j << "; non-norm: "
								<< TMath::Sqrt(unfcov->GetBinContent(j, j)) / unfcovUncDenom << "; norm: "
								<< TMath::Sqrt(unfcovNorm->GetBinContent(j, j)) / unfcovNormUncDenom << endl;
				}
			}
		}

		delete unfres;
		unfres = 0;
		delete unfresNorm;
		unfresNorm = 0;
	}
	delete Lt;
	delete toymean;
	delete toymeanNorm;
	delete unfcov;
	fToyMode = kFALSE;

	return unfcovNorm;
}

//_______________________________________________________________________
TH1D* TopSVDUnfold::IntNormalizeSVDDistribution(TH1D* inputHist) {
	// Added by Joern: adapted from TopSVDFunctions::SVD_IntNormalizeSVDDistribution
	//                 to include the normalisation in the procedure
	// ATTENTION!!!! Make sure this does the same as TopSVDFunctions::SVD_IntNormalizeSVDDistribution!!!
	// Existence of Objects
	if (inputHist == NULL)
		return NULL;

	// Create new Histograms
	TH1D* hist = (TH1D*) inputHist->Clone(TString(inputHist->GetName()) + "Norm");

	// Number of Bins
	int nbins = inputHist->GetNbinsX();

	// Get Integral
	bool doOF = true;
	double integral = -1;
	if (doOF)
		integral = inputHist->Integral(0, nbins + 1);
	else
		integral = inputHist->Integral(1, nbins);

	// Loop over bins, including OF
	for (int i = 1; i <= nbins; i++) {

		double value_old = inputHist->GetBinContent(i);
		//double error_old = inputHist->GetBinError(i);

		double value_new = value_old;
		if (integral > 0.)
			value_new = value_new / integral;
		//double error_new = error_old;
		//if ( integral > 0. ) error_new = error_new / integral ;

		hist->SetBinContent(i, value_new);
		//hist->SetBinError(i, error_new);

		//cout << "TopSVDUnfold::IntNormalizeSVDDistribution; bin " << i << "; value = " << value_new << endl;
	}

	// Return
	return hist;
}
