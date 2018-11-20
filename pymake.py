#!/usr/bin/env python
import sys
import os
import re
"""Authored by Gavin Barrett on 10-04-2018 ->
This project collects .cpp and .hpp files from a directory and constructs an appropriate makefile"""

class MakeRecord:
    """List of FileRecords"""

    def __init__(self):
        self.index = 0
        self.FileRecordList = []
        self.main_file = ""
        self.compile_cmd = '\n\tg++ -g -Wall -Werror -std=c++11 -'
        self.clean_cmd = 'clean:\n\trm -fr '
        self.dot_o = '.o'
        self.dot_c = '.c'

    def return_file_record(self):
        return self.FileRecordList

    def add_to_file_record(self, fileObj):
        self.FileRecordList.append(fileObj)

    def insert_zero_file_record(self, fileObj):
        self.FileRecordList.insert(0, fileObj)

class FileRecord:
    """FileRecord stores dependencies for each file and identifies main"""
    def __init__(self, name, m_bool):
        self.name = name
        self.dependencies = []
        filename, file_ext = os.path.splitext(self.name)
        self.prefix = filename
        self.ext = file_ext
        self.index = 0
        self.main_f = False

    def __iter__(self):
        return self

    def __next__(self):
        self.index += 1
        if self.index == len(self.FileRecordList):
            raise StopIteration
        return self.FileRecordList[self.index]

    def add_depend(self, str):
        self.dependencies.append(str)

    def print_name(self):
        print(self.name)

    def get_dependencies(self):
        return self.dependencies

    def write_dependencies(self):
        for x in self.dependencies:
            print(x + ' ')
        print('\n')

    def id_main(self):
        self.main_f = True

    def is_main(self):
        return self.main_f

def build_multiple(MasterMakeRecord):
    """ This function will be for building multiple executables """
    print("More than one instance of main. Multiple executable compatibility has not yet been implemented yet.\n")
    print("Exiting PyMake...\n")
    sys.exit(0)


def too_many_args():
        sys.stderr.write("\nError: More than one instance of main in directory..\n")
        sys.stderr.write("Exiting PyMake..\n\n")
        sys.exit(0)


def not_enough_args():
        sys.stderr.write("\nError: No instance of main in directory..\n")
        sys.stderr.write("Exiting PyMake..\n\n")
        sys.exit(0)

def  get_args():
    """Read in arguments from cli"""
    try:
        path = sys.argv[2]
        #if second argument is a directory, initiate build stage 1
        #if second argument is a file, initiate build stage 2
        if os.path.isdir(path):
            return path
        else:
            return sys.argv

    except:
        print('Argument error')
        sys.exit(0)

def strip_ext(str):
    """Returns .ext of file"""
    filename, file_ext = os.path.splitext(str)
    return file_ext

def strip_prefix(str):
    """Returns file name without .ext"""
    filename, file_ext = os.path.splitext(str)
    return filename

def strip_include(str):
    """Strip unnecessary junk from our dependencies"""
    str = str.replace('#include ', '')
    str = str.replace('"', '')
    str = str.replace("'", "")
    str = str.replace('\n', '')
    return str

def check_main(file_rec):
    """Check to see if our file contains an instance of 'int main()'"""
    if file_rec.main_f == True:
        return True
    return False

def is_main(file):
    """Extract file that contains main()"""
    main_re = re.compile('int main')
    if(os.path.isfile(file)):
        obj = open(file, 'r')
        found_m = re.findall(r'int main', obj.read())
    if(found_m):
        return True
    else:
        return False

def filter_files(dirs):
    """Filter out results to only .\wpp files"""
    #Looking for .cpp and .hpp files; later we will add .c/.h compatibility
    ccregex = re.compile('.*\.cc$')
    regex = re.compile('\w+\.\wpp')
    main_re = re.compile('int main')
    filtered = []
    for file in dirs:
        h = regex.match(file)
        c = ccregex.match(file)
        if h or c:
            filtered.append(file)
        else:
            pass

    return filtered

def list_files(path):
    """Get list of files in the directory specified"""
    #use try block for now; come back and refactor

    #check if path is a directory
    #if not, and it is a list of files, then enter build stage 1

    try:
        dirs = os.listdir(path)
        filtered = filter_files(dirs)
        return filtered
    except:
        print('Problem with directory')
        sys.exit(0)

def extract_files(proj_files):
    """Create Lists for each file instance"""
    MasterMakeRecord = MakeRecord()
    prog = re.compile(r'([#])(\w+) ("\w+\.\w+")')
    main_instances = 0
    for f in proj_files:
        #Make filerecord obj to store data
        check_main = is_main(f)
        if check_main:
            main_instances += 1
            MasterMakeRecord.main_file = strip_prefix(f)
        fr = FileRecord(f, check_main)
        obj = open(f, 'r')
        for line in obj:
            result = prog.match(line)
            if result is None:
                pass
            else:
                line = strip_include(line)
                fr.dependencies.append(line)
                #With the way our regex is set, group(3) will be the filename
                #print(result.group(3))
        obj.close()
        if is_main(f):
            #error occuring
            MasterMakeRecord.insert_zero_file_record(fr)
        else:
            MasterMakeRecord.add_to_file_record(fr)
    #handle with options to build multiple executables (build stage 3?)
    if main_instances > 1:
        #enter build stage 3
        build_multiple(MasterMakeRecord)
    if main_instances < 1:
        not_enough_args()

    return MasterMakeRecord

def extract_cfiles(filerecord):
    """Returns list of .cc/.cpp filenames"""
    clist = []
    for d in filerecord.dependencies:
        extension = strip_ext(d)
        if extension == '.cpp' or extension == '.cc':
            clist.append(d)
    return clist

def extract_hfiles(filerecord):
    """Returns list of .h/.hpp filenames"""
    hlist = []
    for d in filerecord.dependencies:
        extension = strip_ext(d)
        if extension == '.hpp' or extension == '.h':
            hlist.append(d)
    return hlist

def build_list(list):
    """Returns string of filenames with .o extension"""
    newstring = ""
    for l in list:
        newstring += l + '.o '
    return newstring


def write_heading(fstream, filerecord, project_name):
    """This function writes the executable's build portion as well as the .cc/.cpp file which contains main()"""
    compile_cmd = '\n\tg++ -g -Wall -Werror -std=c++11 -'
    #Write executable instructions; copy filerecord for for duplicability
    filerecord1 = filerecord[:]
    filerecord2 = filerecord[:]
    clist = []

    fstream.write(project_name + ": ")
    while filerecord1:
        d = filerecord1.pop(0)
        clist.append(d.prefix)

    newstring = build_list(clist)
    fstream.write(newstring)
    fstream.write(compile_cmd + 'o ' + project_name + ' ' + newstring + '\n\n')

    #Write main() file instructions
    e = filerecord2.pop(0)
    fstream.write(e.prefix + '.o: ' + e.name + ' ')
    clist = extract_cfiles(e)
    hlist = extract_hfiles(e)
    for cfile in clist:
        fstream.write(cfile + ' ')
    for hfile in hlist:
        fstream.write(hfile + ' ')
    fstream.write(compile_cmd + 'c ')
    fstream.write(e.name + ' ')
    for c3 in clist:
        fstream.write(c3 + ' ')
    fstream.write('\n\n')


def write_dependencies(fstream, filerecord):
    """Write files used alongside main file to build executable"""
    compile_cmd = '\n\tg++ -g -Wall -Werror -std=c++11 -'
    while filerecord:
        e = filerecord.pop(0)
        clist = extract_cfiles(e)
        hlist = extract_hfiles(e)
        fstream.write(e.prefix + '.o: ' + e.name + ' ')
        for x1 in clist:
            fstream.write(x1 + ' ')
        for x2 in hlist:
            fstream.write(x2 + ' ')
        fstream.write(compile_cmd + 'c ' + e.name + ' ')
        for c in clist:
            fstream.write(c + ' ')
        fstream.write('\n\n')

def write_clean_rule(fstream, project_name):
    """Write a clean rule in order to delete executable and any intermediary files"""
    clean_cmd = 'clean:\n\trm -fr '
    fstream.write(clean_cmd + project_name + ' *.o\n')

def make_Makefile(M_Record):
    """Write Makefile"""
    project_name = sys.argv[1]

    #open file
    f = open('Makefile', 'w')

    #retreive filerecord
    file_Record = M_Record.return_file_record()

    #write heading
    write_heading(f, file_Record, project_name)

    # write dependencies
    write_dependencies(f, file_Record)

    # write clean rule
    write_clean_rule(f, project_name)

if __name__ == "__main__":
    #get arguments from cmd line
    path = get_args()

    #get files from diectory
    dirs = list_files(path) # returns valid .cpp/.hpp/.cc files

    #extract information from files
    MakeR = extract_files(dirs)

    #write makefile
    make_Makefile(MakeR)
