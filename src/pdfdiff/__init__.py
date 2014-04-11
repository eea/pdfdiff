#!/usr/bin/env python

import os
import sys
import argparse
import contextlib
from urlparse import urlparse
from urllib2 import urlopen
from datetime import datetime
from PIL import Image as PIL_Image
from random import choice
from string import ascii_uppercase, digits
from wand.image import Image


class PDFTransformer(object):
    """
    The main purpose of the class is to transform a pdf file into multiple
    png files. The number of the png files is equal with pdf pages.(so one page
    for a png file)
    """
    @staticmethod
    def id_generator(size=6, chars=ascii_uppercase + digits):
        return ''.join(choice(chars) for _ in range(size))

    def __new__(cls, *args, **kwargs):
        _instance = super(PDFTransformer, cls).__new__(cls)
        _instance.random_part = PDFTransformer.id_generator()
        directory = kwargs['directory']
        _instance.to_search = os.path.join(directory,
                                           _instance.random_part)
        filename = os.path.join(
            directory, _instance.random_part + ".png")

        with Image(filename=kwargs['pdf']) as img:
            img.save(filename=filename)

        _instance.generated_files = []
        for file in os.listdir(directory):
            if file.startswith(_instance.random_part):
                _instance.generated_files.append(
                    os.path.join(directory, file))

        _instance.generated_files.sort()
        return _instance

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_val, trace):
        for file in self.generated_files:
            os.remove(file)


class ExtendedImage(object):
    """
    Extended PIL.Image delegate unimplemented method to the PIL.Image
    The purpose class is to verify if other img is not equal with self._img
    If differs generate a new picture and marks the different pixels.
    """
    MARK_PIXEL = (255, 0, 0, 255)

    def __init__(self, img, directory):
        """
        left = ExtendedImage(Image.open(file_left))
        """
        self._img = img
        self._work_dir = directory

    def __make_new_picture(self, xy):
        new_image = self._img.copy()
        if new_image.mode != 'RGBA':
            new_image = new_image.convert('RGBA')

        pix_new_image = new_image.load()
        for coordonate in xy:
            pix_new_image[coordonate[1], coordonate[0]] =\
                ExtendedImage.MARK_PIXEL
        new_image.save(
            os.path.join(self._work_dir,
                         datetime.now().strftime("%y-%m-%d-%H:%M:%S:%f.png")))

    def __ne__(self, other):
        xy = []
        if (self._img.size[1] != other.size[1] or
                self._img.size[0] != other.size[0]):
            return True

        pix_lf = self._img.load()
        pix_rg = other.load()

        for x in range(self._img.size[1]):
            for y in range(self._img.size[0]):
                if pix_lf[y, x] != pix_rg[y, x]:
                    xy.append((x, y))

        if xy:
            self.__make_new_picture(xy)
            return True

        return False

def url2file(url, directory="", timeout=60):
    """ Get file from url and return a system path to file
    """
    res = urlparse(url)
    if not res.scheme:
        return url

    filename = None
    defaultname = res.path.replace('/', '-')
    if directory:
        defaultname = os.path.join(directory, defaultname)
    with contextlib.closing(urlopen(url, timeout=timeout)) as conn:
        headers = dict(conn.headers)
        cdisp = headers.get("content-disposition", "")
        filename = cdisp.replace('attachment; filename="', "")
        filename = filename.strip('"')
        if filename:
            if directory:
                filename = os.path.join(directory, filename)
        else:
            filename = defaultname

        with open(filename, "wb") as output:
            for data in conn:
                output.write(data)
    return filename if filename else defaultname

def main():
    """ Main script
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
        help='PDF file path or URL to compare',
        default='input.pdf')
    parser.add_argument('-o', '--output',
        help='PDF file path or URL to compare with',
        default='output.pdf')
    parser.add_argument('-d', '--directory',
        help='Output directory')
    parser.add_argument('-t', '--timeout',
        help="Timeout to be used when using with URLs",
        default=60)

    arguments = parser.parse_args()

    directory = arguments.directory
    if not os.path.exists(directory):
        os.makedirs(directory)

    timeout = int(arguments.timeout)
    left = url2file(arguments.input, directory, timeout)
    right = url2file(arguments.output, directory, timeout)

    with PDFTransformer(pdf=left, directory=directory) as leftPDF:
        with PDFTransformer(pdf=right, directory=directory) as rightPDF:
            are_diffs = False
            for idx in range(len(leftPDF.generated_files)):
                if (ExtendedImage(PIL_Image.open(leftPDF.generated_files[idx]),
                                  directory) !=
                        PIL_Image.open(rightPDF.generated_files[idx])):
                        are_diffs = True

            if are_diffs:
                sys.exit(1)
            sys.exit(0)

if __name__ == "__main__":
    main()
