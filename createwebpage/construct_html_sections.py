'''
################
This file contains the function: construct_html_sections()

The function is called by: create_web_page_core() in create_web_page.py

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
    from bs4 import BeautifulSoup, NavigableString
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
#################
# Function: construct_html_sections()

Description:
* For the WWN web-page, constructs these output HTML-sections:
  * The HTML <head>-section's tags and attributes
  * The HTML for the web-page header-bar
  * The HTML for the document-text's trailer
  * The WWN table-of-contents (TOC), if the input HTML has a TOC

Parameters:
* loaded_parms : a dictionary with the input parameter-file's contents
* jinja_template_variables : the jinja-template object
* head : a BeautifulSoup object that holds the <head> element from the input HTML-file
* body : a BeautifulSoup object that holds the <body> element from the input HTML-file

Return:
* 1, None : error

* 0, body_inner_html : OK
  * The objects returned 
    * Objects passed as parameters:
      * loaded_parms : not changed
      * jinja_template_variables : values added for about 11 keys
      * head : not changed
      * body : it just has the <body> opening and closing tags.
               * The HTML between those tags is removed.
    * body_inner_html
      * The HTML from the <body> section in Word's HTML,
        but with these parts removed:
        * <body> opening and closing tags
        * The table-of-contents
#################
'''
def construct_html_sections(loaded_parms, jinja_template_variables, head, body):

    '''
    ##################
    Constants
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
    PAGE_STRUCTURE_CSS_FILE_NAME = "word_web_nav.css"
    JS_FILE_NAME = "word_web_nav.js"

    '''
    CSS classes that are referenced in some of the HTML that is generated.
    * The classes are defined in the CSS-file whose name is specified above, 
      in the variable: PAGE_STRUCTURE_CSS_FILE_NAME
    '''
    CSS_HEADER_BAR_TEXT = "headerBarText"
    CSS_HEADER_BAR_HREF = "headerBarHref"

    '''
    #############################
    For the WWN web-page, construct the HTML <head>-section's tags and attributes
    * This data includes whole HTML-tags, and attributes used in HTML tags.
    * This data is put in the dictionary jinja_template_variables[]
      * The variables will be used later in the jinja-template, in its HTML <head>-section.
    
    The WWN web-page's HTML <head>-section is constructed from two sources:
    * The <head> section in the input Word-HTML file
    * Data provided in the input parameter-file
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

    # * Get the <head> section in the BeautifulSoup object head, and 
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
        return 1, None

    # regexp "\Z" matches end of the whole string
    regex = r"(\s*<\/head>\s*$)\Z"
    html_string, substitution_count = re.subn(regex, substitution, html_string, 0, re.M)
    if (substitution_count != 1):
        print("")
        print("ERROR.  The expected HTML </head> tag was not found.")
        return 1, None
    html_string += "\n"

    # Jinja will be used to put the head-section contents in the output HTML 
    jinja_template_variables['word_head_section_contents'] = html_string


    '''
    Get the data for the output HTML <head> section, from the input parameter-file
    
    The data is specified under the key "html_head_section:""
    * An example:

      html_head_section:
        title: Sys-Admin How-To Info
        description: Solutions for my various sys-admin tasks
        additional_html: <link rel="icon" type="image/png" href="/favicon-32x32.png" sizes="32x32" />
    '''

    # From the input parameter-file, get the WWN version that is specified
    # * Jinja will be used to put the WWN version in the output HTML <head> section
    jinja_template_variables['version'] = loaded_parms[YML_KEY_REQUIRED][YML_KEY_VERSION]

    # Construct the HTML tag: <title>. . .
    if ( (YML_KEY_HTML_HEAD_SECTION in loaded_parms) and 
         (YML_KEY_TITLE in loaded_parms[YML_KEY_HTML_HEAD_SECTION]) ):
        key_title_value = loaded_parms[YML_KEY_HTML_HEAD_SECTION][YML_KEY_TITLE]
        title_tag = "<title>" + key_title_value + "</title>"
    else:
        title_tag = ""
    # Jinja will be used to put title_tag in the output HTML         
    jinja_template_variables['title_tag'] = title_tag

    # Construct the HTML tag: <meta name="descripton" . . .
    if ( (YML_KEY_HTML_HEAD_SECTION in loaded_parms) and     
         (YML_KEY_DESCRIPTION in loaded_parms[YML_KEY_HTML_HEAD_SECTION]) ): 
        key_description_value = loaded_parms[YML_KEY_HTML_HEAD_SECTION][YML_KEY_DESCRIPTION] 
        meta_description_tag = "<meta name=\"description\" content=\"" + \
                             key_description_value + "\">"
    else:
        meta_description_tag = ""
    # Jinja will be used to put meta_description_tag in the output HTML
    jinja_template_variables['meta_tag_with_description'] = meta_description_tag

    # From the input parameter-file, get the additional_html
    if ( (YML_KEY_HTML_HEAD_SECTION in loaded_parms) and     
         (YML_KEY_ADDITIONAL_HTML in loaded_parms[YML_KEY_HTML_HEAD_SECTION]) ):
        key_additional_html_value = loaded_parms[YML_KEY_HTML_HEAD_SECTION][YML_KEY_ADDITIONAL_HTML]
    else:
        key_additional_html_value = ""
    # Jinja will be used to put key_additional_html_value in the output HTML
    jinja_template_variables['additional_html'] = key_additional_html_value

    # From the input parameter-file, get page_structure_css_file_path
    key_scripts_directory_url_value = loaded_parms[YML_KEY_REQUIRED][YML_KEY_SCRIPTS_DIRECTORY_URL]
    page_structure_css_file_path = os.path.join(key_scripts_directory_url_value, PAGE_STRUCTURE_CSS_FILE_NAME)
    # Jinja will be used to put page_structure_css_file_path in the output HTML
    jinja_template_variables['page_structure_css_file_path'] = page_structure_css_file_path

    # From the input parameter-file, get web_page_js_file_path
    js_file_path = os.path.join(key_scripts_directory_url_value, JS_FILE_NAME)
    # Jinja will be used to put js_file_path in the output HTML
    jinja_template_variables['web_page_js_file_path'] = js_file_path

    '''
    #############################
    Process the Word-HTML's <body> tag:

    Get the <body> opening-tag:
    * For the <body> tag, the <body> opening-tag is the part <body ...>
    * For the input Word-HTML, its <body> opening-tag will be used in the output HTML.
    * Get that <body> opening-tag, in HTML text format, and put it in jinja_template_variables, 
      for use later in the jinja template.

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
    # From the BS docs, "A tag’s children are available in a list called .contents"
    body_contents_list = body.contents
    for i in range(0, len(body_contents_list)):
        # .append moves the HTML element from body to body_inner_html
        # * The BeautifulSoup doc does not make it clear that a move occurs here.
        # * Note body_inner_html and body are two different trees
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
        return 1, None

    # Jinja will be used to put body_opening_tag in the output HTML
    jinja_template_variables['body_opening_tag'] = body_opening_tag

    '''
    ###################
    Construct the HTML for the web-page header-bar

    * The web-page header-bar can be used for navigation breadcrumbs and for other text or URLs.
    * The web-page header-bar is different than the HTML <head> section.

    The HTML is put in jinja_template_variables, for use later in the jinja template.
    ###################
    '''
    '''
    The input parameter-file specifies the contents of the web-page header-bar.
    * The contents are put in an HTML table, which is put in the "header-bar" div.
      * The table has no borders and one row.    
      * There is a table-cell for each "section" specifed in the input parameter-file
        * The WWN user-guide describes the header-bar's sections
      * The sections' table-cells are of equal size.
      * The text within a cell is aligned as specified by the "contents_alignment" key,
        in the input parameter-file
    '''
    header_bar_table = ""
    # Test if the parameter-file has the key "header_bar:"
    if (YML_KEY_HEADER_BAR in loaded_parms):

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

        # The header-bar contents are specified in the parameter-file, under the key YML_KEY_HEADER_BAR
        # * Under YML_KEY_HEADER_BAR, there are one or more "sections", e.g., YML_KEY_BREADCRUMBS
        # * A table-cell is created for each section.
        # * The table-cell's contents are specified in the parameter-file.
        # 
        # Loop for each section under the key YML_KEY_HEADER_BAR
        for section in loaded_parms[YML_KEY_HEADER_BAR]:
            # Generate the opening-tag for the table cell
            if (YML_KEY_CONTENTS_ALIGNMENT in section[YML_KEY_SECTION]):
                table_cell_alignment = section[YML_KEY_SECTION][YML_KEY_CONTENTS_ALIGNMENT]
            else:
                table_cell_alignment = "left"
            header_bar_table += td_opening_tag.format(table_cell_alignment)

            # * For the section, determine its content's data-type, e.g., "breadcrumbs".
            # * And, generate the content's HTML 
            contents = section[YML_KEY_SECTION][YML_KEY_CONTENTS]
            # Data-type "breadcrumbs"
            if YML_KEY_BREADCRUMBS in contents:
                breadcrumbs_html = ""
                # Loop for each "hyperlink"
                for breadcrumb in section[YML_KEY_SECTION][YML_KEY_CONTENTS][YML_KEY_BREADCRUMBS]:
                    # Construct the breadcrumb:  the anchor tag (<a>) and the breadcrumb-separator
                    breadcrumbs_html += f"<a class=\"{CSS_HEADER_BAR_TEXT} {CSS_HEADER_BAR_HREF}\""
                    breadcrumbs_html += f" href=\"{breadcrumb[YML_KEY_HYPERLINK][YML_KEY_URL]}\">"
                    breadcrumbs_html += f"{breadcrumb[YML_KEY_HYPERLINK][YML_KEY_TEXT]}</a>"
                    breadcrumbs_html += BREAD_CRUMB_SEPARATOR

                # Remove the last separator
                separator_length = len(BREAD_CRUMB_SEPARATOR)
                breadcrumbs_html = breadcrumbs_html[0:-separator_length]
                header_bar_table += breadcrumbs_html

            # Data-type "hyperlink"
            elif YML_KEY_HYPERLINK in contents:
                # Construct the anchor tag (<a>)
                hyperlink_dict = section[YML_KEY_SECTION][YML_KEY_CONTENTS][YML_KEY_HYPERLINK]
                header_bar_table += f"<a class=\"{CSS_HEADER_BAR_TEXT} {CSS_HEADER_BAR_HREF}\""
                header_bar_table += f" href=\"{hyperlink_dict[YML_KEY_URL]}\">"
                header_bar_table += f"{hyperlink_dict[YML_KEY_TEXT]}</a>"

            # Data-type "html"
            elif YML_KEY_HTML in contents:
                header_bar_table += section[YML_KEY_SECTION][YML_KEY_CONTENTS][YML_KEY_HTML]

            # Data-type "text"
            elif YML_KEY_TEXT in contents:
                header_bar_table += section[YML_KEY_SECTION][YML_KEY_CONTENTS][YML_KEY_TEXT]

            # Data-type "empty"
            elif YML_KEY_EMPTY in contents:
                pass

            else:
                # * This case is a system error.
                # * The parameter-file's schema-definitions should not have allowed this data-type.
                #   Cerberus should have flagged the data-type as an error.
                print("")
                print("ERROR.  Input parameter-file has an unrecognized key under:")
                print(f"          {YML_KEY_HEADER_BAR}: {YML_KEY_SECTION}: {YML_KEY_CONTENTS}:")
                print("")
                return 1, None

            # Generate the closing-tag for the table cell
            header_bar_table += "</td>\n"
        # Generate the closing-tags for the table-row and table
        header_bar_table += "</tr>\n</table>\n"

    # Jinja will be used to put header_bar_table in the output HTML
    jinja_template_variables['header_bar'] = header_bar_table

    '''
    ###################
    Construct the HTML for the document-text's trailer
    ###################
    '''
    # Test if the trailer was specified in the parameter-file
    trailer_html = ""
    if (YML_KEY_DOCUMENT_TEXT_TRAILER in loaded_parms):
        # Create horizontal line
        trailer_html += "<!-- For the document-text trailer: generate the horizontal line, and the anchor tag -->\n"
        trailer_html += "<br><br><br><hr>\n"
        # * Create an anchor tag.  Use the name attribute, with the value in DOCUMENT_TEXT_TRAILER_ANCHOR_NAME.
        # * A hyperlink in the web-page header-bar can use this name to link to the document-text-trailer.
        trailer_html += "<a name=\"" + DOCUMENT_TEXT_TRAILER_ANCHOR_NAME + "\"></a>\n"
        # Get the document-text-trailer's HTML that was specified in the parameter file
        trailer_html += f"<!-- For the document-text trailer:  the HTML specified in the parameter-file is inserted here: -->\n"
        trailer_html += loaded_parms[YML_KEY_DOCUMENT_TEXT_TRAILER]
    # Jinja will be used to put trailer_html in the output HTML
    jinja_template_variables['document_text_trailer'] = trailer_html

    '''
    #######################################################
    Creates the WWN table-of-contents (TOC), if the input HTML has a TOC
    
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
    * For the TOC-entry paragraphs found, move them from the "body_inner_html" BeautifulSoup object, 
      to the "soup_toc" BeautifulSoup object
    '''
    soup_toc = BeautifulSoup("", 'html.parser')
    if (num_toc_paragraphs > 0):
        # Delete empty paragraphs from object "body_inner_html"
        # * From BS docs: "Tag.decompose() removes a tag from the tree, 
        #   then completely destroys it and its contents"
        for i in range(0, num_empty_paragraphs):
            empty_paragraphs[i].decompose()

        # Move TOC paragraphs from the object body_inner_html to the object soup_toc
        # * .append() moves an HTML tag in this case
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

    ############
    # Return
    ############
    return 0, body_inner_html

# END OF: construct_html_sections()