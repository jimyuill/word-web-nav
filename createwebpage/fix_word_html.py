'''
################
This file contains the function: fix_word_html()
The function is called by: create_web_page_core() in create_web_page.py

This file also contains these local functions:
* fix_unordered_list_items()
* test_if_span_with_only_spaces()

Call graph:
  create_web_page_core()
    --> fix_word_html()
          --> fix_unordered_list_items()
                --> test_if_span_with_only_spaces()
          --> test_if_span_with_only_spaces()

MIT License, Copyright (c) 2021-present Jim Yuill
################
'''

import re
import sys
import os
# Specifies the YAML keys for the input parameter-file
from input_parameter_file_keys import *

# This library needs to have been installed by the user
try:
    # BeautifulSoup:  pip install beautifulsoup4
    from bs4 import BeautifulSoup, NavigableString, Tag
except ImportError as e:
    print("")
    print("ERROR.  Could not import a required Python module.")
    print("        The installation instructions specify the required modules.")
    print("        Import-error description:")
    print("")
    print(e)
    print("")    
    sys.exit()

"""
##################
* Define:
  * Constants
  * html_entity_encodings_g : 
    * A global-variable (a dictionary) that is used in fixing particular Word-HTML bugs.
    * These are bugs in ordered-lists and unordered-lists.
  
* Naming convention:
  * FIX_ : prefix for global constants defined in this file
  * FIX_KEY_ : prefix for dictionary keys
  * _g : suffix for the global variable
##################
"""

'''
* Among the Word-HTML bugs that are fixed, some of the bugs are fixed by replacing a 
  particular string within an HTML paragraph.
  * The replacement process is the same for each of those bugs, but the data differs.
  * The replacement process is coded within two functions: fix_unordered_list_items() and generate_html().
  * The data used by those replacement-processes is defined here.
'''

# Defines the keys used in the dictionary HTML_ENTITY_ENCODING_SPECS
FIX_KEY_DESCRIPTION = "description"
FIX_KEY_ENCODE = "encode"
FIX_KEY_DECODE = "decode"
FIX_KEY_NUMBER_ENCODED = "number_encoded"

# A dictionary used to store the data used to fix a particular bug
HTML_ENTITY_ENCODING_SPECS = {
    FIX_KEY_DESCRIPTION: "",  # Constant, used in console messages
    FIX_KEY_ENCODE: "",  # Constant, specifies the new HTML, within a script tag
    FIX_KEY_DECODE: "",  # Constant, specifies the new HTML, without the script tag
    FIX_KEY_NUMBER_ENCODED: 0  # Variable, specifies the number of instances of the fix
}

# Defines the top-level keys used in the dictionary html_entity_encodings_g
FIX_KEY_SOLID_DOT_BULLET = "solid_dot_bullet"
FIX_KEY_SOLID_SQUARE_BULLET = "solid_square_bullet"
FIX_KEY_LETTER_O_BULLET = "letter_o_bullet"
FIX_KEY_SIX_NBSPS = "six_nbsps"

# Defines some tags that are used in the dictionary html_entity_encodings_g
# * The fixes to the Word-HTML involve replacing HTML strings with particular
#   HTML entities.
# * Those replacement HTML-entities are put inside script opening and closing tags,
#   which are defined here.
FIX_SCRIPT_OPENING_TAG = "<script type=\"word_web_page_nav\">"
FIX_SCRIPT_CLOSING_TAG = "</script>"

# * html_entity_encodings_g is a dictionary.
#   * The suffix "_g" indicates the dictionary is a global variable.
#   * Each entry specifies the HTML used to fix a particular bug in
#     the Word-HTML.
#   * Each entry's value is itself a dictionary.  
#     * The value is initialized to be a copy of HTML_ENTITY_ENCODING_SPECS.
html_entity_encodings_g = {
    FIX_KEY_SOLID_DOT_BULLET: HTML_ENTITY_ENCODING_SPECS.copy(),
    FIX_KEY_SOLID_SQUARE_BULLET: HTML_ENTITY_ENCODING_SPECS.copy(),
    FIX_KEY_LETTER_O_BULLET: HTML_ENTITY_ENCODING_SPECS.copy(),
    FIX_KEY_SIX_NBSPS: HTML_ENTITY_ENCODING_SPECS.copy()
}

# Fix for solid-dot bullet-symbols
html_entity_encodings_g[FIX_KEY_SOLID_DOT_BULLET][FIX_KEY_DESCRIPTION] = \
    "solid-dot bullet-symbols (used in levels 1,4,7)"
html_entity_encodings_g[FIX_KEY_SOLID_DOT_BULLET][FIX_KEY_ENCODE] = \
    FIX_SCRIPT_OPENING_TAG + "&#9679;" + FIX_SCRIPT_CLOSING_TAG   
html_entity_encodings_g[FIX_KEY_SOLID_DOT_BULLET][FIX_KEY_DECODE] = "&#9679;"

# Fix for solid-square bullet-symbols
html_entity_encodings_g[FIX_KEY_SOLID_SQUARE_BULLET][FIX_KEY_DESCRIPTION] = \
    "solid-square bullet-symbols (used in levels 3,6,9)"
html_entity_encodings_g[FIX_KEY_SOLID_SQUARE_BULLET][FIX_KEY_ENCODE] = \
    FIX_SCRIPT_OPENING_TAG + "&#9632;" + FIX_SCRIPT_CLOSING_TAG   
html_entity_encodings_g[FIX_KEY_SOLID_SQUARE_BULLET][FIX_KEY_DECODE] = "&#9632;"

# For letter "o" bullet-symbols, specify no fix is needed for the bullet-symbol
html_entity_encodings_g[FIX_KEY_LETTER_O_BULLET][FIX_KEY_DESCRIPTION] = \
    "letter \"o\" bullet-symbols (used in levels 2,5,8)"
html_entity_encodings_g[FIX_KEY_LETTER_O_BULLET][FIX_KEY_ENCODE] = ""   
html_entity_encodings_g[FIX_KEY_LETTER_O_BULLET][FIX_KEY_DECODE] = ""

# Fix for spacing after a bullet-symbol (unordered list), or list-item symbol (ordered-list).
html_entity_encodings_g[FIX_KEY_SIX_NBSPS][FIX_KEY_DESCRIPTION] = "list-item spacing"
html_entity_encodings_g[FIX_KEY_SIX_NBSPS][FIX_KEY_ENCODE] = \
    FIX_SCRIPT_OPENING_TAG + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + FIX_SCRIPT_CLOSING_TAG   
html_entity_encodings_g[FIX_KEY_SIX_NBSPS][FIX_KEY_DECODE] = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"


'''
##############
# Function: test_if_span_with_only_spaces()

* This is a local function, called by:
  * fix_word_html()
  * fix_unordered_list_items()

Description
* For the input HTML-elemement, determine if it is a span-tag with
  a single string made-up of only spaces
  
Returns True or False
##############
'''
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
# Function: fix_unordered_list_items()

* This is a local function, called by: fix_word_html()

Description:
* This function fixes commonly-found bugs in Word-HTML, for unordered-lists.

Parameters:
* word_list_item_list : a Python list, holds candidate Word list-items
* font_family : used in specifying the bullet-symbol of the list-items to be fixed
* symbol : used in specifying the bullet-symbol of the list-items to be fixed
* html_entity_encodings_key : the HTML for fixing the bullet-symbol, if it needs to be fixed

Global variable: html_entity_encodings_g

Return:
* word_list_item_list : Fixed list-items are removed from word_list_item_list.
* html_entity_encodings_g : Stats are recorded for fixed list-items
    
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

* The function examines each candidate Word list-item in the Python list "word_list_item_list".
  * A candidate list-item could be a list-item, but additional examination is needed to confirm that.
  * In HTML, a list-item is specified as a paragraph (<p ...> ... </p>)
  * If a list-item is for an unordered-list, and it has the specified bullet-symbol, 
    then the list-item's HTML is edited, to fix its bugs.

* The bug-fixes just described involve replacing HTML strings with HTML entities.
  * The replacements are done in the BeautifulSoup HTML.
  * During the replacement, BeautifulSoup itself can potentially alter those HTML entities,
    in undesirable ways.
  * To prevent BeautifulSoup from making those alternations, the replacement HTML entities
    are put insides of an HTML <script> tag, e.g., <script>[replacement HTML entities]</script>.
  * Later in fix_word_html(), the BeautifulSoup HTML will be converted to HTML text.  
    Those added opening and closing script tags will be removed then, from the HTML text.

* The Word-HTML bugs, and their fixes, are further described in the WWN development-documents.
'''
def fix_unordered_list_items(word_list_item_list, 
                             font_family: str, 
                             symbol: str, 
                             html_entity_encodings_key: str):

    global html_entity_encodings_g

    list_elements_to_remove = []

    symbol_replace_count = 0
    bullets_fixed_count = 0
    # Loop for each HTML paragraph in word_list_item_list
    for word_list_item_list_index in range(0, len(word_list_item_list)):
        '''
        * Determine if the paragraph is an unordered-list list-item, 
          and if it has the required bullet-symbol.
        '''
        
        # A list-item paragraph will have at least two strings
        paragraph = word_list_item_list[word_list_item_list_index]
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
        if (html_entity_encodings_g[html_entity_encodings_key][FIX_KEY_ENCODE] != ""):
            first_string.replace_with(
                BeautifulSoup(html_entity_encodings_g[html_entity_encodings_key][FIX_KEY_ENCODE],
                            'html.parser') )
            symbol_replace_count += 1
        
        # Replace the "&nbsp;"s, using the HTML defined in html_entity_encodings_g
        '''        
        For list-items that use common bullet-symbols, there is an additional bug in the Word HTML.
          * Word puts "&nbsp;" entities after the bullet-symbol, to provide spacing between the 
            bullet-symbol and the list-item's text.
          * However, the number of "&nbsp;" entities is often incorrect, and it often results in
            a visibly misaligned unordered-list.
          * The problem is fixed by replacing the "&nbsp;"'s with six "&nbsp"'s.
        '''
        second_string.replace_with(BeautifulSoup(html_entity_encodings_g[FIX_KEY_SIX_NBSPS][FIX_KEY_ENCODE],
                            'html.parser') )
        
        # The HTML paragraph has been fixed.  Its index in word_list_item_list is recorded.
        list_elements_to_remove.append(word_list_item_list_index)
        bullets_fixed_count += 1

    # * For the HTML paragraphs that have been fixed, remove them from the list
    #   word_list_item_list
    # * Removing them from the list does not remove them from the BeautifulSoup HTML
    #   (i.e., they are not removed from the BeautifulSoup object "soup")
    for i in sorted(list_elements_to_remove, reverse=True):
        del word_list_item_list[i]

    print("INFO.  Editing the Word-HTML.  Fixing list-items with " +
          html_entity_encodings_g[html_entity_encodings_key][FIX_KEY_DESCRIPTION] + 
          "  Number of list-items found: " +  str(bullets_fixed_count) )
    # Record stats for fixes
    html_entity_encodings_g[html_entity_encodings_key][FIX_KEY_NUMBER_ENCODED] = symbol_replace_count
    html_entity_encodings_g[FIX_KEY_SIX_NBSPS][FIX_KEY_NUMBER_ENCODED] += bullets_fixed_count
# END OF:  def fix_unordered_list_items()


'''
#############
# Function fix_word_html()

Description:
* Fix bugs in Word's HTML

Parameters:
* loaded_parms : a dictionary with the input parameter-file's contents
* jinja_template_variables : the jinja-template object
* body_inner_html : The HTML from the <body> section in Word's HTML,
                    but with these parts removed:
                    * <body> opening and closing tags
                    * The table-of-contents
* num_warning_messages : counter

Calls local functions:
* fix_unordered_list_items()
* test_if_span_with_only_spaces()

Return:
* 1, None : error

* 0, num_warning_messages : OK
  * The objects returned 
    * Objects passed as parameters:
      * loaded_parms : not changed
      * jinja_template_variables : added the document-text's HTML, with the fixes applied    
      * body_inner_html : contents not specified (no longer used)
      
The Word-HTML bugs, and their fixes, are further described in the WWN development-documents.
The documents are:
* In the repo, under /docs/development-docs
* On the WWN web-site
#############
'''

'''
  * Word's HTML has several bugs. This function fixes those bugs, if present.
  * The bugs are fixed by editing the HTML.
    * The HTML is in the BeautifulSoup object "body_inner_html".
      * body_inner_html has the HTML from the <body> section in Word's HTML, 
        but with the outer <body...> tags removed, and the table-of-contents removed

  * The Word-HTML bugs fixed are:
    * Formatting problems in bulleted lists (unordered lists)
    * Formatting problems in ordered lists
    * Text whose color is incorrectly set to be white
'''
def fix_word_html(loaded_parms, jinja_template_variables, body_inner_html, num_warning_messages):

    global html_entity_encodings_g

    '''
    #####################
    Get the HTML paragraphs that are candidate list-items.
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
        * They are described in the WWN development-documents, but their HTML is not edited by the system.

    * body_inner_html.find_all() creates a Python list with the HTML paragraphs that have those distinctive features
      *  Each element in the Python list is an HTML paragraph, stored as a BeautifulSoup object
      *  That BeautifulSoup object is a pointer into the original BeautifulSoup object "soup"
      *  In creating the paragraph's BeautifulSoup object, the paragraph was not removed from "soup"
    '''

    # word_list_item_list contains candidate list-items  
    # * A candidate list-item could be a Word list-item, but additional examination is needed to confirm.
    word_list_item_list = []

    # "regex" is a reg-ex pattern used to match known class names, e.g., class=MsoNormal
    #  * These names have been observed in both ordered and unordered lists.
    #  * The only exception is the name "MsoListParagraph", which has only been observed in ordered lists.
    regex = r'(^MsoListParagraph(CxSp(First|Middle|Last))?$)|(^MsoNormal$)|(^MsoBodyText$)'
    word_list_item_list = body_inner_html.find_all('p', 
        class_=re.compile(regex, re.M), 
        attrs={'style': re.compile('text-indent:')})


    '''
    ######################
    Fix the list-items in unordered-lists
    ######################
    '''
    # Fix solid-dot bullet symbols, and their spacing
    # * Word's solid-dot bullet is not displayed properly by Firefox.
    #   * It is replaced here by the HTML solid-dot symbol "&#9679;"
    fix_unordered_list_items(word_list_item_list,
                          font_family="Symbol",
                          symbol="Â·",
                          html_entity_encodings_key=FIX_KEY_SOLID_DOT_BULLET)

    # Fix solid-square bullet symbols, and their spacing
    # * Word's solid-square bullet is not displayed properly by Firefox.
    #   * It is replaced here by the HTML solid-square symbol "&#9632;"
    fix_unordered_list_items(word_list_item_list,
                          font_family="Wingdings",
                          symbol="Â§",
                          html_entity_encodings_key=FIX_KEY_SOLID_SQUARE_BULLET)

    # Fix the spacing for the letter-"o" bullet symbols
    fix_unordered_list_items(word_list_item_list,
                          font_family='"Courier New"',
                          symbol="o",
                          html_entity_encodings_key=FIX_KEY_LETTER_O_BULLET)

    '''
    ######################
    Fix the list-items in ordered-lists
    ######################
    '''

    '''
    This code fixes commonly-found bugs in Word-HTML, for ordered-lists.

    * Terminology
      * An ordered list is made-up of list-items.
        * The list-item symbols are typically: integers, Roman-numerals, and letters.
        * Examples of the typical formatting for the list-item symbols is:
          1., 1), and [1]

    * The function examines each candidate list-item in the Python list "word_list_item_list".
      * In HTML, a list-item is specified as a paragraph (<p ...> ... </p>)
      * If a list-item is for an ordered-list, then the list-item's HTML is edited, to fix its bugs.
    
    *	There are two commonly-found bugs in these list-items:
      * The list-item symbol is often not properly indented
      *	The text after the list-item symbol is often not properly indented 
        * (It does not have the proper number of spaces between the symbol and the start of the text)
        
    *	An example of a typical list-item paragraph, for an ordered-list
        <p class=MsoListParagraphCxSpMiddle style='margin-left:1.5in;text-indent:-1.5in'>
        <span style='font:7.0pt "Times New Roman"'>&nbsp;&nbsp;&nbsp;&nbsp;</span>i.<span 
        style='font:7.0pt "Times New Roman"'>&nbsp;&nbsp;</span>List-item text</p>
    '''

    unrecognized_indentation_units_list = []
    num_text_indent_unrecognized = 0
    num_list_items_fixed = 0
    # Loop for each HTML paragraph in word_list_item_list    
    for paragraph in word_list_item_list:
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
            BeautifulSoup(html_entity_encodings_g[FIX_KEY_SIX_NBSPS][FIX_KEY_ENCODE],
                        'html.parser') )
        html_entity_encodings_g[FIX_KEY_SIX_NBSPS][FIX_KEY_NUMBER_ENCODED] += 1
        
        # * Pre-symbol-spaces are within a span tag.
        # * If there are pre-symbol-spaces, delete the whole span tag.
        # * From BS docs: "Tag.decompose() removes a tag from the tree, 
        #   then completely destroys it and its contents"        
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
            return 1, num_warning_messages
        paragraph['style'] = new_style

        num_list_items_fixed += 1

    print("INFO.  Editing the Word-HTML.  Fixing ordered-list list-items." + \
        "  %s list-items were fixed." % num_list_items_fixed)

    # * For a list-item, the text-indent value can have units other than inches.
    # * If such text-indent units were encountered, display a warning message.
    if (num_text_indent_unrecognized > 0):
        num_warning_messages += 1
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
    For the Word-HTML, fix text that is incorrectly set to "color:white"
    ######################
    '''

    # * The input parameter-file has a key that's used to specify what types of Word-HTML are to be 
    #   fixed, for "color:white" 
    #   * The key's name is specified in the constant YML_KEY_WHITE_COLORED_TEXT
    if ( (YML_KEY_WORD_HTML_EDITS in loaded_parms) and 
         (YML_KEY_WHITE_COLORED_TEXT in loaded_parms[YML_KEY_WORD_HTML_EDITS]) ):
        key_white_text_value = loaded_parms[YML_KEY_WORD_HTML_EDITS][YML_KEY_WHITE_COLORED_TEXT]
    else:
        # If the key isn't specified in the parameter-file, use the default value
        key_white_text_value = YML_DO_NOT_REMOVE

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
        if ((key_white_text_value == YML_REMOVE_IN_PARAGRAPHS) and paragraph_ancestor_found) or \
            (key_white_text_value == YML_REMOVE_ALL):
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
                    return 1, num_warning_messages
                span['style'] = new_style

    print("INFO.  Checking for span tags with attribute \"style\" and value \"color:white\".")
    print("       The number of such span-tags:  Within an HTML paragraph: %s;  Not within an HTML paragraph: %s" %
          (num_spans_under_paragraph, num_spans_not_under_paragraph))

    if ((num_spans_not_under_paragraph + num_spans_under_paragraph) > 0):
        num_warning_messages += 1
        print("")
        print("WARNING.  Span tag(s) found, with attribute \"style\" and value \"color:white\".")
        print("          INFO messages provide details.  Further info is in the system docs.")
        print("")    


    '''
    ################################
    Generate the document-body's HTML, with the fixes applied
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
        if html_entity_encodings_g[key][FIX_KEY_NUMBER_ENCODED] != 0:
            # The new-HTML is specified by the entry FIX_KEY_ENCODE.  
            # * This HTML includes the script opening-tag and closing-tag
            regex = html_entity_encodings_g[key][FIX_KEY_ENCODE]
            # * The new-HTML, without the script opening-tag and closing-tag, is specified by the 
            #   entry FIX_KEY_DECODE 
            substitution = html_entity_encodings_g[key][FIX_KEY_DECODE]
            # Use a reg-ex to replace the new-HTML, and remove the script opening-tag and closing-tag.
            generated_html, substitution_count = re.subn(regex, substitution, generated_html, 0)
            if substitution_count != html_entity_encodings_g[key][FIX_KEY_NUMBER_ENCODED]:
                print("")
                print("ERROR.  Decoding the " + html_entity_encodings_g[key][FIX_KEY_DESCRIPTION] +
                    ".  Number decoded (%s) is not equal to the number encoded (%s)."  
                    % (substitution_count, html_entity_encodings_g[key][FIX_KEY_NUMBER_ENCODED]))
                return 1, num_warning_messages
            print("INFO.  Decoding the " + html_entity_encodings_g[key][FIX_KEY_DESCRIPTION])

    # * generated_html has the document-text's HTML, with the fixes applied.
    # * Later, Jinja will be used to put generated_html in the output HTML
    jinja_template_variables['document_text'] = generated_html

    ##############
    # Return
    ##############
    return 0, num_warning_messages

# END OF: def fix_word_html()