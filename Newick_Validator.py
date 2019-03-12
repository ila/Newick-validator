#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Newick format validator
# imported in CLI.py

# imports
from re import split


# returns true if the given input is a number
def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


# returns the index of the first comma outside parenthesis
# comma separates branches
def find_branch(parsed_tokens):
    open = 0
    closed = 0
    first_comma_index = None

    for char_index, char in enumerate(parsed_tokens):
        if char == "(":
            open += 1
        elif char == ")":
            closed += 1

        if open - closed == 0:
            if char == "," \
                    and first_comma_index is None:
                first_comma_index = char_index

    return first_comma_index


# tree -> subtree [label] [: length] ";"
# tree -> subtree ";" | branch ";"
def parse_tree(parsed_tokens):
    if is_number(parsed_tokens[-1]):
        # found a branch with length
        return parse_branch(parsed_tokens)

    # subtree without label and length
    return parse_subtree(parsed_tokens)


# subtree -> leaf | internal
def parse_subtree(parsed_tokens):
    try:
        if parsed_tokens[0] == '(':

            # found an internal node
            if parsed_tokens[-1] == ')':
                return parse_internal(parsed_tokens)

            if ')' not in parsed_tokens:
                print("Unbalanced parentheses in %s!" % ''.join(parsed_tokens))
                return False

            else:

                if parse_name(parsed_tokens[-1]):
                    # found a labelled internal node
                    return parse_internal(parsed_tokens[:-1])

                else:
                    return False

        else:

            if ')' in parsed_tokens:
                print("Unbalanced parentheses in %s!" % ''.join(parsed_tokens))
                return False

            # found a leaf
            return parse_name(parsed_tokens[0])

    except IndexError:
        pass


# leaf --> name
# name --> empty | string
def parse_name(name):

    # checking whether a string contains a space
    if ' ' in name:
        print("Error: space in %s." % name)
        return False

    # checking whether a string contains :
    if ':' in name:
        print("Error: colon in %s." % name)
        return False

    # checking whether a string contains (
    if '(' in name or ')' in name:
        print("Error: unbalanced parentheses in %s." % name)
        return False

    # checking whether a string contains ;
    if ';' in name:
        print("Error: semicolon in %s." % name)
        return False

    return True


# branchset --> branch | branch "," branchset
def parse_branchset(parsed_tokens):
    comma = find_branch(parsed_tokens)

    if comma is None:
        # found a single branch
        return parse_branch(parsed_tokens)

    # found a branch and a branchset
    else:

        if parse_branch(parsed_tokens[0:comma]):
            # successful parsing
            return parse_branchset(parsed_tokens[comma + 1:])

        else:
            return False


# branch --> subtree length
def parse_branch(parsed_tokens):
    # empty branch
    if not parsed_tokens:
        return True

    # length is not empty
    try:
        if parsed_tokens[-2] == ':':
            length_ok = parse_length(parsed_tokens[-1])

            # label or subtree are not empty
            if parsed_tokens[:-2]:
                subtree_ok = parse_subtree(parsed_tokens[:-2])
                return length_ok and subtree_ok

            else:
                return length_ok

    except IndexError:
        pass

    # there is only a subtree
    return parse_subtree(parsed_tokens)


# length --> empty | ":" number
def parse_length(number):
    if is_number(number):
        return True

    print("%s is not a number." % number)
    return False


# internal --> "(" branchset ")" name
def parse_internal(parsed_tokens):
    if parsed_tokens[-1] != ')':
        # name is not empty
        name_ok = parse_name(parsed_tokens[-1])

        if name_ok:
            return parse_branchset(parsed_tokens[1:-2])

        else:
            return False

    # controls on balanced parentheses already made
    return parse_branchset(parsed_tokens[1:-1])


# first function performing the initial controls
def is_newick(tree):
    # dividing the string into tokens, to check them singularly
    tokens = split(r'([A-Za-z]+[^A-Za-z,)]+[A-Za-z]+|[0-9.]*[A-Za-z]+[0-9.]+|[0-9.]+\s+[0-9.]+|[0-9.]+|[A-za-z]+|\(|\)|;|:|,)', tree)

    # removing spaces and empty strings (spaces within labels are still present)
    parsed_tokens = list(filter(lambda x: not (x.isspace() or not x), tokens))

    # checking whether the tree ends with ;
    if parsed_tokens[-1] != ';':
        print("Tree without ; at the end.")
        return False

    # first controls passed, calling the recursive function
    else:
        del parsed_tokens[-1]
        return parse_tree(parsed_tokens)
