# terrainworks-build

The goal of this repository is to have a reproducible setup to compile TerrainWorks fortran code and create releases of selected binaries (currently `MakeGrids` and `bldgrds2`). These binaries are currently available for Linux and Windows. It includes the `modules` and `GridUtilites` repositories as submodules, so its basic components are a Makefile and a Dockerfile. This repository also contains a python package which allows programmatic access to built binaries for use in "wrappers", etc.

## Python package

The `terrainworks-build` package provides Python access to selected binaries in Linux and Windows. It is published to the teal-waters Azure Artifacts feed.

### Package Installation

```
uv add terrainworks-build --index https://pkgs.dev.azure.com/teal-waters/default/_packaging/python/pypi/simple/
```

Authentication is required — use an Azure DevOps personal access token with **Packaging (read)** scope.

### Usage

`get_binary_path` returns the path to a binary, downloading it from the matching GitHub release on first use.
This path can be used by a "wrapper" to have a reliable path to the desired executable.

```python
from subprocess import run
from terrainworks_build import get_binary_path

makegrids = get_binary_path("MakeGrids")
# Example usage
run([makegrids, "makegrids_config.txt"])
```

## Updating binaries

Follow this process if new functionality is available in the submodules and you wish to release a new version of this package with the updates. This process does not require local development, and can be completed on all platforms.

### Update submodules

Assuming submodules are on the correct branch, we can point to the most current commits using:

`git pull --recurse-submodules`.

Then commit the submodule pointer changes:

`git add modules GridUtilities && git commit -m "chore: update submodules"`

### Release a new version

Tag the commit with a version number (please see existing releases/tags for the next version):

`git tag v1.2.3 && git push origin v1.2.3`

Pushing a `v*` tag triggers CI to build Linux and Windows binaries, publish them as a GitHub Release, build Python wheels, and publish the package to Azure Artifacts.

## Local Development

To compile binaries locally or if you need to work to compile other binaries, the build process will need to be run locally for development.

These instructions are for Linux. This process has not been tested on Windows. If you are interested in testing this on Windows, check the setup process in [.github/workflows/release.yml](.github/workflows/release.yml) for an example.

First, clone this repository, then run

`git submodule update --init --recursive`

to pull submodules.

### Prerequisites

The intel fortran compiler "`ifx`" needs to be installed, using one of the methods [here](https://www.intel.com/content/www/us/en/developer/tools/oneapi/fortran-compiler-download.html?operatingsystem=linux&distribution-linux=offline). To enable the compiler, you will also need to [run the setvars script](https://www.intel.com/content/www/us/en/docs/oneapi/programming-guide/2025-1/use-the-setvars-and-oneapi-vars-scripts-with-linux.html) by running

`source /opt/intel/oneapi/setvars.sh`.

You will also need [makedepf90](https://linux.die.net/man/1/makedepf90), which may already be installed.

### Building the programs

Run `make`.

### Running tests

Some simple tests have been written in tests/. To run them, change into that directory and run

`./run_tests.sh`.
