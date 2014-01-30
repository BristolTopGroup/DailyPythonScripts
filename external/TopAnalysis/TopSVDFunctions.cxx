#include "TopSVDFunctions.h"
#include "TopSVDUnfold.h"
#include <math.h>
#include "TMatrix.h"
#include <iostream>
#include <cstdlib>

// Namespaces
using namespace std;

std::pair<double, double> TopSVDFunctions::get_optimal_tau_values(const TH1D* b_data, const TH1D* b_ini,
		const TH1D* x_ini, const TH2D* A_det, double tau_min, double tau_max, unsigned int number_of_points) {
	pair<double, double> result(0., 0.);
	TopSVDUnfold* svd_unfold = new TopSVDUnfold(b_data, b_ini, x_ini, A_det);

	vector<double> tau_values = calculate_tau_scan_points(tau_min, tau_max, number_of_points);
	vector<double> curvatures, global_correlation_values;
	curvatures.resize(number_of_points, 0.);
	global_correlation_values.resize(number_of_points, 0.);

	cout
			<< "*******************************************************************************************************************"
			<< endl;
	cout << "Perform Tau Scan from " << tau_min << " to " << tau_max << " for plotting purpose" << endl;
	for (unsigned int i = 0; i < number_of_points; ++i) {
		double tau = tau_values.at(i);
		svd_unfold->SetTau(tau);

		curvatures.at(i) = svd_unfold->GetCurv();

		global_correlation_values.at(i) = get_global_correlation(b_data);

	}

	cout
			<< "*******************************************************************************************************************"
			<< endl;
	cout << "Perform Tau Scan from " << tau_min << " to " << tau_max << " with Golden Section Search" << endl;
	double golden_section = (3. - sqrt(5.)) / 2.;
	double global_correlaton_tau_min = 1000.;
	double global_correlaton_tau_max = 1000.;

	double new_tau_min = pow(10., log10(tau_min) + golden_section * (log10(tau_max) - log10(tau_min)));
	double new_tau_max = pow(10., log10(tau_max) - golden_section * (log10(tau_max) - log10(tau_min)));

	double optimal_tau(-1);
	return result;
}

vector<double> TopSVDFunctions::calculate_tau_scan_points(double tau_min, double tau_max,
		unsigned int number_of_points) {
	// Use 3 scan points minimum
	if (number_of_points < 3)
		number_of_points = 3;

	// Setup Vector
	vector<double> result;
	result.resize(number_of_points, 0.);

	// Find the scan points
	// Use equidistant steps on a logarithmic scale
	double step = (log10(tau_max) - log10(tau_min)) / (number_of_points - 1);
	for (unsigned int i = 0; i < number_of_points; ++i) {
		result.at(i) = pow(10., (log10(tau_min) + i * step));
	}

	return result;
}

double TopSVDFunctions::get_global_correlation(const TH1D* data_histogram) {
	TH1D * global_correlation_hist = get_global_correlation_hist(data_histogram);

	double sum = 0.;
	double average = 0.;
	int bincounter = 0;
	unsigned int n_bins = global_correlation_hist->GetNbinsX();

	for (unsigned int i = 1; i <= n_bins; i++) {
		if (i == 1)
			continue;
		if (i == n_bins)
			continue;
		double globcorr = global_correlation_hist->GetBinContent(i);
		sum += globcorr;
		bincounter++;
	}

	// Averaging
	if (bincounter > 0) {
		average = sum / ((double) bincounter);
	}

	delete global_correlation_hist;

	return average;
}

TH1D* TopSVDFunctions::get_global_correlation_hist(const TH1D* data_histogram) {
	TH2D* covariance_hist = (TH2D*) get_data_covariance_matrix(data_histogram)->Clone();

	unsigned int n_bins = data_histogram->GetNbinsX();
	vector<int> bin_map;
	bin_map.resize(n_bins);

	unsigned int number_of_bins_to_skip(0);
	unsigned int bin_counter(0);
	for (unsigned int i = 1; i <= n_bins; ++i) {
		double data = data_histogram->GetBinContent(i);
		if (data <= 0.) {
			// Through out bin with no data
			bin_map[i - 1] = -1;
			number_of_bins_to_skip++;
		} else if (i == 1) {
			// Through out underflow bin
			bin_map[i - 1] = -1;
			number_of_bins_to_skip++;
		} else if (i == n_bins) {
			// Through out overflow bin
			bin_map[i - 1] = -1;
			number_of_bins_to_skip++;
		} else {
			// Search for  bins with empty rows/columns
			bool skip_bin = true;
			for (unsigned int j = 2; j <= n_bins - 1; j++) {
				double value = covariance_hist->GetBinContent(i, j);
				if (value != 0.) {
					skip_bin = false;
				}
			}
			// Through out bins with empty rows/columns
			if (skip_bin == true) {
				bin_map[i - 1] = -1;
				number_of_bins_to_skip++;
			} else {
				bin_map[i - 1] = bin_counter;
				bin_counter++;
			}
		}
	}

	unsigned int matrix_dimension = n_bins - number_of_bins_to_skip;
	TMatrixDSym covariance_matrix(matrix_dimension);

	// New Matrix
	// Beware the side bins of the problem
	// AND the side bins of the TH2D object
	for (unsigned int i = 2; i <= n_bins - 1; i++) {
		for (unsigned int j = 2; j <= n_bins - 1; j++) {

			// Is this bin to be skipped?
			bool skip_bin = false;
			if (bin_map[i - 1] == -1)
				skip_bin = true;
			if (bin_map[j - 1] == -1)
				skip_bin = true;
			// Set Element
			if (skip_bin == false) {
				double value = covariance_hist->GetBinContent(i, j);
				int bin_nr_i = bin_map[i - 1];
				int bin_nr_j = bin_map[j - 1];
				covariance_matrix[bin_nr_i][bin_nr_j] = value;
			}
		}
	}

	// Determinant
	double *det_covariance_matrix = new double(0.);

	// Invert the whole thing
	TMatrixDSym covariance_matrix_invers = covariance_matrix;
	covariance_matrix_invers.Invert(det_covariance_matrix);

	// Check Invertibility
	bool is_invertible = *det_covariance_matrix != 0.;
	if (is_invertible == false) {
		cout << "Error in TopSVDFunctions::SVD_CalcGlobCorr() " << endl;
		cout << "Covariance Matrix cannot be inverted." << endl;
		cout << "Check the reason for this now." << endl;
		exit(1);
	}

	// Create new Histo for global correlation
	TH1D* global_correlation_hist = new TH1D();
	global_correlation_hist->SetNameTitle("global_correlation_hist", "global_correlation_hist");
	if (covariance_hist->GetXaxis()->IsVariableBinSize() == true) {
		const TArrayD* xbins = covariance_hist->GetXaxis()->GetXbins();
		global_correlation_hist->SetBins(n_bins, xbins->GetArray());
	} else {
		double xmin = covariance_hist->GetXaxis()->GetXmin();
		double xmax = covariance_hist->GetXaxis()->GetXmax();
		global_correlation_hist->SetBins(n_bins, xmin, xmax);
	}

	// Fill the histo you just created
	for (unsigned int i = 1; i <= n_bins; i++) {
		double global_correlation = 0.;

		// Find out the "true" bin number
		int binnr = bin_map[i - 1];

		// Skip bad bins
		bool skipThis = false;
		if (binnr == -1)
			skipThis = true;

		// Run over good bins
		if (skipThis == false) {
			double cov = covariance_matrix[binnr][binnr];
			double covinv = covariance_matrix_invers[binnr][binnr];
			// The product cov*covinv should be greater than zero
			double var = divide(1., cov * covinv);
			double global_correlation_squared = 0.;
			if (var > 0.)
				global_correlation_squared = 1. - var;
			global_correlation = 100. * svd_sqrt(global_correlation_squared);
		} else {
			global_correlation = 0.;
		}

		// Set the value
		global_correlation_hist->SetBinContent(i, global_correlation);
		global_correlation_hist->SetBinError(i, 0.);
	}
	delete covariance_hist;

	return global_correlation_hist;
}

TH2D* TopSVDFunctions::get_data_covariance_matrix(const TH1D* data_histogram) {
	// get bins from data_histogram
	unsigned int n_bins = data_histogram->GetNbinsX();
	vector<double> bin_edges;
	for (unsigned int i = 1; i <= n_bins; ++i) {
		double low_edge = data_histogram->GetBinLowEdge(i);
		double bin_width = data_histogram->GetBinWidth(i);
		bin_edges.push_back(low_edge);
		bin_edges.push_back(low_edge + bin_width);
	}

	// create 2D histogram
	TH2D * data_covariance_matrix = new TH2D("data_covariance_matrix", "data_covariance_matrix", n_bins, &bin_edges[0],
			n_bins, &bin_edges[0]);

	// fill it
	for (unsigned int i = 1; i <= n_bins; ++i) {
		double variance = pow(data_histogram->GetBinError(i), 2.);
		data_covariance_matrix->SetBinContent(i, i, variance);
	}

	return data_covariance_matrix;
}

double TopSVDFunctions::divide(double numerator, double denominator) {
	double result = 0.;
	if (numerator > 0. && denominator > 0.) {
		result = numerator / denominator;
	}
	return result;
}

double TopSVDFunctions::svd_sqrt(double number) {
	double result = 0.;
	if (number > 0.) {
		result = sqrt(number);
	}

	return result;
}

