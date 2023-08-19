#!/usr/bin/env python
'''
########################################################################

DESCRIPTION:  Converts a Word HTML-file into a WordWebNav (WWN) web-page

USAGE:  
* Calling from the Windows command-line:
> cd <directory with create_web_page.py>
> python create_web_page.py <full-path of parameter-file>

  * If <full-path of parameter-file> is omitted, the user is prompted for it.

  * The parameter-file includes specification of the input Word HTML-file,
    and the directory for the output WWN web-page.
  * Parameter-file templates are provided in the WWN repo.

USAGE: 
* Calling from a Python module
  * Call: create_web_page()
  * If create_web_page() is called more than once, a reload is needed:
    import create_web_page
      # Reload needed to refresh the global variables
      reload(create_web_page)
      return_value, num_warning_messages = create_web_page.create_web_page(wwn_input_parameter_file_path)

* WWN's documentation is on the WWN web-page, and in the repo under /docs.
  The documentation includes:
  * WWN's introduction, installation and use
  * Development documents, describing WWN's R&D, including the code.

MIT License, Copyright (c) 2021-present Jim Yuill

########################################################################
'''

# Python pre-installed libraries
import argparse
import sys
import importlib

# Modules in this package
# * To import modules from this package, code was added to __init__.py
from load_input_parameter_file import load_input_parameter_file
from load_html_files import load_html_files
from copy_words_embedded_files import copy_words_embedded_files
from construct_html_sections import construct_html_sections
import fix_word_html
# * fix_word_html needs to be reloaded for the case of create_web_page() being
#   called from another Python module.
# * The reload is needed due to fix_word_html using a global variable.
importlib.reload(fix_word_html)

# This library needs to have been installed by the user
try:
    # Jinja2:  pip install jinja2
    from jinja2 import Template
except ImportError as e:
    print("")
    print("ERROR.  Could not import a required Python module.")
    print("        The installation instructions specify the required modules.")
    print("        Import-error description:")
    print("")
    print(e)
    print("")    
    sys.exit()


'''
################
# Function: create_web_page_core()

* Description: 
  * This is WWN's primary function.
  * This function reads the input parameter-file, and creates the WWN web-page.
  * This function is called by the wrapper-function create_web_page().
  
* Input:
  * parameter_file_path: the input parameter-file's full-path
  * num_warning_messages: the number of warning messages, thus far
* Return:
  * 1, num_warning_messages
  * 0, None
#################
'''
def create_web_page_core(parameter_file_path: str,
                         num_warning_messages: int):
    
    # Check Python version 3
    # * Works with Python 2.6 and below:
    #   * https://stackoverflow.com/questions/446052/how-can-i-check-for-python-version-in-a-program-that-uses-new-language-features
    if sys.version_info[0] < 3:
        print("")
        print("ERROR.  Python version 3 is required.")
        print("        WordWebNav has been tested with Python 3.7.0 and 3.9.6")
        print("")    
        sys.exit()

    # Check Python version is at least 3.7
    if sys.version_info[1] < 7:
        num_warning_messages += 1
        print("")
        print("WARNING.  Python version is less than 3.7.")
        print("          WordWebNav has been tested with Python 3.7.0 and 3.9.6")   
        print("")    

    # This dictionary holds the "variables" that will be copied into the Jinja template (jinja_template)
    # * The Jinja template is used to create the output HTML.
    # * This dictionary is used in calling the Jinja method render(), to create the output HTML:
    #   * generated_html = jinja_template.render(jinja_template_variables)
    jinja_template_variables = {
        'version': "",
        'title_tag': "",
        'meta_tag_with_description': "",
        'page_structure_css_file_path': "",
        'web_page_js_file_path': "", 
        'word_head_section_contents': "",
        'additional_html': "",
        'body': "",
        'header_bar': "",
        'table_of_contents': "",
        'document_text': "",
        'document_text_trailer': ""
    }

    ####################
    # Call the functions that process the input files
    # and that construct the WWN web-page's HTML-sections
    # * The functions are in separate files
    ####################

    #
    # Call load_input_parameter_file()
    #
    # * The input parameter-file is in YAML format
    # * The file's contents are verified and loaded into a Python
    #   object, made-up of dictionaries and lists.
    # * That object is returned in the variable loaded_parms
    return_value, loaded_parms = load_input_parameter_file(parameter_file_path)
    if (return_value == 1):
        return 1, num_warning_messages
 
    #
    # Call load_html_files()
    #
    # * Verifies the HTML-related input-files, and the output directory
    # * Returns 4 objects and a string variable, which are described below.
    return_value, returned_objects_dict = load_html_files(loaded_parms)
    if (return_value == 1):
        return 1, num_warning_messages
    else:
        # Data is returned in the dictionary returned_objects_dict[]
        
        # The Jinja template is loaded from a file, and returned in jinja_template
        # * jinja_template is a jinja2 object, created by calling jinja2.Template() 
        jinja_template = returned_objects_dict["jinja_template"]
        
        # The input Word HTML-file is loaded, and it is returned in BeautifulSoup objects:
        #
        # head is a BeautifulSoup object
        # * It holds the <head> element from the input HTML-file
        head = returned_objects_dict["head"]
        # body is a BeautifulSoup object
        # * It holds the <body> element from the input HTML-file
        body = returned_objects_dict["body"]
        
        # The output HTML-file is created, and it is currently empty:
        output_html_file_path = returned_objects_dict["output_html_file_path"]
        output_html_file_handle = returned_objects_dict["output_html_file_handle"]
    
    #
    # Call copy_words_embedded_files()
    #
    # * Copies Word's embedded files
    # * If the input Word HTML-file has embedded-files, they are copied to 
    #   the output directory
    return_value = copy_words_embedded_files(loaded_parms)
    if (return_value == 1):
        return 1, num_warning_messages

    #
    # Call construct_html_sections()
    #
    # * Constructs the output HTML-sections, and puts them in:
    #   * BeautifulSoup object: body_inner_html
    #   * The dictionary jinja_template_variables
    return_value, body_inner_html = construct_html_sections(loaded_parms, jinja_template_variables, head, body)
    if (return_value == 1):
        return 1, num_warning_messages

    #
    # Call fix_word_html()
    #
    # * Fixes a set of known bugs in Word's HTML
    #
    # * Parameters:
    #   * Input:  loaded_parms, jinja_template_variables, body_inner_html, num_warning_messages
    #   * Output:
    #     * jinja_template_variables : the document-text's HTML is added, with the fixes applied
    return_value, num_warning_messages = fix_word_html.fix_word_html(loaded_parms, jinja_template_variables, body_inner_html, num_warning_messages)
    if (return_value == 1):
        return 1, num_warning_messages


    ################
    # Create the output WWN web-page
    ################
    # The web-page is created from the Jinja template and template-variables.
    print("INFO.  Generating the output HTML, using the HTML-template.")
    generated_html = jinja_template.render(jinja_template_variables)

    # Write the web-page to the output HTML-file
    print("INFO.  Writing the output HTML, to the output HTML-file:")
    print("       " + output_html_file_path)
    try:
        output_html_file_handle.write(generated_html)
        output_html_file_handle.close()
    except IOError as e:
        print("")
        print("ERROR.  Could not write-to or close the output HTML-file.")
        print("        %s - %s." % (e.strerror, e.filename))
        return 1, num_warning_messages

    print("")
    print("INFO.  Processing completed.  No errors.  Warning messages: " +
          str(num_warning_messages))

    return 0, num_warning_messages
# END of: create_web_page_core()


'''
###########################
Function: create_web_page()

* create_web_page() is a wrapper for calling create_web_page_core().
* This wrapper makes it possible for create_web_page_core() to simply return if it encounters any errors.
###########################
'''
def create_web_page(parameter_file_path):
    num_warning_messages = 0
    
    # Check Python version 3
    # * https://docs.python.org/2.7/library/sys.html#sys.version_info
    if sys.version_info[0] < 3:
        # Pylance incorrectly flags this code as unreachable
        # * https://github.com/microsoft/pylance-release/issues/470
        print("")
        print("ERROR.  Python version 3 is required.")
        print("        WordWebNav has been tested with Python 3.7.0 and 3.9.6")
        print("")    
        sys.exit()

    # Check Python version is at least 3.7
    if sys.version_info[1] < 7:
        num_warning_messages += 1
        print("")
        print("WARNING.  Python version is less than 3.7.")
        print("          WordWebNav has been tested with Python 3.7.0 and 3.9.6")   
        print("")    
    
    # Call create_web_page_core(), to create the WWN web-page for the input Word HTML-file
    return_value, num_warning_messages = create_web_page_core(parameter_file_path, num_warning_messages)
    if return_value == 1:
        print("")
        print("INFO.  Error encountered, processing not completed.  Error messages: 1.  Warning messages: " + str(num_warning_messages))
        print("")        

    return return_value, num_warning_messages
# END OF: create_web_page()

'''
################
Function:  create_arg_parser()
################
* Creates and returns the ArgumentParser object
* Argparse is used to process the command-line argument 
  * Argparse docs: https://docs.python.org/3/library/argparse.html
  * The argparse code here is from:  https://stackoverflow.com/questions/14360389/getting-file-path-from-command-line-argument-in-python/47324233
'''
def create_arg_parser():
    parser = argparse.ArgumentParser(description=
        'Converts a Word HTML-file to a usable web-page.')
    # * One positional argument, and it is optional
    # * https://stackoverflow.com/questions/4480075/argparse-optional-positional-arguments/31243133
    parser.add_argument('parameter_file_path', nargs='?', metavar="<parameter-file-path>",
                    help='Full-path to the parameter-file.')
    return parser
# END OF:  def create_arg_parser()

'''
#############
Command-line interface
#############
'''
if __name__ == "__main__":
    # Get the parameter-file path from the command-line
    # * argparser also verifies the command-line syntax
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args()
    parameter_file_path = parsed_args.parameter_file_path

    # * If a parameter-file-path was not provided on the command-line,
    #   then prompt for it
    if parameter_file_path == None:
        prompted_for_parameter_file = True
        parameter_file_path = input("Enter parameter-file path: ").strip()
        if parameter_file_path == "":
            print("")
            print("ERROR.  Parameter-file path not provided.")
            print("")    
            sys.exit()
    else:
        prompted_for_parameter_file = False

    # Create the WWN web-page
    create_web_page(parameter_file_path)

    # If the command-window would close at program exit, then prompt for a key-press:
    # * If the program was called by clicking on it, the command window will close 
    #   when the program exits, and the program's messages will not be viewable.
    # * Determining if the program was called by clicking on it is non-trivial.
    # * If the program was called by clicking on it, the user will be prompted for
    #   the parameter-file.
    # * So, check if the user was prompted for the parameter-file.
    if prompted_for_parameter_file == True:
        print("")
        input("Press any key to exit.")
        print("")
