"""Helper for handling files."""


def readlines(file):
    """
    Helper method for reading one line at a time from a file and yielding it
    for loops. The file is closed automatically even if the caller exits the
    loop early (break, exception, etc).

    :param file: The file to read data from.
    :return: yield a line in a loop
    """
    with open(file) as f:
        for line in f:
            yield line.rstrip()


def readlines_both(file1, file2):
    """
    Helper method for reading one line at a time from two files and yielding
    them for loops. For each line in file1 it will also loop through all lines
    of file2. Total no. of yields is lines in file1 x lines in file2.
    The files are closed automatically even if the caller exits the loop early
    (break, exception, etc).

    :param file1: The first file to read data from
    :param file2: The second file to read data from
    :return:
    """
    with open(file1) as f1:
        for l1 in f1:
            with open(file2) as f2:
                for l2 in f2:
                    yield l1.rstrip(), l2.rstrip()
