gdbdbg
======

gdbdbg will gather some general debugging information as well as the stack
traces from each thread.

```
gdbdbg-info <pid>
```

gdbdbg-inject can be used to inject some python code into the running process.

If you have manhole installed you can write a script like this:

```manhole.py
import manhole
manhole.install()
```

And inject it with gdbdbg-inject:

```
gdbdbg-inject <pid> manhole.py
```
