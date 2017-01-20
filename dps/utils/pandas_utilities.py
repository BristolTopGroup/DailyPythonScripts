import pandas as pd 
import os

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 4096)
pd.set_option('display.max_rows', 50)
pd.set_option('display.width', 1000)
pd.set_option('precision',10)

def dict_to_df(d):
	'''
	Transform a dictionary nto a dataframe
	'''
	df = pd.DataFrame(d)
	return df

def list_to_series(l):
	'''
	Transform a list into a series
	'''
 	s = pd.Series( l )
 	return s

def df_to_file(filename, df, index=True):
	'''
	Save a dataframe to an output text file
	Nicely human readable
	'''
	# Make the folder if it doesnt exist
	import os
	from dps.utils.file_utilities import make_folder_if_not_exists
	make_folder_if_not_exists(os.path.dirname(filename))

	with open(filename,'w') as f:
		df.to_string(f, index=index)
		f.write('\n')
		print('DataFrame written to {}'.format(f))
		f.close()
	return

def file_to_df(f):
	'''
	Read a dataframe from file
	'''
	if os.path.exists(f):
		with open(f,'r') as f:
			df = pd.read_table(f, delim_whitespace=True)    	
			# print('DataFrame read form {}'.format(f))
			f.close()
	else:
		print "Could not find {} ".format(f)
		return
	return df

def append_to_df(df, df_new):
	'''
	Append something to dataframe.
	Must have the same number of indexes
	'''
	# Overwrite existing columns of the same name
	for newcols in df_new.columns:
		for cols in df.columns:
			if newcols == cols:
				del df[cols]
	df = pd.concat([df, df_new], axis=1)
	return df

def divide_by_series(s1, s2):
	'''
	Divide one series by another
	'''
	s = s1.div(s2)
	return s

def add_dfs(l_df):
	'''
	Add N dataframes together of the same format
	'''
	# Initialise summed dataframe to first in list
	df_summed = l_df[0]
	# Remove from list
	del l_df[0]
	if len(l_df) == 0:
		return

	for df in l_df:
		df_summed = df_summed.add(df)
	return df_summed


def tupleise_cols(vals, errs):
	'''
	tupleising two cols
	'''
	vals_errs = [ (v, e) for v,e in zip(vals, errs)]
	return vals_errs

def write_tuple_to_df( d_norm, filename ):
	'''
	Writing tuples to a dataframe

	Takes a pandas dataframe of tuples of the form:
		A 	| 	B 	
	  (v,e) | (v,e)

	Write a pandas output file of the form:
		A 	|	A_Unc 	|	B 	| 	B_Unc	
	   (v)  |    (e)	|  (v)  |    (e)

	'''
	# First create the dataframe
	df = dict_to_df(d_norm)

	# pandas really cant handle reading in tuples. Have to split here
	for col in df.columns:
	    df[[col, col+'_Unc']] = df[col].apply(pd.Series)
	# Make columns alphabetical for easy reading
	l=df.columns.tolist()
	l.sort()
	df = df[l]

	# Write dataframe
	df_to_file(filename, df, index=False)
	return

def read_tuple_from_file( filename ):
	'''
	Reading the output of 01 to a dataframe

	Reads a pandas output file of the form:
		A 	|	A_Unc 	|	B 	| 	B_Unc	
	   (v)  |    (e)	|  (v)  |    (e)

	Returns a pandas dataframe of the form:
		A 	| 	B 
	  (v,e) | (v,e)

	'''
	from dps.config.xsection import XSectionConfig
	config = XSectionConfig(13)

	# First read the dataframe
	df = file_to_df(filename)
	l=df.columns.tolist()

	# Now to retupleise the columns
	for sample in l:
		if '_Unc' in sample: continue
		vals = df[sample]
		errs = df[sample+'_Unc']
		df[sample] = tupleise_cols(vals, errs)
		del df[sample+'_Unc']
	return df

def combine_complex_df( df1, df2 ):
	'''
	Takes a 2 pandii dataframes of the form:
		A 	| 	B   	 	A 	| 	B 
	  (v,e) | (v,e)		  (v,e) | (v,e) 

	Returns 1 pandas dataframe of the form
			      A   |   B 
	  			(v,e) | (v,e)
	'''
	from uncertainties import ufloat
	l1=df1.columns.tolist()
	l2=df2.columns.tolist()
	if l1 != l2:
		print "Trying to combine two non compatible dataframes"
		print l1
		print l2
		return

	combined_result = {}
	for sample in l1:
		results = []
		for entry1, entry2 in zip(df1[sample], df2[sample]):
			v1 = ufloat(entry1[0], entry1[1])
			v2 = ufloat(entry2[0], entry2[1])
			s = v1 + v2
			results.append( ( s.nominal_value, s.std_dev ) )
		combined_result[sample] = results
	df = dict_to_df(combined_result)
	return df

def create_covariance_matrix( matrix, outfile ):
	'''
	Takes a numpy.matrix

	Returns a Pandas DataFrame of the form:

		|   1	 |    2   |   N   
	1	| Cov_11 | Cov_12 | Cov_1N
	2	| Cov_21 | Cov_22 | Cov_2N
	N	| Cov_N1 | Cov_N2 | Cov_NN
	'''

	df = pd.DataFrame(matrix)
	df_to_file(outfile, df)
	return

def matrix_from_df( df ):
	'''
	Takes a Pandas DataFrame of the form:

		| 1	 | 2  | N   
	1	| 11 | 12 | 1N
	2	| 21 | 22 | 2N
	N	| N1 | N2 | NN

	Returns a numpy.matrix
	'''
	matrix = df.as_matrix()
	return matrix


