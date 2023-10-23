# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Use gdb to pull python stack traces for every thread in a parent process and all of it's children.
"""
import os
import pathlib
import pprint
import subprocess
import sys
import tempfile

import psutil

CMD_TPL = """
set pagination off
set logging file {output}
set logging enabled on
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


def find_dist_info():
    """Find relenv_gdb's dist-info directory."""
    for name in pathlib.Path(__file__).parent.parent.rglob("relenv_gdb*dist-info"):
        return name


def find_relenv_gdb():
    """Find the relenv-gdb script location."""
    dist_info = find_dist_info()
    text = pathlib.Path(dist_info, "RECORD").read_text()
    for line in text.split("\n"):
        if "bin/relenv-gdb" in line:
            location, digest, size = line.rsplit(",", 2)
            script = (pathlib.Path(dist_info).parent / location).resolve()
            if script.exists():
                return script


def append_line(path, line):
    """
    Append a line to the path.
    """
    with open(path, "a") as fp:
        fp.write(line + "\n")


def debug(gdb, proc, output):
    """
    Run debug.
    """
    print(f"Debugging {proc.pid} {' '.join(proc.cmdline())}")
    fd, path = tempfile.mkstemp()
    with open(path, "w") as fp:
        fp.write(
            CMD_TPL.format(
                output=output,
                pid=proc.pid,
                libpython=(pathlib.Path(__file__).parent / "libpython.py").resolve(),
            )
        )
    append_line(output, f"===[ begin {proc.pid} ]===")
    append_line(output, pprint.pformat(proc.as_dict()))
    subprocess.run([gdb, "-p", f"{proc.pid}", "--command", path], capture_output=True)
    append_line(output, f"===[ end {proc.pid} ]===")
    os.close(fd)
    os.remove(path)


def main():
    """
    The debug programs entrypoint.
    """
    try:
        pid = int(sys.argv[1])
    except (IndexError, ValueError):
        pid = -1
    try:
        parent = psutil.Process(pid)
    except (ValueError, psutil.NoSuchProcess):
        print("Please provide a valid pid as the only argument")
        sys.exit(1)

    gdb = find_relenv_gdb()
    if not gdb:
        print("Unable to find relenv-gdb script")
    output = "gdb-output.txt"

    debug(gdb, parent, output)

    for child in parent.children():
        debug(child, output)


if __name__ == "__main__":
    main()
