'''
################
This file contains the function: copy_words_embedded_files()

The function is called by: create_web_page_core() in create_web_page.py

MIT License, Copyright (c) 2021-present Jim Yuill
################
'''

import shutil
import os
# Specifies the YAML keys for the input parameter-file
from input_parameter_file_keys import *


def copy_words_embedded_files(loaded_parms):
    '''
    Description:
    * Copy Word's embedded-files-directory to the output directory
    * For a Word-HTML-file, Word will create a directory to hold embedded files, such as pictures.
      * That directory will be referred to as the "embedded-files directory".
      * For the embedded-files directory, its name is the same as the Word-HTML-file, but with a suffix "_files"
        * e.g., for index.html, the embedded-files directory is index_files
    
    Parameter: loaded_parms, contains the input paramter-file, in dictionary format
    
    Return:
    0 : OK
    1 : Error
    '''    
    
    # Get the relevant values specified in the input parameter-file
    input_html_path_value = loaded_parms[YML_KEY_REQUIRED][YML_KEY_INPUT_HTML_PATH]
    output_directory_path_value = loaded_parms[YML_KEY_REQUIRED][YML_KEY_OUTPUT_DIRECTORY_PATH]    

    # For the input Word-HTML-file, if an embedded-files directory exists, copy it to the output directory.
    input_html_file_directory, input_html_file_name = os.path.split(input_html_path_value)
    input_html_file_name_without_extension, input_html_file_name_extension =  os.path.splitext(input_html_file_name)
    embedded_files_directory_name = input_html_file_name_without_extension + "_files"
    input_embedded_files_directory_path = os.path.join(input_html_file_directory, embedded_files_directory_name)
    output_embedded_files_directory_path = os.path.join(output_directory_path_value, 
                                                    embedded_files_directory_name)
    if not os.path.exists(input_embedded_files_directory_path):
        print("INFO.  For the input Word-HTML-file, an embedded-files-directory was not found. " + 
              "It is optional:")
        print("       " + input_embedded_files_directory_path)
    else:
        print("INFO.  For the input Word-HTML-file, an embedded-files-directory was found, at:")
        print("       " + input_embedded_files_directory_path)
        print("INFO.  Copying the embedded-files-directory to the output directory, at:")
        print("       " + output_embedded_files_directory_path)

        # Test if the embedded-files directory already exists in the output directory
        if os.path.exists(output_embedded_files_directory_path):
            print("INFO.  An embedded-files-directory already exists in the output directory. " + \
                  "It will be deleted. ")
            # How to delete a directory in Windows:
            # * https://stackoverflow.com/questions/6996603/how-to-delete-a-file-or-folder
            try:
                shutil.rmtree(output_embedded_files_directory_path)
            except OSError as e:
                print("")
                print("ERROR.  Could not delete the existing output directory:")
                print("        " + output_embedded_files_directory_path)
                print("        %s - %s." % (e.strerror, e.filename))
                return 1

        # shutil.copytree() requires that the destination does not exist
        # * https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
        try:
            shutil.copytree(input_embedded_files_directory_path, output_embedded_files_directory_path)
        except OSError as e:
            print("")
            print("ERROR.  Could not copy the embedded-files-directory.")
            print("        %s - %s." % (e.strerror, e.filename))
            return 1

    return 0