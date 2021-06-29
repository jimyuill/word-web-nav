/*
DESCRIPTION:  Javascript functions for WordWebNav's web-page

There are three functions.  They are run, respectively, when:
* The HTML file is loaded
* The splitter-bar is dragged
* The web-browser is resized

The system documentation has additional info on its: installation, use, design 
and implementation (code).

MIT License, Copyright (c) 2021-present Jim Yuill

*/


/*  
This function runs when the HTML file is loaded.

This script fixes possible alignment problems in the web-page's div's.
* The div's sizing and alignment are specified in an accompanying CSS file.
* There are limitations in CSS that can result in alignment problemsj for the div's.
* Those limitations are described in the accompanying CSS file.
    
The widths calculated here are the same amounts as those calculated in the CSS file.
* There are accuracy limitations in CSS, and it may have calculated the
  widths inaccurately

https://stackoverflow.com/questions/2926227/how-to-do-jquery-code-after-page-loading
https://stackoverflow.com/questions/8396407/jquery-what-are-differences-between-document-ready-and-window-load
*/
$(window).on('load', function() {
  
    var // Width of the container div

        /* 
        * parseInt(): second parameter is the radix (base) for the number returned, i.e., base 10
          *  https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/parseInt
           
        * .width():  
          * Does not include the margin nor border widths (confirmed).
          * It probably does not include the padding width (not confirmed; it is 0 in the container div).
          * It includes the content width (confirmed).
          * https://api.jquery.com/width/
        */
        totalWidth = parseInt($('#container').width(), 10),

        /* For the table-of-contents div, this is comparable to the CSS calculation in: 
           * width: calc(25% - 20px);
           In addition, the amount is corrected to not be negative
        */
        tocWidth = Math.max(0, (Math.floor(totalWidth * .25) - 20)),

        /* For the table-of-contents div, its total-width is:
           * (content-area width) + (padding-left width)
        */
        tocTotalWidth = tocWidth + 20,
        
        /* For the splitter-bar div, this is comparable to the CSS calculation in: 
           * left: 25%;
        */
        splitterBarLeft = tocTotalWidth,

        /* For the document div, this is comparable to the CSS calculation in: 
           * left: calc(25% + 12px);
        */
        documentLeft = tocTotalWidth + 12,
        
        /* For the document div, this is comparable to the CSS calculation in: 
           * width: calc(75% - (12px + 20px + 20px + 2px));         
           In addition, the size is corrected to not be negative
        */
        documentWidth = Math.max(0, ((totalWidth - tocTotalWidth) - (12 + 20 + 20 + 2)));

    /* Set the new values, for the CSS IDs and declarations
    */
    $('#table-of-contents').css({width : tocWidth}); 
    $('#splitter-bar').css({left : tocTotalWidth}); 
    $('#document').css({left : documentLeft});             
    $('#document').css({width : documentWidth}); 
});


/* This function enables the splitter-bar to be dragged, to resize the
   table-of-contents and document sections.
*/
$(function(){
    var // Width of the container div
        totalWidth = parseInt($('#container').width(), 10),
          
        /* For the container div, gets the left and top positions
        */
        /* .offset():  
           * From the API doc: "Gets the current coordinates of the first element in the set of 
             matched elements, relative to the document."
           * Returns 2 values: <var>.left, <var>.top
           * These positions are relative to the whole browser window
             * offset.left is 0
             * offset.top is 42 (height of the header div)
           * https://api.jquery.com/offset/
        */
        offset = $('#container').offset(),

        /* This function is called after the splitter-bar has been moved
        */
        splitter = function(event, ui){
            /* After the splitter-bar is moved, ui.position.left contains the location 
               of the splitter-bar's left edge
            */
            var splitterBarLeft = parseInt(ui.position.left, 10),

                // The table-of-contents total-width is the same as splitterBarLeft
                tocTotalWidth = splitterBarLeft,
            
                /* For the table-of-contents div, its total-width is:
                   * (content-area width) + (padding-left width)
                   * The padding-left width is 20
                   tocWidth is the content-area width
                   * Math.max(0, ...) ensures the tocWidth is not negative
                */
                tocWidth = Math.max(0, (tocTotalWidth - 20)),  
            
                /* For the document div, its left position is:
                   * (table-of-contents total-width) + (splitter-bar width)
                   * The splitter-bar width is 12
                */
                documentLeft =  tocTotalWidth + 12, 
            
                /* For the document div, its content-area width is specified
                   in the CSS file
                   * Math.max(0, ...) ensures the tocWidth is not negative
                */
                documentWidth = Math.max(0, ((totalWidth - tocTotalWidth) - (12 + 20 + 20 + 2)))
            ; // END OF: var section

            /* Set the new values, for the CSS IDs and declarations
            */
            $('#table-of-contents').css({width : tocWidth}); 
            $('#document').css({left : documentLeft});                         
            $('#document').css({width : documentWidth}); 
        } // END OF: function(event, ui)
    ; // END OF: var section
        
    // https://jqueryui.com/draggable/
    $('#splitter-bar').draggable({
        // Controlling the movement of the splitter-bar along the x-axis
        axis : 'x',
        
        // Specifies the left and right boundaries for the splitter-bar
        // * A boundary is specified for the splitter-bar's left-edge
        // * A boundary is specified by the pair: left-position and top-position
        containment : [
            // Left-side boundary for the splitter-bar 
            20, // Left-position. Prevent tocWidth from becoming negative
            offset.top,
            
            // Right-side boundary for the splitter-bar             
            (totalWidth - (12 + 20 + 20 + 2)),  // Left-position. Prevent documentWidth from becoming negative
            offset.top
            ],
        
        // Specifies the function called for dragging
        drag : splitter
    }); // END OF:  ('#splitter-bar').draggable

}); // END OF:  $(function(){


/* This function is run when the browser-window is resized.
   * It reloads the web-page. 
   * Reloading resets the sizing and the alignment, for the web-page's sections.

https://stackoverflow.com/questions/14915653/refresh-page-on-resize-with-javascript-or-jquery
https://stackoverflow.com/questions/5836779/how-can-i-refresh-the-screen-on-browser-resize
https://stackoverflow.com/questions/29546539/refresh-page-when-container-div-is-resized
*/
$(window).bind('resize', function(e)
{
  if (window.RT) clearTimeout(window.RT);
  window.RT = setTimeout(function()
  {
    this.location.reload(false); /* false to get page from cache */
  }, 100);
});