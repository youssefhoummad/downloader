from PIL import Image , ImageColor

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


if __name__ == '__main__':
  image = Image.open('video.tif')

  img = change_img_color(image, 'purple', 'black')
  img.show()