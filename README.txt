On Debian based distributions you must install the gdb and salt-dbg system
packages.

On RPM based distributions you must install the salt-debuginfo and gdb system
packages.

Once you have the pre-requisists find the top level Salt process and pass it's
PID to the dbg.py script using Salt's python interpreter.

/opts/saltstack/salt/bin/python3 ./dbg.py <PID>

The dbg.py script will use gdb to run gdb-command.txt the PID and all of it's
child processes. The output is saved to gdb-output.txt.
