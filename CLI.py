#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example CLI usage of the newick validator library
run with python3 cli.py [input-file]
"""

from io import StringIO
from sys import argv
from newick_validator import is_newick
from Bio import Phylo


# read a file to a string
try:
    with open(argv[1], 'r') as file:
        content = file.read()  # string
        # file.close()

except (OSError, IndexError, UnicodeDecodeError):
    print("File not found or wrong file format!")
    exit()
    # interrupts the execution if there are any issues with the file

# \n tree separator
forest = content.split("\n")

# calls function on each tree
for i in forest:

    if not i or i.isspace():
        print("\nFound an empty string.")

    else:
        print("\nParsing %s" % i)
        newick = is_newick(i)

        if newick:
            print("\nFound a tree: \n%s\n" % i)

            try:
                t = Phylo.read(StringIO(i), "newick")
                Phylo.draw_ascii(t)
                # empty labels as clade

                # Phylo.draw(t)

            except Exception as e:
                print("\nSomething went wrong, tree unrecognised by Pyhlo. ")
                print("Exception: %s" % e)

        else:
            print("\nNot a valid Newick tree: \n%s\n" % i)