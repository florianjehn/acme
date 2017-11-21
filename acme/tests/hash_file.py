# -*- coding: utf-8 -*-
"""
Created on Nov 21 12:41 2017
@author(s): Florian U. Jehn

Hashes a file
"""
import hashlib


def hashing(file):
    """

    :param file: filelike object
    :return: Hash of the filelike object
    """
    curfile = open(file, "rb")
    hasher = hashlib.md5()
    buf = curfile.read()
    hasher.update(buf)
    print(hasher.hexdigest())


if __name__ == '__main__':
    hashing("description.txt")
