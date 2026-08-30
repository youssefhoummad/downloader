"""Implementation of the scrollable frame widget."""
# https://github.com/bmjcode/tkScrolledFrame/blob/master/tkscrolledframe/widget.py

import sys

import tkinter as tk
import tkinter.ttk as ttk



__all__ = ["ScrolledFrame"]


class ScrolledFrame(tk.Frame):
    """Scrollable Frame widget.
    Use display_widget() to set the interior widget. For example,
    to display a Label with the text "Hello, world!", you can say:
        sf = ScrolledFrame(self)
        sf.pack()
        sf.display_widget(Label, text="Hello, world!")
    The constructor accepts the usual Tkinter keyword arguments, plus
    a handful of its own:
      scrollbars (str; default: "both")
        Which scrollbars to provide.
        Must be one of "vertical", "horizontal," "both", or "neither".
      use_ttk (bool; default: False)
        Whether to use ttk widgets if available.
        The default is to use standard Tk widgets. This setting has
        no effect if ttk is not available on your system.
    """

    def __init__(self, master=None, **kw):
        """Return a new scrollable frame widget."""

        tk.Frame.__init__(self, master)
        self.config(bg=master['bg'], bd=0)

        # Hold these names for the interior widget
        self._interior = None
        self._interior_id = None

        # Whether to fit the interior widget's width to the canvas
        self._fit_width = False
        self._fit_height = False

        # Which scrollbars to provide
        if "scrollbars" in kw:
            scrollbars = kw["scrollbars"]
            del kw["scrollbars"]

            if not scrollbars:
                scrollbars = self._DEFAULT_SCROLLBARS
            elif not scrollbars in self._VALID_SCROLLBARS:
                raise ValueError("scrollbars parameter must be one of "
                                 "'vertical', 'horizontal', 'both', or "
                                 "'neither'")
        else:
            scrollbars = self._DEFAULT_SCROLLBARS

        # Whether to use ttk widgets if available
        if "use_ttk" in kw:
            if ttk and kw["use_ttk"]:
                Scrollbar = ttk.Scrollbar
            else:
                Scrollbar = tk.Scrollbar
            del kw["use_ttk"]
        else:
            Scrollbar = tk.Scrollbar

        # Default to a 1px sunken border
        if not "borderwidth" in kw:
            kw["borderwidth"] = 0
        if not "relief" in kw:
            kw["relief"] = "flat"

        # Set up the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Canvas to hold the interior widget
        c = self._canvas = tk.Canvas(self,
                                     borderwidth=0,
                                     highlightthickness=0,
                                     takefocus=0, bg=self['bg'])

        # Enable scrolling when the canvas has the focus
        self.bind_arrow_keys(c)
        # Wheel scrolling: bind globally, then route to this frame
        # only when the pointer is over its content (see _on_wheel)
        self._wheel_acc = 0
        self.bind_all("<MouseWheel>", self._on_wheel, add="+")
        self.bind_all("<Button-4>", self._on_wheel, add="+")
        self.bind_all("<Button-5>", self._on_wheel, add="+")

        # Re-layout when the canvas is resized
        c.bind("<Configure>", self._layout)
        # Scrollbars
        # xs = self._x_scrollbar = Scrollbar(self,
        #                                    orient="horizontal",
        #                                    command=c.xview)
        ys = self._y_scrollbar = Scrollbar(self,
                                           orient="vertical",
                                           command=c.yview)
        c.configure(yscrollcommand=ys.set) # xscrollcommand=xs.set

        # Lay out our widgets
        c.grid(row=0, column=0, sticky="nsew")
        if scrollbars == "vertical" or scrollbars == "both":
            ys.grid(row=0, column=1, sticky="ns")
        # if scrollbars == "horizontal" or scrollbars == "both":
        #     xs.grid(row=1, column=0, sticky="we")

        # Forward these to the canvas widget
        self.bind = c.bind
        self.focus_set = c.focus_set
        self.unbind = c.unbind
        # self.xview = c.xview
        # self.xview_moveto = c.xview_moveto
        self.yview = c.yview
        self.yview_moveto = c.yview_moveto

        # Process our remaining configuration options
        self.configure(**kw)

    def __setitem__(self, key, value):
        """Configure resources of a widget."""

        if key in self._CANVAS_KEYS:
            # Forward these to the canvas widget
            self._canvas.configure(**{key: value})

        else:
            # Handle everything else normally
            tk.Frame.configure(self, **{key: value})

    # ------------------------------------------------------------------------

    def bind_arrow_keys(self, widget):
        """Bind the specified widget's arrow key events to the canvas."""

        widget.bind("<Up>",
                    lambda event: self._canvas.yview_scroll(-1, "units"))

        widget.bind("<Down>",
                    lambda event: self._canvas.yview_scroll(1, "units"))

        # widget.bind("<Left>",
        #             lambda event: self._canvas.xview_scroll(-1, "units"))

        # widget.bind("<Right>",
        #             lambda event: self._canvas.xview_scroll(1, "units"))


    def cget(self, key):
        """Return the resource value for a KEY given as string."""

        if key in self._CANVAS_KEYS:
            return self._canvas.cget(key)

        else:
            return tk.Frame.cget(self, key)

    # Also override this alias for cget()
    __getitem__ = cget

    def configure(self, cnf=None, **kw):
        """Configure resources of a widget."""

        # This is overridden so we can use our custom __setitem__()
        # to pass certain options directly to the canvas.
        if cnf:
            for key in cnf:
                self[key] = cnf[key]

        for key in kw:
            self[key] = kw[key]

    # Also override this alias for configure()
    config = configure

    def display_widget(self, widget_class, fit_width=False, fit_height=False, **kw):
        """Create and display a new widget.

        If fit_width == True, the interior widget will be stretched
        as needed to fit the width of the frame.

        If fit_height == True and the widget is shorter than the frame,
        it will be centered vertically.
        """
        self.erase()

        self._fit_width = fit_width
        self._fit_height = fit_height

        self._interior = widget_class(self._canvas, **kw)
        self._interior_id = self._canvas.create_window(0, 0,
                                                       anchor="nw",
                                                       window=self._interior)

        # Re-layout whenever the interior widget is resized
        self._interior.bind("<Configure>", self._layout)

        self._layout()
        self.scroll_to_top()
        return self._interior

    def erase(self):
        """Erase the displayed widget."""

        # Clear the canvas
        self._canvas.delete("all")

        # Delete the interior widget
        del self._interior
        del self._interior_id

        # Save these names
        self._interior = None
        self._interior_id = None

        # Reset width fitting
        self._fit_width = False
        self._fit_height = False

    def scroll_to_top(self):
        """Scroll to the top-left corner of the canvas."""

        # self._canvas.xview_moveto(0)
        self._canvas.yview_moveto(0)

    # ------------------------------------------------------------------------

    # Widgets that scroll themselves (don't double-scroll them)
    _SELF_SCROLL_CLASSES = ("Text", "Listbox", "Treeview", "Entry",
                            "Spinbox", "TCombobox", "TSpinbox")

    def _on_wheel(self, event):
        """Scroll only if the pointer is over this frame's content."""

        if event.widget.winfo_class() in self._SELF_SCROLL_CLASSES:
            return  # let the widget handle its own scrolling

        # Walk up from the widget under the pointer; scroll only
        # if we reach our own canvas (pointer is over our content)
        w = event.widget
        while w is not None:
            if w in (self._canvas, self._y_scrollbar):
                self._scroll_canvas(event)
                return
            w = w.master

    def _scroll_canvas(self, event):
        c = self._canvas

        if event.num == 4:
            # Linux - wheel/touchpad up
            c.yview_scroll(-1, "units")
        elif event.num == 5:
            # Linux - wheel/touchpad down
            c.yview_scroll(1, "units")
        elif sys.platform.startswith("darwin"):
            # macOS
            c.yview_scroll(-event.delta, "units")
        elif sys.platform.startswith("win"):
            # Windows - one notch = 120, but touchpads send smaller
            # deltas, so accumulate until we have a full notch.
            # int() (not //) so positive and negative behave the same
            self._wheel_acc += event.delta
            clicks = int(self._wheel_acc / 120) # /120 speed of scrolling
            if clicks:
                self._wheel_acc -= clicks * 120
                c.yview_scroll(-clicks, "units")
        else:
            # Linux with smooth scrolling (Tk 8.6.10+ / XInput2):
            # many small deltas with event.num == 0
            self._wheel_acc += event.delta
            lines = int(self._wheel_acc / 15)
            if lines:
                self._wheel_acc -= lines * 15
                c.yview_scroll(-lines, "units") # لعكس اتجاه التمرير نغير -lines ب lines

    def _layout(self, event=None):
        """Position the interior widget and update the scroll region."""

        if not self._interior_id:
            return

        canvas_width = self._canvas.winfo_width()
        canvas_height = self._canvas.winfo_height()

        # Stretch the width to fit the canvas if requested
        if self._fit_width:
            req_width = self._interior.winfo_reqwidth()
            self._canvas.itemconfigure(self._interior_id,
                                       width=max(canvas_width, req_width))

        # Center vertically when the content is shorter than the canvas
        x, y = 0, 0
        if self._fit_height:
            req_height = self._interior.winfo_reqheight()
            if req_height < canvas_height:
                y = (canvas_height - req_height) // 2
        self._canvas.coords(self._interior_id, x, y)

        # Scroll region covers both the content and the visible area
        req_width = self._interior.winfo_reqwidth()
        req_height = self._interior.winfo_reqheight()
        self._canvas.configure(scrollregion=(0, 0,
                                             max(req_width, canvas_width),
                                             max(req_height, canvas_height)))
        

    def interior(self, fit_width=False, fit_height=False):
        """أعد الإطار الداخلي الجاهز لحزم الأدوات فيه مباشرة."""
        if self._interior is None:
            self.display_widget(tk.Frame,
                                fit_width=fit_width,
                                fit_height=fit_height)
        return self._interior
    # ------------------------------------------------------------------------

    # Keys for configure() to forward to the canvas widget
    _CANVAS_KEYS = "width", "height", "takefocus"

    # Scrollbar-related configuration
    _DEFAULT_SCROLLBARS = "both"
    _VALID_SCROLLBARS = "vertical", "horizontal", "both", "neither"