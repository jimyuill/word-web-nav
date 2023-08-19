# This code is needed to import functions from another file in the same directory
# * Example, from create_web_page.py:
#   > from load_input_parameter_file import load_input_parameter_file
# * See: https://stackoverflow.com/a/49375740
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))