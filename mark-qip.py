#!/usr/bin/python
from __future__ import print_function  #allows print as function
import sys
import csv # see https://docs.python.org/2/library/csv.html

#download the responses to this file
FN = 'qip.csv'
GRADE_FILE_HEADER = """*/,
* this file generated by quiz marking python script
qip / 5
"""

answer = [
 "You are paying to enter into an agreement which allows you to copy the software",
 "TRUE",
 "Physical control of an object gives the owner mostly all the rights they might need",
 "Registers a concept as an official corporate secret",
 "All of the Above"
]

# be paranoid about data until sure it's clean
SCRUB = True

# just give mark of 1 or zero
PASS_OR_FAIL = False

PRINT_STATS = True

# make this into python module
execfile("mark-quiz.py")
