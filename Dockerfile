FROM intel/fortran-essentials:2025.1.2-0-devel-ubuntu24.04

RUN apt-get update && apt-get install -y \
  python3-pip \
  python3-dev \
  makedepf90 \
  && apt-get autoclean \
  && apt-get autoremove \
  && rm -rf /var/lib/{apt,dpkg,cache,log}

ADD . /code
WORKDIR /code
RUN make

# Add /code to PATH so binaries are there too
ENV PATH="/code:${PATH}"
