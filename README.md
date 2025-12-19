# terrainworks-build

The goal of this repository is to have a reproducible setup to compile TerrainWorks fortran code under Linux, and create and publish a Docker image with tool executables. It includes the `modules` and `GridUtilites` repositories as submodules, so its basic components are a Makefile and a Dockerfile.

It currently builds the `bldgrds` and `MakeGrids` executables.

## Installation

Clone this repository, then run

`git submodule update --init --recursive`

to pull submodules.

## Usage

### Prerequisites

ifx needs to be installed, using one of the methods [here](https://www.intel.com/content/www/us/en/developer/tools/oneapi/fortran-compiler-download.html?operatingsystem=linux&distribution-linux=offline). To enable the compiler, you will also need to [run the setvars script](https://www.intel.com/content/www/us/en/docs/oneapi/programming-guide/2025-1/use-the-setvars-and-oneapi-vars-scripts-with-linux.html) but running .e.git

`source /opt/intel/oneapi/setvars.sh`.

You will also need [makedepf90](https://linux.die.net/man/1/makedepf90), which may already be installed.

### Building the programs

Run `make`.

### Updating submodules

Assuming submodules are on the correct branch, they can be updating using

`git pull --recurse-submodules`.

### Running tests

Some simple tests have been written in tests/. To run them, change into the that directory and run

`source run_tests.sh`.
