#!/usr/bin/env python

import sys

infile = sys.argv[1]

maxcols = -1

with open(infile, 'r') as file:
	lines = file.readlines()

for line in lines:
	ncols = line.count(',')
	maxcols = max(ncols, maxcols)

for i in range(len(lines)):
	ncols = lines[i].count(',')
	num_rows_to_add = maxcols - ncols
	lines[i] = lines[i].strip('\n') + ',' * num_rows_to_add + '\n'
	# print(lines[i].count(','))

with open(infile, 'w') as file:
	file.writelines(lines)

# print(maxcols)