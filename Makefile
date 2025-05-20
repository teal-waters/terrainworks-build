FC = ifx
MOD_OUT = built_mods
# Most of these flags are the recommended ones. A couple notes though for ifx:
# 1. -qmkl includes the lapack95 library shipped with ifx
# 2. -assume byterecl is needed in the tiff (and perhaps flt) opening routines or
#    the data are loaded as bytes, not longwords (4 byte units). This makes the outputs
#    of e.g. MakeGrids unreadable
FFLAGS = -O2 -c -fpp -nowarn -check bounds -traceback -I modules -I modules/OrderPack \
				 -I $(MOD_OUT) -module built_mods -qmkl -assume byterecl


# For now, everything that goes into MakeGrids. Unfortunately there are some modules
# that can't compile, I think because they are out of sync with the rest of the code,
# so we can't just add all modules.
MODULES = modules/data_modules.f90 modules/error_handler.f90 modules/Utilities.f90 \
					modules/TIFF_module.f90 modules/TIFF_LZW_Module.f90 \
					modules/DataTableModule.f90 modules/Grid_Module.f90 \
					modules/ValleyFloor_Module.f90 modules/filters.f90 \
					modules/DEM_module.f90 modules/ChannelNode_Module.f90 \
					modules/ChannelNetworks.f90 modules/edgeHeap.f90 \
					modules/Piece_Module.f90 modules/random.f90 \
					modules/maxheap.f90 \
					modules/OrderPack/refsor.f90 modules/OrderPack/mrgrnk.f90 \
					GridUtilities/MakeGrids.f90

SRC = $(MODULES)

MODULE_OBJS = $(SRC:.f90=.o)

DEPS_FILE = deps.mk

# lapack should not be hardcoded here
MakeGrids: $(DEPS_FILE) $(MODULE_OBJS)
	ifx -O2  -fpp -nowarn -check bounds -traceback -I /opt/intel/oneapi/2025.1/lib  -I modules -I modules/OrderPack -I built_mods -module built_mods -qmkl modules/OrderPack/*.o  modules/*.o /opt/intel/oneapi/2025.1/lib/libmkl_lapack95_ilp64.a GridUtilities/MakeGrids.o -o MakeGrids

include $(DEPS_FILE)

%.o: %.f90
	$(FC) $(FFLAGS) $< -o $@

$(DEPS_FILE): $(SRC)
	makedepf90 -I GridUtilites -I modules -I modules/OrderPack $(SRC) > $(DEPS_FILE)

clean:
	rm -f modules/*.o GridUtilities/*.o modules/OrderPack/*.o built_mods/*
	rm -f deps.mk
