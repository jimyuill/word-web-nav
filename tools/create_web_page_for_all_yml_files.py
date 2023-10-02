'''

Description:
* Calls create_web_page.py, for the all of the *.yml files at the specified directory.
  * The *.yml files must be WWN input parameter-files
* This program was created for running regresion-tests
  * See: docs\development-docs\WWN--testing--regression-tests.docx

Command-line input: the full path to a directory with WWN input parameter-files

'''

import argparse
import sys
import os

from os import listdir
from os.path import isfile, join

sys.path.append(r'..\createwebpage')
import create_web_page

'''
Argparse is used to process the command-line argument 
* Argparse docs: https://docs.python.org/3/library/argparse.html
* The argparse code here is from:  https://stackoverflow.com/questions/14360389/getting-file-path-from-command-line-argument-in-python/47324233
'''
# Creates and returns the ArgumentParser object
def create_arg_parser():
    parser = argparse.ArgumentParser(description=
        'Calls create_web_page.py, for the all of the *.yml files at the specified directory.')
    parser.add_argument('input_dir_path', metavar="<input-dir-path>",
                    help='Path to the directory containing the *.yml files.')
    return parser

MAX_FILES_TO_PROCESS = sys.maxsize
#MAX_FILES_TO_PROCESS = 2

'''
#########
Main
#########
'''
if __name__ == "__main__":
    # Get the directory path from the command-line
    # * argparser also verifies the command-line syntax
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args()
    input_dir_path = parsed_args.input_dir_path

    # For the input directory, create a list of files with extension .yml
    all_files = [item for item in listdir(input_dir_path) if isfile(join(input_dir_path, item))]
    yml_files = []
    for file_name in all_files:
        file_name_root, file_name_extension =  os.path.splitext(file_name)
        if (file_name_extension.lower() == ".yml"):
            yml_files.append(file_name)

    # Process each input .yml file
    file_count = 0
    failed_file_count = 0
    failed_file_names = ""
    files_with_warning_messages = 0
    total_num_warning_messages = 0
    for file_name in yml_files:
        file_count += 1
        print("\nINFO.  Processing the .yml file:  " + file_name)

        # Create the file-path for the yml-file 
        yml_file_path = join(input_dir_path, file_name)

        '''
        Call create_web_page.main(), pass it the path to the yml-file
        '''
        return_value, num_warning_messages = create_web_page.create_web_page(yml_file_path)
        if return_value == 1:
            failed_file_count += 1
            failed_file_names += file_name + ", "
        if (num_warning_messages > 0):
            files_with_warning_messages += 1
            total_num_warning_messages += num_warning_messages

        if (file_count == MAX_FILES_TO_PROCESS):
            break

    print("\nBatch processing completed.")
    print("Files processed: " + str(file_count))
    print("Files processed successfully: " + str(file_count - failed_file_count))    
    if (failed_file_count != 0):
        failed_files_string = "  File-names: " + failed_file_names
    else:
        failed_files_string = ""
    print("Files processed unsuccessfully:  Count:" + str(failed_file_count) + \
          failed_files_string)
    print("Number of files with warning messages: " + str(files_with_warning_messages))                        
    print("Number of warning messages: " + str(total_num_warning_messages))              
    print("")