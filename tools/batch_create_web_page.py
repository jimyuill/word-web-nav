'''

Description:
* This program is used to create WWN web-pages for all of the Word HTML files in a directory
  * This program was created for running regresion-tests
    * See: docs\development-docs\WWN--testing--regression-tests.docx

* For each .htm* file at the specified directory:
  * Create a WWN input parameter-file (.yml), for the .htm* file
    * To create the file, the following are used: 
      * The input config-file, the path to the input .htm* file, and Jinja2
  * Call create_web_page.py, and provide the path to the WWN input parameter-file

Inputs:
* Command-line input: Path to the directory containing the Word HTML-files.
* Input config-file: batch_create_web_page.yml, in the input directory.
  * The config-file is provided by the caller
  * It is a Jinja template, used to create the .yml files
  * An example config-file is provided in the repo. (The file-paths will need to be changed.)
* The .html and .htm files in the input directory.

'''


import argparse
import sys
import os

from os import listdir
from os.path import isfile, join

from importlib import reload

from jinja2 import Template

sys.path.append(r'..\createwebpage')
import create_web_page

CONFIG_FILE_NAME_ROOT = "batch_create_web_page"

'''
Argparse is used to process the command-line argument 
* Argparse docs: https://docs.python.org/3/library/argparse.html
* The argparse code here is from:  https://stackoverflow.com/questions/14360389/getting-file-path-from-command-line-argument-in-python/47324233
'''
# Creates and returns the ArgumentParser object
def create_arg_parser():
    parser = argparse.ArgumentParser(description=
        'Calls create_web_page.py, for the Word HTML-files at the specified directory.')
    parser.add_argument('input_dir_path', metavar="<input-dir-path>",
                    help='Path to the directory containing the Word HTML-files.')
    return parser

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

    '''
    * A config-file is expected, in the input directory.
    * Open the config-file, and use it as a Jinja2 template
    '''

    # Verify the expected config-file exists
    config_file_name = CONFIG_FILE_NAME_ROOT + ".yml"
    print("INFO.  Opening the config-file, and loading it as a Jinja2 template: " + config_file_name)    
    config_file_path = os.path.join(input_dir_path, config_file_name)
    if not (os.path.exists(config_file_path)):
        print("")
        print("ERROR.  The input directory must have the config file: " + config_file_path)
        print("")        
        sys.exit()  

    # Verify no HTML files have the root-name specified in CONFIG_FILE_NAME_ROOT
    disallowed_file_path1 = os.path.join(input_dir_path, (CONFIG_FILE_NAME_ROOT + ".htm"))
    disallowed_file_path2 = os.path.join(input_dir_path, (CONFIG_FILE_NAME_ROOT + ".html"))
    if os.path.exists(disallowed_file_path1) or os.path.exists(disallowed_file_path2):
        print("")
        print("ERROR.  The input directory cannot have HTML files with these names:")
        print("        " + CONFIG_FILE_NAME_ROOT + ".htm or " + CONFIG_FILE_NAME_ROOT +".html")
        print("")        
        sys.exit()  

    # Open the expected config-file
    try:
        config_file_handle = open(config_file_path)
    except IOError as e:
        print("")
        print("ERROR.  Could not open the config-file:")
        print("%s - %s." % (e.strerror, e.filename))
        print("")                
        sys.exit()  
    config_file_data = config_file_handle.read()
    config_file_handle.close()
    config_file_template = Template(config_file_data)


    # For the input directory, create a list of files with extension .htm or .html
    all_files = [item for item in listdir(input_dir_path) if isfile(join(input_dir_path, item))]
    word_html_files = []
    word_html_file_roots = []
    for file_name in all_files:
        file_name_root, file_name_extension =  os.path.splitext(file_name)
        if (file_name_extension.lower() == ".html") or (file_name_extension.lower() == ".htm"):
            word_html_files.append(file_name)
            word_html_file_roots.append(file_name_root)

    # * Test if there's two files whose names have the same root-name, and the extensions .htm and .html,
    #   e.g., "foo.htm" and "foo.html".
    # * This isn't allowed because a config-file is created for each HTML file, for calling create_web_page.
    #   The config-file's name is derived from the HTML-file's root-name: <root-name>.yml.
    #   So, two HTML files cannot have the same root-name.
    # * set() converts the list to a set, and thus removes duplicates
    if len(word_html_file_roots) != len(set(word_html_file_roots)):
        print("")
        print("ERROR.  The input directory has two files with the same root-name and with " +
              " extensions \".htm\" and \".html\"")
        print("")
        sys.exit()  

    # Process each input Word HTML-file
    file_count = 0
    failed_file_count = 0
    failed_file_names = ""
    total_num_warning_messages = 0
    for file_name in word_html_files:
        file_count += 1
        print("\nINFO.  Processing the Word HTML-file:  " + file_name)

        '''
        For this Word HTML-file, create the WWN input parameter-file that will be used by create_web_page.py, 
        '''

        # Create the file-name for the WWN input parameter-file 
        file_name_root, file_name_extension =  os.path.splitext(file_name)
        wwn_input_parameter_file_name = file_name_root + ".yml"
        wwn_input_parameter_file_path = join(input_dir_path, wwn_input_parameter_file_name)

        # Use Jinja to generate the data for the WWN input parameter-file 
        file_path = join(input_dir_path, file_name)
        wwn_input_parameter_file_data = config_file_template.render({'inputHtmlPath':file_path})

        # Write the WWN input parameter-file to disk
        print("INFO.  Creating the WWN input parameter-file used by create_web_page.py:  " + \
              wwn_input_parameter_file_name)
        wwn_input_parameter_file_handle = open(wwn_input_parameter_file_path, 'w')
        wwn_input_parameter_file_handle.write(wwn_input_parameter_file_data)
        wwn_input_parameter_file_handle.close()

        '''
        Call create_web_page.main(), pass it the path to the WWN input parameter-file
        '''

        # Reload needed to refresh the global variables
        reload(create_web_page)
        return_value, num_warning_messages = create_web_page.create_web_page(wwn_input_parameter_file_path)
        if return_value == 1:
            failed_file_count += 1
            failed_file_names += file_name + ", "
        total_num_warning_messages += num_warning_messages

    print("\nBatch processing completed.")
    print("Files processed: " + str(file_count))
    print("Number of warning messages: " + str(total_num_warning_messages))    
    print("Files processed unsuccessfully:  Count:" + str(failed_file_count) + \
          "  File-names: " + failed_file_names)
    print("")