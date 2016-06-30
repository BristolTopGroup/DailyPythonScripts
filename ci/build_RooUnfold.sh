#!/bin/bash

export base=`pwd`
major_root_version=`echo $ROOT | cut -d. -f1`

if [ ! -d "$base/external/lib" ]; then
	mkdir $base/external/lib
	echo "Building RooUnfold"
	cd $base/external/RooUnfold/
	cmake CMakeLists.txt
	make RooUnfold
	#remove tmp folder
	rm -fr $base/external/RooUnfold/tmp
	mv $base/external/RooUnfold/libRooUnfold.so $base/external/lib/.
	echo "Updating RooUnfold config"
	cat $base/config/RooUnfold_template.py > $base/config/RooUnfold.py
	echo "library = '$base/external/lib/libRooUnfold.so'" >> $base/config/RooUnfold.py
	# this file is only created for ROOT 6
	if [ $major_root_version -eq 6 ]; then
	 cp $base/external/RooUnfold/RooUnfoldDict_rdict.pcm $base/.
	fi
fi
