# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Inject python code into a running process.

Usage:
  python3 ./inject.py <pid> mycode.py

Example mycode.py that will install a manhole into the running process. Manhole
should already be in the path:

  import manhole
  manhole.install()

"""
import os
import subprocess
import sys
import tempfile

import psutil

INJ_TPL = """
set pagination off
source libpython.py
source {}
echo acquire gill\\n
call PyGILState_Ensure()
p $SCRIPT
call PyRun_SimpleString($SCRIPT)
echo release gill\\n
call PyGILState_Release($1)
quit
"""


SCRIPT = """#!/usr/bin/python
import gdb
with open("{}", "r") as fp:
    gdb.set_convenience_variable("SCRIPT", fp.read())
"""


def main():
    """
    The inject program entrypoint.
    """
    try:
        pid = int(sys.argv[1])
    except (IndexError, ValueError):
        pid = -1
    try:
        psutil.Process(pid)
    except (ValueError, psutil.NoSuchProcess):
        print("Please provide a valid pid as the first argument")
        sys.exit(1)

    try:
        file = sys.argv[2]
    except IndexError:
        print("Please provide an input file as the second argument")

    s_fd, s_path = tempfile.mkstemp(suffix=".py")
    with open(s_path, "w") as fp:
        fp.write(SCRIPT.format(file))

    fd, path = tempfile.mkstemp()
    try:
        with open(path, "w") as fp:
            fp.write(INJ_TPL.format(s_path))
        subprocess.run(["gdb", "-p", f"{pid}", "--command", path], capture_output=False)
    finally:
        os.close(fd)
        os.remove(path)
        os.close(s_fd)
        os.remove(s_path)


if __name__ == "__main__":
    main()
