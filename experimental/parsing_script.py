#!/usr/bin/python
import sys, string
import glob
from math import *

events = [ ]


def getList(file):
	input = open(file, "r")
	lines = input.readlines()
	for line in lines:
		columns = string.split(line)
		events.append(columns[1])

if __name__ == "__main__":
	print "Crab failed events parsing script"

	args = sys.argv
	if not len(args) >= 2:
		print "Please specify a file with a tabel to get the events from"
		sys.exit()
        file = sys.argv[1]

	print "Looking at the table in the file ", file

	getList(file)

	event_list = ''
	for event in events:
		event_list += event
		event_list += ','
	print event_list
