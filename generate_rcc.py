#!/usr/bin/env python

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__copyright__ = "Copyright (c) 2015 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import argparse
import xml.etree.ElementTree as etree
import xml.dom.minidom as minidom
import subprocess

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

# Third party modules.

# Local modules.

# Globals and constants variables.

# This comversion make the cmake process extremely slow
# bur without this the qrc would contains msys styled path
# so it cannot be built by mingw
# anyway, cmake would runs for only once
def MsysPath_2_WinPath(msysPath, doubleSlash=False):
    comm = "cygpath -w %s" % msysPath
    #print("%s =>"%comm)
    winpath = os.popen(comm).read().rstrip()
    if doubleSlash:
        winpath = winpath.replace("\\", "\\\\")
    #print("  %s"%winpath)
    return winpath

def create_qrc(themefilepath, exts=['.png', '.svg']):
    """
    Generates .qrc file from all images in the directory of the theme path.
    """
    basepath = os.path.dirname(themefilepath)
    isMSYS = (sys.platform == "msys")
    if isMSYS:
        print('Using MSYS / MSYS2, path would be fixed to windows style in order to compile.')

    # Parse index.theme
    parser = configparser.ConfigParser()
    parser.read(themefilepath)
    name = parser.get('Icon Theme', 'Name')
    directories = parser.get('Icon Theme', 'Directories').split(',')

    # Create root
    root = etree.Element('RCC', version='1.0')
    element_qresource = etree.SubElement(root, 'qresource',
                                         prefix='icons/%s' % name)

    element = etree.SubElement(element_qresource, 'file', alias='index.theme')
    element.text = os.path.abspath(themefilepath)
    if isMSYS:
        element.text = MsysPath_2_WinPath(element.text, True)

    # Find all image files
    for directory in directories:
        for dirpath, _, filenames in os.walk(os.path.join(basepath, directory)):
            for filename in filenames:
                if os.path.splitext(filename)[1] not in exts:
                    continue
                alias = os.path.join(directory, filename)
                text = os.path.abspath(os.path.join(dirpath, filename))
                if isMSYS:
                    text = MsysPath_2_WinPath(text, True)
                element = etree.SubElement(element_qresource, 'file', alias=alias)
                element.text = text

    # Write
    outfilepath = os.path.join(basepath, name + '.qrc')
    with open(outfilepath, 'w') as fp:
        fp.write(minidom.parseString(etree.tostring(root)).toprettyxml())

    return outfilepath

def run_rcc(qrcfilepath):
    outfilepath = os.path.splitext(qrcfilepath)[0] + '.rcc'
    subprocess.check_call(['rcc', '--binary', '-o', outfilepath,
                           '--compress', '9', qrcfilepath])

def run():
    parser = argparse.ArgumentParser(description='Generate rcc')
    parser.add_argument('theme', metavar='FILE', help='Path to .theme file')
    parser.add_argument('--rcc', action='store_true', default=False,
                        help='compile qrc with rcc')

    args = parser.parse_args()

    qrcfilepath = create_qrc(args.theme)
    if args.rcc:
        run_rcc(qrcfilepath)

if __name__ == '__main__':
    run()
