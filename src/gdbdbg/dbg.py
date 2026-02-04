# Copyright 2026 Broadcom, Inc.
# Copyright 2023-2026 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Use gdb to pull python stack traces a parent process and all of it's children.
"""
import argparse
import os
import pathlib
import pprint
import subprocess
import sys
import tempfile

import psutil

from .util import append_line, find_relenv_gdb

CMD_TPL = """
set pagination off
source {libpython}
echo --- thread info for pid {pid} ---\\n

info threads
echo --- end - thread info for pid {pid}---\\n\\n\\n

echo --- tracebacks for pid {pid} ---\\n
thread apply all bt
echo --- end - tracebacks ---\\n\\n\\n

echo --- python tracebacks for pid {pid} ---\\n
thread apply all py-bt-full
echo --- end - python tracebacks for pid {pid} ---\\n
set logging enabled off
quit
"""


def debug(gdb, proc, output):
    """
    Run debug.
    """
    print(f"Debugging {proc.pid} {' '.join(proc.cmdline())}")
    fd, path = tempfile.mkstemp()
    with open(path, "w") as fp:
        fp.write(
            CMD_TPL.format(
                pid=proc.pid,
                libpython=(pathlib.Path(__file__).parent / "libpython.py").resolve(),
            )
        )
    append_line(output, f"===[ begin {proc.pid} ]===")
    append_line(output, pprint.pformat(proc.as_dict()))
    if output == sys.stdout:
        capture_output = False
    else:
        capture_output = True
    subprocess.run(
        [gdb, "-p", f"{proc.pid}", "--command", path], capture_output=capture_output
    )
    append_line(output, f"===[ end {proc.pid} ]===")
    os.close(fd)
    os.remove(path)


def main():
    """
    The debug programs entrypoint.
    """
    parser = argparse.ArgumentParser(
        prog="relenv-dbg",
        description="Use gdb to debug python programs running in a relenv",
        epilog="",
    )
    parser.add_argument("pid", type=int)
    parser.add_argument(
        "--output", "-o", type=argparse.FileType("w"), default=sys.stdout
    )
    args = parser.parse_args()
    try:
        parent = psutil.Process(args.pid)
    except (ValueError, psutil.NoSuchProcess):
        print("Please provide a valid pid")
        sys.exit(1)

    gdb = find_relenv_gdb()
    if not gdb:
        print("Unable to find relenv-gdb script")

    debug(gdb, parent, args.output)

    for child in parent.children():
        debug(gdb, child, args.output)


if __name__ == "__main__":
    main()
