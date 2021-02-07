"""
    AwesomeTkinter, a new tkinter widgets design using custom styles and images
    :copyright: (c) 2020 by Mahmoud Elshahat.
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageFilter, ImageColor, ImageTk
# from .utils import *

def change_img_color(img, new_color, old_color=None):
    """Change image color
    Args:
        img: pillow image
        new_color (str): new image color, ex: 'red', '#ff00ff', (255, 0, 0), (255, 0, 0, 255)
        old_color (str): color to be replaced, if omitted, all colors will be replaced with new color keeping
                         alpha channel.
    Returns:
        pillow image
    """

    # convert image to RGBA color scheme
    img = img.convert('RGBA')

    # load pixels data
    pixdata = img.load()

    # handle color
    new_color = color_to_rgba(new_color)
    old_color = color_to_rgba(old_color)

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            alpha = pixdata[x, y][-1]
            if old_color:
                if pixdata[x, y] == old_color:
                    r, g, b, _ = new_color
                    pixdata[x, y] = (r, g, b, alpha)
            else:
                r, g, b, _ = new_color
                pixdata[x, y] = (r, g, b, alpha)

    return img


def color_to_rgba(color):
    """Convert color names or hex notation to RGBA,
    Args:
        color (str): color e.g. 'white' or '#333' or formats like #rgb or #rrggbb
    Returns:
        (4-tuple): tuple of format (r, g, b, a) e.g. it will return (255, 0, 0, 255) for solid red
    """

    if color is None:
        return None

    if isinstance(color, (tuple, list)):
        if len(color) == 3:
            r, g, b = color
            color = (r, g, b, 255)
        return color
    else:
        return ImageColor.getcolor(color, 'RGBA')


def create_circle(size=100, thickness=None, color='black', fill=None, antialias=4, offset=0):
    """create high quality circle
    the idea to smooth circle line is to draw a bigger size circle and then resize it to the requested size
    inspired from  https://stackoverflow.com/a/34926008
    Args:
        size (tuple or list, or int): outer diameter of the circle or width of bounding box
        thickness (int): outer line thickness in pixels
        color (str): outer line color
        fill (str): fill color, default is a transparent fill
        antialias (int): used to enhance outer line quality and make it smoother
        offset (int): correct cut edges of circle outline
    Returns:
        PIL image: a circle on a transparent image
    """

    if isinstance(size, int):
        size = (size, size)
    else:
        size = size

    fill_color = '#0000'

    requested_size = size

    # calculate thickness to be 2% of circle diameter
    thickness = thickness or max(size[0] * 2 // 100, 2)

    offset = offset or thickness // 2

    # make things bigger
    size = [x * antialias for x in requested_size]
    thickness *= antialias

    # create a transparent image with a big size
    img = Image.new(size=size, mode='RGBA', color='#0000')

    draw = ImageDraw.Draw(img)

    # draw circle with a required color
    draw.ellipse([offset, offset, size[0] - offset, size[1] - offset], outline=color, fill=fill_color, width=thickness)

    img = img.filter(ImageFilter.BLUR)

    # resize image back to the requested size
    img = img.resize(requested_size, Image.LANCZOS)

    # change color again will enhance quality (weird)
    if fill:
        img = change_img_color(img, color, old_color=color)
        img = change_img_color(img, fill, old_color=fill)
    else:
        img = change_img_color(img, color)

    return img


class RadialProgressbar(tk.Frame):
    """create radial flat progressbar
    basically this is a ttk horizontal progressbar modified using custom style layout and images
    Example:
        bar = RadialProgressbar(frame1, size=150, fg='green')
        bar.grid(padx=10, pady=10)
        bar.start()
    """

    # class variables to be shared between objects
    styles = []  # hold all style names created for all objects

    def __init__(self, parent, size=50, bg='white', fg=None, text_fg='black', text_bg='white', font=None, font_size_ratio=None,
                 base_img=None, indicator_img=None, parent_bg='white', **extra):
        """initialize progressbar
        Args:
            parent  (tkinter object): tkinter container, i.e. toplevel window or frame
            size (int or 2-tuple(int, int)) size of progressbar in pixels
            bg (str): color of base ring
            fg(str): color of indicator ring
            text_fg (str): percentage text color
            font (str): tkinter font for percentage text, e.g. 'any 20'
            font_size_ratio (float): font size to progressbar width ratio, e.g. for a progressbar size 100 pixels,
                                     a 0.1 ratio means font size 10
            base_img (tk.PhotoImage): base image for progressbar
            indicator_img (tk.PhotoImage): indicator image for progressbar
            parent_bg (str): color of parent container
            extra: any extra kwargs (not used)
        """

        self.parent = parent
        self.parent_bg = parent_bg # or get_widget_attribute(self.parent, 'background')
        self.bg = bg # or calc_contrast_color(self.parent_bg, 30)
        self.fg = fg or 'cyan'
        self.text_fg = text_fg # or calc_font_color(self.parent_bg)
        self.text_bg = text_bg # or self.parent_bg
        self.size = size if isinstance(size, (list, tuple)) else (size, size)
        self.font_size_ratio = font_size_ratio or 0.2
        self.font = font  or f'any {int((sum(self.size) // 2) * self.font_size_ratio)}'

        self.base_img = base_img
        self.indicator_img = indicator_img

        self.var = tk.IntVar()

        # initialize super class
        tk.Frame.__init__(self, master=parent)

        # create custom progressbar style
        self.bar_style = self.create_style()

        # create tk Progressbar
        self.bar = ttk.Progressbar(self, orient='horizontal', mode='determinate', length=self.size[0],
                                   variable=self.var, style=self.bar_style)
        self.bar.pack()

        # percentage Label
        self.percent_label = ttk.Label(self.bar, text='0%')
        self.percent_label.place(relx=0.5, rely=0.5, anchor="center")

        # trace progressbar value to show in label
        self.var.trace_add('write', self.show_percentage)

        # set default attributes
        self.config()

        self.start = self.bar.start
        self.stop = self.bar.stop

    def set(self, value):
        """set and validate progressbar value"""
        value = self.validate_value(value)
        self.var.set(value)

    def get(self):
        """get validated progressbar value"""
        value = self.var.get()
        return self.validate_value(value)

    def validate_value(self, value):
        """validate progressbar value
        """

        try:
            value = int(value)
            if value < 0:
                value = 0
            elif value > 100:
                value = 100
        except:
            value = 0

        return value

    def create_style(self):
        """create ttk style for progressbar
        style name is unique and will be stored in class variable "styles"
        """

        # create unique style name
        bar_style = f'radial_progressbar_{len(RadialProgressbar.styles)}'

        # add to styles list
        RadialProgressbar.styles.append(bar_style)

        # create style object
        s = ttk.Style()

        if not self.indicator_img:
            img = create_circle(self.size, color=self.fg)
            self.indicator_img = ImageTk.PhotoImage(img)

        if not self.base_img:
            img = create_circle(self.size, color=self.bg)
            self.base_img = ImageTk.PhotoImage(img)

        # create elements
        indicator_element = f'top_img_{bar_style}'
        base_element = f'bottom_img_{bar_style}'

        try:
            s.element_create(base_element, 'image', self.base_img, border=0, padding=0)
        except:
            pass

        try:
            s.element_create(indicator_element, 'image', self.indicator_img, border=0, padding=0)
        except:
            pass

        # create style layout
        s.layout(bar_style,
                 [(base_element, {'children':
                        [('pbar', {'side': 'left', 'sticky': 'nsew', 'children':
                                [(indicator_element, {'sticky': 'nswe'})]})]})])

        # configure new style
        s.configure(bar_style, pbarrelief='flat', borderwidth=0, troughrelief='flat')

        return bar_style

    def show_percentage(self, *args):
        """display progressbar percentage in a label"""
        bar_value = self.get()
        self.percent_label.config(text=f'{bar_value}%')

    def config(self, **kwargs):
        """config widgets' parameters"""

        # create style object
        s = ttk.Style()

        kwargs = {k: v for k, v in kwargs.items() if v}
        self.__dict__.update(kwargs)

        # frame bg
        self['bg'] = self.parent_bg

        # bar style configure
        s.configure(self.bar_style, background=self.parent_bg, troughcolor=self.parent_bg)

        # percentage label
        self.percent_label.config(background=self.text_bg, foreground=self.text_fg, font=self.font)


if __name__ == '__main__':
  root = tk.Tk()
  r = RadialProgressbar(root)
  r.set(99)
  r.pack()
  root.mainloop()
