#!/usr/bin/python
import sys, string
import glob
from math import *

events = [ ]


def getList(file):
	input = open(file, "r")
	lines = input.readlines()
	N_events = 0
	for line in lines:
		columns = string.split(line)
		N_events += int(columns[5])
	print "Number of processed events: ", N_events

if __name__ == "__main__":
	print "Welcome to crab number of processed events parsing script."

	args = sys.argv
	if not len(args) >= 2:
		print "Please specify a file with a table to get the numbers of events from."
		sys.exit()
        file = sys.argv[1]

	print "Looking at the table in the file", file

	getList(file)
