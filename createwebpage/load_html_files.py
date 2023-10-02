'''
################
This file contains the function: load_html_files()

The function is called by: create_web_page_core() in create_web_page.py

MIT License, Copyright (c) 2021-present Jim Yuill
################
'''

import re
import sys
import os
# Specifies the YAML keys for the input parameter-file
from input_parameter_file_keys import *

# These libraries need to have been installed by the user
try:
    '''
    HTML-related libraries
    '''
    # BeautifulSoup:  pip install beautifulsoup4
    from bs4 import BeautifulSoup
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


def load_html_files(loaded_parms):
    '''
    Description:
    * Open the jinja template-file, and create a jinja-template object
    * Open the input Word-HTML-file, and load it into Beautiful Soup objects
    * Create and open the output HTML-file

    Return:
    * 1, None : Error
    * 1, returned_objects_dict : Returns a dictionary with the objects that were created.
                                Specified at the end of this function.
    ################
    '''

    # Name of WWN's jinja-template file
    # * It's in the same directory as the present file.
    JINJA_TEMPLATE_FILE_NAME = "jinja_template.html"

    ###################
    # Open the jinja template-file, and use Jinja2 to create a jinja-template object
    ###################
 
    # Get the path to the WWN jinja template-file.
    scripts_directory = os.path.dirname(os.path.realpath(__file__))
    jinja_template_file_path = os.path.join(scripts_directory, JINJA_TEMPLATE_FILE_NAME)

    print("INFO.  Opening the jinja template-file, and loading it:")
    print("       " + jinja_template_file_path)
    try:
        jinja_template_file_handle = open(jinja_template_file_path)
    except IOError as e:
        print("")
        print("ERROR.  Could not open the expected jinja template-file.")
        print("        %s - %s." % (e.strerror, e.filename))
        return 1, None
  
    jinja_template_file_data = jinja_template_file_handle.read()
    jinja_template_file_handle.close()

    # Verify the jinja tempate-file has the expected signature:
    # Regex pattern tested and explained:  https://regex101.com/r/EZTpUo/2/
    jinja_template_file_signature = "<meta name=Generator content=\"WordWebNav, version {{version}}\">"
    regex = r"<meta\s+name=Generator\s+content=\"WordWebNav, version {{version}}\">"
    search_result = re.search(regex, jinja_template_file_data, (re.M | re.S))
    if search_result == None:
        print("")
        print("ERROR.  The jinja template-file does not have the expected signature:")
        print("        " + jinja_template_file_signature)
        return 1, None

    # Load the jinja template-file, as a Jinja-template object
    # * This load technique will break if there is template inheritance, but it's not used here.
    # * There are techniques that don't break, but they are more complicated.
    # * https://stackoverflow.com/questions/38642557/how-to-load-jinja-template-directly-from-filesystem
    jinja_template = Template(jinja_template_file_data)


    ####################
    # Open the input Word-HTML-file, and load it into BeautifulSoup objects.
    ####################
 
    input_html_path_value = loaded_parms[YML_KEY_REQUIRED][YML_KEY_INPUT_HTML_PATH]
    print("INFO.  Opening the input Word-HTML-file:")
    print("       " + input_html_path_value)
    try:
        input_html_handle = open(input_html_path_value)
    except IOError as e:
        print("")
        print("ERROR.  Could not open the input Word-HTML-file.")
        print("        %s - %s." % (e.strerror, e.filename))
        return 1, None    

    # * BeautifulSoup may fail to load the HTML due to the HTML using an
    #   unrecognized encoding.
    try:
        soup = BeautifulSoup(input_html_handle, 'html.parser')
    except Exception as error:
        print("")
        print("ERROR.  Could not load the input Word HTML-file.")
        print("        Exception in call to BeautifulSoup:")
        print("")
        print(str(error))
        return 1, None    
    finally:
        input_html_handle.close()


    #########################
    # * Verify the Word-HTML has the expected HTML elements
    # * Also, get the HTML head and body sections, as BeautifulSoup objects
    ##########################

    # Veryify that the HTML has excatly one <head> element
    heads = soup.find_all('head')
    if len(heads) != 1:
        print("")
        print("ERROR.  The input Word-HTML does not have exactly one <head> element.")
        return 1, None
    head = heads[0]

    # There should be exactly one <body> element
    bodys = soup.find_all('body')
    if len(bodys) != 1:
        print("")
        print("ERROR.  The input Word-HTML does not have exactly one <body> element.")
        return 1, None
    body = bodys[0]

    # Check for expected <div> sections
    # * There can be multiple <div> sections
    # * If there are none, it's just reported as an INFO message
    divs = soup.find_all('div')
    if len(divs) == 0:
        print("")
        print("INFO.  The input Word-HTML does not have <div> sections. ")
    else:
        # Check for expected <div> section
        div = soup.find('div', class_="WordSection1")
        if (div == None):
            print("INFO.  The input Word-HTML does not have the div section: " +
                  "<div class=WordSection1>")

    # Check the HTML <head> section for this MS Word signature:
    # * <meta name=Generator content="Microsoft Word [version] (filtered)">
    # The signature appears to be used back to at least Word 2007:
    # * https://answers.microsoft.com/en-us/msoffice/forum/msoffice_word-mso_winother-msoversion_other/creating-html-with-word-2007/5d344731-d2f3-4568-b504-45256567f782
    signature_found = False
    meta_found = soup.head.find('meta', attrs={'name': 'Generator'})
    if (meta_found != None) and ('content' in meta_found.attrs):
        meta_content = meta_found['content']
        regex = r"^Microsoft Word [0-9]+ \(filtered\)$"
        search_result = re.search(regex, meta_content, re.M)
        if search_result != None:
            signature_found = True

    if signature_found == False:
        print("")
        print("ERROR.  The input Word-HTML does not have the expected MS-Word signature:")
        print("        <meta name=Generator content=\"Microsoft Word [version] (filtered)\">")
        print("")        
        return 1, None


    #################
    # Test that the output directory exists
    #################
 
    output_directory_path_value = loaded_parms[YML_KEY_REQUIRED][YML_KEY_OUTPUT_DIRECTORY_PATH]
    # * os.path.normpath() will remove any trailing "/".  
    #   This is needed later, e.g., for os.path.dirname
    output_directory_path = os.path.normpath(output_directory_path_value)
    if not os.path.exists(output_directory_path):
        print("")
        message = "ERROR.  The specified output-directory does not exist: " + output_directory_path_value
        print(message)                  
        return 1, None


    ###############
    # Create and open the output HTML-file
    ###############
 
    key_input_html_file_path_value = loaded_parms[YML_KEY_REQUIRED][YML_KEY_INPUT_HTML_PATH]
    file_name = os.path.basename(key_input_html_file_path_value)
    output_html_file_path = os.path.join(output_directory_path_value, file_name)
    print("INFO.  Creating the output HTML-file:")
    print("       " + output_html_file_path)
    # Test if the output HTML-file already exists in the output directory
    if os.path.exists(output_html_file_path):
        print("INFO.  For the output HTML-file, there is an existing file with the same name. " + 
              "It will be overwritten:")
        print("       " + output_html_file_path)
  
    try:
        # If there is an existing file, it will be overwritten
        # * encoding="utf-8"
        #   * Use from:  
        #     https://stackoverflow.com/questions/27092833/unicodeencodeerror-charmap-codec-cant-encode-characters
        #   * Fixes exception in processing test file: 
        #     * MS-tutorial--Deep Learning for Signal and Information Processing.htm
        #     * https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/Final-DengYu-NOW-Book-DeepLearn2013-ForLecturesJuly2.docx
        #   * Error when writing final HTML to file:
        #     * UnicodeEncodeError: 'charmap' codec can't encode character '\ufb01' in position 131432: character maps to <undefined>
        output_html_file_handle = open(output_html_file_path, "w", encoding="utf-8")
    except OSError as e:
        print("")
        print("ERROR.  Could not open the output HTML-file.")
        print("        %s - %s." % (e.strerror, e.filename))
        return 1, None    


    ################
    # Return the objects that were created
    ################

    returned_objects_dict = { 
        # jinja_template is a jinja2 object, created by calling jinja2.Template()
        "jinja_template" : jinja_template,
        # head is a BeautifulSoup object
        # * It holds the <head> element from the input HTML-file
        "head" : head,
        # body is a BeautifulSoup object
        # * It holds the <body> element from the input HTML-file
        "body" : body, 
        # The output HTML-file:
        "output_html_file_path" : output_html_file_path,
        "output_html_file_handle" : output_html_file_handle }

    return 0, returned_objects_dict

# END of: load_html_files()