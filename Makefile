# I don't know if ifx/ifort was previously used but it seems to function better with
# the existing codebase than gfortran. 
# Note that /opt/intel/oneapi/setvars.sh (locally) needs to be called before
# running ifx, but I think it can only be called once.
FC = ifx
MOD_OUT = built_mods
# Most of these flags are the recommended ones. A couple notes though for ifx:
# 1. `-qmkl` includes the lapack95 library shipped with ifx
# 2. `-assume byterecl` is needed in the tiff (and perhaps flt) opening routines so 
#    the data are loaded as bytes, not longwords (4 byte units). This makes the outputs
#    of e.g. MakeGrids unreadable (and 4x as large) because they have 128 bit data 
#    rather than 32.
# 3. `-static-intel` links intel libraries statically so you don't need
# 	 e.g. libmkl_intel_lp64.so.2 installed locally
FFLAGS = -O2 -fpp -nowarn -check bounds -traceback -I modules -I modules/OrderPack \
				 -I $(MOD_OUT) -module $(MOD_OUT) -qmkl -assume byterecl -static-intel

# These are all modules needed to compile MakeGrids and bldgrds. We could include
# _everything_, but there are several modules which I couldn't get to compile and
# appeared to be dependent on older code versions.
MODULES = modules/data_modules.f90 modules/error_handler.f90 modules/Utilities.f90 \
					modules/TIFF_module.f90 modules/TIFF_LZW_Module.f90 \
					modules/DataTableModule.f90 modules/Grid_Module.f90 \
					modules/ValleyFloor_Module.f90 modules/filters.f90 \
					modules/DEM_module.f90 modules/ChannelNode_Module.f90 \
					modules/ChannelNetworks.f90 modules/edgeHeap.f90 \
					modules/Piece_Module.f90 modules/random.f90 \
					modules/maxheap.f90 \
					modules/OrderPack/refsor.f90 modules/OrderPack/mrgrnk.f90 \
					GridUtilities/MakeGrids.f90 GridUtilities/bldGrds2.f90

MODULE_OBJS = $(MODULES:.f90=.o)

DEPS_FILE = deps.mk

all: bldgrds MakeGrids

bldgrds: $(DEPS_FILE) $(MODULE_OBJS) | $(MOD_OUT)
	$(FC) $(FFLAGS) GridUtilities/bldGrds2.o modules/*.o modules/OrderPack/*.o $(MKLROOT)/lib/libmkl_lapack95_ilp64.a  -o bldgrds

MakeGrids: $(DEPS_FILE) $(MODULE_OBJS) | $(MOD_OUT)
	$(FC) $(FFLAGS) GridUtilities/MakeGrids.o modules/*.o modules/OrderPack/*.o $(MKLROOT)/lib/libmkl_lapack95_ilp64.a  -o MakeGrids

include $(DEPS_FILE)

# -c is to indicate we're building a module.
%.o: %.f90 | $(MOD_OUT)
	$(FC) -c $(FFLAGS) $< -o $@

$(MOD_OUT):
	mkdir -p $(MOD_OUT)

# makedepf90 only calculates dependencies using things in SRC. So even though
# we only need e.g. MakeGrids.o and its dependencies, it won't find them
# unless we include all of them. Ideally we could just include modules/*.f90
# but there were some modules that didn't build, and I think they may be deprecated.
# A future solution may be to just include modules in the active branch that are
# actually up to date.
$(DEPS_FILE): $(MODULES)
	makedepf90 -I GridUtilites -I modules -I modules/OrderPack $(MODULES) > $(DEPS_FILE)

clean:
	rm -f modules/*.o GridUtilities/*.o modules/OrderPack/*.o built_mods/*
	rm -f deps.mk
