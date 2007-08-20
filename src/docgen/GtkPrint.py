#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007       Zsolt Foldvari
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""Printing interface based on gtk.Print*.
"""

__revision__ = "$Revision$"

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
import BaseDoc
from PluginUtils import register_text_doc, register_draw_doc, register_book_doc
import Errors

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".GtkPrint")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gtk
import cairo
import pango
import pangocairo

if gtk.pygtk_version < (2,10,0):
    raise Errors.UnavailableError(_("PyGtk 2.10 or later is required"))

###------------------------------------------------------------------------
###
### PreviewCanvas and PreviewWindow
###
### These classes provide a simple print preview functionality.
### They do not actually render anything themselves, they rely
### upon the Print opertaion to do the rendering.
###
###------------------------------------------------------------------------
##class PreviewCanvas(gtk.DrawingArea):
    ##"""Provide a simple widget for displaying a
    ##cairo rendering used to show print preview windows.
    ##"""
    
    ##def __init__(self,
                 ##operation,
                 ##preview_operation,
                 ##print_context):
        ##gtk.DrawingArea.__init__(self)
        ##self._operation = operation
        ##self._preview_operation = preview_operation
        ##self._print_context = print_context

        ##self.connect("expose_event",self.expose)
        ##self.connect("realize",self.realize)
        
        ##self._page_no = 1 # always start on page 1


    ##def set_page(self,page):
        ##"""Change which page is displayed"""
        ##if page > 0:
            ##self._page_no = page
            ##self.queue_draw()
        
    ##def realize(self, dummy=None):
        ##"""Generate the cairo context for this drawing area
        ##and pass it to the print context."""
        ##gtk.DrawingArea.realize(self)
        ##self._context = self.window.cairo_create()
        ##self._print_context.set_cairo_context(self._context,72,72)

    ##def expose(self, widget, event):
        ##"""Ask the print operation to actually draw the page."""
        ##self.window.clear()
        ##self._preview_operation.render_page(self._page_no)

        ### need to calculate how large the widget now is and
        ### set it so that the scrollbars are updated.
        ### I can't work out how to do this.
        ###self.set_size_request(200, 300)

    
##class PreviewWindow(gtk.Window):
    ##"""A dialog to show a print preview."""
    
    ##def __init__(self,
                 ##operation,
                 ##preview_operation,
                 ##print_context,
                 ##parent):
        ##gtk.Window.__init__(self)
        ##self.set_default_size(640, 480)

        ##self._operation = operation
        ##self._preview_operation = preview_operation

        ##self.connect("delete_event", self.delete_event)

        ##self.set_title("Print Preview")
        ##self.set_transient_for(parent)

        ### Setup widgets
        ##self._vbox = gtk.VBox()
        ##self.add(self._vbox)
        ##self._spin = gtk.SpinButton()
        ##self._spin.set_value(1)
        
        ##self._close_bt = gtk.Button(stock=gtk.STOCK_CLOSE)
        ##self._close_bt.connect("clicked",self.close)
                               
        ##self._hbox = gtk.HBox()
        ##self._hbox.pack_start(self._spin)
        ##self._hbox.pack_start(self._close_bt,expand=False)
        ##self._vbox.pack_start(self._hbox,expand=False)


        ##self._scroll = gtk.ScrolledWindow(None,None)
        ##self._canvas = PreviewCanvas(operation,preview_operation,print_context)
        ##self._scroll.add_with_viewport(self._canvas)
        ##self._vbox.pack_start(self._scroll,expand=True,fill=True)

        ### The print operation does not know how many pages there are until
        ### after the first expose event, so we use the expose event to
        ### trigger an update of the spin box.
        ### This still does not work properly, sometimes the first expose event
        ### happends before this gets connected and the spin box does not get
        ### updated, I am probably just not doing it very cleverly.
        ##self._change_n_pages_connect_id = self._canvas.connect("expose_event", self.change_n_pages)
        ##self._spin.connect("value-changed",
                           ##lambda spinbutton: self._canvas.set_page(spinbutton.get_value_as_int()))
        
        ##self._canvas.set_double_buffered(False)

        ##self.show_all()



    ##def change_n_pages(self, widget, event ):
        ##"""Update the spin box to have the correct number of pages for the
        ##print operation"""
        ##n_pages = self._preview_operation.get_property("n_pages")
        
        ##if n_pages != -1:
            ### As soon as we have a valid number of pages we no
            ### longer need this call back so we can disconnect it.
            ##self._canvas.disconnect(self._change_n_pages_connect_id)
            
        ##value = int(self._spin.get_value())
        ##if value == -1: value = 1
        ##self._spin.configure(gtk.Adjustment(value,1,
                                            ##n_pages,
                                            ##1,1,1),1,0)

    ##def end_preview(self):
        ##self._operation.end_preview()
        
    ##def delete_event(self, widget, event, data=None):
        ##self.end_preview()
        ##return False

    ##def close(self,btn):
        ##self.end_preview()
        ##self.destroy()

        ### I am not sure that this is the correct way to do this
        ### but I expect the print dialog to reappear after I
        ### close the print preview button.
        ##self._operation.do_print()
        ##return False       

#------------------------------------------------------------------------
#
# Font selection
#
#------------------------------------------------------------------------

_TTF_FREEFONT = {
    BaseDoc.FONT_SERIF: 'FreeSerif',
    BaseDoc.FONT_SANS_SERIF: 'FreeSans',
    BaseDoc.FONT_MONOSPACE: 'FreeMono',
}

_MS_TTFONT = {
    BaseDoc.FONT_SERIF: 'Times New Roman',
    BaseDoc.FONT_SANS_SERIF: 'Arial',
    BaseDoc.FONT_MONOSPACE: 'Courier New',
}

_GNOME_FONT = {
    BaseDoc.FONT_SERIF: 'Serif',
    BaseDoc.FONT_SANS_SERIF: 'Sans',
    BaseDoc.FONT_MONOSPACE: 'Monospace',
}

font_families = _GNOME_FONT

def set_font_families(pango_context):
    """Set the used font families depending on availability.
    """
    global font_families
    
    families = pango_context.list_families()
    family_names = [family.get_name() for family in families]
    
    fam = [f for f in _TTF_FREEFONT.values() if f in family_names]
    if len(fam) == len(_TTF_FREEFONT):
        font_families = _TTF_FREEFONT
        log.debug('Using FreeFonts: %s' % font_families)
        return
    
    fam = [f for f in _MS_TTFONT.values() if f in family_names]
    if len(fam) == len(_MS_TTFONT):
        font_families = _MS_TTFONT
        log.debug('Using MS TrueType fonts: %s' % font_families)
        return
    
    fam = [f for f in _GNOME_FONT.values() if f in family_names]
    if len(fam) == len(_GNOME_FONT):
        font_families = _GNOME_FONT
        log.debug('Using Gnome fonts: %s' % font_families)
        return
    
    log.debug('No fonts found.')
    
#------------------------------------------------------------------------
#
# Converter functions
#
#------------------------------------------------------------------------

def paperstyle_to_pagesetup(paper_style):
    """Convert a BaseDoc.PaperStyle instance into a gtk.PageSetup instance.
    
    @param paper_style: Gramps paper style object to convert
    @param type: BaseDoc.PaperStyle
    @return: page_setup
    @rtype: gtk.PageSetup
    """
    gramps_to_gtk = {
        "Letter": "na_letter",
        "Legal": "na_legal",
        "A0": "iso_a0",
        "A1": "iso_a1",
        "A2": "iso_a2",
        "A3": "iso_a3",
        "A4": "iso_a4",
        "A5": "iso_a5",
        "B0": "iso_b0",
        "B1": "iso_b1",
        "B2": "iso_b2",
        "B3": "iso_b3",
        "B4": "iso_b4",
        "B5": "iso_b5",
        "B6": "iso_b6",
        "B": "iso_b",
        "C": "iso_c",
        "D": "iso_d",
        "E": "iso_e",
    }

    # First set the paper size
    gramps_paper_size = paper_style.get_size()
    gramps_paper_name = gramps_paper_size.get_name()
    
    if gramps_to_gtk.has_key(gramps_paper_name):
        paper_size = gtk.PaperSize(gramps_to_gtk[gramps_paper_name])
    elif gramps_paper_name == "Custom Size":
        paper_width = gramps_paper_size.get_width() * 10
        paper_height = gramps_paper_size.get_height() * 10
        paper_size = gtk.paper_size_new_custom("custom",
                                               "Custom Size",
                                               paper_width,
                                               paper_height,
                                               gtk.UNIT_MM)
    else:
        def_paper_size_name = gtk.paper_size_get_default()
        paper_size = gtk.PaperSize(def_paper_size_name)
        log.debug("Unknown paper size, falling back to the default: %s" %
                  def_paper_size_name)
        
    page_setup = gtk.PageSetup()
    page_setup.set_paper_size(paper_size)
    
    # Set paper orientation
    if paper_style.get_orientation() == BaseDoc.PAPER_PORTRAIT:
        page_setup.set_orientation(gtk.PAGE_ORIENTATION_PORTRAIT)
    else:
        page_setup.set_orientation(gtk.PAGE_ORIENTATION_LANDSCAPE)

    # gtk.PageSize provides default margins for the standard papers.
    # Anyhow, we overwrite those with the settings from Gramps,
    # though at the moment all of them are fixed at 1 inch.
    page_setup.set_top_margin(paper_style.get_top_margin() * 10,
                              gtk.UNIT_MM)
    page_setup.set_bottom_margin(paper_style.get_bottom_margin() * 10,
                                 gtk.UNIT_MM)
    page_setup.set_left_margin(paper_style.get_left_margin() * 10,
                               gtk.UNIT_MM)
    page_setup.set_right_margin(paper_style.get_right_margin() * 10,
                                gtk.UNIT_MM)
    
    return page_setup

def fontstyle_to_fontdescription(font_style):
    """Convert a BaseDoc.FontStyle instance to a pango.FontDescription one.
    
    Font color and underline is not implemented in pango.FontDescription,
    and has to be set with pango.Layout.set_attributes(attrlist) method.
    
    """
    if font_style.get_bold():
        f_weight = pango.WEIGHT_BOLD
    else:
        f_weight = pango.WEIGHT_NORMAL
        
    if font_style.get_italic():
        f_style = pango.STYLE_ITALIC
    else:
        f_style = pango.STYLE_NORMAL
        
    font_description = pango.FontDescription(font_families[font_style.face])
    font_description.set_size(font_style.get_size() * pango.SCALE)
    font_description.set_weight(f_weight)
    font_description.set_style(f_style)
    
    return font_description

def tabstops_to_tabarray(tab_stops, dpi):
    """Convert a list of tabs given in cm to a pango.TabArray.
    """
    tab_array = pango.TabArray(len(tab_stops), False)
    
    for index in range(len(tab_stops)):
        location = tab_stops[index] * dpi * pango.SCALE / 2.54
        tab_array.set_tab(index, pango.TAB_LEFT, int(location))
        
    return tab_array

#------------------------------------------------------------------------
#
# Table row style
#
#------------------------------------------------------------------------
        
class RowStyle(list):
    """Specifies the format of a table row.
    
    RowStyle extents the available styles in BaseDoc.
    
    The RowStyle contains the width of each column as a percentage of the
    width of the full row. Note! The width of the row is not know until
    divide() or draw() method is called.
    
    """
    def __init__(self):
        self.columns = []

    def set_columns(self, columns):
        """Set the number of columns.

        @param columns: number of columns that should be used.
        @param type: int
        
        """
        self.columns = columns

    def get_columns(self):
        """Return the number of columns.
        """
        return self.columns 

    def set_column_widths(self, clist):
        """Set the width of all the columns at once.
        
        @param clist: list of width of columns in % of the full row.
        @param tyle: list
        
        """
        self.columns = len(clist)
        for i in range(self.columns):
            self.colwid[i] = clist[i]

    def set_column_width(self, index, width):
        """
        Sets the width of a specified column to the specified width.

        @param index: column being set (index starts at 0)
        @param width: percentage of the table width assigned to the column
        """
        self.colwid[index] = width

    def get_column_width(self, index):
        """
        Returns the column width of the specified column as a percentage of
        the entire table width.

        @param index: column to return (index starts at 0)
        """
        return self.colwid[index]

#------------------------------------------------------------------------
#
# Document element classes
#
#------------------------------------------------------------------------
        
class GtkDocBaseElement(object):
    """Base of all document elements.
    
    Support document element structuring and can render itself onto
    a Cairo surface.
    
    There are two cathegories of methods:
      1. hierarchy building methods (add_child, get_children, set_parent,
         get_parent);
      2. rendering methods (divide, draw).
      
    The hierarchy building methods generally don't have to be overriden in
    the subclass, while the rendering methods (divide, draw) must be
    implemented in the subclasses.
    
    """
    _type = 'BASE'
    _allowed_children = []
    
    def __init__(self, style=None):
        self._parent = None
        self._children = []
        self._style = style
    
    def get_type(self):
        """Get the type of this element.
        """
        return self._type
    
    def set_parent(self, parent):
        """Set the parent element of this element.
        """
        self._parent = parent
        
    def get_parent(self):
        """Get the parent element of this element.
        """
        return self._parent
    
    def add_child(self, element):
        """Add a child element.
        
        Returns False if the child cannot be added (e.g. not an allowed type),
        or True otherwise.
        
        """
        # check if it is an allowed child for this type
        if element.get_type() not in self._allowed_children:
            log.debug("%r is not an allowed child for %r" %
                      (element.__class__, self.__class__))
            return False
        
        # append the child and set it's parent
        self._children.append(element)
        element.set_parent(self)
        return True
        
    def get_children(self):
        """Get the list of children of this element.
        """
        return self._children
    
    def divide(self, layout, width, height, dpi_x, dpi_y):
        """Divide the element into two depending on available space.
        
        @param layout: pango layout to write on
        @param type: pango.Layout
        @param width: width of available space for this element
        @param type: device points
        @param height: height of available space for this element
        @param type: device points
        @param dpi_x: the horizontal resolution
        @param type: dots per inch
        @param dpi_y: the vertical resolution
        @param type: dots per inch
        
        @return: the divided element, and the height of the first part
        @rtype: (GtkDocXXX-1, GtkDocXXX-2), device points
        
        """
        raise NotImplementedError
    
    def draw(self, cairo_context, pango_layout, width, dpi_x, dpi_y):
        """Draw itself onto a cairo surface.
        
        @param cairo_context: context to draw on
        @param type: cairo.Context class
        @param pango_layout: pango layout to write on
        @param type: pango.Layout class
        @param width: width of available space for this element
        @param type: device points
        @param dpi_x: the horizontal resolution
        @param type: dots per inch
        @param dpi_y: the vertical resolution
        @param type: dots per inch        
        
        @return: height of the element
        @rtype: device points
        
        """
        raise NotImplementedError
    
class GtkDocDocument(GtkDocBaseElement):
    """The whole document or a page.
    """
    _type = 'DOCUMENT'
    _allowed_children = ['PARAGRAPH', 'PAGEBREAK', 'TABLE', 'IMAGE']
    
    def draw(self, cairo_context, pango_layout, width, dpi_x, dpi_y):
            
        x = y = elem_height = 0
        
        for elem in self._children:
            cairo_context.translate(x, elem_height)
            elem_height = elem.draw(cairo_context, pango_layout,
                                    width, dpi_x, dpi_y)
            y += elem_height
            
        return y
    
class GtkDocPagebreak(GtkDocBaseElement):
    """Implement a page break.
    """
    _type = 'PAGEBREAK'
    _allowed_children = []
    
    def divide(self, layout, width, height, dpi_x, dpi_y):
        return (None, None), 0
    
class GtkDocParagraph(GtkDocBaseElement):
    """Paragraph.
    """
    _type = 'PARAGRAPH'
    _allowed_children = []
    
    # line spacing is not defined in BaseDoc.ParagraphStyle
    spacing = 2
    
    def __init__(self, style, leader=None):
        GtkDocBaseElement.__init__(self, style)

        if leader:
            self._text = leader + '\t'
            # FIXME append new tab to the existing tab list
            self._style.set_tabs([-1 * self._style.get_first_indent()])
        else:
            self._text = ''
        
    def add_text(self, text):
        self._text = self._text + text
        
    def divide(self, layout, width, height, dpi_x, dpi_y):
        l_margin = self._style.get_left_margin() * dpi_x / 2.54
        r_margin = self._style.get_right_margin() * dpi_x / 2.54
        t_margin = self._style.get_top_margin() * dpi_y / 2.54
        b_margin = self._style.get_bottom_margin() * dpi_y / 2.54
        h_padding = self._style.get_padding() * dpi_x / 2.54
        v_padding = self._style.get_padding() * dpi_y / 2.54
        f_indent = self._style.get_first_indent() * dpi_x / 2.54
        
        # calculate real width available for text
        text_width = width - l_margin - 2 * h_padding - r_margin
        if f_indent < 0:
            text_width -= f_indent
        layout.set_width(int(text_width * pango.SCALE))
        
        # set paragraph properties
        layout.set_wrap(pango.WRAP_WORD_CHAR)
        layout.set_spacing(self.spacing * pango.SCALE)
        layout.set_indent(int(f_indent * pango.SCALE))
        layout.set_tabs(tabstops_to_tabarray(self._style.get_tabs(), dpi_x))
        #
        align = self._style.get_alignment_text()
        if align == 'left':
            layout.set_alignment(pango.ALIGN_LEFT)
        elif align == 'right':
            layout.set_alignment(pango.ALIGN_RIGHT)
        elif align == 'center':
            layout.set_alignment(pango.ALIGN_CENTER)
        elif align == 'justify':
            layout.set_justify(True)
        #
        font_style = self._style.get_font()
        layout.set_font_description(fontstyle_to_fontdescription(font_style))
        
        # calculate the height of one line
        layout.set_text('Test')
        layout_width, layout_height = layout.get_size()
        line_height = layout_height / pango.SCALE + self.spacing
        # and the number of lines fit on the available height
        text_height = height - t_margin - 2 * v_padding
        line_per_height = text_height / line_height
        
        # if nothing fits
        if line_per_height < 1:
            return (None, self), 0
        
        # calculate where to cut the paragraph
        layout.set_markup(self._text)
        layout_width, layout_height = layout.get_size()
        line_count = layout.get_line_count()
        
        # if all paragraph fits we don't need to cut
        if line_count <= line_per_height:
            paragraph_height = ((layout_height / pango.SCALE) +
                                t_margin +
                                (2 * v_padding))
            if height - paragraph_height > b_margin:
                paragraph_height += b_margin
            return (self, None), paragraph_height
        
        # get index of first character which doesn't fit on available height
        layout_line = layout.get_line(int(line_per_height))
        index = layout_line.start_index
        # and divide the text, first create the second part
        new_style = BaseDoc.ParagraphStyle(self._style)
        new_style.set_top_margin(0)
        new_paragraph = GtkDocParagraph(new_style)
        new_paragraph.add_text(self._text.encode('utf-8')[index:])
        # then update the first one
        self._text = self._text.encode('utf-8')[:index]
        self._style.set_bottom_margin(0)
        
        # FIXME do we need to return the proper height???
        #paragraph_height = line_height * line_count + t_margin + 2 * v_padding
        paragraph_height = 0
        return (self, new_paragraph), paragraph_height
    
    def draw(self, cr, layout, width, dpi_x, dpi_y):
        l_margin = self._style.get_left_margin() * dpi_x / 2.54
        r_margin = self._style.get_right_margin() * dpi_x / 2.54
        t_margin = self._style.get_top_margin() * dpi_y / 2.54
        b_margin = self._style.get_bottom_margin() * dpi_y / 2.54
        h_padding = self._style.get_padding() * dpi_x / 2.54
        v_padding = self._style.get_padding() * dpi_y / 2.54
        f_indent = self._style.get_first_indent() * dpi_x / 2.54
        
        # calculate real width available for text
        text_width = width - l_margin - 2 * h_padding - r_margin
        if f_indent < 0:
            text_width -= f_indent
        layout.set_width(int(text_width * pango.SCALE))
        
        # set paragraph properties
        layout.set_wrap(pango.WRAP_WORD_CHAR)
        layout.set_spacing(self.spacing * pango.SCALE)
        layout.set_indent(int(f_indent * pango.SCALE))
        layout.set_tabs(tabstops_to_tabarray(self._style.get_tabs(), dpi_x))
        #
        align = self._style.get_alignment_text()
        if align == 'left':
            layout.set_alignment(pango.ALIGN_LEFT)
        elif align == 'right':
            layout.set_alignment(pango.ALIGN_RIGHT)
        elif align == 'center':
            layout.set_alignment(pango.ALIGN_CENTER)
        elif align == 'justify':
            layout.set_justify(True)
        #
        font_style = self._style.get_font()
        layout.set_font_description(fontstyle_to_fontdescription(font_style))

        # layout the text
        layout.set_markup(self._text)
        layout_width, layout_height = layout.get_size()
        
        # render the layout onto the cairo surface
        x = l_margin + h_padding
        if f_indent < 0:
            x += f_indent
        cr.move_to(x, t_margin + v_padding)
        cr.set_source_rgb(0, 0, 0)
        cr.show_layout(layout)
        
        # calculate the full paragraph height
        height = layout_height/pango.SCALE + t_margin + 2*v_padding + b_margin

        # draw the borders
        if self._style.get_top_border():
            cr.move_to(l_margin, t_margin)
            cr.rel_line_to(width - l_margin - r_margin, 0)
        if self._style.get_right_border():
            cr.move_to(width - r_margin, t_margin)
            cr.rel_line_to(0, height - t_margin - b_margin)
        if self._style.get_bottom_border():
            cr.move_to(l_margin, height - b_margin)
            cr.rel_line_to(width - l_margin - r_margin, 0)
        if self._style.get_left_border():
            cr.move_to(l_margin, t_margin)
            cr.line_to(0, height - t_margin - b_margin)

        cr.set_line_width(1)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()
        
        if DEBUG:
            cr.set_line_width(0.1)
            cr.set_source_rgb(1.0, 0, 0)
            cr.rectangle(0, 0, width, height)
            cr.stroke()
            cr.set_source_rgb(0, 0, 1.0)
            cr.rectangle(l_margin, t_margin,
                         width-l_margin-r_margin, height-t_margin-b_margin)
            cr.stroke()
        
        return height
        
class GtkDocTable(GtkDocBaseElement):
    """Implement a table.
    """
    _type = 'TABLE'
    _allowed_children = ['ROW']
    
    def divide(self, layout, width, height, dpi_x, dpi_y):
        #calculate real table width
        table_width = width * self._style.get_width() / 100
        
        # calculate the height of each row
        table_height = 0
        row_index = 0
        while row_index < len(self._children):
            row = self._children[row_index]
            (r1, r2), row_height = row.divide(layout, table_width, height,
                                              dpi_x, dpi_y)
            if table_height + row_height >= height:
                break
            table_height += row_height
            row_index += 1
            
        # divide the table if any row did not fit
        new_table = None
        if row_index < len(self._children):
            new_table = GtkDocTable(self._style)
            for row in self._children[row_index:]:
                new_table.add_child(row)
            del self._children[row_index:]
            
        return (self, new_table), table_height
    
    def draw(self, cr, layout, width, dpi_x, dpi_y):
        #calculate real table width
        table_width = width * self._style.get_width() / 100
        # TODO is a table always left aligned??
        table_height = 0
        
        # draw all the rows
        for row in self._children:
            cr.save()
            cr.translate(0, table_height)
            row_height = row.draw(cr, layout, table_width, dpi_x, dpi_y)
            cr.restore()
            table_height += row_height
            
        if DEBUG:
            cr.set_line_width(0.1)
            cr.set_source_rgb(1.0, 0, 0)
            cr.rectangle(0, 0, table_width, table_height)
            cr.stroke()

        return table_height

class GtkDocTableRow(GtkDocBaseElement):
    """Implement a row in a table.
    """
    _type = 'ROW'
    _allowed_children = ['CELL']

    def divide(self, layout, width, height, dpi_x, dpi_y):
        # the highest cell gives the height of the row
        cell_heights = []
        cell_width_iter = self._style.__iter__()
        for cell in self._children:
            cell_width = 0
            for i in range(cell.get_span()):
                cell_width += cell_width_iter.next()
            cell_width = cell_width * width / 100
            (c1, c2), cell_height = cell.divide(layout, cell_width, height,
                                                dpi_x, dpi_y)
            cell_heights.append(cell_height)
        
        # save height [inch] of the row to be able to draw exact cell border
        row_height = max(cell_heights)
        self.height = row_height / dpi_y
        
        return (self, None), row_height
    
    def draw(self, cr, layout, width, dpi_x, dpi_y):
        cr.save()

        # get the height of this row
        row_height = self.height * dpi_y

        # draw all the cells in the row
        cell_width_iter = self._style.__iter__()
        for cell in self._children:
            cell_width = 0
            for i in range(cell.get_span()):
                cell_width += cell_width_iter.next()
            cell_width = cell_width * width / 100
            cell.draw(cr, layout, cell_width, row_height, dpi_x, dpi_y)
            cr.translate(cell_width, 0)
        cr.restore()

        if DEBUG:
            cr.set_line_width(0.1)
            cr.set_source_rgb(0, 0, 1.0)
            cr.rectangle(0, 0, width, row_height)
            cr.stroke()
            
        return row_height

class GtkDocTableCell(GtkDocBaseElement):
    """Implement a cell in a table row.
    """
    _type = 'CELL'
    _allowed_children = ['PARAGRAPH', 'IMAGE']
    
    def __init__(self, style, span=1):
        GtkDocBaseElement.__init__(self, style)
        self._span = span

    def get_span(self):
        return self._span
    
    def divide(self, layout, width, height, dpi_x, dpi_y):
        h_padding = self._style.get_padding() * dpi_x / 2.54
        v_padding = self._style.get_padding() * dpi_y / 2.54

        # calculate real available width
        width -= 2 * h_padding

        # calculate height of each children
        cell_height = 0
        for child in self._children:
            (e1, e2), child_height = child.divide(layout, width, height,
                                                 dpi_x, dpi_y)
            cell_height += child_height
        
        # calculate real height
        cell_height += 2 * v_padding
        
        return (self, None), cell_height
    
    def draw(self, cr, layout, width, cell_height, dpi_x, dpi_y):
        """Draw a cell.
        
        This draw method is a bit different from the others, as common
        cell height of all cells in a row is also given as parameter.
        This is needed to be able to draw proper vertical borders around
        each cell, i.e. the border should be as long as the highest cell
        in the given row.
        
        """
        h_padding = self._style.get_padding() * dpi_x / 2.54
        v_padding = self._style.get_padding() * dpi_y / 2.54

        # calculate real available width
        i_width = width - 2 * h_padding
        
        # draw children
        cr.save()
        cr.translate(h_padding, v_padding)
        for child in self._children:
            child_height = child.draw(cr, layout, i_width, dpi_x, dpi_y)
            cr.translate(0, child_height)
        cr.restore()
        
        # draw the borders
        if self._style.get_top_border():
            cr.move_to(0, 0)
            cr.rel_line_to(width , 0)
        if self._style.get_right_border():
            cr.move_to(width, 0)
            cr.rel_line_to(0, cell_height)
        if self._style.get_bottom_border():
            cr.move_to(0, cell_height)
            cr.rel_line_to(width, 0)
        if self._style.get_left_border():
            cr.move_to(0, 0)
            cr.line_to(0, cell_height)

        cr.set_line_width(1)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()
        
        if DEBUG:
            cr.set_line_width(0.1)
            cr.set_source_rgb(0, 1.0, 0)
            cr.rectangle(0, 0, width, cell_height)
            cr.stroke()
            
        return cell_height

class GtkDocPicture(GtkDocBaseElement):
    """Implement an image.
    """
    _type = 'IMAGE'
    _allowed_children = []
    
    def __init__(self, style, filename, width, height):
        GtkDocBaseElement.__init__(self, style)
        self._filename = filename
        self._width = width
        self._height = height
    
    def divide(self, layout, width, height, dpi_x, dpi_y):
        img_width = self._width * dpi_x / 2.54
        img_height = self._height * dpi_y / 2.54
        
        if img_height <= height:
            return (self, None), img_height
        else:
            return (None, self), 0

    def draw(self, cr, layout, width, dpi_x, dpi_y):
        img_width = self._width * dpi_x / 2.54
        img_height = self._height * dpi_y / 2.54
        
        if self._style == 'right':
            l_margin = width - img_width
        elif self._style == 'center':
            l_margin = (width - img_width) / 2.0
        else:
            l_margin = 0
        
        # load the image and get its extents
        pixbuf = gtk.gdk.pixbuf_new_from_file(self._filename)
        pixbuf_width = pixbuf.get_width()
        pixbuf_height = pixbuf.get_height()
        
        # calculate the scale to fit image into the set extents
        scale = min(img_width / pixbuf_width, img_height / pixbuf_height)
        
        # draw the image
        cr.save()
        cr.translate(l_margin, 0)
        cr.scale(scale, scale)
        gcr = gtk.gdk.CairoContext(cr)
        gcr.set_source_pixbuf(pixbuf,
                              (img_width / scale - pixbuf_width) / 2,
                              (img_height / scale - pixbuf_height) / 2)
        cr.rectangle(0 , 0, img_width / scale, img_height / scale)
        ##gcr.set_source_pixbuf(pixbuf,
                              ##(img_width - pixbuf_width) / 2,
                              ##(img_height - pixbuf_height) / 2)
        ##cr.rectangle(0 , 0, img_width, img_height)
        ##cr.scale(scale, scale)
        cr.fill()
        cr.restore()
        
        if DEBUG:
            cr.set_line_width(0.1)
            cr.set_source_rgb(1.0, 0, 0)
            cr.rectangle(l_margin, 0, img_width, img_height)
            cr.stroke()

        return (img_height)
                
#------------------------------------------------------------------------
#
# CairoDoc and GtkPrint class
#
#------------------------------------------------------------------------
class CairoDoc(BaseDoc.BaseDoc, BaseDoc.TextDoc, BaseDoc.DrawDoc):
    """Act as an abstract document that can render onto a cairo context.
    
    Maintains an abstract model of the document. The root of this abstract
    document is self._doc. The model is build via the subclassed BaseDoc, and
    the implemented TextDoc, DrawDoc interface methods.
    
    It can render the model onto cairo context pages, according to the received
    page style.
        
    """
    
    # BaseDoc implementation
    
    def open(self, filename):
        self._doc = GtkDocDocument()
        self._active_element = self._doc
        self._pages = []
    
    def close(self):
        raise NotImplementedError
    
    # TextDoc implementation
    
    def page_break(self):
        self._active_element.add_child(GtkDocPagebreak())

    def start_bold(self):
        self.write_text('<b>')
    
    def end_bold(self):
        self.write_text('</b>')
    
    def start_superscript(self):
        self.write_text('<small><sup>')
    
    def end_superscript(self):
        self.write_text('</sup></small>')
    
    def start_paragraph(self, style_name, leader=None):
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_paragraph_style(style_name)
        
        new_paragraph = GtkDocParagraph(style, leader)
        self._active_element.add_child(new_paragraph)
        self._active_element = new_paragraph
    
    def end_paragraph(self):
        self._active_element = self._active_element.get_parent()
    
    def start_table(self, name, style_name):
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_table_style(style_name)
        
        new_table = GtkDocTable(style)
        self._active_element.add_child(new_table)
        self._active_element = new_table
        
        # we need to remember the column width list from the table style.
        # this is an ugly hack, but got no better idea.
        self._active_row_style = []
        for i in range(style.get_columns()):
            self._active_row_style.append(style.get_column_width(i))
    
    def end_table(self):
        self._active_element = self._active_element.get_parent()
    
    def start_row(self):
        new_row = GtkDocTableRow(self._active_row_style)
        self._active_element.add_child(new_row)
        self._active_element = new_row
    
    def end_row(self):
        self._active_element = self._active_element.get_parent()
    
    def start_cell(self, style_name, span=1):
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_cell_style(style_name)
        
        new_cell = GtkDocTableCell(style, span)
        self._active_element.add_child(new_cell)
        self._active_element = new_cell
    
    def end_cell(self):
        self._active_element = self._active_element.get_parent()
    
    def write_note(self, text, format, style_name):
        if format == 1:
            for line in text.split('\n'):
                self.start_paragraph(style_name)
                self.write_text(line)
                self.end_paragraph()
        elif format == 0:
            for line in text.split('\n\n'):
                self.start_paragraph(style_name)
                line = line.replace('\n',' ')
                line = ' '.join(line.split())
                self.write_text(line)
                self.end_paragraph()

    def write_text(self, text, mark=None):
        # FIXME this is ugly, do we really need it?
        text = text.replace('<super>', '<small><sup>')
        text = text.replace('</super>', '</sup></small>')
        self._active_element.add_text(text)
    
    def add_media_object(self, name, pos, x_cm, y_cm):
        new_image = GtkDocPicture(pos, name, x_cm, y_cm)
        self._active_element.add_child(new_image)

    # DrawDoc implementation
    
    def start_page(self):
        pass
    
    def end_page(self):
        pass
    
    def draw_path(self, style, path):
        pass
        
    def draw_box(self, style, text, x, y, w, h):
        pass
    
    def draw_text(self, style, text, x, y):
        pass
    
    def center_text(self, style, text, x, y):
        pass
    
    def draw_line(self, style, x1, y1, x2, y2):
        pass

    def rotate_text(self, style, text, x, y, angle):
        pass
    
class GtkPrint(CairoDoc):
    
    def close(self):
        page_setup = paperstyle_to_pagesetup(self.paper)
        
        print_operation = gtk.PrintOperation()
        print_operation.set_default_page_setup(page_setup)
        print_operation.set_show_progress(True)
        print_operation.connect("begin_print", self.on_begin_print)
        print_operation.connect("draw_page", self.on_draw_page)
        print_operation.connect("paginate", self.on_paginate)
        print_operation.connect("preview", self.on_preview)        

        self.print_settings = None
        self.do_print(print_operation)

    def do_print(self, operation):
        """Run the Gtk Print operation.
        """
        # set print settings if it was stored previously
        if self.print_settings is not None:
            operation.set_print_settings(self.print_settings)

        # run print dialog
        res = operation.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG, None)
        
        # store print settings if printing was successful
        if res == gtk.PRINT_OPERATION_RESULT_APPLY:
            self.print_settings = operation.get_print_settings()

    def on_begin_print(self, operation, context):
        """Setup environment for printing.
        """
        # choose installed font faces
        set_font_families(context.create_pango_context())
        
        # get page size
        self.page_width = context.get_width()
        self.page_height = context.get_height()
        
        # get all document level elements and beging a new page
        self.elements_to_paginate = self._doc.get_children()
        self._pages.append(GtkDocDocument())
        self.available_height = self.page_height
       
    def on_paginate(self, operation, context):
        """Paginate the whole document in chunks.
        
        Only one document level element is handled at one run.
        
        """
        layout = context.create_pango_layout()
        dpi_x = context.get_dpi_x()
        dpi_y = context.get_dpi_y()
        
        # try to fit the next element to current page, divide it if needed
        elem = self.elements_to_paginate.pop(0)
        (e1, e2), e1_h = elem.divide(layout,
                                     self.page_width,
                                     self.available_height,
                                     dpi_x,
                                     dpi_y)

        # if (part of) it fits on current page add it
        if e1 is not None:
            self._pages[len(self._pages) - 1].add_child(e1)

        # if elem was divided remember the second half to be processed
        if e2 is not None:
            self.elements_to_paginate.insert(0, e2)

        # calculate how much space left on current page
        self.available_height -= e1_h

        # start new page if needed
        if (e1 is None) or (e2 is not None):
            self._pages.append(GtkDocDocument())
            self.available_height = self.page_height
            
        # update page number
        operation.set_n_pages(len(self._pages))
        
        # tell operation whether we finished or not
        finished = len(self.elements_to_paginate) == 0
        return finished

    def on_draw_page(self,operation, context, page_nr):
        """Draw the requested page.
        """
        cr = context.get_cairo_context()
        layout = context.create_pango_layout()
        dpi_x = context.get_dpi_x()
        dpi_y = context.get_dpi_y()

        if DEBUG:
            cr.set_line_width(0.1)
            cr.set_source_rgb(0, 1.0, 0)
            cr.rectangle(0, 0, self.page_width, self.page_height)
            cr.stroke()

        self._pages[page_nr].draw(cr, layout, self.page_width, dpi_x, dpi_y)
        
    def on_preview(self, operation, preview, context, parent, dummy=None):
        """Implement custom print preview functionality.
        """
        #preview = PreviewWindow(self, preview, context, parent)
        return False
        

#------------------------------------------------------------------------
#
# Register the document generator with the GRAMPS plugin system
#
#------------------------------------------------------------------------
DEBUG = False
#raise Errors.UnavailableError("Work in progress...")
register_text_doc(_('Print... (Gtk+)'), GtkPrint, 1, 1, 1, "", None)
##register_draw_doc(_('GtkPrint'), GtkPrint, 1, 1, "", None)
##register_book_doc(_("GtkPrint"), GtkPrint, 1, 1, 1, "", None)
