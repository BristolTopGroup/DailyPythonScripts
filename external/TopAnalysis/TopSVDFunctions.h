#ifndef TOPSVDFUNCTIONS_H
#define TOPSVDFUNCTIONS_H
#include <vector>
#include "TH1D.h"
#include "TH2D.h"

class TopSVDFunctions {

public:
//	TopSVDFunctions() {
//	}
//	;
	static std::pair<double, double> get_optimal_tau_values(const TH1D* b_data, const TH1D* b_ini, const TH1D* x_ini,
			const TH2D* A_det, double tau_min, double tau_max, unsigned int number_of_points);

	static std::vector<double> calculate_tau_scan_points(double tau_min, double tau_max, unsigned int number_of_points);

	static TH2D* get_data_covariance_matrix(const TH1D* data_histogram);

	static double get_global_correlation(const TH1D* data_histogram);
	static TH1D* get_global_correlation_hist(const TH1D* data_histogram);

	static double divide(double numerator, double denominator);
	static double svd_sqrt(double number);
};

#endif

