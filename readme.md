# Newick format validator

Given a textual file, the *Newick format validator* checks whether it respects the Newick notation and shows eventual deformities. The program has been written using Python: both 2.7 and 3 are compatible.

Newick notation rules have been extracted by [Wikipedia](https://en.wikipedia.org/wiki/Newick_format) and [Phylip documentation](http://evolution.genetics.washington.edu/phylip/newick_doc.html).

The Newick validator works using the `Phylo`, `io` and `re` packages, respectively to draw trees, handle input/output and use regular expressions.



### Newick format for trees

The *Newick format* is a way to represent graph-theoretical trees with edge lengths, using parentheses and commas. This format is typically used to define phylogenetic trees.

When an unrooted tree is represented in Newick notation, an arbitrary node (typically an internal one) is chosen as its root.

A *rooted* (on an internal node) *binary tree* has exactly two immediate descendant nodes for each internal node.

An *unrooted binary tree* has exactly three immediate descendant nodes for the root node (an arbitrary internal one) and two for each other internal node.

A *binary tree rooted from a leaf* has at most one immediate descendant node for the root, and exactly two for each other internal node.



### Grammar rules

*Tree* → the full input Newick format for a single tree.

*Subtree* → an internal node and its descendants, or a leaf node.

*Branch* → a tree edge and its descendant subtree.

*BranchSet* → a set of one or more Branches.

Colon, semicolon, parentheses, comma and quotes are required parts of the format.

``` 
Tree → Subtree “;” | Branch “;”
Subtree → Leaf | Internal
Internal → “(“ BranchSet “)” Name
BranchSet → Branch | Branch “,” BranchSet
Branch → Subtree Length
Name → empty | string
Length → empty | “:” number
```

All grammar rules have been implemented through recursion (unrooted tree is accepted, and so are labelled internal nodes).

##### Notes on grammar rules

Whitespace within *number* is prohibited. Whitespace within *string* is often prohibited (in this case, the validator considers a whitespace within *string* as an error). Whitespace elsewhere is ignored.

The *name* string doesn’t have fixed length, but the punctuation characters from the grammar are prohibited. The tree must end with a semicolon.

The validator is able to recognise the following errors:

* Missing semicolon at the end;
* Semicolon, colon, whitespace, number and open parentheses within *name*;
* Invalid *number* format;
* Unbalanced parentheses.

There is no explicit handling of comma and close parenthesis within string, since the string `ab,cd` can eiher represent an error or two nodes without length, and the string `ab)cd` may represent a labelled internal node. Mistakes of these types are found while parsing subtrees.

##### Special characters

All special characters besides colon, semicolon, parentheses and comma are allowed and parsed as part of the label. Labels must still be a non-numeric string.

Quotes aren't explicitly handled, but quotes within (before, after and in the middle) strings are recognised and ignored. Underscore is recognised and ignored as well.

There is the possibility to have more than a tree in the `.txt` file: newline is used as separator, so a single tree in multiple lines will return an error of some kind.

Tabs are ignored and correctly parsed: there might be some issues displaying trees containing tabs within strings because of the `Phylo.draw_ascii` function which draws the tree on terminal.



### Functioning of the validator

The Python validator takes a file as input (parameter, when running the program) and proceeds to read the whole content and split the trees using newlines.

All functions used to parse string are imported in the main file from a separated package.

The main Python program is CLI.py, which includes the functions to read the textual file, split the content and then calls `newick_validator.is_newick()` on each string. After the latter returns a value, the tree is drawn on console.

The library `newick_validator` groups all the methods to divide the tree in components according to grammar rules and recursively check the syntax.

The first function, called on every string of the file, is `is_newick`. A regular expression is used to split each string in tokens:

```python
tokens = split(r'([A-Za-z]+[^A-Za-z,)]+[A-Za-z]+|[0-9.]*[A-Za-z]+[0-9.]+|[0-9. ]+|[A-za-z]+|\(|\)|;|:|,)', tree)
```

This is able to recognise:

* Strings of at least two alphabetic characters with at least one forbidden special symbol (to find errors);
* Strings composed of alphabetic charachers, numbers and special symbols;
* Alphabetic characters strings;
* Numbers with dots;
* Parentheses, colon, semicolon and comma.

After that, the final semicolon and the spaces are removed (if present) and the recursive calls begin, deleting eventual parentheses surrounding internal nodes. Each call returns a boolean value which determines whether to continue parsing or stop because of an error.

The `BranchSet → Branch | Branch "," BranchSet` rule is implemented finding the index of each external comma (outside all sets of parentheses) and splitting according to every index.

Empty values are permitted and handled: *name* and *number* can be empty, so there can be branches and subtrees containing nothing.

Whenever the validator finds an empty tree (newline with no following text), it prints a message and doesn't call the functions.

The validator, if the tree is valid, draws it on console using the `Phylo.draw_ascii()` function. It is also possible to draw the tree using Matlab, uncommenting the last two lines of code. Empty nodes are labelled as *clades*.

If the tree is not valid, the validator prints an error message at the *first occurrence* of a mistake, prints the substring where the mistake was found and stops parsing.

The program contains exception handling, since some controls have been implemented using list indexes or forcing string casting.

##### Example with working string

String: `(ant:17, (bat:31, cow:22):25, dog:22, (elk:33, fox:12):40):30;`

All recursive calls return True, then the validator proceeds to parse the sub-elements and the rest of the tree. The Python program doesn't print each function call: they are just shown to illustrate and track recursion.

```python
Calling newick on (ant:17, (bat:31, cow:22):25, dog:22, (elk:33, fox:12):40):30; 
Calling parse_tree on (ant:17,(bat:31,cow:22):25,dog:22,(elk:33,fox:12):40):30
Calling parse_branch on (ant:17,(bat:31,cow:22):25,dog:22,(elk:33,fox:12):40):30
Calling parse_length on 30
Calling parse_subtree on (ant:17,(bat:31,cow:22):25,dog:22,(elk:33,fox:12):40)
Calling parse_internal on (ant:17,(bat:31,cow:22):25,dog:22,(elk:33,fox:12):40)
Calling parse_branchset on ant:17,(bat:31,cow:22):25,dog:22,(elk:33,fox:12):40
Calling parse_branch on ant:17
Calling parse_length on 17
Calling parse_subtree on ant
Found a leaf as ant
Calling parse_name on ant
Calling parse_branchset on (bat:31,cow:22):25,dog:22,(elk:33,fox:12):40
Calling parse_branch on (bat:31,cow:22):25
Calling parse_length on 25
Calling parse_subtree on (bat:31,cow:22)
Calling parse_internal on (bat:31,cow:22)
Calling parse_branchset on bat:31,cow:22
Calling parse_branch on bat:31
Calling parse_length on 31
Calling parse_subtree on bat
Found a leaf as bat
Calling parse_name on bat
Calling parse_branchset on cow:22
Calling parse_branch on cow:22
Calling parse_length on 22
Calling parse_subtree on cow
Found a leaf as cow
Calling parse_name on cow
Calling parse_branchset on dog:22,(elk:33,fox:12):40
Calling parse_branch on dog:22
Calling parse_length on 22
Calling parse_subtree on dog
Found a leaf as dog
Calling parse_name on dog
Calling parse_branchset on (elk:33,fox:12):40
Calling parse_branch on (elk:33,fox:12):40
Calling parse_length on 40
Calling parse_subtree on (elk:33,fox:12)
Calling parse_internal on (elk:33,fox:12)
Calling parse_branchset on elk:33,fox:12
Calling parse_branch on elk:33
Calling parse_length on 33
Calling parse_subtree on elk
Found a leaf as elk
Calling parse_name on elk
Calling parse_branchset on fox:12
Calling parse_branch on fox:12
Calling parse_length on 12
Calling parse_subtree on fox
Found a leaf as fox
Calling parse_name on fox

Found a tree: 
(ant:17, (bat:31, cow:22):25, dog:22, (elk:33, fox:12):40):30; 

                       ___________ ant
                      |
                      |                 _____________________ bat
                      |________________|
______________________|                |_______________ cow
                      |
                      |______________ dog
                      |
                      |                            _______________________ elk
                      |___________________________|
                                                  |________ fox          
                                                  
```

##### Example with not working string

String: `(dog:20, (elep:hant:30, horse:60):20):50;`

The validator stops as soon as it finds the error (colon within `elephant`).

```python
Calling newick on (dog:20, (elep:hant:30, horse:60):20):50;
Calling parse_tree on (dog:20,(elep:hant:30,horse:60):20):50
Calling parse_branch on (dog:20,(elep:hant:30,horse:60):20):50
Calling parse_length on 50
Calling parse_subtree on (dog:20,(elep:hant:30,horse:60):20)
Calling parse_internal on (dog:20,(elep:hant:30,horse:60):20)
Calling parse_branchset on dog:20,(elep:hant:30,horse:60):20
Calling parse_branch on dog:20
Calling parse_length on 20
Calling parse_subtree on dog
Found a leaf as dog
Calling parse_name on dog
Calling parse_branchset on (elep:hant:30,horse:60):20
Calling parse_branch on (elep:hant:30,horse:60):20
Calling parse_length on 20
Calling parse_subtree on (elep:hant:30,horse:60)
Calling parse_internal on (elep:hant:30,horse:60)
Calling parse_branchset on elep:hant:30,horse:60
Calling parse_branch on elep:hant:30
Calling parse_length on 30
Calling parse_subtree on elep:hant
Found a leaf as elep:hant
Calling parse_name on elep:hant
Error: colon in elep:hant.

Not a valid Newick tree: 
(dog:20, (elep:hant:30, horse:60):20):50;
```



### Test examples

A complete list of test examples can be found running `test.py`.

##### Working strings

```
(ant:17, (bat:31, cow:22):25, dog:22, (elk:33, fox:12):40); 
((cow:12, gnu:10)bigThings:3, (ant:23, bat:19)smallThings:5); 
(dog:20, (elephant:30, horse:60):20):50;
(A,B,(C,D)); 
(A,B,(C,D)E)F;
(((One:0.2,Two:0.3):0.3,(Three:0.5,Four:0.3):0.2):0.3,Five:0.7):0.0;
(:0.1,:0.2,(:0.3,:0.4):0.5);
(:0.1,:0.2,(:0.3,:0.4):0.5):0.0;
(A:0.1,B:0.2,(C:0.3,D:0.4):0.5);
(A:0.1,B:0.2,(C:0.3,D:0.4)E:0.5)F;
((B:0.2,(C:0.3,D:0.4)E:0.5)A:0.1)F;
(,,(,));
```

##### Not working strings

```
(ant:17, (bat:31, cow:22):25, dog:22, (elk:33, fox:12:40); → unbalanced parentheses
(ant:17, (bat:31, co w:22):25, dog:22, (elk:33, fox:12):40); → space within string
(a:nt:17, (bat:31, cow:22):25, dog:22, (elk:33, fox:12):40); → colon within string
(a(nt:17, (bat:31, cow:22):25, dog:22, (elk:33, fox:12):40); → parentheses within string
(ant:17, (bat:3 1, cow:22):25, dog:22, (elk:33, fox:12):40); → space within number
(ant:17, (bat:31, cow:22):25, dog:22, (elk:33, fox:12:40):30:30; → too many numbers
(ant:17, (bat:31, cow:22):25, dog:22:abc, (elk:33, fox:12):40):30; → number as label
```