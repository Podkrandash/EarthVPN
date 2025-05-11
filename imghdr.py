"""Recognize image file formats based on their first few bytes."""

from os import PathLike
import os
import struct

__all__ = ["what"]

#-------------------------#
# Recognize image headers #
#-------------------------#

def what(file, h=None):
    """Recognize image format of a file or buffer.

    Arguments:
      file: a file path, bytes object, or a seekable binary file object.
      h: bytes object; file header, previously read from the file.

    Output:
      file format (string like "jpeg" or "png"), or None if not identified.
    """
    if h is None:
        if isinstance(file, (str, PathLike)):
            with open(file, 'rb') as f:
                h = f.read(32)
        else:
            location = file.tell()
            h = file.read(32)
            file.seek(location)
            
    if not h:
        return None

    for tf in tests:
        res = tf(h, file)
        if res:
            return res
    return None


#---------------------------------#
# Subroutines per image file type #
#---------------------------------#

tests = []

def test_jpeg(h, f):
    """JPEG data in JFIF or Exif format"""
    if h[0:2] == b'\xff\xd8':
        return 'jpeg'

tests.append(test_jpeg)

def test_png(h, f):
    """PNG data"""
    if h[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'

tests.append(test_png)

def test_gif(h, f):
    """GIF ('87 and '89 variants)"""
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'

tests.append(test_gif)

def test_tiff(h, f):
    """TIFF (can be in Motorola or Intel byte order)"""
    if h[:2] in (b'MM', b'II'):
        if h[2:4] == b'\x00\x2a':
            return 'tiff'

tests.append(test_tiff)

def test_rgb(h, f):
    """SGI image library"""
    if h[:2] == b'\x01\xda':
        return 'rgb'

tests.append(test_rgb)

def test_pbm(h, f):
    """PBM (portable bitmap)"""
    if len(h) >= 3 and \
        h[0] == ord(b'P') and h[1] in b'14' and h[2] in b' \t\n\r':
        return 'pbm'

tests.append(test_pbm)

def test_pgm(h, f):
    """PGM (portable graymap)"""
    if len(h) >= 3 and \
        h[0] == ord(b'P') and h[1] in b'25' and h[2] in b' \t\n\r':
        return 'pgm'

tests.append(test_pgm)

def test_ppm(h, f):
    """PPM (portable pixmap)"""
    if len(h) >= 3 and \
        h[0] == ord(b'P') and h[1] in b'36' and h[2] in b' \t\n\r':
        return 'ppm'

tests.append(test_ppm)

def test_rast(h, f):
    """Sun raster file"""
    if h[:4] == b'\x59\xa6\x6a\x95':
        return 'rast'

tests.append(test_rast)

def test_xbm(h, f):
    """X bitmap (X10 or X11)"""
    if h[:8] == b'#define ':
        return 'xbm'

tests.append(test_xbm)

def test_bmp(h, f):
    """BMP file"""
    if h[:2] == b'BM':
        return 'bmp'

tests.append(test_bmp)

def test_webp(h, f):
    """WebP file"""
    if h[:4] == b'RIFF' and h[8:12] == b'WEBP':
        return 'webp'

tests.append(test_webp)

def test_exr(h, f):
    """OpenEXR file"""
    if h[:4] == b'\x76\x2f\x31\x01':
        return 'exr'

tests.append(test_exr) 