#!/usr/bin/env python3
'''
monofont2c.py
    Convert characters from monospace truetype fonts to a c bitmap.
    Adapted from monofont2python.py.

positional arguments:

  font_file             Name of font file to convert.
  font_size             Size of font to create bitmaps from.
  bits_per_pixel        The number of bits (1..8) to use per pixel.

optional arguments:

  -h, --help            show this help message and exit
  -n NAME, --name NAME
                        Name to apply to the c variable for the font
  -f FOREGROUND, --foreground FOREGROUND
                        Foreground color of characters.
  -b BACKGROUND, --background BACKGROUND
                        Background color of characters.

character selection:
  Characters from the font to include in the bitmap.

  -c CHARACTERS, --characters CHARACTERS
                        integer or hex character values and/or ranges to
                        include.

                        For example: "65, 66, 67" or "32-127" or
                        "0x30-0x39, 0x41-0x5a"

  -s STRING, --string STRING
                        String of characters to include For example:
                        "1234567890-."
'''

import sys
import shlex
from PIL import Image, ImageFont, ImageDraw
import argparse

image_bitstring = ''


def to_int(str):
    return int(str, base=16) if str.startswith("0x") else int(str)


def get_characters(str):
    return ''.join([chr(b) for a in [
        (lambda sub: range(sub[0], sub[-1] + 1))
        (list(map(to_int, ele.split('-'))))
        for ele in str.split(',')]
            for b in a])


def process_char(img, bits):
    global image_bitstring

    # Run through the image and create a string with the ascii binary
    # representation of the color of each pixel.

    for y in range(img.height):
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            color = pixel
            bit_string = ''
            for bit in range(bits, 0, -1):
                bit_string += '1' if (color & (1 << bit-1)) else '0'
            image_bitstring += bit_string


def main():
    parser = argparse.ArgumentParser(
        prog='font2bitmap',
        description=('''
            Convert characters from monospace truetype fonts to a
            python bitmap for use with the bitmap method in the
            st7789 and ili9342 drivers.'''))

    parser.add_argument(
        'font_file',
        help='Name of font file to convert.')

    parser.add_argument(
        'font_size',
        type=int,
        default=8,
        help='Size of font to create bitmaps from.')

    parser.add_argument(
        'bits_per_pixel',
        type=int,
        choices=range(1, 9),
        default=1,
        metavar='bits_per_pixel',
        help='The number of bits (1..8) to use per pixel.')

    parser.add_argument(
        '-f', '--foreground',
        default='white',
        help='Foreground color of characters.')

    parser.add_argument(
        '-b', '--background',
        default='black',
        help='Background color of characters.')

    parser.add_argument(
        '-n', '--name',
        default='myfont',
        help='Name to use in the c variable'
    )

    group = parser.add_argument_group(
        'character selection',
        'Characters from the font to include in the bitmap.')

    excl = group.add_mutually_exclusive_group()
    excl.add_argument(
        '-c', '--characters',
        help='''integer or hex character values and/or ranges to include.
        For example: "65, 66, 67" or "32-127" or "0x30-0x39, 0x41-0x5a"''')

    excl.add_argument(
        '-s', '--string',
        help='''String of characters to include
        For example: "1234567890-."''')

    args = parser.parse_args()
    bpp = args.bits_per_pixel
    font_file = args.font_file
    font_size = args.font_size

    if args.string is None:
        characters = get_characters(args.characters)
    else:
        characters = args.string

    forground = args.foreground
    background = args.background
    name = args.name

    # load font and get size of characters string in pixels
    font = ImageFont.truetype(font_file, font_size)
    size = font.getsize(characters)

    # create image large enough to all characters
    im = Image.new('RGB', size, color=background)

    # draw all specified characters in the image
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), characters, font=font, color=forground)

    # convert image to a palletized image with the requested color depth
    bpp_im = im.convert(mode='P', palette=Image.ADAPTIVE, colors=1 << bpp)
    palette = bpp_im.getpalette()

    # convert all characters into a ascii bit string
    ofs = 0
    for char in characters:
        char_size = font.getsize(char)
        crop = (ofs, 0, ofs + char_size[0], size[1])
        char_im = bpp_im.crop(crop)
        process_char(char_im, bpp)
        ofs += char_size[0]

    bitmap_bits = len(image_bitstring)
    char_map = characters.replace('\\', '\\\\').replace('"', '\\"')
    cmdline = " ".join(map(shlex.quote, sys.argv))

    # write a .c file
    print(f"// {cmdline}")
    print()

    print("include \"font.h\"")
    print()

    print(f"static const char *name = \"{name}\";")
    print(f"static const uint8_t width = {char_im.width};")
    print(f"static const uint8_t height = {char_im.height};")
    print(f"static const uint8_t bpp = {bpp};")

    print(f"static const char *map = \"{char_map}\";") 
    print()

    print("static const uint8_t bitmap[] = {", sep='', end='')
    for i in range(0, bitmap_bits, 8):
        if i % (16 * 8) == 0:
            print("\n    ", end='', sep='')

        value = image_bitstring[i:i+8]
        color = int(value, 2)
        print(f'0x{color:02x}', sep='', end='')
        if i != bitmap_bits-8:
            print(', ', sep='', end='')

    print("\n};")
    print()

    print(f"const font_t font_{name} = {{")
    print(f"    .name = name,")
    print(f"    .width = width,")
    print(f"    .height = height,")
    print(f"    .bpp = bpp,")
    print(f"    .map = map,")
    print("    .bitmap = bitmap")
    print("};")
    print()

main()
