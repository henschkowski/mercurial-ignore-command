This command extension for Mercurial / hg allows to add files and folders to the `<project-root>/.hgignore` file. Mercurial will then ignore those files
and directories in the `hg status` command.

The `.hgignore` file will be created if it does not exist.


## Installation ##

Add the following two lines to your `~/.hgrc` or `<project-root>/.hg/hgrc` file:

```
[extensions]
ignore=/your/path/to/ignore_cmd.py
```


## Usage ##

This adds files  `file1, file2` and directories ` dir1, dir2` to `.hgignore`:

```
hg ignore file1 file2 dir1 dir2
```

To add  file patterns to `.hgignore`, change the file with an editor.
