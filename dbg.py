"""
Use gdb to pull python stack traces for every thread in a parent process and all of it's children.
"""
import sys
import psutil
import subprocess
import pprint


def append_line(path, line):
    with open(path, "a") as fp:
        fp.write(line + "\n")


if __name__ == "__main__":
    try:
        pid = int(sys.argv[1])
    except (IndexError, ValueError):
        pid = -1
    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print("Please provide a valid pid as the only argument")
        sys.exit(1)

    output = "gdb-output.txt"

    append_line(output, f"===[ begin {parent.pid} ]===")
    append_line(output, pprint.pformat(parent.as_dict()))
    subprocess.run(["gdb", "-p", f"{parent.pid}", "--command", "gdb-command.txt"])
    append_line(output, f"===[ end {parent.pid} ]===")
    for child in parent.children():
        append_line(output, f"===[ begin {child.pid} ]===")
        append_line(output, pprint.pformat(child.as_dict()))
        subprocess.run(["gdb", "-p", f"{child.pid}", "--command", "gdb-command.txt"])
        append_line(output, f"===[ end {child.pid} ]===")

