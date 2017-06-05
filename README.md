miditxt
========================

miditxt is a python script which can convert midi files (.mid) into a human readable format called midi txt. It can then be edited via text editor, and then 

Usage
------------------------
    python miditxt.py filename.mid
Reads 'filename.mid' and outputs its miditxt equivalent to 'filename.txt'

TODO & Bugs
------------------------
- TODO: Implement converting from miditxt to midi. Currently only works one way :( 
- TODO: Test most events
- TODO: Ensure that support for midi formats 0, 1, 2 work properly
- TODO: Implement SMTPE  ticks/frame frames/second divisioning
