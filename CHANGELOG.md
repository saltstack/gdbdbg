0.2.5
=====

This is the first public release.

* Automation of test release pipeline
* Upgrade gdb and relenv versions used while building
* Fix issues in wheel missing needed shared libraries
* Improve inject script reliability by using PyRun_SimpleFile instead of
  PyRun_SimpleString.
* Add script to build wheel in docker container.

0.1.0
=====

Initial release.

* Bundles gdb in a wheel. 
* Adds gdb entry point to start gdb.
* Adds dbg entry point to quickly get information threads and their python stack
  traces.
* Adds inject entrypoint to inject python into a running cpython process.
