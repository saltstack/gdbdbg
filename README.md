On Debian based distributions you must install the gdb and salt-dbg system
packages.

On RPM based distributions you must install the salt-debuginfo and gdb system
packages.

relenv-dbg will gather some general debugging information as well as the stack traces from each thread.

```
/opts/saltstack/extras-3.10/bin/relenv-dbg <pid>
```

relenv-inject can be used to inject some python code into the running process.

If you have manhole installed you can write a script like this:

```manhole.py
import manhole
manhole.install()
```

And inject it with relenv-inject:

```
/opts/saltstack/extras-3.10/bin/relenv-inject <pid> manhole.py
```
