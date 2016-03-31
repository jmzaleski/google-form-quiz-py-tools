#!/usr/bin/python
from __future__ import print_function  #allows print as function
import sys
import csv # see https://docs.python.org/2/library/csv.html

#download the responses to this file
FN = 'q6-responses.csv'
GRADE_FILE_HEADER = """*/,
* this file generated by quiz marking python script
q6 / 5
"""

answer = [
"gender roles social stratification and ethnicity",
"an ethical or moral",
"SKIP_ME", #"moral",
"Scott Aaronson",
"similar but unique",
"structural"
]

# be paranoid about data until sure it's clean (missing students)
SCRUB = True

PRINT_STATS = False

# just give mark of 1 or zero
PASS_OR_FAIL = False #True

# make this into python module
execfile("mark-quiz.py")
