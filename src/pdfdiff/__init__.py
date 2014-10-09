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
        _instance.random_part = kwargs.get('type',
                                            PDFTransformer.id_generator())
        _instance.random_part += '-page'

        _instance.cleanup = kwargs.get('cleanup', True)

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
        if self.cleanup:
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
        self._diffs = 0

    def __make_new_picture(self, xy):
        new_image = self._img.copy()
        if new_image.mode != 'RGBA':
            new_image = new_image.convert('RGBA')

        pix_new_image = new_image.load()
        for coordonate in xy:
            pix_new_image[coordonate[1], coordonate[0]] =\
                ExtendedImage.MARK_PIXEL

        filename = self._img.filename.split('-')[-1]
        filename = 'diff-page-%s' % filename
        new_image.save(
            os.path.join(self._work_dir, filename)
        )

    def __ne__(self, other):
        xy = []
        if self._img.size[1] != other.size[1]:
            self._diffs += other.size[1]
            return True
        elif self._img.size[0] != other.size[0]:
            self._diffs += other.size[1]
            return True

        pix_lf = self._img.load()
        pix_rg = other.load()

        for x in range(self._img.size[1]):
            for y in range(self._img.size[0]):
                if pix_lf[y, x] != pix_rg[y, x]:
                    xy.append((x, y))

        if xy:
            self.__make_new_picture(xy)
            self._diffs += len(xy)
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
        help='PDF file path or URL to compare. Default: input.pdf',
        default='input.pdf')
    parser.add_argument('-o', '--output',
        help='PDF file path or URL to compare with. Default: output.pdf',
        default='output.pdf')
    parser.add_argument('-d', '--directory',
        help='Output directory. No default')
    parser.add_argument('-t', '--timeout',
        help="Timeout to be used when using with URLs. Default: 60 seconds",
        default=60)

    parser.add_argument('--cleanup-input', dest='cleanupInput',
        help="(default) Auto cleanup generated input images.",
        action='store_true',
        default=True)
    parser.add_argument('--no-cleanup-input', dest='cleanupInput',
        help="Do not auto cleanup generated input images.",
        action='store_false')

    parser.add_argument('--cleanup-output', dest='cleanupOutput',
        help="(default) Do not auto cleanup generated output images.",
        action='store_true',
        default=True)
    parser.add_argument('--no-cleanup-output',  dest='cleanupOutput',
        help="Do not auto cleanup generated output images.",
        action='store_false')

    parser.add_argument('-a', '--allow',
        help="Allow a number of differences. Default: 0",
        default=0)

    arguments = parser.parse_args()

    directory = arguments.directory
    if not os.path.exists(directory):
        os.makedirs(directory)

    timeout = int(arguments.timeout)
    allow = int(arguments.allow)
    left = url2file(arguments.input, directory, timeout)
    right = url2file(arguments.output, directory, timeout)
    cleanup_input = arguments.cleanupInput
    cleanup_output = arguments.cleanupOutput

    with PDFTransformer(pdf=left, directory=directory,
                        type='input', cleanup=cleanup_input) as leftPDF:
        with PDFTransformer(pdf=right, directory=directory,
                            type='output', cleanup=cleanup_output) as rightPDF:
            diffs = 0
            for idx in range(len(leftPDF.generated_files)):
                leftImg = ExtendedImage(PIL_Image.open(
                                      leftPDF.generated_files[idx]), directory)
                rightImg = PIL_Image.open(rightPDF.generated_files[idx])
                if (leftImg != rightImg):
                    diffs += leftImg._diffs

            if diffs > allow:
                sys.exit(1)
            sys.exit(0)

if __name__ == "__main__":
    main()
