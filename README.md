# WordWebNav: create usable MS-Word web-pages

[Link to WWN home-page and docs](https://jimyuill.com/software/www/WordWebNav/)

## **Overview**
WordWebNav (WWN) is an app that converts a Microsoft-Word document to a usable web-page.
WWN is free and open-source.

The present web-page was created from a Word-doc using WWN.

WWN's web-page features are described in the screen-shots below.  The features  include:
- A document-text pane, with adjustable width, and support for user-comments at the bottom
- A navigation pane, with hyperlinks to the headings in the document-text pane
- A header-bar for site-navigation, e.g., breadcrumbs
- Fixes for common bugs in Word's HTML, such as: 
  - Word-HTML's paragraphs span the browser's width, which makes them difficult to read.
  - Word-HTML's multi-level lists are misformatted

## **Screen-shots**
- WWN web-page components:

<img border="0" height="321" src="readme-figure-1.png" width="789"/>


- The comments section, at the bottom of the document-text pane (Commento is used here):

<img border="0" height="538" src="readme-figure-2.png" width="937"/>


## **Examples**
- [A demo WWN web-page](https://jimyuill.com/software/www/WordWebNav/demo.html) was created from a Word-doc with typical features for recording technical info.
- [The WWN author's web-site](https://jimyuill.com) is created mostly from Word documents and their WWN web-pages.

## **Description**
Word is a powerful tool for recording technical info.  Word can save a document in HTML format, but, for the web-page to be usable, additional features are needed, as well as fixes for bugs in Word's HTML.

WWN can be used to create a personal web-site from Word documents.  The WWN web-pages' user-interface is simple, and it provides the features needed for navigation and user-comments.  And, of course, WWN web-pages can be used on any web-site, not just a personal web-site.

WWN is relatively easy to use.  First, a copy of the Word document is saved in Word HTML-format.  Next, the user creates a parameter-file to specify the WWN web-page's files, header-bar contents, etc.  WWN is then run to generate the WWN web-page.  