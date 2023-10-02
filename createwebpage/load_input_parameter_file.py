'''
################
This file contains the function: load_input_parameter_file()

The function is called by: create_web_page_core() in create_web_page.py

MIT License, Copyright (c) 2021-present Jim Yuill
################
'''

import sys 
import os
# Specifies the YAML keys for the input parameter-file
from input_parameter_file_keys import *

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
except ImportError as e:
    print("")
    print("ERROR.  Could not import a required Python module.")
    print("        The installation instructions specify the required modules.")
    print("        Import-error description:")
    print("")
    print(e)
    print("")    
    sys.exit()

def load_input_parameter_file(parameter_file_path : str):
    '''
    Description:
    * Loads the WWN input parameter-file, and verifies it
    
    Operation:
    * Verifies the input parameter-file's syntax
    * yamllint is used to verify the parameter-file's YAML syntax. 
    * PyYAML's YAML-loader is used to load the parameter-file into a Python
      object, made-up of dictionaries and lists.
    * Cerberus is used to verify the parameter-file's syntax, using a schema.
    * Verifies the WordWebNav version that is specified in the parameter-file
    * The syntax verification is further described in the WWN development-documents.
      The documents are:
      * In the repo, under /docs/development-docs
      * On the WWN web-site

    Parameter: parameter_file_path, specifies the input parameter-file's path

    Return
    * 1, None : Error
    * 0, loaded_parms : loaded_parms is a dictionary with the input parameter-file's
                        contents
    '''    

    '''
    ##################
    Constants
    ##################
    '''
    # Name for the yamllint config-file
    YAMLLINT_CONFIG_FILE_NAME = "yamllint_config_file.yml"

    '''
    # The following are Cerberus schema-definitons, for the input parameter-file.
      * The parameter-file is in YAML formt.
      * The parameter-file is validated by calling Cerberus.
      * These schema-definitions are used by Cerberus, to validate the parameter-file.

      * These schema-definitons specify the parameter-file's structure, keys, and values.
      * The parameter-file is described in the system documentation.
      * These schema-definitons specify the parameter-file syntax that is described in the 
        system documentation.
      * Since Cerberus is used to validate the parameter-file, the WWN code that processes the parameter-file
        assumes the parameter-file has valid syntax, e.g., it assumes that required keys are present.
    '''

    # The Cerberus schema-definition
    PARAMETER_FILE_SCHEMA = {

        # Parameter-file section. Name: "required":
        # Example contents for the section:
        #
        #   required:
        #     version: "1.0"
        #     input_html_path: D:\Documents\Professional-projects\My-web-site-development\Word-to-HTML\automation-dev\testing\test-Word-files\test-Word-files\tests-for-create_web_page_py\WordWebNav--Word-HTML\all-primary-Word-features.html
        #     output_directory_path: D:\Documents\Professional-projects\My-web-site-development\Word-to-HTML\automation-dev\testing\test-Word-files\test-Word-files\tests-for-create_web_page_py\WordWebNav--HTML
        #     scripts_directory_url: D:\Documents\Professional-projects\My-web-site-development\Word-to-HTML\WordWebNav\word_web_nav\assets
        #
        YML_KEY_REQUIRED: {
            "type": "dict",
            "required": True,
            "schema": {
                YML_KEY_VERSION: {
                    "type": "string",
                    "required": True,
                    "minlength": 1
                },
                YML_KEY_INPUT_HTML_PATH: {
                    "type": "string",
                    "required": True,
                    "minlength": 1                
                },
                YML_KEY_OUTPUT_DIRECTORY_PATH: {
                    "type": "string",
                    "required": True,
                    "minlength": 1                
                },
                YML_KEY_SCRIPTS_DIRECTORY_URL: {
                    "type": "string",
                    "required": True,
                    "minlength": 1                
                }
            }
        },

        # Parameter-file section. Name: "html_head_section":
        # Example contents for the section:
        #
        #   html_head_section:
        #     title: Sys-Admin How-To Info
        #     description: Solutions for my various sys-admin tasks
        #     additional_html: <link rel="icon" type="image/png" href="/favicon-32x32.png" sizes="32x32" />
        #
        YML_KEY_HTML_HEAD_SECTION: {
            "type": "dict",
            "required": False,
            "schema": {
                YML_KEY_TITLE: {
                    "type": "string",
                    "required": False,
                    "minlength": 1                
                },
                YML_KEY_DESCRIPTION: {
                    "type": "string",
                    "required": False,
                    "minlength": 1                
                },
                YML_KEY_ADDITIONAL_HTML: {
                    "type": "string",
                    "required": False,
                    "minlength": 1                
                }
            }
        },

        # Parameter-file section. Name: "header_bar":
        # Example contents for the section:
        #
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
        #        contents_alignment:
        #
        YML_KEY_HEADER_BAR: {
            "type": "list",
            "required": False,
            "schema": {
                "type": "dict",
                "schema": {
                    YML_KEY_SECTION: {
                        "type": "dict",
                        "schema": {
                            YML_KEY_CONTENTS: {
                                "type": "dict",
                                "required": True,
                                # Only one entry allowed in dict
                                "maxlength" : 1, 
                                "schema" : {
                                    YML_KEY_BREADCRUMBS: {
                                        # * This entry is a list, and 
                                        #   each list-member specifies a hyperlink
                                        "type": "list",
                                        "required": False,
                                        "schema": {
                                            "type": "dict",
                                            "schema": {
                                                YML_KEY_HYPERLINK : {
                                                    "type": "dict",
                                                    "schema": {
                                                        YML_KEY_TEXT: {
                                                            "type": "string",
                                                            "required": True,
                                                            "minlength": 1
                                                        },
                                                        YML_KEY_URL: {
                                                            "type": "string",
                                                            "required": True,
                                                            "minlength": 1                            
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    },

                                    YML_KEY_HYPERLINK : {
                                        "type": "dict",
                                        "required": False,
                                        "schema": {
                                            YML_KEY_TEXT: {
                                                "type": "string",
                                                "required": True,
                                                "minlength": 1            
                                            },
                                            YML_KEY_URL: {
                                                "type": "string",
                                                "required": True,
                                                "minlength": 1            
                                            }
                                        }
                                    },

                                    YML_KEY_TEXT : {
                                        "type": "string",
                                        "required": False,
                                        "minlength": 1
                                    },

                                    YML_KEY_HTML : {
                                        "type": "string",
                                        "required": False,
                                        "minlength": 1
                                    },

                                    YML_KEY_EMPTY : {
                                        "type": "string",
                                        "required": False,
                                        "maxlength" : 0,   # Ensures no value is specified
                                        "nullable": True   # Allows key to have no value
                                    }
                                }
                            },

                            YML_KEY_CONTENTS_ALIGNMENT: {
                                "type": "string",
                                "required": False,
                                "allowed": ["left", "right", "center", "justify"]
                            }
                        }
                    }
                }
            }
        },

        # Parameter-file section. Name: "document_text_trailer":
        # Example contents for the section:
        #
        #   document_text_trailer: |
        #     <div id="commento"></div>
        #     <script defer
        #       src="https://cdn.commento.io/js/commento.js">
        #     </script>
        #
        YML_KEY_DOCUMENT_TEXT_TRAILER: {
            "type": "string",
            "required": False,
            "minlength" : 1
        },

        # Parameter-file section. Name: "word_html_edits":
        # Example contents for the section:
        #
        #   word_html_edits:
        #     white_colored_text: removeAll
        #
        YML_KEY_WORD_HTML_EDITS: {
            "type": "dict",
            "required": False,
            "schema": {
                YML_KEY_WHITE_COLORED_TEXT: {
                    "type": "string",
                    "required": False,
                    "allowed": [YML_DO_NOT_REMOVE, YML_REMOVE_IN_PARAGRAPHS, YML_REMOVE_ALL]
                }
            }
        }
    }
    # END of: PARAMETER_FILE_SCHEMA = {


    '''
    ##################
    Function body
    ##################
    '''
    
    # Open the input parameter-file
    print("INFO.  Processing the parameter-file:")
    print("       " + parameter_file_path)
    try:
        parameter_file_handle = open(parameter_file_path)
    except IOError as e:
        print("")
        print("ERROR.  Could not open the parameter-file.")
        print("        %s - %s." % (e.strerror, e.filename))
        print("")        
        return 1, None

    '''
    ############
    # yamllint is used to verify the parameter-file's YAML syntax. 
    ############
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
        return 1, None

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
        return 1, None

    '''
    ################
    # PyYAML's YAML-loader is used to load the parameter-file
    ################
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
        return 1, None

    # This can happen if the input file just has a line "---"
    if (loaded_parms == None):
        print("")
        print("ERROR.  The YAML-loader did not load anything.")
        print("        The parameter-file appears to be in error, e.g., has no keys.")
        return 1, None

    '''
    ###################
    # Cerberus is used to verify the parameter-file's syntax, using a schema.
    # * Schemas are defined (above) for the parameter-file's structure, keys and values.
    ###################
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
        return 1, None

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
        return 1, None

    '''
    ##############
    # Verify the WordWebNav version that is specified in the parameter-file
    ##############
    '''
    key_version_value = loaded_parms[YML_KEY_REQUIRED][YML_KEY_VERSION]
    if key_version_value != "1.0":
        print("")
        print( "ERROR.  Error in the parameter-file.  In section \"" + YML_KEY_REQUIRED + \
               "\", the key \"" + YML_KEY_VERSION + "\" has an incorrect value: " + key_version_value )
        return 1, None


    # Return loaded_parms
    return 0, loaded_parms

# END OF: load_input_parameter_file()