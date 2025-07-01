FROM intel/fortran-essentials:2025.1.2-0-devel-ubuntu24.04

RUN apt-get update && apt-get install -y \
  python3-pip \
  python3-dev \
  git \
  makedepf90 \
  wget \
  unzip \
  && apt-get autoclean \
  && apt-get autoremove \
  && rm -rf /var/lib/{apt,dpkg,cache,log}

ADD . /code
WORKDIR /code
RUN mkdir -p /code/scratch /code/Skykomish_90503
RUN make bldgrds

COPY input_bldgrds.txt /code/input_bldgrds.txt
RUN wget -O /code/Skykomish_90503.zip "https://www.dropbox.com/scl/fi/n7hhdm6mayo8vwmt7oqul/Skykomish_90503.zip?rlkey=n68yzu3hf87vgufau0y5wkjct&st=2u9n3p4a&dl=1" \
    && unzip -o /code/Skykomish_90503.zip -d /code/Skykomish_90503 \
    && rm /code/Skykomish_90503.zip

RUN ls -l /code
RUN ls -l /code/Skykomish_90503
RUN ls -l /code/built_mods

ENTRYPOINT ["/code/bldgrds", "input_bldgrds.txt" ]