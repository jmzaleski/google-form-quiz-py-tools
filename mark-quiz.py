import csv # see https://docs.python.org/2/library/csv.html

def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

def debug_message(*objs):
    print("DEBUG: ", *objs, file=sys.stderr)

def verbose_message(*objs):
    print("VERBOSE: ", *objs, file=sys.stderr)

#idea is that this is included from a wrapper than defines 
# FN, GRADE_FILE_HEADER, and answers

try:
 FN
except NameError:
  warning( "FN, GRADE_FILE_HEADER, or answers not defined by wrapper!")
  exit(1)
try:
 GRADE_FILE_HEADER
except NameError:
  warning( "GRADE_FILE_HEADER not defined by wrapper!")
  exit(1)
try:
 answer
except NameError:
  warning( "answer not defined by wrapper!")
  exit(1)
try:
 SCRUB
except NameError:
  warning( "SCRUB not defined by wrapper!")
  exit(1)
try:
 PASS_OR_FAIL
except NameError:
  warning( "PASS_OR_FAIL not defined by wrapper!" )
  exit(1)
try:
 PRINT_STATS
except NameError:
  warning( "PRINT_STATS not defined by wrapper!")
  exit(1)


# if the cdf userid is one of the unfortunate ones that is too short for Jim's grading program map it..
# jim's mark programs dislike names that are too short
# TODO: should put a clause to catch too_short_cdf_id above too and move it's defn to caller
# but same for all quizzes in a class, so leave it here until think of better idea

too_short_cdf_id = {
"g4ag" :"g4ag__",
"g4p" :"g4p__",
"1234" : "1234_"
}

SCRUB_ZERO_CORRECT = SCRUB
CHECK_MISSING_STUDENTS = False #SCRUB

# edit this for each semester. maps UofT student number to CDF id
MAP_FILE = '../CSC300H1S-ID-cdfuserid-map.txt'

#map cdf userid's to number of correct answers on the quiz
grade = {}

# maps over question 
correct_q = {} # how many students answered q[ix] correctly
answered_q = {}# how many students answered q[ix] 
response_count = {} #stats

num_answers = 0
for a in answer:
 correct_q[num_answers] = 0
 answered_q[num_answers] = 0
 response_count[num_answers] = {} #dict of answer to int
 num_answers += 1

quit_because_student_got_zero = False #student getting zero is a clue to busted csv file

try:
  VERBOSE
except NameError:
  VERBOSE = False

VERBOSE_INCORRECT = VERBOSE
VERBOSE_SKIP = True #VERBOSE

with open(FN, 'rb') as csvfile:
 spamreader = csv.reader(csvfile, delimiter=',', quotechar='|',dialect=csv.excel_tab)
 first_line = True
 for list_of_strings in spamreader:
     if first_line:
         squirrel = str(list_of_strings[4:])
         first_line = False
         continue
     #debug_message( list_of_strings)
     cdf_name = list_of_strings[1].lower()
     if VERBOSE:
        verbose_message( "about to process responses for:", cdf_name, list_of_strings)

     #debug_message( 'list_of_strings[1]', cdf_name)
     data = list_of_strings[2:]
     ix = 0
     num_correct = 0
     for datum in data:
         if len(datum) == 0:
            #debug_message( "zero length datum at ix=", ix)
            continue #marking qi google forms seemed to toss in the occasional empty field??
         if ix >= num_answers: # will be more data fields in CSV than answers.
            break
         if VERBOSE:
            verbose_message( "verbose response:", ix, cdf_name, datum)
            verbose_message( "verbose  correct:", ix, cdf_name, answer[ix])
            
         answered_q[ix] += 1 # someone answered question ix

         if answer[ix] == "SKIP_ME" :
            if VERBOSE_SKIP: verbose_message( "skipping question", ix)
         else:
            if not datum in response_count[ix]:
                response_count[ix][datum] = 1;
            response_count[ix][datum] +=1
            if datum == answer[ix]:
               num_correct += 1   # cdf_name got question ix correct
               correct_q[ix] += 1 
            else:
               # cdf_name got question ix wrong
               if VERBOSE_INCORRECT:
                  verbose_message( cdf_name, ix, "incorrect" )
                  verbose_message( "response:", datum)
                  verbose_message( " correct:", answer[ix])
         ix += 1

     #exit(1) # peek at first data line
     
     DEBUG_PRINT_CORRECT = VERBOSE
     if DEBUG_PRINT_CORRECT: verbose_message( cdf_name, "num_correct", num_correct, "of", num_answers)

     # all answers in datum incorrect.
     # take a look to see if something lexical is the problem for zero correct responses
     # print details here while responses still available
     if num_correct == 0:
        if SCRUB_ZERO_CORRECT: # dump answers for students who got zero in detail
         print( cdf_name, "** dumping because num_correct",num_correct)
         ix = 0
         for datum in data:
          print( ix,")", "student", datum)
          if ix == len(answer):
             break
          print( ix,")", "answer ", answer[ix])
          ix += 1

        if quit_because_student_got_zero:
         print( "quitting because a student got zero")
         exit(1)


     grade[cdf_name] = num_correct


# create a list of the CDF id's we saw in the form response.
# a really annoying thing is that a student's cdf name may be shorter than 5 chars
# which is shorter than Jim's grading programs allow. hacks to follow.
#
sorted_list_cdf_names = sorted(grade.keys())

#debug_message( "sorted_list_cdf_names", sorted_list_cdf_names)

# now read the file mapping student ID to cdf userid from ROSI data
# need to filter out students that answer the quiz but are no longer enrolled
# this was written as side effect of running init-grades.sh

cdf_id_to_student_number = {}

with open( MAP_FILE, 'rb') as csvfile:
 csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')

 for a_map in csv_reader:
    id = a_map[0]         #student number
    cdf_id = a_map[1]     #cdf userid
    cdf_id_to_student_number[cdf_id] = id

#debug_message( "cdf_id_to_student_number", cdf_id_to_student_number)

# check for students who submitted a response but do not appear in the class list from CDF
# happens when students drop course after writing a quiz
# oh bummer, what about the kids that have too short cdf user ids?
#
if CHECK_MISSING_STUDENTS:
 is_missing_student = False
 for cdf_name in sorted_list_cdf_names:
    if cdf_name in too_short_cdf_id.keys() :
       cdf_userid_for_grades_files = too_short_cdf_id[cdf_name]
    else:
       cdf_userid_for_grades_files = cdf_name.lower()

    if not cdf_userid_for_grades_files in cdf_id_to_student_number:
        print( cdf_name, "is missing in cdf_id_to_student_number map")
        is_missing_student = True
 if is_missing_student:
    print( "There exist missing students!! specifically, we saw CDF ids in google forms response that did not appear in student_number to cdf_id map file. exit(2)")
    exit(2)

# debug_message( out a Jim Clark format grades file header)
# now can pump out a grades file with student number (from rosi) and cdf id (from quiz)
PRINT_GRADES = True

if PRINT_GRADES :
 print( GRADE_FILE_HEADER)
 for cdf_name in sorted_list_cdf_names:
    if PASS_OR_FAIL:
        gr = 1
    else:
        gr = grade[cdf_name]

    if cdf_name in too_short_cdf_id.keys() :
       cdf_userid_for_grades_files = too_short_cdf_id[cdf_name]
    else:
       cdf_userid_for_grades_files = cdf_name.lower()

    if len(cdf_userid_for_grades_files) < 5 :
       warning( "probably missed a student in too_short_cdf_id because", cdf_name, "is shorter than 5 chars")
       if SCRUB:
         exit(2)

    #real work!
    if cdf_userid_for_grades_files in cdf_id_to_student_number:
        print( cdf_id_to_student_number[cdf_userid_for_grades_files] + "    " + cdf_userid_for_grades_files + "," + str(gr))

if PRINT_STATS:
 STATS_FILE=FN+"-stats"
 fs = open(STATS_FILE,"w")
 fs.write("stats for responses in " + FN + " " + squirrel + "\n")
 
 ix = 0
 for a in answer:
    s = "%4d: %3d/%3d" % ( ix, correct_q[ix],  answered_q[ix])
    if answered_q[ix] != 0:
       s += " %5.2f %%" % ( 100.0 * correct_q[ix]/ answered_q[ix] )
    #debug_message( s)
    fs.write(s + "\n")
    ix += 1
 
 fs.write("\n\nquestion breakdown\n");
 for q in response_count.keys():
    fs.write( "------ Question %d -------\n" % (q))
    qq = response_count[q]
    for a in qq.keys():
        fs.write( "%4d %s\n" % ( qq[a], a )  )
 fs.close()
 
