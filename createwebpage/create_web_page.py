#!/usr/bin/env python
'''
DESCRIPTION:  Converts a Word HTML-file into a WordWebNav (WWN) web-page

USAGE:  
* From the Windows command-line:  
> cd <directory with create_web_page.py>
> python create_web_page.py <full-path of parameter-file>

* If <full-path of parameter-file> is omitted, the user is prompted for it.

* The parameter-file includes specification of the input Word HTML-file,
  and the directory for the output WWN web-page.
* A parameter-file template is provided with the system distribution.

* The system documentation has additional info on its: installation, use, design 
  and implementation (code).

MIT License, Copyright (c) 2021-present Jim Yuill

'''

# Python pre-installed libraries
import argparse
from html.parser import HTMLParser
import os
import re
import shutil
import sys 

# These libraries need to have been installed by the user
try:
    '''
    YAML-related libraries
    '''
    # Cerberus:  pip install cerberus
    from cerberus import Validator
    # pprint++:  pip install pprintpp
    import pprintpp 
    # PyYAML:  pip install PyYAML
    import yaml
    # yamllint:  pip install yamllint
    import yamllint
    from yamllint.config import YamlLintConfig
    '''
    HTML-related libraries
    '''
    # BeautifulSoup:  pip install beautifulsoup4
    from bs4 import BeautifulSoup, NavigableString, Tag
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

# Check Python version 3
# * Works with Python 2.6 and below:
#   * https://stackoverflow.com/questions/446052/how-can-i-check-for-python-version-in-a-program-that-uses-new-language-features
if sys.version_info[0] < 3:
    print("")
    print("ERROR.  Python version 3 is required.")
    print("        WordWebNav has been tested with Python 3.7.0 and 3.9.6")
    print("")    
    sys.exit()

'''
##################
Code Section: Global constants and variables
##################
'''

'''
##################
Global variables
##################
'''
num_warning_messages_g = 0
list_item_list_g = []

# Check Python version is at least 3.7
if sys.version_info[1] < 7:
    num_warning_messages_g += 1
    print("")
    print("WARNING.  Python version is less than 3.7.")
    print("          WordWebNav has been tested with Python 3.7.0 and 3.9.6")   
    print("")    

'''
##################
Global constants
##################
'''
# Text added to the generated HTML
# * For the web-page header-bar, specifies the separator between
#   breadcrumbs, e.g., the " / " in:  Home / Topic-1 / Topic-1.1 
BREAD_CRUMB_SEPARATOR = " / "
# For the document-text trailer, specifies the anchor name.
# * The anchor name can be linked-to from the web-page header-bar.
DOCUMENT_TEXT_TRAILER_ANCHOR_NAME = "word_web_nav_document_text_trailer"

# Names of WordWebNav files that are opened or referenced
YAMLLINT_CONFIG_FILE_NAME = "yamllint_config_file.yml"
PAGE_STRUCTURE_CSS_FILE_NAME = "word_web_nav.css"
JS_FILE_NAME = "word_web_nav.js"
JINJA_TEMPLATE_FILE_NAME = "jinja_template.html"

'''
CSS classes that are referenced in some of the HTML that is generated.
* The classes are defined in the CSS-file whose name is specified above, in the variable: 
  PAGE_STRUCTURE_CSS_FILE_NAME
'''
CSS_HEADER_BAR_TEXT = "headerBarText"
CSS_HEADER_BAR_HREF = "headerBarHref"

'''
Schema definitons, for the parameter-file.
* The parameter-file is in YAML formt.
* The parameter-file is validated by calling Cerberus.
* These schema-definitions are used by Cerberus, to validate the parameter-file.

* These schema-definitons specify the parameter-file's structure, keys, and values.
  * The parameter-file is specified and described in the system documentation, using prose.
  * These schema-definitons specify the parameter-file syntax that is described in the 
    system documentation.
* Since Cerberus validates the parameter-file, the code that processes the parameter-file
  assumes valid syntax, e.g., that required keys are present.
'''
# Parameter-file key-name definitions
# * These constants define the names of the YAML keys in the parameter-file

KEY_REQUIRED = "required"
KEY_VERSION = "version"
KEY_INPUT_HTML_PATH = "input_html_path"
KEY_OUTPUT_DIRECTORY_PATH = "output_directory_path"
KEY_SCRIPTS_DIRECTORY_URL = "scripts_directory_url"

KEY_HTML_HEAD_SECTION = "html_head_section"
KEY_TITLE = "title"
KEY_DESCRIPTION = "description"
KEY_ADDITIONAL_HTML = "additional_html"

KEY_HEADER_BAR = "header_bar"
KEY_SECTION = "section"
KEY_CONTENTS = "contents"

KEY_BREADCRUMBS = "breadcrumbs"
KEY_TEXT = "text"
KEY_URL = "url"

KEY_HYPERLINK = "hyperlink"
KEY_HTML = "html"
KEY_EMPTY = "empty"

KEY_CONTENTS_ALIGNMENT = "contents_alignment"
LEFT = "left"
RIGHT = "right"
CENTER = "center"
JUSTIFY = "justify"

KEY_DOCUMENT_TEXT_TRAILER = "document_text_trailer"

KEY_WORD_HTML_EDITS = "word_html_edits"
KEY_WHITE_COLORED_TEXT = "white_colored_text"
# The allowable values for the key "white_colored_text"
DO_NOT_REMOVE = "doNotRemove"
REMOVE_IN_PARAGRAPHS = "removeInParagraphs"
REMOVE_ALL = "removeAll"

# The schema-definition
PARAMETER_FILE_SCHEMA = {

    # Parameter-file section:  required:
    # Example:
    #   required:
    #     version: "1.0"
    #     input_html_path: D:\Documents\Professional-projects\My-web-site-development\Word-to-HTML\automation-dev\testing\test-Word-files\test-Word-files\tests-for-create_web_page_py\WordWebNav--Word-HTML\all-primary-Word-features.html
    #     output_directory_path: D:\Documents\Professional-projects\My-web-site-development\Word-to-HTML\automation-dev\testing\test-Word-files\test-Word-files\tests-for-create_web_page_py\WordWebNav--HTML
    #     scripts_directory_url: D:\Documents\Professional-projects\My-web-site-development\Word-to-HTML\WordWebNav\word_web_nav\assets
    KEY_REQUIRED: {
        "type": "dict",
        "required": True,
        "schema": {
            KEY_VERSION: {
                "type": "string",
                "required": True,
                "minlength": 1
            },
            KEY_INPUT_HTML_PATH: {
                "type": "string",
                "required": True,
                "minlength": 1                
            },
            KEY_OUTPUT_DIRECTORY_PATH: {
                "type": "string",
                "required": True,
                "minlength": 1                
            },
            KEY_SCRIPTS_DIRECTORY_URL: {
                "type": "string",
                "required": True,
                "minlength": 1                
            }
        }
    },

    # Parameter-file section:  html_head_section:
    # Example:
    #   html_head_section:
    #     title: Sys-Admin How-To Info
    #     description: Solutions for my various sys-admin tasks
    #     additional_html: <link rel="icon" type="image/png" href="/favicon-32x32.png" sizes="32x32" />    
    KEY_HTML_HEAD_SECTION: {
        "type": "dict",
        "required": False,
        "schema": {
            KEY_TITLE: {
                "type": "string",
                "required": False,
                "minlength": 1                
            },
            KEY_DESCRIPTION: {
                "type": "string",
                "required": False,
                "minlength": 1                
            },
            KEY_ADDITIONAL_HTML: {
                "type": "string",
                "required": False,
                "minlength": 1                
            }
        }
    },

    # Parameter-file section:  header_bar:
    # Example:
    #  header_bar:
	#    # One or more sections
    #    - section:
    #        contents:
    #          # Exactly one of the following keys:
    #          breadcrumbs:
    #            # One or more hyperlinks 
    #            - hyperlink:
    #                text: Home
    #                url: http://jimyuill.com
    #          text:
    #          html:
    #          empty:
    #
    #        contents_alignment:
    KEY_HEADER_BAR: {
        "type": "list",
        "required": False,
        "schema": {
            "type": "dict",
            "schema": {
                KEY_SECTION: {
                    "type": "dict",
                    "schema": {
                        KEY_CONTENTS: {
                            "type": "dict",
                            "required": True,
                            # Only one entry allowed in dict
                            "maxlength" : 1, 
                            "schema" : {
                                KEY_BREADCRUMBS: {
                                    # * This entry is a list, and 
                                    #   each list-member specifies a hyperlink
                                    "type": "list",
                                    "required": False,
                                    "schema": {
                                        "type": "dict",
                                        "schema": {
                                            KEY_HYPERLINK : {
                                                "type": "dict",
                                                "schema": {
                                                    KEY_TEXT: {
                                                        "type": "string",
                                                        "required": True,
                                                        "minlength": 1
                                                    },
                                                    KEY_URL: {
                                                        "type": "string",
                                                        "required": True,
                                                        "minlength": 1                            
                                                    }
                                                }
                                            }
                                        }
                                    }
                                },

                                KEY_HYPERLINK : {
                                    "type": "dict",
                                    "required": False,
                                    "schema": {
                                        KEY_TEXT: {
                                            "type": "string",
                                            "required": True,
                                            "minlength": 1            
                                        },
                                        KEY_URL: {
                                            "type": "string",
                                            "required": True,
                                            "minlength": 1            
                                        }
                                    }
                                },

                                KEY_TEXT : {
                                    "type": "string",
                                    "required": False,
                                    "minlength": 1
                                },

                                KEY_HTML : {
                                    "type": "string",
                                    "required": False,
                                    "minlength": 1
                                },

                                KEY_EMPTY : {
                                    "type": "string",
                                    "required": False,
                                    "maxlength" : 0,   # Ensures no value is specified
                                    "nullable": True   # Allows key to have no value
                                }
                            }
                        },

                        KEY_CONTENTS_ALIGNMENT: {
                            "type": "string",
                            "required": False,
                            "allowed": ["left", "right", "center", "justify"]
                        }
                    }
                }
            }
        }
    },

    # Parameter-file section:  document_text_trailer:
    # Example:
    #   document_text_trailer: |
    #     <div id="commento"></div>
    #     <script defer
    #       src="https://cdn.commento.io/js/commento.js">
    #     </script>
    KEY_DOCUMENT_TEXT_TRAILER: {
        "type": "string",
        "required": False,
        "minlength" : 1
    },

    # Parameter-file section:  word_html_edits:
    # Example:
    #   word_html_edits:
    #     white_colored_text: removeAll
    KEY_WORD_HTML_EDITS: {
        "type": "dict",
        "required": False,
        "schema": {
            KEY_WHITE_COLORED_TEXT: {
                "type": "string",
                "required": False,
                "allowed": [DO_NOT_REMOVE, REMOVE_IN_PARAGRAPHS, REMOVE_ALL]
            }
        }
    }
}

"""
##################
* Constants and variables used in editing the Word-HTML, 
  to fix Word-HTML bugs in ordered-lists and unordered-lists.
##################
"""

'''
* Among the Word-HTML bugs that are fixed, some of the bugs are fixed by replacing a 
  particular string within an HTML paragraph.
* The replacement process is the same for each of those bugs, but the data differs.
* The replacement process is coded within two functions: fix_unordered_list_items() and generate_html().
* The data used by those replacement-processes is defined here.
'''

'''
Create the data-structures (dictionaries) and constants
'''

# Defines the keys used in the dictionary HTML_ENTITY_ENCODING_SPECS
KEY_DESCRIPTION = "description"
KEY_ENCODE = "encode"
KEY_DECODE = "decode"
KEY_NUMBER_ENCODED = "number_encoded"

# A dictionary used to store the data used to fix a particular bug
HTML_ENTITY_ENCODING_SPECS = {
    KEY_DESCRIPTION: "",  # Constant, used in console messages
    KEY_ENCODE: "",  # Constant, specifies the new HTML, within a script tag
    KEY_DECODE: "",  # Constant, specifies the new HTML, without the script tag
    KEY_NUMBER_ENCODED: 0  # Variable, specifies the number of instances of the fix
}

# Defines the keys used in the dictionary html_entity_encodings_g
KEY_SOLID_DOT_BULLET = "solid_dot_bullet"
KEY_SOLID_SQUARE_BULLET = "solid_square_bullet"
KEY_LETTER_O_BULLET = "letter_o_bullet"
KEY_SIX_NBSPS = "six_nbsps"

# * html_entity_encodings_g is a dictionary.
#   * The suffix "_g" indicates the dictionary is a global variable.
#   * Each entry specifies the HTML used to fix a particular bug in
#     the Word-HTML.
#   * Each entry's value is itself a dictionary.  
#     * The value is initialized to be a copy of HTML_ENTITY_ENCODING_SPECS.
html_entity_encodings_g = {
    KEY_SOLID_DOT_BULLET: HTML_ENTITY_ENCODING_SPECS.copy(),
    KEY_SOLID_SQUARE_BULLET: HTML_ENTITY_ENCODING_SPECS.copy(),
    KEY_LETTER_O_BULLET: HTML_ENTITY_ENCODING_SPECS.copy(),
    KEY_SIX_NBSPS: HTML_ENTITY_ENCODING_SPECS.copy()
}

# * The fixes to the Word-HTML involve replacing HTML strings with particular
#   HTML entities.
# * Those replacement HTML-entities are put inside script opening and closing tags,
#   which are defined here.
SCRIPT_OPENING_TAG = "<script type=\"word_web_page_nav\">"
SCRIPT_CLOSING_TAG = "</script>"

'''
The dictionary "html_entity_encodings_g" is filled with the bug-fix data.
'''

# Fix for solid-dot bullet-symbols
html_entity_encodings_g[KEY_SOLID_DOT_BULLET][KEY_DESCRIPTION] = \
    "solid-dot bullet-symbols (used in levels 1,4,7)"
html_entity_encodings_g[KEY_SOLID_DOT_BULLET][KEY_ENCODE] = \
    SCRIPT_OPENING_TAG + "&#9679;" + SCRIPT_CLOSING_TAG   
html_entity_encodings_g[KEY_SOLID_DOT_BULLET][KEY_DECODE] = "&#9679;"

# Fix for solid-square bullet-symbols
html_entity_encodings_g[KEY_SOLID_SQUARE_BULLET][KEY_DESCRIPTION] = \
    "solid-square bullet-symbols (used in levels 3,6,9)"
html_entity_encodings_g[KEY_SOLID_SQUARE_BULLET][KEY_ENCODE] = \
    SCRIPT_OPENING_TAG + "&#9632;" + SCRIPT_CLOSING_TAG   
html_entity_encodings_g[KEY_SOLID_SQUARE_BULLET][KEY_DECODE] = "&#9632;"

# For letter "o" bullet-symbols, specify no fix is needed for the bullet-symbol
html_entity_encodings_g[KEY_LETTER_O_BULLET][KEY_DESCRIPTION] = \
    "letter \"o\" bullet-symbols (used in levels 2,5,8)"
html_entity_encodings_g[KEY_LETTER_O_BULLET][KEY_ENCODE] = ""   
html_entity_encodings_g[KEY_LETTER_O_BULLET][KEY_DECODE] = ""

# Fix for spacing after a bullet-symbol (unordered list), or list-item symbol (ordered-list).
html_entity_encodings_g[KEY_SIX_NBSPS][KEY_DESCRIPTION] = "list-item spacing"
html_entity_encodings_g[KEY_SIX_NBSPS][KEY_ENCODE] = \
    SCRIPT_OPENING_TAG + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + SCRIPT_CLOSING_TAG   
html_entity_encodings_g[KEY_SIX_NBSPS][KEY_DECODE] = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"


'''
#########
Code Section:  Functions called from generate_html()
#########
'''

'''
Function:  create_arg_parser()
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

"""
Function: test_if_span_with_only_spaces()
* For the input HTML-elemement, determine if it's a span tag, with
  a single string made-up of only spaces
"""
def test_if_span_with_only_spaces(element):
    # Have to use .decode() to get the "&nbsp;"s
    if ( isinstance(element, Tag) and (element.name == "span") and
       ('style' in element.attrs) and (len(element.contents) == 1) ):

        span_html_str = element.decode(formatter='html')
        regex = r"^<span[^>]*?>(?:\s*?(?:&nbsp;)\s*?)+</span>$"
        search_result = re.search(regex, span_html_str, re.M)
        if search_result != None:
            return True

    return False
# END OF:  def test_if_span_with_only_spaces()

'''
###########################
Function: fix_unordered_list_items()
###########################
'''

'''
This function fixes commonly-found bugs in Word-HTML, for unordered-lists.

* Terminology
  * An unordered list is made-up of list-items.
    * For the list-items, three types of bullet-symbols are typically used:
      * solid-dot, solid-square, and the letter "o"

* The function's parameters specify:
  * The bullet-symbol of the list-item to be fixed, e.g., a round dot
    * It's specified by the parameters "font_family" and "symbol"
  * The HTML needed to fix the bullet-symbol, if it needs to be fixed.
    * The parameter "html_entity_encodings_key" is a key for the dictionary html_entity_encodings_g.
    * In the dictionary, that key's value has the HTML for fixing the bug.
      If no fix is needed, the empty string is specified.

* The function examines each candidate list-item in the Python list "list_item_list_g".
  * list_item_list_g is a global variable, and it's described elsewhere in this program.
  * In HTML, a list-item is specified as a paragraph (<p ...> ... </p>)
  * If a list-item is for an unordered-list, and it has the specified bullet-symbol, 
    then the list-item's HTML is edited, to fix its bugs.

* The bug-fixes just described involve replacing HTML strings with HTML entities.
  * The replacements are done in the BeautifulSoup HTML.
  * During the replacement, BeautifulSoup itself can potentially alter those HTML entities,
    in undesirable ways.
  * To prevent BeautifulSoup from making those alternations, the replacement HTML entities
    are put insides of an HTML <script> tag, e.g., <script>[replacement HTML entities]</script>.
  * Later in the present program, the BeautifulSoup HTML will be converted to HTML text.  
    Those added opening and closing script tags will be removed then, from the HTML text.

* The Word-HTML bugs, and their fixes, are further described in the system documentation. 
'''
def fix_unordered_list_items(font_family: str, 
                             symbol: str, 
                             html_entity_encodings_key: str):

    global list_item_list_g, html_entity_encodings_g

    list_elements_to_remove = []

    symbol_replace_count = 0
    bullets_fixed_count = 0
    # Loop for each HTML paragraph in list_item_list_g
    for list_item_list_index in range(0, len(list_item_list_g)):
        '''
        * Determine if the paragraph is an unordered-list list-item, 
          and if it has the required bullet-symbol.
        '''
        
        # A list-item paragraph will have at least two strings
        paragraph = list_item_list_g[list_item_list_index]
        paragraph_strings = paragraph.find_all(string=True)
        if len(paragraph_strings) < 2:
            continue
        
        # Test that the first string is the required bullet-symbol
        first_string = paragraph_strings[0]
        if (first_string.string != symbol):
            continue

        # For the bullet-symbol, test if its parent is an HTML span tag with the attribute 'style'
        first_string_parent = first_string.parent
        if not ( isinstance(first_string_parent, Tag) and (first_string_parent.name == 'span') and 
                 ('style' in first_string_parent.attrs) ):
            continue

        # For the style attribute, test that it contains the required font-family specification
        style = first_string_parent.attrs['style']
        regex = r"(?:^|;)" + r"font-family:" + font_family + r"(?:$|;)"
        result = re.search(regex, style, re.M)
        if result == None:
            continue

        # Test if the second string is all spaces ("&nbsp;"), within an enclosing span tag
        second_string = paragraph_strings[1]
        second_string_parent = second_string.parent
        if not test_if_span_with_only_spaces(second_string_parent):
            continue

        # Test if the spaces' enclosing span tag is a child of the bullet-symbol's parent
        if not (first_string_parent is second_string_parent.parent):
            continue
            
        '''
        Make needed fixes to the HTML
        '''

        # Replace the bullet symbol, if needed, using the HTML defined in html_entity_encodings_g
        if (html_entity_encodings_g[html_entity_encodings_key][KEY_ENCODE] != ""):
            first_string.replace_with(
                BeautifulSoup(html_entity_encodings_g[html_entity_encodings_key][KEY_ENCODE],
                            'html.parser') )
            symbol_replace_count += 1
        
        # Replace the "&nbsp;"s, using the HTML defined in html_entity_encodings_g
        second_string.replace_with(BeautifulSoup(html_entity_encodings_g[KEY_SIX_NBSPS][KEY_ENCODE],
                            'html.parser') )
        
        # The HTML paragraph has been fixed.  Its index in list_item_list_g is recorded.
        list_elements_to_remove.append(list_item_list_index)
        bullets_fixed_count += 1

    # * For the HTML paragraphs that have been fixed, remove them from the list
    #   list_item_list_g
    # * Removing them from the list does not remove them from the BeautifulSoup HTML
    #   (i.e., they are not removed from the BeautifulSoup object "soup")
    for i in sorted(list_elements_to_remove, reverse=True):
        del list_item_list_g[i]

    print("INFO.  Editing the Word-HTML.  Fixing list-items with " +
          html_entity_encodings_g[html_entity_encodings_key][KEY_DESCRIPTION] + 
          "  Number of list-items found: " +  str(bullets_fixed_count) )
    # Record stats for fixes
    html_entity_encodings_g[html_entity_encodings_key][KEY_NUMBER_ENCODED] = symbol_replace_count
    html_entity_encodings_g[KEY_SIX_NBSPS][KEY_NUMBER_ENCODED] += bullets_fixed_count
# END OF:  def fix_unordered_list_items()

'''
#########
Code Section:  generate_html()
#########
'''
def generate_html(parameter_file_path: str):

    global list_item_list_g, html_entity_encodings_g, num_warning_messages_g

    # Variables used in the Jinja template
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

    print("INFO.  Processing the parameter-file:")
    print("       " + parameter_file_path)
    try:
        parameter_file_handle = open(parameter_file_path)
    except IOError as e:
        print("")
        print("ERROR.  Could not open the parameter-file.")
        print("        %s - %s." % (e.strerror, e.filename))
        print("")        
        return 1, num_warning_messages_g

    '''
    #######################################
    Code Section:  Parameter-file syntax verification

    * The parameter-file is in YAML format.
    * Its syntax verification is further described in the system documentation.
    #######################################
    '''

    '''
    yamllint is used to verify the parameter-file's YAML syntax. 
    '''
    print("INFO.  Verifying the parameter-file's YAML syntax. (Calling yamllint.)")
    # Call yamllint
    # * A yamllint config-file is used, which is distrubted with WordWebNav.
    # * The config-file's name is defined above in: YAMLLINT_CONFIG_FILE_NAME
    program_directory = os.path.dirname(os.path.realpath(__file__))
    yamllint_config_file_path = os.path.join(program_directory, YAMLLINT_CONFIG_FILE_NAME)
    print("INFO.  Opening the config-file for yamllint:")
    print("       " + yamllint_config_file_path)
    try:
        # YamlLintConfig():  https://github.com/adrienverge/yamllint/blob/master/yamllint/config.py
        yamllint_configuration = YamlLintConfig(file=yamllint_config_file_path)
    except IOError as e:
        print("")
        print("ERROR.  Could not open the config-file for yamllint.")
        print("        %s - %s." % (e.strerror, e.filename))
        print("")        
        parameter_file_handle.close()
        return 1, num_warning_messages_g

    # If yamllint finds errors, write them to the console and exit.
    # * The linter's error output:  https://yamllint.readthedocs.io/en/stable/development.html

    # The linter returns a generator, for the errors found.
    # * Convert the generator to a list.
    yaml_error_list = list(yamllint.linter.run(parameter_file_handle, yamllint_configuration))
    if len(yaml_error_list) > 0:
        print("")
        print("ERROR.  yamllint found syntax errors in the parameter-file.")
        print("        A reported error may be caused by a problem earlier in the file.")
        for message in yaml_error_list:
            if message.rule != None:
                yamllint_rule = str(message.rule)
            else:
                yamllint_rule = "[not specified]"
            if message.line != None:
                yaml_error_line = str(message.line)
            else:
                yaml_error_line = "[not specified]"
            if message.desc != None:
                yaml_error_description = message.desc
            else:
                yaml_error_description = "[not specified]"
            print("")
            print("ERROR.  Error on line: " + yaml_error_line)
            print("        yammllint rule-type: " + yamllint_rule)
            print("        yamllint error-description:")
            print(yaml_error_description)

        print("")
        print("INFO.  yamllint documentation: https://yamllint.readthedocs.io/en/stable/")        
        print("       yamllint rule-types: https://yamllint.readthedocs.io/en/stable/rules.html")
        parameter_file_handle.close()
        return 1, num_warning_messages_g

    '''
    PyYAML's YAML-loader is used to load the parameter-file
    '''
    # Read in the parameter-file, for use by the YAML-loader.
    # * The file-pointer is first reset to the beginning
    parameter_file_handle.seek(0)
    parameter_file_text = parameter_file_handle.read()
    parameter_file_handle.close()

    print("INFO.  Loading the parameter-file, using PyYAML's YAML-loader.")
    try:
        # Call the YAML-loader
        # * yaml.load's exceptions:  https://pyyaml.org/wiki/PyYAMLDocumentation
        loaded_parms = yaml.load(parameter_file_text, Loader=yaml.FullLoader)
    except yaml.YAMLError as e:
        print("")
        print("ERROR.  The YAML-loader was not able to load the parameter-file.")
        if hasattr(e, 'problem_mark'):
            mark = e.problem_mark
            print("        Error in the parameter-file on, or near, line: " + str(mark.line+1))
        print("        Error-message from the YAML-loader:")
        print(e)
        print("")
        print("INFO.  PyYAML documentation: https://pyyaml.org/wiki/PyYAMLDocumentation")
        return 1, num_warning_messages_g

    # This can happen if the input file just has a line "---"
    if (loaded_parms == None):
        print("")
        print("ERROR.  The YAML-loader did not load anything.")
        print("        The parameter-file appears to be in error, e.g., has no keys.")
        return 1, num_warning_messages_g

    '''
    Cerberus is used to verify the parameter-file's syntax, using a schema.
    * Schemas are defined (above) for the parameter-file's structure, keys and values.
    '''
    print("INFO.  Using Cerberus to verify the parameter-file's syntax.")
    # Create an instance of the Cerberus Validator
    cerberus_validator = Validator()
    # Validate the parameter-file, using the schema
    # * By default, Cerberus will flag keys that are not defined in the schema.
    # * Cerberus can crash with some invlaid inputs (e.g., loaded_parms == None), so use try/except.
    try:
        validation_result = cerberus_validator.validate(loaded_parms, PARAMETER_FILE_SCHEMA)
    except:
        print("")
        print("ERROR.  An exception was raised in Cerberus.")
        print("        The parameter-file is likely to be in error.")
        return 1, num_warning_messages_g

    # Check if errors were found
    if validation_result == False:
        print("")
        print("ERROR.  An error was found in the parameter-file.")
        print("        The error message is below.  It is from Cerberus.")
        print("        Cerberus's error messages can be difficult to read.")
        print("        * The error-message typically includes:")
        print("          * Specification of the relevant key-name(s), e.g., {'web_page_files': [{'output_directory_path': ...")
        print("          * Followed by an error descripton, e.g., ['null value not allowed']")
        print("        * The docs have more info on the Cerberus error messages.")
        print("")
        # The Cerberus error-message is formatted using pprint++, a pretty-printer app.
        # * pprint++ docs: https://github.com/wolever/pprintpp
        pretty_printer = pprintpp.PrettyPrinter()
        pretty_printer.pprint(cerberus_validator.errors)     
        return 1, num_warning_messages_g

    '''
    Verify the WordWebNav version that is specified in the parameter-file
    '''
    key_version_value = loaded_parms[KEY_REQUIRED][KEY_VERSION]
    if key_version_value != "1.0":
        print("")
        print( "ERROR.  Error in the parameter-file.  In section \"" + KEY_REQUIRED + \
               "\", the key \"" + KEY_VERSION + "\" has an incorrect value: " + key_version_value )
        return 1, num_warning_messages_g
    # * The version's value is put in the output HTML, in the HTML element "<meta name=Generator ...>"
    # * Jinja will be used to put key_version_value in the output HTML 
    jinja_template_variables['version'] = key_version_value

    '''
    ####################
    Code Section:  Initial file-processing

    * Verify the needed files can be opened, and the output directory exists.
    * Load the jinja template-file and the input Word-HTML-file
    * Verify the Word-HTML has the expected HTML elements
    ####################
    '''

    '''
    Open the jinja template-file, and use Jinja2 to create a template instance
    '''
    # Get the path to the WordWebNav jinja template-file.
    # * It's in the same directory as the present script.
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
        return 1, num_warning_messages_g
  
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
        return 1, num_warning_messages_g

    # Load the jinja template-file, as a Jinja template
    # * This load technique will break if there is template inheritance, but it's not used here.
    # * There are techniques that don't break, but they are more complicated.
    # * https://stackoverflow.com/questions/38642557/how-to-load-jinja-template-directly-from-filesystem
    jinja_template = Template(jinja_template_file_data)

    '''
    Open the input Word-HTML-file, and load it into a Beautiful Soup object.
    '''
    key_input_html_path_value = loaded_parms[KEY_REQUIRED][KEY_INPUT_HTML_PATH]
    print("INFO.  Opening the input Word-HTML-file:")
    print("       " + key_input_html_path_value)
    try:
        input_html_handle = open(key_input_html_path_value)
    except IOError as e:
        print("")
        print("ERROR.  Could not open the input Word-HTML-file.")
        print("        %s - %s." % (e.strerror, e.filename))
        return 1, num_warning_messages_g    

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
        return 1, num_warning_messages_g    
    finally:
        input_html_handle.close()

    '''
    * Verify the Word-HTML has the expected HTML elements
    * Also, get the HTML head and body sections, as BeautifulSoup objects
    '''

    # Veryify that the HTML has excatly one <head> element
    heads = soup.find_all('head')
    if len(heads) != 1:
        print("")
        print("ERROR.  The input Word-HTML does not have exactly one <head> element.")
        return 1, num_warning_messages_g
    head = heads[0]

    # There should be exactly one <body> element
    bodys = soup.find_all('body')
    if len(bodys) != 1:
        print("")
        print("ERROR.  The input Word-HTML does not have exactly one <body> element.")
        return 1, num_warning_messages_g
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
        return 1, num_warning_messages_g

    '''
    Test that the output directory exists
    '''
    key_output_directory_path_value = loaded_parms[KEY_REQUIRED][KEY_OUTPUT_DIRECTORY_PATH]
    # * os.path.normpath() will remove any trailing "/".  
    #   This is needed later, e.g., for os.path.dirname
    output_directory_path = os.path.normpath(key_output_directory_path_value)
    if not os.path.exists(output_directory_path):
        print("")
        message = "ERROR.  The specified output-directory does not exist: " + key_output_directory_path_value
        print(message)                  
        return 1, num_warning_messages_g

    '''
    Create and open the output HTML-file
    '''
    key_input_html_file_path_value = loaded_parms[KEY_REQUIRED][KEY_INPUT_HTML_PATH]
    file_name = os.path.basename(key_input_html_file_path_value)
    output_html_file_path = os.path.join(key_output_directory_path_value, file_name)
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
        return 1, num_warning_messages_g    


    '''
    #################################
    Code Section:  Copy the Word's embedded-files-directory to the output directory
    #################################
    '''
    # For a Word-HTML-file, Word will create a directory to hold imbedded files, such as pictures.
    # * That directory will be referred to as the "embedded-files directory".
    # * For the embedded-files directory, its name is the same as the Word-HTML-file, but with a suffix "_files"
    #   * e.g., for index.html, the embedded-files directory is index_files
    
    # For the input Word-HTML-file, if an embedded-files directory exists, copy it to the output directory.
    input_html_file_directory, input_html_file_name = os.path.split(key_input_html_path_value)
    input_html_file_name_without_extension, input_html_file_name_extension =  os.path.splitext(input_html_file_name)
    embedded_files_directory_name = input_html_file_name_without_extension + "_files"
    input_embedded_files_directory_path = os.path.join(input_html_file_directory, embedded_files_directory_name)
    output_embedded_files_directory_path = os.path.join(key_output_directory_path_value, 
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
                return 1, num_warning_messages_g

        # shutil.copytree() requires that the destination does not exist
        # * https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
        try:
            shutil.copytree(input_embedded_files_directory_path, output_embedded_files_directory_path)
        except OSError as e:
            print("")
            print("ERROR.  Could not copy the embedded-files-directory.")
            print("        %s - %s." % (e.strerror, e.filename))
            return 1, num_warning_messages_g

    '''
    #############################
    Code Section:  Create the HTML <head> section's tags and attributes 

    * The data is put in variables that will be used later in the jinja template, in the HTML <head> section.
    * The data includes whole HTML tags and attributes used in HTML tags.

    The HTML <head> section is constructed from two sources:
    * The <head> section in the input Word-HTML
    * Data provided by the caller in the parameter-file
    #############################
    '''

    '''
    Get the HTML within the <head> section of the input Word-HTML

    The elements within that <head> section include:
      * <meta> tags
      * An optional <title> tag
      * A <style> section with CSS statements:  <style><!-- ... --></style>
      * An optional <script> section:  <script><!-- ... --></script>
    '''

    # * Get the <head> section from the BeautifulSoup object, and 
    #   convert the <head> section to HTML text format
    html_string = head.decode(formatter='html')

    # Remove the tags <head> and </head>
    # regexp "\A" matches beginning of the whole string
    regex = r"\A(^\s*<head>\s*)"
    substitution = ""
    html_string, substitution_count = re.subn(regex, substitution, html_string, 0, re.M)
    if (substitution_count != 1):
        print("")
        print("ERROR.  The expected HTML <head> tag was not found.")
        return 1, num_warning_messages_g

    # regexp "\Z" matches end of the whole string
    regex = r"(\s*<\/head>\s*$)\Z"
    html_string, substitution_count = re.subn(regex, substitution, html_string, 0, re.M)
    if (substitution_count != 1):
        print("")
        print("ERROR.  The expected HTML </head> tag was not found.")
        return 1, num_warning_messages_g
    html_string += "\n"

    # Jinja will be used to put the head-section contents in the output HTML 
    jinja_template_variables['word_head_section_contents'] = html_string

    '''
    Get the data for the output HTML <head> section, from the caller's parameter-file
    '''
    # The data is specified under the key "html_head_section:""
    # Example:
    #   html_head_section:
    #     title: Sys-Admin How-To Info
    #     description: Solutions for my various sys-admin tasks
    #     additional_html: <link rel="icon" type="image/png" href="/favicon-32x32.png" sizes="32x32" />    

    # Get the data for the Jinja variable: title
    if ( (KEY_HTML_HEAD_SECTION in loaded_parms) and 
         (KEY_TITLE in loaded_parms[KEY_HTML_HEAD_SECTION]) ):
        key_title_value = loaded_parms[KEY_HTML_HEAD_SECTION][KEY_TITLE]
        title_tag = "<title>" + key_title_value + "</title>"
    else:
        title_tag = ""
    # Jinja will be used to put title_tag in the output HTML         
    jinja_template_variables['title_tag'] = title_tag

    # Get the data for the Jinja variable: description
    if ( (KEY_HTML_HEAD_SECTION in loaded_parms) and     
         (KEY_DESCRIPTION in loaded_parms[KEY_HTML_HEAD_SECTION]) ): 
        key_description_value = loaded_parms[KEY_HTML_HEAD_SECTION][KEY_DESCRIPTION] 
        meta_description_tag = "<meta name=\"description\" content=\"" + \
                             key_description_value + "\">"
    else:
        meta_description_tag = ""
    # Jinja will be used to put meta_description_tag in the output HTML
    jinja_template_variables['meta_tag_with_description'] = meta_description_tag

    # Get the data for the Jinja variable: additional_html
    if ( (KEY_HTML_HEAD_SECTION in loaded_parms) and     
         (KEY_ADDITIONAL_HTML in loaded_parms[KEY_HTML_HEAD_SECTION]) ):
        key_additional_html_value = loaded_parms[KEY_HTML_HEAD_SECTION][KEY_ADDITIONAL_HTML]
    else:
        key_additional_html_value = ""
    # Jinja will be used to put key_additional_html_value in the output HTML
    jinja_template_variables['additional_html'] = key_additional_html_value

    # Get the data for the Jinja variable: page_structure_css_file_path
    key_scripts_directory_url_value = loaded_parms[KEY_REQUIRED][KEY_SCRIPTS_DIRECTORY_URL]
    page_structure_css_file_path = os.path.join(key_scripts_directory_url_value, PAGE_STRUCTURE_CSS_FILE_NAME)
    # Jinja will be used to put page_structure_css_file_path in the output HTML
    jinja_template_variables['page_structure_css_file_path'] = page_structure_css_file_path

    # Get the data for the Jinja variable: web_page_js_file_path
    js_file_path = os.path.join(key_scripts_directory_url_value, JS_FILE_NAME)
    # Jinja will be used to put js_file_path in the output HTML
    jinja_template_variables['web_page_js_file_path'] = js_file_path

    '''
    #############################
    Code Section:  Process the Word-HTML's <body> tag:

    Get the <body> opening-tag:
    * For the <body> tag, the <body> opening-tag is just the part <body ...>
    * For the input Word-HTML, its <body> opening-tag will be used in the output HTML.
    * Get that <body> opening-tag, in HTML text format, and put it in a variable, for use later in the jinja template.

    Get the HTML within the <body>'s opening and closing tags
    * This does not include the opening and closing tags.
    * Get the HTML in a BeautifulSoup object, for use later in creating the
      output HTML.
    #############################
    '''

    # The variable "body" is a BeautifulSoup object that contains the input HTML's <body> section.
    # The following code will:
    # * Create a BeautifulSoup object "body_inner_html"
    # * For "body", the HTML within the <body> opening and closing tags will be moved to "body_inner_html"
    # * "body" will then have just the <body> opening and closing tags
    body_inner_html = BeautifulSoup("", 'html.parser')
    body_contents_list = body.contents
    for i in range(0, len(body_contents_list)):
        # .append moves the HTML element from body to body_inner_html
        body_inner_html.append(body_contents_list[0])

    # Convert the <body> opening and closing tags to HTML text format
    body_tags = body.decode(formatter='html')
    # Extract the opening tag, by removing the closing tag
    regex = r"(\s*<\/body\s*>\s*$)\Z"
    substitution = ""
    body_opening_tag, substitution_count = re.subn(regex, substitution, body_tags, 0, re.M)
    if (substitution_count != 1):
        print("")
        print("ERROR.  The expected HTML </body> tag was not found.")
        return 1, num_warning_messages_g

    # Jinja will be used to put body_opening_tag in the output HTML
    jinja_template_variables['body_opening_tag'] = body_opening_tag

    '''
    ###################
    Code Section:  Construct the HTML for the web-page header-bar

    * The web-page header-bar can be used for navigation breadcrumbs and for other text or URLs.
    * The web-page header-bar is different than the HTML <head> section.

    The HTML is put in a variable that will be used later in the jinja template.
    ###################
    '''
    '''
    The input parameter-file specifies the contents of the web-page header-bar.
    * The contents are put in an HTML table, which is put in the "header-bar" div.
    * The table has no borders and one row.    
    * The system docs provide more info on how the table is constructed
    '''
    header_bar_table = ""
    # Test if the parameter-file has the key "header_bar:"
    if (KEY_HEADER_BAR in loaded_parms):

        # Generate the opening-tag for the table 
        # * By default, the columns are made equal-width.
        # * Table attribute for the table to span the whole page-width:  width="%100"
        #   * https://stackoverflow.com/questions/539309/html-table-span-entire-width
        # * Table style value for table to be centered on page:
        #   * "margin-left:auto;margin-right:auto;"
        #   * https://www.w3schools.com/howto/howto_css_table_center.asp
        # * Table style value to create a table with no border nor margin:
        #   * "border-collapse:collapse;"
        #   * https://stackoverflow.com/questions/16427903/remove-all-padding-and-margin-table-html-and-css
        # * Table style values to format over-flow text as hidden, with elipses displayed (...)
        #   * "table-layout:fixed;"
        #   * Also need this table attribute:  width="100%"
        #   * https://stackoverflow.com/questions/43561602/add-text-overflow-ellipsis-to-table-cell
        #   * https://developer.mozilla.org/en-US/docs/Web/CSS/table-layout
        header_bar_table += '<table width="100%" ' + \
                       'style="margin-left:auto;margin-right:auto;border-collapse:collapse;table-layout:fixed;">\n'
        # Generate table-row opening tag
        header_bar_table += '<tr>\n'

        # Construct the opening tag for the table-cells (<td>)
        # * The table-cell styles include "text-align".  
        #   * The "text-align" value is specified in the parameter-file, e.g., "left", "centered", etc.
        # * Table-cell style values that create table-cells with no margin nor padding:
        #   * "padding:0;margin:0;"
        #   * https://stackoverflow.com/questions/16427903/remove-all-padding-and-margin-table-html-and-css
        # * Table-cell style values needed to format over-flow text as hidden, with elipses displayed (...)
        #   * "text-overflow:ellipsis;overflow:hidden;white-space:nowrap;""
        td_opening_tag = '<td  style="text-align:{0};padding:0;margin:0;' + \
                       'text-overflow:ellipsis;overflow:hidden;white-space:nowrap;">'

        # The header-bar contents are specified in the parameter-file, under the key KEY_HEADER_BAR
        # * Under KEY_HEADER_BAR, there are one or more "sections", e.g., KEY_BREADCRUMBS
        # * A table-cell is created for each section.
        # * The table-cell's contents are specified in the parameter-file.
        # 
        # Loop for each section under the key KEY_HEADER_BAR
        for section in loaded_parms[KEY_HEADER_BAR]:
            # Generate the opening-tag for the table cell
            if (KEY_CONTENTS_ALIGNMENT in section[KEY_SECTION]):
                table_cell_alignment = section[KEY_SECTION][KEY_CONTENTS_ALIGNMENT]
            else:
                table_cell_alignment = "left"
            header_bar_table += td_opening_tag.format(table_cell_alignment)

            # * For the section, determine its content's data-type, e.g., "breadcrumbs".
            # * And, generate the content's HTML 
            contents = section[KEY_SECTION][KEY_CONTENTS]
            # Data-type "breadcrumbs"
            if KEY_BREADCRUMBS in contents:
                breadcrumbs_html = ""
                # Loop for each "hyperlink"
                for breadcrumb in section[KEY_SECTION][KEY_CONTENTS][KEY_BREADCRUMBS]:
                    # Construct the breadcrumb:  the anchor tag (<a>) and the breadcrumb-separator
                    breadcrumbs_html += f"<a class=\"{CSS_HEADER_BAR_TEXT} {CSS_HEADER_BAR_HREF}\""
                    breadcrumbs_html += f" href=\"{breadcrumb[KEY_HYPERLINK][KEY_URL]}\">"
                    breadcrumbs_html += f"{breadcrumb[KEY_HYPERLINK][KEY_TEXT]}</a>"
                    breadcrumbs_html += BREAD_CRUMB_SEPARATOR

                # Remove the last separator
                separator_length = len(BREAD_CRUMB_SEPARATOR)
                breadcrumbs_html = breadcrumbs_html[0:-separator_length]
                header_bar_table += breadcrumbs_html

            # Data-type "hyperlink"
            elif KEY_HYPERLINK in contents:
                # Construct the anchor tag (<a>)
                hyperlink_dict = section[KEY_SECTION][KEY_CONTENTS][KEY_HYPERLINK]
                header_bar_table += f"<a class=\"{CSS_HEADER_BAR_TEXT} {CSS_HEADER_BAR_HREF}\""
                header_bar_table += f" href=\"{hyperlink_dict[KEY_URL]}\">"
                header_bar_table += f"{hyperlink_dict[KEY_TEXT]}</a>"

            # Data-type "html"
            elif KEY_HTML in contents:
                header_bar_table += section[KEY_SECTION][KEY_CONTENTS][KEY_HTML]

            # Data-type "text"
            elif KEY_TEXT in contents:
                header_bar_table += section[KEY_SECTION][KEY_CONTENTS][KEY_TEXT]

            # Data-type "empty"
            elif KEY_EMPTY in contents:
                pass

            else:
                # * This case is a system error.
                # * The parameter-file's schema-definitions should not have allowed this data-type.
                #   Cerberus would then have flagged the data-type as an error.
                print("")
                print("ERROR.  Input parameter-file has an unrecognized key under:")
                print(f"          {KEY_HEADER_BAR}: {KEY_SECTION}: {KEY_CONTENTS}:")
                print("")
                return 1, num_warning_messages_g

            # Generate the closing-tag for the table cell
            header_bar_table += "</td>\n"
        # Generate the closing-tags for the table-row and table
        header_bar_table += "</tr>\n</table>\n"

    # Jinja will be used to put header_bar_table in the output HTML
    jinja_template_variables['header_bar'] = header_bar_table

    '''
    ###################
    Code Section:  Construct the HTML for the document-text's trailer
    ###################
    '''
    # Test if the trailer was specified in the parameter-file
    trailer_html = ""
    if (KEY_DOCUMENT_TEXT_TRAILER in loaded_parms):
        # Create horizontal line
        trailer_html += "<!-- For the document-text trailer: generate the horizontal line, and the anchor tag -->\n"
        trailer_html += "<br><br><br><hr>\n"
        # * Create an anchor tag.  Use the name attribute, with the value in DOCUMENT_TEXT_TRAILER_ANCHOR_NAME.
        # * A hyperlink in the web-page header-bar can use this name to link to the document-text-trailer.
        trailer_html += "<a name=\"" + DOCUMENT_TEXT_TRAILER_ANCHOR_NAME + "\"></a>\n"
        # Get the document-text-trailer's HTML that was specified in the parameter file
        trailer_html += f"<!-- For the document-text trailer:  the HTML specified in the parameter-file is inserted here: -->\n"
        trailer_html += loaded_parms[KEY_DOCUMENT_TEXT_TRAILER]
    # Jinja will be used to put trailer_html in the output HTML
    jinja_template_variables['document_text_trailer'] = trailer_html

    '''
    #######################################################
    Code Section:  Process the Word-HTML's table-of-contents (TOC), if there is one:

    * A TOC will be processed only if it's at the beginning of the web-page.
    * Each TOC entry is an HTML paragraph (<p>)

    The TOC entries are initially in the BeautifulSoup object "body_inner_html".
    * The TOC will be displayed in a different web-page frame than the document body.
    * So, the TOC entries are removed from "body_inner_html".

    For each TOC entry:
    * The TOC entry's HTML is edited to use WordWebNav's TOC style
    * The TOC entry's HTML is appended to a string variable that holds the TOC.
    * That string variable will be used later in the jinja template, to 
      put the TOC HTML in the web-page section:  <div id='table-of-contents'>
      * That section is the web-page frame that displays the TOC
    #######################################################    
    '''
    # For each TOC entry, the Word-HTML looks like this:
    # * <p class=MsoToc1><span class=MsoHyperlink><a href="#_Toc68878247">Heading Name Goes Here</a></span></p>

    # For the input Word-HTML, in its <body> section, get all of the HTML paragraphs.
    # * .find_all('p') returns a list of paragraphs, and each paragraph is a BeautifulSoup object.
    all_paragraphs = body_inner_html.find_all('p')

    '''
    Skip any initial paragraphs that only contain white-space
    '''
    # * Note: 
    #   * There can be a TOC entry with just white-space, e.g., 
    #     <p class=MsoToc1>&nbsp;</p>
    #   * Such a TOC entry is not useful.  It would almost certainly have been created by mistake.
    #   * If a TOC starts with such TOC entries, they will also be removed by this code.
    regex = r'^\s*$'
    empty_paragraphs = []
    for paragraph in all_paragraphs:
        # Test if empty paragraph
        # * paragraph.string will convert HTML entities to Unicode, e.g., &nbsp; is converted to \xa0
        # * paragraph.string returns None if the element has children (in which case, the paragraph isn't empty)
        paragraph_text = paragraph.string
        if (paragraph_text == None):
            break
        else:
            # The regex pattern specifies a string of all whitespace
            result = re.search(regex, paragraph_text , re.M)
            if (result == None):
                # Paragraph text is not all whitespace
                break
            empty_paragraphs.append(paragraph)

    num_empty_paragraphs = len(empty_paragraphs)

    '''
    Get the TOC-entries' paragraphs
    '''
    toc_paragraphs = []
    regex = r'^MsoToc[1-9]$'
    # * Loop for each TOC-entry paragraph
    #   * Start with the paragraph just after the last empty paragraph
    #   * break for a paragraph that is not a TOC-entry
    for i in range(num_empty_paragraphs, len(all_paragraphs)):
        paragraph = all_paragraphs[i]
        if ( (not 'class' in paragraph.attrs) or (len(paragraph['class']) != 1) ):
            break
        # Check if the class is "MsoToc" followed by a single digit
        paragraph_class = paragraph['class'][0]
        result = re.search(regex, paragraph_class, re.M)
        if (result == None):
            break
        toc_paragraphs.append(paragraph)

    num_toc_paragraphs = len(toc_paragraphs)
    print("INFO.  Table-of-contents entries found, for use in the navigation pane: " + str(num_toc_paragraphs))

    '''
    * For the TOC-entry paragraphs found, move them from the "soup" BeautifulSoup object, 
      to the "soup_toc" BeautifulSoup object
    '''
    soup_toc = BeautifulSoup("", 'html.parser')
    if (num_toc_paragraphs > 0):
        # Delete empty paragraphs from object soup
        for i in range(0, num_empty_paragraphs):
            empty_paragraphs[i].decompose()

        # Move TOC paragraphs from the object soup to the object soup_toc
        # * .append() moves an HTML tag
        for i in range(0, num_toc_paragraphs):
            # Also move any newlines after the TOC paragraph
            # * These newlines just affect the formatting of the HTML source, 
            #   and not what is displayed on the web-page.
            newline_after_toc_paragraph = False
            element_after_toc_paragarph = toc_paragraphs[i].next_sibling
            if isinstance(element_after_toc_paragarph, NavigableString):
                text = element_after_toc_paragarph.string 
                regex = r'^\n+$'
                result = re.search(regex, text, re.M)
                if result != None:
                    newline_after_toc_paragraph = True
            soup_toc.append(toc_paragraphs[i])
            if newline_after_toc_paragraph == True:
                soup_toc.append(element_after_toc_paragarph)

    '''
    For each TOC paragraph, edit the HTML to use WordWebNav's CSS classes.
    * These classes implement WordWebNav's hyperlink style:
      * Hyperlinks are not underlined, and clicking on a link does not change its color
    '''

    # Note:  This processing does not confirm that the HTML conforms with the expected tag
    #        structure, e.g., that the anchor (<a>) is within the expected span (<span>).
    toc_entries_without_hyperlink = 0
    toc_paragraphs = soup_toc.find_all('p')
    for paragraph in toc_paragraphs:
        # Test if the paragraph has a <span> tag with the attribute class=MsoHyperlink
        span = paragraph.find('span', class_="MsoHyperlink")
        if (span != None):
            span['class'].append('tocAnchor')

        # * Usually there is just one anchor tag, but there can be more.
        # * When there are multiple anchor-tags in a TOC entry:
        #   * The anchor tags are not nested
        #   * The last anchor tag has text, and the others do not
        # * The class 'tocAnchor' is added the first anchor-tag
        #   which is an ancestor to the paragraph's first string.

        paragraph_string = paragraph.find(string=True)
        if (paragraph_string == None):
            toc_entries_without_hyperlink += 1
            continue

        for parent in paragraph_string.parents:
            if (parent.name == "a"):
                if not ('class' in parent.attrs):
                    parent['class'] = []
                parent['class'].append('tocAnchor')
                break
            elif (parent.name == "p"):
                toc_entries_without_hyperlink += 1
                break

    if toc_entries_without_hyperlink > 0:        
        print("INFO.  Table-of-contents entries without a hyperlink: " + str(toc_entries_without_hyperlink))

    # Create a string variable with the TOC entries, in HTML text-format.
    toc_html = soup_toc.decode(formatter="html")

    # Jinja will be used to put toc_html in the output HTML
    jinja_template_variables['table_of_contents'] = toc_html

    '''
    #######################################################
    Code Section:  Fix bugs in Word's HTML

    * Word's HTML has several bugs. This section fixes those bugs, if present.
    * The bugs are fixed by editing the HTML.
      * The HTML is in the BeautifulSoup object "body_inner_html".
        * body_inner_html has the HTML from the <body> section in Word's HTML, 
          but with the table-of-contents removed

    * The Word-HTML bugs fixed are:
      * Formatting problems in bulleted lists (unordered lists)
      * Formatting problems in ordered lists
      * Text whose color is incorrectly set to be white
    * The system documentation has additional info on the bugs and fixes.
    #######################################################    
    '''

    '''
    #####################
    Code Section:  Get the HTML paragraphs that are candidate list-items.
    #####################
    '''

    '''
    * List-item paragraphs:
      * For ordered and unordered lists, Word usually implements the list-items as HTML paragraphs <p>.
      * An example of the opening tag for a typical list-item paragraph:
        * <p class=MsoListParagraphCxSpMiddle style='margin-left:1.25in;text-indent:-.25in'>
      * For typical list-item paragraphs, their opening tag has these distinctive features:
        * A class attribute, with a known set of class names, e.g., MsoNormal, MsoListParagraphCxSpFirst, etc.
        * A style attribute, with a "text-indent" value
      * Paragraphs with these distinctive features are not necessarily list-items.
        * Thus, such paragraphs are "candidate" list-items. 
      * There are other ways that Word-HTML implements list-items.
        * They are described in the system-documentation, but their HTML is not edited by the system.

    * body_inner_html.find_all() creates a Python list with the HTML paragraphs that have those distinctive features
      *  Each element in the Python list is an HTML paragraph, stored as a BeautifulSoup object
      *  That BeautifulSoup object is a pointer into the original BeautifulSoup object "soup"
      *  In creating the paragraph's BeautifulSoup object, the paragraph was not removed from "soup"
    '''

    # "regex" is a reg-ex pattern used to match known class names, e.g., class=MsoNormal
    #  * These names have been observed in both ordered and unordered lists.
    #  * The only exception is the name "MsoListParagraph", which has only been observed in ordered lists.
    regex = r'(^MsoListParagraph(CxSp(First|Middle|Last))?$)|(^MsoNormal$)|(^MsoBodyText$)'
    list_item_list_g = body_inner_html.find_all('p', 
        class_=re.compile(regex, re.M), 
        attrs={'style': re.compile('text-indent:')})

    '''
    ######################
    Code Section:  Fix the list-items in unordered-lists
    ######################
    '''
    # Fix solid-dot bullet symbols, and their spacing
    # * Word's solid-dot bullet is not displayed properly by Firefox.
    #   * It is replaced here by the HTML solid-dot symbol "&#9679;"
    fix_unordered_list_items(font_family="Symbol",
                          symbol="·",
                          html_entity_encodings_key=KEY_SOLID_DOT_BULLET)

    # Fix solid-square bullet symbols, and their spacing
    # * Word's solid-square bullet is not displayed properly by Firefox.
    #   * It is replaced here by the HTML solid-square symbol "&#9632;"
    fix_unordered_list_items(font_family="Wingdings",
                          symbol="§",
                          html_entity_encodings_key=KEY_SOLID_SQUARE_BULLET)

    # Fix the spacing for the letter-"o" bullet symbols
    fix_unordered_list_items(font_family='"Courier New"',
                          symbol="o",
                          html_entity_encodings_key=KEY_LETTER_O_BULLET)

    '''
    ######################
    Code Section:  Fix the list-items in ordered-lists
    ######################
    '''

    '''
    This code fixes commonly-found bugs in Word-HTML, for unordered-lists.

    * Terminology
      * An ordered list is made-up of list-items.
        * The list-item symbols are typically: integers, Roman-numerals, and letters.
        * Examples of the typical formatting for the list-item symbols is:
          1., 1), and [1]

    * The function examines each candidate list-item in the Python list "list_item_list_g".
      * list_item_list_g is a global variable, and it's described elsewhere in this program.
      * In HTML, a list-item is specified as a paragraph (<p ...> ... </p>)
      * If a list-item is for an ordered-list, then the list-item's HTML is edited, to fix its bugs.

    * The Word-HTML bugs, and their fixes, are further described in the system documentation.     
    '''

    # Fix ordered-list list-items
    unrecognized_indentation_units_list = []
    num_text_indent_unrecognized = 0
    num_list_items_fixed = 0
    # Loop for each HTML paragraph in list_item_list_g    
    for paragraph in list_item_list_g:
        '''
        * Determine if the paragraph is an ordered-list list-item.
        * Also, determine the structure of the relevant HTML tags and strings within
          the paragraph.
        * In this code-section, references to "list-item" are for an ordered-list.
        '''

        # Strings present in a list-item paragraph:
        # * In BeautifulSoup format, strings are stored in an object of
        #   type NavigableString.
        # * In a list-item paragraph, the first string can be either:
        #   * All spaces ("&nbsp;"), within a span tag, or
        #   * The list-item symbol, e.g., "1."
        # * If the first string is all spaces:
        #   * The second string is the list-item symbol.
        #   * The first string is referred to as the "pre-symbol spaces".
        # * There's a seperate string after the list-item symbol. 
        #   * It is all spaces ("&nbsp;"), within a span tag.
        #   * These spaces are referred to as the "post-symbol spaces".

        # A list-item paragraph will have at least two strings
        paragraph_strings = paragraph.find_all(string=True)
        if len(paragraph_strings) < 2:
            continue

        # Determine if the paragraph's first string is all spaces, within a span tag
        first_string = paragraph_strings[0]
        first_string_parent = first_string.parent
        if test_if_span_with_only_spaces(first_string_parent):
            first_string_is_all_spaces = True
        else:
            first_string_is_all_spaces = False
        
        # * Assume the paragraph is a list-item, and set variables
        #   to "point" to these strings:  the list-item symbol, and the post-symbol spaces.
        if first_string_is_all_spaces:
            if len(paragraph_strings) < 3:
                continue
            list_item_symbol_navigable_string = paragraph_strings[1]
            ending_span_with_only_spaces = paragraph_strings[2].parent
        else:
            list_item_symbol_navigable_string = paragraph_strings[0]
            ending_span_with_only_spaces = paragraph_strings[1].parent

        # * Test if there is a list-item symbol, in the string where the list-item symbol is
        #   expected to be.
        # * 
        if not isinstance(list_item_symbol_navigable_string, NavigableString):
            continue
        text = list_item_symbol_navigable_string.string
        # * This reg-ex matches the typical types of list-item symbols, and symbol formatting: 
        #   [1], 1), and 1.
        # * \S matches everything except whitespace, e.g., numbers, letters
        regex = r'^[\[]?\S+[\)\.\]]$'
        result = re.search(regex, text, re.M)
        if result == None:
            continue

        # * Test if the list-item symbol is followed by the post-symbol spaces
        if not test_if_span_with_only_spaces(ending_span_with_only_spaces):
            continue

        # * Test the parents of the two strings:  the list-item symbol, and the post-symbol spaces.
        # * The strings should have the same HTML parent.
        if not (list_item_symbol_navigable_string.parent is ending_span_with_only_spaces.parent):
            continue
        # * If there is a pre-symbol-spaces string, test that it and the list-item-symbol have
        #   the same HTML parent.
        if (first_string_is_all_spaces and 
            not (first_string_parent.parent is list_item_symbol_navigable_string.parent)):
            continue

        # Test if the paragraph's text-indent value is in the expected form.
        style = paragraph['style']
        regex = r"(?:^|;)(text-indent:[+-]?[\.0-9]+)([a-zA-Z]+)(?:$|;)"
        result = re.search(regex, style, re.M)
        if (result == None):
            continue
        # If the text-indent length-units are in not in inches, a warning message will be displayed, later.
        # * Length-units consist of letters (upper and/or lower-case), e.g., cm, mm, px, in, etc.
        #   * https://developer.mozilla.org/en-US/docs/Web/CSS/text-indent
        #   * https://developer.mozilla.org/en-US/docs/Web/CSS/length
        elif (result.group(2) != 'in'):
            num_text_indent_unrecognized += 1
            text_indent_specs = result.group(1) + result.group(2) 
            unrecognized_indentation_units_list.append(text_indent_specs)

        # * Replace the post-symbol spaces with the correct number of spaces (&nbsp;)
        # * The spaces are enclosed in a script tag, as was done in fixing unordered-lists.
        ending_span_with_only_spaces.contents[0].replace_with(
            BeautifulSoup(html_entity_encodings_g[KEY_SIX_NBSPS][KEY_ENCODE],
                        'html.parser') )
        html_entity_encodings_g[KEY_SIX_NBSPS][KEY_NUMBER_ENCODED] += 1
        
        # * Pre-symbol-spaces are within a span tag.
        # * If there are pre-symbol-spaces, delete the whole span tag.
        if first_string_is_all_spaces:
            first_string_parent.decompose()

        # Fix the paragraph's text-indent field by setting it to -.25
        regex = r"((?:^|;)text-indent:)([+-]?[\.0-9]+[a-zA-Z]+)($|;)"
        substitution = "\\1-.25in\\3"
        new_style, substitution_count = re.subn(regex, substitution, style, 0, re.M)
        if (substitution_count != 1):
            print("")
            print("ERROR.  Unexpected error, while fixing unordered-list list-items.")
            print("        Regular-expression substitution failed, in setting text-indent to \"-.25in\"")
            print("        List-item HTML:")
            print(paragraph.decode(formatter='html'))
            return 1, num_warning_messages_g
        paragraph['style'] = new_style

        num_list_items_fixed += 1

    print("INFO.  Editing the Word-HTML.  Fixing ordered-list list-items." + \
        "  %s list-items were fixed." % num_list_items_fixed)

    # * For a list-item, the text-indent value can have units other than inches.
    # * If such text-indent units were encountered, display a warning message.
    if (num_text_indent_unrecognized > 0):
        num_warning_messages_g += 1
        # Remove duplicates from the list: unrecognized_indentation_units_list
        unrecognized_indentation_units_list = list(set(unrecognized_indentation_units_list))
        # Create a string with the unrecognized units, separated by commas.
        string = ""
        for element in unrecognized_indentation_units_list:
            string += (element + ", ")
        string = string[0:-2]
        print("")
        print("WARNING.  Ordered-list list-item(s) were fixed.")
        print(f"          There were {num_text_indent_unrecognized} list-items whose " + \
              "text-indent values were not \"in\".")
        print("          In fixing their text-indent values, they were changed to use \"in\" units.")
        print("          It's possible that these list-items are not properly indented.")
        print("          The text-indent units that were not \"in\" are: " + string)
        print("")


    '''
    ######################
    Code Section:  For the Word-HTML, fix text that is incorrectly set to "color:white"

    The system docs have additional information about this Word-HTML bug, and the fix.
    ######################
    '''

    # * The parameter-file has a key that's used to specify what types of Word-HTML are to be 
    #   fixed, for "color:white" 
    #   * The key's name is specified in the constant KEY_WHITE_COLORED_TEXT
    if ( (KEY_WORD_HTML_EDITS in loaded_parms) and 
         (KEY_WHITE_COLORED_TEXT in loaded_parms[KEY_WORD_HTML_EDITS]) ):
        key_white_text_value = loaded_parms[KEY_WORD_HTML_EDITS][KEY_WHITE_COLORED_TEXT]
    else:
        # If the key isn't specified in the parameter-file, use the default value
        key_white_text_value = DO_NOT_REMOVE

    print("INFO.  Processing the span tags with attribute \"style\" and value \"color:white\".  ") 
    print("       Processing-type used (specified via the parameter-file key \"white_colored_text\"): " + key_white_text_value)

    # * Get all of the span tags that have a style attribute, and the style attribute
    #   includes the value "color:white"
    style_color_white = "color:white"
    regex = r"(?:^|;)(?:" + style_color_white + ")(?:$|;)"
    spans = body_inner_html.find_all('span', attrs={"style": re.compile(regex, re.M)})

    num_spans_under_paragraph = 0
    num_spans_not_under_paragraph = 0
    # Loop for each span tag
    for span in spans:
        paragraph_ancestor_found = False
        # Determine if the span tag is within a paragraph
        for span_parent in span.parents:
            if span_parent.name == 'p':
                paragraph_ancestor_found = True
                break
        
        if paragraph_ancestor_found == True:
            num_spans_under_paragraph += 1
        else:
            num_spans_not_under_paragraph += 1

        # Remove "color:white" from the span tag's style attribute, as required
        if ((key_white_text_value == REMOVE_IN_PARAGRAPHS) and paragraph_ancestor_found) or \
            (key_white_text_value == REMOVE_ALL):
            style = span['style']
            # If the style-attribute's only value is "color:white", delete the style attribute
            if (style == style_color_white):
                del span['style']
            else:
                regex = r"((?:^|;)(?:" + style_color_white + ")(?:$|;))"
                substitution = ""
                new_style, substitution_count = re.subn(regex, substitution, style, 0, re.M)
                if (substitution_count != 1):
                    print("")
                    print("ERROR.  Editing HTML span tags within a paragraph, having span attribute \"style\" and value \"color:white\".")
                    print("        For a span-tag, the regular-expression substitution failed in removing \"color:white\".")
                    print("        span-tag HTML:")
                    print("")
                    print(span.decode(formatter='html'))
                    return 1, num_warning_messages_g
                span['style'] = new_style

    print("INFO.  Checking for span tags with attribute \"style\" and value \"color:white\".")
    print("       The number of such span-tags:  Within an HTML paragraph: %s;  Not within an HTML paragraph: %s" %
          (num_spans_under_paragraph, num_spans_not_under_paragraph))

    if ((num_spans_not_under_paragraph + num_spans_under_paragraph) > 0):
        num_warning_messages_g += 1
        print("")
        print("WARNING.  Span tag(s) found, with attribute \"style\" and value \"color:white\".")
        print("          INFO messages provide details.  Further info is in the system docs.")
        print("")    

    '''
    ################################
    Code Section:  Generate the output HTML file
    ################################    
    '''

    '''
    Generate the HTML, from BeautifulSoup format, into text format
    '''
    # generated_html is a string variable
    generated_html = body_inner_html.decode(formatter='html')

    '''
    * If any HTML fixes were within a script tag, the script opening-tag and closing-tag 
      is removed from the HTML text
    '''
    # * When the HTML was edited, if HTML entities were added (e.g., &nbsp;), they were put inside of
    #   a script tag.  This prevented BeautifulSoup from altering the HTML entities.
    # * The script opening-tags and closing-tags are removed, using reg-ex substitution.
    #
    # * html_entity_encodings_g is a dictionary, and it was described earlier.
    #   * Each dictionary-entry specifies the HTML used to fix a particular bug in
    #     the Word-HTML.
    #   * Each dictionary-entry itself has a dictionary (defined by HTML_ENTITY_ENCODING_SPECS), and 
    #     that dictionary's entries include the info needed for removing the script opening-tags and 
    #     closing-tags.
    #
    # Loop for each entry in html_entity_encodings_g
    for key in html_entity_encodings_g:
        # Test if new HTML was added for this HTML-fix
        if html_entity_encodings_g[key][KEY_NUMBER_ENCODED] != 0:
            # The new-HTML is specified by the entry KEY_ENCODE.  
            # * This HTML includes the script opening-tag and closing-tag
            regex = html_entity_encodings_g[key][KEY_ENCODE]
            # * The new-HTML, without the script opening-tag and closing-tag, is specified by the 
            #   entry KEY_DECODE 
            substitution = html_entity_encodings_g[key][KEY_DECODE]
            # Use a reg-ex to replace the new-HTML, and remove the script opening-tag and closing-tag.
            generated_html, substitution_count = re.subn(regex, substitution, generated_html, 0)
            if substitution_count != html_entity_encodings_g[key][KEY_NUMBER_ENCODED]:
                print("")
                print("ERROR.  Decoding the " + html_entity_encodings_g[key][KEY_DESCRIPTION] +
                    ".  Number decoded (%s) is not equal to the number encoded (%s)."  
                    % (substitution_count, html_entity_encodings_g[key][KEY_NUMBER_ENCODED]))
                return 1, num_warning_messages_g
            print("INFO.  Decoding the " + html_entity_encodings_g[key][KEY_DESCRIPTION])

    # * generated_html has the document-text's HTML, with the fixes applied.
    # * Jinja will be used to put generated_html in the output HTML
    jinja_template_variables['document_text'] = generated_html

    '''
    Use Jinja to generate the final web-page HTML
    '''
    print("INFO.  Generating the output HTML, using the HTML-template.")
    generated_html = jinja_template.render(jinja_template_variables)

    print("INFO.  Writing the output HTML, to the output HTML-file:")
    print("       " + output_html_file_path)
    try:
        output_html_file_handle.write(generated_html)
        output_html_file_handle.close()
    except IOError as e:
        print("")
        print("ERROR.  Could not write-to or close the output HTML-file.")
        print("        %s - %s." % (e.strerror, e.filename))
        return 1, num_warning_messages_g

    print("")
    print("INFO.  Processing completed.  No errors.  Warning messages: " +
          str(num_warning_messages_g))

    return 0, num_warning_messages_g
# END of: generate_html()


# main() is a wrapper for calling generate_html()
def main(parameter_file_path):
    return_value, num_warning_messages = generate_html(parameter_file_path)
    if return_value == 1:
        print("")
        print("INFO.  Error encountered, processing not completed.  Error messages: 1.  Warning messages: " + str(num_warning_messages))
        print("")        
    return return_value, num_warning_messages


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
        prompted_for_input = True
        parameter_file_path = input("Enter parameter-file path: ").strip()
        if parameter_file_path == "":
            print("")
            print("ERROR.  Parameter-file path not provided.")
            print("")    
            sys.exit()
    else:
        prompted_for_input = False

    main(parameter_file_path)

    # * If the program was called by clicking on it, the command window will close 
    #   when the program exits, and the program's messages will not be viewable.
    # * Determining if the program was called by clicking on it is non-trivial,
    #   so just check if the user was prompted for input.
    if prompted_for_input == True:
        print("")
        input("Press any key to exit.")
        print("")