# ignore_cmd.py - Ignore command extension for Mercurial
#
# Copyright (c) 2012 Ralf Henschkowski <ralf at henschkowski dot com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


""" ignore command

Add argument files (i.e., command line arguments to 'hg ignore <file1> <file2> ...'
to .hgignore file (using glob syntax)

Installation:
Add the following two lines to your ~/.hgrc or <project-root>/.hg/hgrc file:

  [extensions]
  ignorecmd=/your/path/to/ignore_cmd.py

"""
import os, fileinput, re, sys
from mercurial import util


def is_already_ignored(file_rel, ignore_filename):
    """ Check if <file> is already ignored in <ignore_filename> """
    with open(ignore_filename) as ignore_file:
        for line in ignore_file:
                l = line.strip()
                if l == file_rel:
                    return True
    return False
                        
# Every command must take ui and and repo as arguments.
# opts is a dict where you can find other command line flags.
#
# Other parameters are taken in order from items on the command line that
# don't start with a dash. If no default value is given in the parameter list,
# they are required.
#
# For experimenting with Mercurial in the python interpreter:
# Getting the repository of the current dir:
#    >>> from mercurial import hg, ui
#    >>> repo = hg.repository(ui.ui(), path = ".")

def ignore(ui, repo, *user_files, **opts):
    # The doc string below will show up in hg help.
    """Add files to ignore list in the .hgignore file."""

    # Use HG API call to get all files in state "unknown". Those are relative to the repo root
    unknown_files = repo.status(unknown=True)[4]
    # Bring user-given file names into the "relative-to-HG-root" format
    files_absolute = [ os.path.realpath(p) for p in user_files ]
    files = [ os.path.relpath(p, repo.root) for p in files_absolute ]

    # Check if ignore file exists, otherwise create it
    ignore_filename = os.path.normpath(os.path.join(repo.root, ".hgignore"))
    try:
        with open(ignore_filename, "a") as f: pass
    except:
        with open(ignore_filename, "w") as f: f.write()

    # Check if the files given on the command line are really unknown to HG
    already_ignored = set()
    for f in files:
        if os.path.isdir(f):
            # Directories are not tracked, but we want to add them to .hgignore, anyway. 
            continue
        if f not in unknown_files:
            if is_already_ignored(f, ignore_filename):
                ui.write("File %s is already ignored.\n" % (f,))
                already_ignored.add(f)
            else:
                raise util.Abort("File %s is not in state UNKNOWN." % (f,))

    # Prepare list of files to be ignored in .hgignore line-by-line syntax
    ignores = ""
    for f in (set(files) - already_ignored):
        ignores += f
        ignores += '\n'
    ui.write("Ignored:\n%s" % (ignores,))

    # Search for the glob section in .hgignore; when found, insert filenames after
    found_glob = False
    for line in fileinput.input(ignore_filename, inplace=True, mode="rU"):
        if re.match("^syntax:.*glob", line):
            sys.stdout.write(line)
            sys.stdout.write(ignores)
            found_glob = True
        else:
            sys.stdout.write(line)

    # No "syntax: glob" section in .hgignore file found -> create one
    if not found_glob:
        with open(ignore_filename, "a") as ignore_file:
            ignore_file.write("syntax: glob\n")
            ignore_file.write(ignores)


# Boilerplate code for Mercurial command extensions
cmdtable = {
    # cmd name        function call
    'ignore': (ignore,
               # See mercurial/fancyopts.py for all of the command flag options.
               [], "hg ignore <files...>"
               )
}

testedwith = '1.4'

