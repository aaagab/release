# Release Package Manager (GPM in disguise aka Generic Package Manager)

There are five location types for packages:  
- bin (binaries) packages repository
- pkg (package) only package
- rel (releases) packages repository
- src (sources) packages repository
- wrk (work) packages repository

All location types have a default location (fty means factory):  
- bin = %userprofile%/fty/bin
- rel = %userprofile%/fty/rel
- pkg = current directory
- src = %userprofile%/fty/src
- wrk = %userprofile%/fty/wrk

Each package at a location type has a defined structure.
Transfering a package from one location to another may imply modifying its structure at destination.

to delete a package in a release repository, delete the folder manually and run --generate-db --path-rel


To select a package you use a package filter:  
use one value:
  uuid4|name|version|bound

name,version,