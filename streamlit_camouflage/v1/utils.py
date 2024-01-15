
def rgb_to_hex(rgb):
    """Convert RGB values (0 to 255) to HEX"""
    _rgb = tuple([int(c) for c in rgb])
    hex = '#%02x%02x%02x' % _rgb
    return hex