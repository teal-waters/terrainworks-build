all: bldgrds mkgrids deptowater hand

# Detect OS
UNAME_S := $(shell uname -s)

bldgrds:
	$(MAKE) -f Makefile_bldgrds

mkgrids:
	$(MAKE) -f Makefile_mkgrids

deptowater:
	$(MAKE) -f Makefile_deptowater

hand:
	$(MAKE) -f Makefile_hand

.PHONY: all clean

clean:
	$(MAKE) -f Makefile_bldgrds clean
	$(MAKE) -f Makefile_mkgrids clean
	$(MAKE) -f Makefile_deptowater clean
	$(MAKE) -f Makefile_hand clean