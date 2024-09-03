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
import pathlib
import subprocess
import sys
import tempfile

import psutil

from .util import find_relenv_gdb

INJ_TPL = """
set pagination off
source {libpython}
echo acquire gill\\n
call (char *) PyGILState_Ensure()
call (PyObject *) Py_BuildValue("s", "{inject_path}")
call (FILE *) _Py_fopen_obj($2, "r+")
call (void) PyRun_SimpleFile($3, "{inject_path}")
echo release gill\\n
call (void) PyGILState_Release($1)
quit
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

    s_fd, inject_path = tempfile.mkstemp(suffix=".py")
    with open(file, "r") as fp:
        with open(inject_path, "w") as fp2:
            fp2.write(fp.read())
    fd, gdb_command = tempfile.mkstemp()
    try:
        with open(gdb_command, "w") as fp:
            fp.write(
                INJ_TPL.format(
                    inject_path=inject_path,
                    libpython=(
                        pathlib.Path(__file__).parent / "libpython.py"
                    ).resolve(),
                )
            )
        subprocess.run(
            [str(find_relenv_gdb()), "-p", f"{pid}", "--command", gdb_command],
            capture_output=False,
        )
    finally:
        os.close(fd)
        os.remove(gdb_command)
        os.close(s_fd)
        os.remove(inject_path)


if __name__ == "__main__":
    main()
