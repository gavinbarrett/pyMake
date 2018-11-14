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
        self.clean_cmd = 'clean:\n\trm -fr *.o\n'
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
        return path
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
    print("str is: " + str)
    return str

def check_main(file_rec):
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
    ccregex = re.compile('\.cc')
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
                print(result.group(3))
        obj.close()
        if is_main(f):
            #error occuring
            MasterMakeRecord.insert_zero_file_record(fr)
        else:
            MasterMakeRecord.add_to_file_record(fr)
    if main_instances > 1:
        too_many_args() 
    if main_instances < 1:
        not_enough_args()

    return MasterMakeRecord

def make_Makefile(M_Record):
    """Write Makefile"""
    project_name = sys.argv[1]
    f = open('Makefile', 'w')
    f.write(project_name + ": ")
    f.write(M_Record.main_file + M_Record.dot_o + ' ')

    ff = M_Record.return_file_record()
    for ffa in ff:
        #FIXME: treat e better -> it is very important
        e = ff.pop(0)
        for d in e.dependencies:
            #hpp = ".hpp"
            if strip_ext(d) == '.hpp':
                pass
            else:
                f.write(strip_prefix(d) + '.o ')
        f.write(M_Record.compile_cmd)

        f.write(project_name + ' ' + M_Record.main_file + '.o ')
        for t in e.dependencies:
            if strip_ext(t) == '.hpp':
                pass
            else:
                f.write(strip_prefix(t) + '.o ')
        f.write('\n\n')


    #e = ff.pop(0)

    #for z in e.dependencies:
        #if strip_ext(z) == '.hpp':
          #  pass
        #else:
            #f.write(strip_prefix(z) + '.o: ' + strip_prefix(z) + '.cpp')

    f.close()

if __name__ == "__main__":
    path = get_args()
    dirs = list_files(path) # returns valid .cpp/.hpp/.cc files
    MakeR = extract_files(dirs)
    make_Makefile(MakeR)
