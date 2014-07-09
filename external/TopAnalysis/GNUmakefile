#===============================================================================
# File and Version Information:
#      $Id$
#
# Description:
#      Makefile for the TopSVDUnfold package
#
# Instructions:
#      o Make sure the ROOTSYS environment variable is set and points
#        to your ROOT release, and that $ROOTSYS/bin is in your PATH.
#
#      o run 'make <target>'
#        - Default target makes shared library (libTopSVDUnfold.so) for use
#          in ROOT.
#        - Add NOROOFIT=1 to build test programs (TopSVDUnfoldTest*)
#          without RooFit (this is default if RooFit is not available).
#        - Add SHARED=1 to link test executables with shared library
#          (libTopSVDUnfold.so). Otherwise links with static library
#          (libTopSVDUnfold.a).
#        - Add ROOTBUILD=debug for debug version.
#        - Add VERBOSE=1 to show main commands as they are executed
#
# Build targets:
#      help    - give brief help
#      shlib   - make libTopSVDUnfold.so (default target)
#      include - make dependency files (*.d)
#      lib     - make libTopSVDUnfold.a
#      bin     - make lib and example programs
#      commands- show commands to make each type of target
#      html    - make documentation in htmldoc subdirectory
#      cleanbin- delete test binaries and objects
#      clean   - delete all intermediate and final build objects
#
# Author: Tim Adye <T.J.Adye@rl.ac.uk>
#
#===============================================================================

# === ROOT setup ===============================================================

ROOTSYS      ?= ERROR_RootSysIsNotDefined

-include $(ROOTSYS)/test/Makefile.arch
ifeq ($(ROOTCONFIG),)
ROOTCONFIG    = $(ROOTSYS)/bin/root-config
endif

ifeq ($(ARCH),)
# === This section is just in case ROOT's test/Makefile.arch didn't work =======
out := $(shell echo "$(ROOTSYS)/test/Makefile.arch not found - trying a basic Linux config" >&2)
ARCH          = $(shell $(ROOTCONFIG) --arch)
ROOTLIBS      = $(shell $(ROOTCONFIG) --libs)
CXXFLAGS      = $(shell $(ROOTCONFIG) --cflags)
CXX           = g++
CXXFLAGS     += -Wall -fPIC
LD            = g++
LDFLAGS       =
SOFLAGS       = -shared
ObjSuf        = o
ExeSuf        =
DllSuf        = so
OutPutOpt     = -o # keep whitespace after "-o"
ifneq ($(findstring debug,$(ROOTBUILD)),)
CXXFLAGS     += -g
LDFLAGS      += -g
endif
endif

ifeq ($(PLATFORM),macosx)
# Fix stupid shared library option on MacOSX. This doesn't work (and we don't
# need it) because our linker output file specifies the full path.
SOFLAGS      := $(subst -install_name $(CURDIR)/,,$(SOFLAGS))
endif

ROOTINCDIR    = $(shell $(ROOTCONFIG) --incdir)
ROOTLIBDIR    = $(shell $(ROOTCONFIG) --libdir)
ROOTINCLUDES  = -I$(ROOTINCDIR)

ROOTVERSION = $(shell $(ROOTCONFIG) --version)
ROOTMAJORVERSION = $(firstword $(subst ., ,$(ROOTVERSION)))

ifeq ($(ROOTCINT),)
ifeq ($(ROOTMAJORVERSION),6)
ROOTCINT      = rootcling
else
ROOTCINT      = rootcint
endif
endif
ifeq ($(RLIBMAP),)
RLIBMAP       = rlibmap
endif
ifeq ($(VERBOSE),1)
_             =
else
_             = @
endif

# === TopSVDUnfold directories ========================================

PACKAGE       = TopSVDUnfold
SRCDIR        = $(CURDIR)/
INCDIR        = $(SRCDIR)
WORKDIR       = $(CURDIR)/tmp/$(ARCH)/
LIBDIR        = $(CURDIR)/
SHLIBDIR      = $(CURDIR)/
HTMLDOC       = htmldoc
OBJDIR        = $(WORKDIR)obj/
DEPDIR        = $(WORKDIR)dep/

# === TopSVDUnfold options ===================================================

# Only provide TopSVDUnfoldTUnfold if TUnfold is available.
# TUnfold is included in ROOT 5.22 and later.
#ifeq ($(HAVE_TUNFOLD),)
#ifneq ($(wildcard $(ROOTINCDIR)/TUnfold.h),)
#HAVE_TUNFOLD  = 1
#endif
#endif
#
#ifneq ($(HAVE_TUNFOLD),1)
#CPPFLAGS     += -DNOTUNFOLD
#EXCLUDE      += TopSVDUnfoldTUnfold.C TopSVDUnfoldTUnfold.h
#endif

# TopSVDUnfoldDagostini is an interface to D'Agostini's implementation
# of his algorithm: http://www.roma1.infn.it/~dagos/bayes_distr.txt .
# To use this, put it in src/bayes.for and src/bayes_c.for.
#ifeq ($(HAVE_DAGOSTINI),)
#ifneq ($(wildcard $(SRCDIR)/bayes.for),)
#HAVE_DAGOSTINI = 1
#endif
#endif
#
#ifeq ($(HAVE_DAGOSTINI),1)
#EXTRASRC     += bayes.for
#FDEP          = $(SRCDIR)bayes_c.for
#CPPFLAGS     += -DHAVE_DAGOSTINI
#else
#EXCLUDE      += TopSVDUnfoldDagostini.cxx TopSVDUnfoldDagostini.h
#endif

# TSVDUnfold is included in ROOT 5.28 and later. In earlier versions, use our own copy.
ifeq ($(HAVE_TSVDUNFOLD),)
ifeq ($(wildcard $(ROOTINCDIR)/TSVDUnfold.h),)
HAVE_TSVDUNFOLD = 1
endif
endif

#ifeq ($(HAVE_TSVDUNFOLD),1)
#CPPFLAGS     += -DHAVE_TSVDUNFOLD
#else
#EXCLUDE      += TSVDUnfold.cxx TSVDUnfold_local.h
#endif

# RooFit is included in ROOT if ROOT was compiled with --enable-roofit.
# We only use it for better-normalised test distributions in TopSVDUnfoldTest
# (uses examples/TopSVDUnfoldTestPdfRooFit.icc instead of examples/TopSVDUnfoldTestPdf.icc).
ifeq ($(NOROOFIT),)
ifneq ($(shell $(ROOTCONFIG) --has-roofit),yes)
out := $(shell echo "This version of ROOT does not support RooFit. We will build the test programs without it." >&2)
NOROOFIT      = 1
endif
endif

ifneq ($(NOROOFIT),)
CPPFLAGS     += -DNOROOFIT
else
ROOFITLIBS   += -lRooFit
# Different versions of ROOT require different libraries with RooFit, so
# include all the ones that exist.
# Note that if the ROOT shared libraries were linked against them
# (configure --enable-explicitlink ?), as is done in the CERN AFS versions,
# then these are not required. But they do no harm.
ROOFITLIBS   += $(patsubst $(ROOTLIBDIR)/lib%.$(DllSuf),-l%,$(wildcard $(patsubst %,$(ROOTLIBDIR)/lib%.$(DllSuf),RooFitCore Thread Minuit Foam MathMore Html)))
endif

# === Internal configuration ===================================================

#MAIN          = $(filter-out $(EXCLUDE),$(notdir $(wildcard $(EXESRC)*.cxx)))
#MAINEXE       = $(addprefix $(EXEDIR),$(patsubst %.cxx,%$(ExeSuf),$(MAIN)))
LINKDEF       = $(INCDIR)$(PACKAGE)_LinkDef.h
HLIST         = $(filter-out $(addprefix $(INCDIR),$(EXCLUDE)) $(LINKDEF),$(wildcard $(INCDIR)*.h)) $(LINKDEF)
CINTFILE      = $(WORKDIR)$(PACKAGE)Dict.cxx
CINTOBJ       = $(OBJDIR)$(PACKAGE)Dict.o
LIBNAME       = $(PACKAGE)
STATICLIBNAME = $(PACKAGE)_static
LIBFILE       = $(LIBDIR)lib$(LIBNAME).a
STATICLIBFILE = $(LIBDIR)lib$(STATICLIBNAME).a
SHLIBFILE     = $(SHLIBDIR)lib$(LIBNAME).$(DllSuf)
ROOTMAP       = $(SHLIBDIR)lib$(LIBNAME).rootmap

CPPFLAGS     += -DMAKEBUILD
ifneq ($(findstring g++,$(CXX)),)
MFLAGS        = -MM
endif
INCLUDES      = -I$(INCDIR) -I$(HOME) -iquote$(INCDIR) -iquote$(HOME)
CXX          += $(EXTRAINCLUDES)
LDFLAGS      += $(EXTRALDFLAGS)

ifneq ($(SHARED),)
LIBS          = -L$(SHLIBDIR)
LINKLIB       = $(SHLIBFILE)
LINKLIBOPT    = -l$(LIBNAME) $(EXTRALIBS)
else
LIBS          = -L$(LIBDIR)
LINKLIB       = $(STATICLIBFILE)
LINKLIBOPT    = -l$(STATICLIBNAME) $(EXTRALIBS)
endif

# List of all object files to build
SRCLIST       = $(filter-out $(EXCLUDE),$(notdir $(wildcard $(SRCDIR)*.cxx))) $(EXTRASRC)
OLIST         = $(addprefix $(OBJDIR),$(addsuffix .o,$(basename $(SRCLIST))))

ifneq ($(filter %.for,$(SRCLIST)),)
GCCLIBS       = -lg2c
endif

ROOTLIBFILES := $(wildcard $(patsubst -l%,$(ROOTLIBDIR)/lib%.$(DllSuf),$(filter -l%,$(ROOTLIBS))))

ifeq ($(MFLAGS),)

# Can't make dependency files, so make every compilation dependent on all headers.
HDEP          = $(HLIST)

else

# List of all dependency files to make
DLIST         = $(addprefix $(DEPDIR),$(patsubst %.cxx,%.d,$(filter %.cxx,$(SRCLIST) $(filter-out $(EXCLUDE),$(notdir $(wildcard $(EXESRC)*.cxx))))))

# If possible, limit ROOTLIBFILES to libraries that we actually use.
DLISTLIB      = $(wildcard $(addprefix $(DEPDIR),$(patsubst %.cxx,%.d,$(filter %.cxx,$(SRCLIST)))))
ifneq ($(DLISTLIB),)
ROOTLIBMAPS  := $(wildcard $(patsubst %.$(DllSuf),%.rootmap,$(ROOTLIBFILES)))
ifneq ($(ROOTLIBMAPS),)
ROOTLIBFILESUSED := $(patsubst %.rootmap,%.$(DllSuf),$(shell sed -n 's,^ *$(ROOTINCDIR)[^ ]*/\([^ /]*\)\.h .*,^Library\.\1:,p' $(DLISTLIB) | sort -u | grep -l -f- $(ROOTLIBMAPS)))
ifneq ($(ROOTLIBFILESUSED),)
ROOTLIBFILES := $(ROOTLIBFILESUSED)
endif
endif
endif

endif

ifeq ($(NOROOFIT),)
ifeq ($(DLIST),)
# Since we can't check the dependencies, include RooFit on all binaries
ROOFITCLIENTS = $(patsubst %.cxx,$(OBJDIR)%.o,$(MAIN))
else
# List of programs that use RooFit. Should only be those in $(EXESRC)
ROOFITCLIENTS = $(patsubst $(DEPDIR)%.d,$(OBJDIR)%.o,$(shell fgrep -l '/RooAbsArg.h ' $(DLIST) 2>/dev/null))
endif
endif

# === Implicit rules ===========================================================

# Implicit rule making all dependency Makefiles included at the end of this makefile
$(DEPDIR)%.d : $(SRCDIR)%.cxx
	@echo "Making $@"
	@mkdir -p $(DEPDIR)
	@rm -f $@
	$(_)set -e; \
	 $(CXX) $(MFLAGS) $(CPPFLAGS) $(INCLUDES) $(ROOTINCLUDES) $< \
	 | sed 's,\($(notdir $*)\.o\) *:,$(OBJDIR)\1 $@ :,g' > $@; \
	 [ -s $@ ] || rm -f $@

$(DEPDIR)%.d : $(EXESRC)%.cxx
	@echo "Making $@"
	@mkdir -p $(DEPDIR)
	@rm -f $@
	$(_)set -e; \
	 $(CXX) $(MFLAGS) $(CPPFLAGS) $(INCLUDES) $(ROOTINCLUDES) $< \
	 | sed 's,\($(notdir $*)\.o\) *:,$(OBJDIR)\1 $@ :,g' > $@; \
	 [ -s $@ ] || rm -f $@

# Implicit rule to compile all classes
$(OBJDIR)%.o : $(SRCDIR)%.cxx $(HDEP)
	@echo "Compiling $<"
	@mkdir -p $(OBJDIR)
	$(_)$(CXX) $(CXXFLAGS) $(CPPFLAGS) -c $< -o $@ $(INCLUDES)

# Implicit rule to compile intermediate files
$(OBJDIR)%.o : $(WORKDIR)%.cxx $(HDEP)
	@echo "Compiling $<"
	@mkdir -p $(OBJDIR)
	$(_)$(CXX) $(CXXFLAGS) $(CPPFLAGS) -c $< -o $@ $(INCLUDES)

# Implicit rule for Fortran (if any)
$(OBJDIR)%.o : $(SRCDIR)%.for $(FDEP)
	@echo "Compiling $<"
	@mkdir -p $(OBJDIR)
	$(_)$(FC) $(FFFLAGS) $(CXXFLAGS) $(CPPFLAGS) -c $< -o $@

# Implicit rule to compile main program
$(OBJDIR)%.o : $(EXESRC)%.cxx $(HDEP)
	@echo "Compiling main program $<"
	@mkdir -p $(OBJDIR)
	$(_)$(CXX) $(CXXFLAGS) $(CPPFLAGS) -c $< -o $@ $(INCLUDES)

# === Explicit rules ===========================================================

default : shlib

help        :
	@echo "Usage: $(MAKE) [TARGET] [ROOTBUILD=debug] [VERBOSE=1] [NOROOFIT=1] [SHARED=1]"
	@echo "Some TARGETs are: 'bin', 'html', 'clean', and 'commands'"

# Rule to make ROOTCINT output file
$(CINTFILE) : $(HLIST)
	@mkdir -p $(WORKDIR)
	@mkdir -p $(OBJDIR)
	@echo "Generating dictionary from $(LINKDEF)"
	$(_)cd $(SRC) ; $(ROOTCINT) -f $(CINTFILE) -c -p $(CPPFLAGS) $(INCLUDES) $(HLIST)

$(ROOTMAP) : $(SHLIBFILE) $(LINKDEF)
	@echo "Making $@"
	$(_)$(RLIBMAP) -o $@ -l $< -d $(ROOTLIBFILES) -c $(LINKDEF)

# Rule to combine objects into a library
$(LIBFILE) : $(OLIST) $(CINTOBJ)
	@echo "Making $@"
	@mkdir -p $(LIBDIR)
	@rm -f $@
	$(_)ar q $@ $^
	@ranlib $@

# Make symlink to static library so we can refer to that without picking up shared library.
# Assumes $(LIBFILE) and $(STATICLIBFILE) are in the same directory
$(STATICLIBFILE) : $(LIBFILE)
	@rm -f $@
	$(_)ln -s $(patsubst $(dir $@)%,%,$<) $@

# Rule to combine objects into a shared library
$(SHLIBFILE) : $(OLIST) $(CINTOBJ)
	@echo "Making $@"
	@mkdir -p $(SHLIBDIR)
	@rm -f $@
	$(_)$(LD) $(SOFLAGS) $(LDFLAGS) $^ $(OutPutOpt)$@ $(ROOTLIBS) $(GCCLIBS)

$(MAINEXE) : $(EXEDIR)%$(ExeSuf) : $(OBJDIR)%.o $(LINKLIB)
	@echo "Making executable $@"
	@mkdir -p $(EXEDIR)
	$(_)$(LD) $(LDFLAGS) $< $(OutPutOpt)$@ $(LIBS) $(LINKLIBOPT) $(ROOTLIBS) $(if $(findstring $<,$(ROOFITCLIENTS)),$(ROOFITLIBS)) $(GCCLIBS)

# Useful build targets
include: $(DLIST)
lib: $(LIBFILE)
shlib: $(SHLIBFILE)# $(ROOTMAP)
bin: shlib $(MAINEXE)

commands :
	@echo "Make $(DEPDIR)%.d:	$(CXX) $(MFLAGS) $(CPPFLAGS) $(INCLUDES) $(ROOTINCLUDES) $(SRCDIR)%.cxx | sed 's,\(%\.o\) *:,$(OBJDIR)\1 $(DEPDIR)%.d :,g' > $(DEPDIR)%.d"
	@echo
	@echo "Make dictionary: $(ROOTCINT) -f $(CINTFILE) -c -p $(INCLUDES) $(HLIST)"
	@echo
	@echo "Compile $(SRCDIR)%.cxx:	$(CXX) $(CXXFLAGS) $(CPPFLAGS) -c $(SRCDIR)%.cxx -o $(OBJDIR)%.o $(INCLUDES)"
	@echo
	@echo "Make $(SHLIBFILE):	$(LD) $(SOFLAGS) $(LDFLAGS) *.o $(OutPutOpt)$(SHLIBFILE) $(ROOTLIBS) $(GCCLIBS)"
	@echo
	@echo "Make executable $(EXEDIR)TopSVDUnfoldTest$(ExeSuf):	$(LD) $(LDFLAGS) $(OBJDIR)TopSVDUnfoldTest.o $(OutPutOpt)$(EXEDIR)TopSVDUnfoldTest$(ExeSuf) $(LIBS) $(LINKLIBOPT) $(ROOTLIBS) $(ROOFITLIBS) $(GCCLIBS)"

clean : cleanbin
	rm -f $(DLIST)
	rm -f $(CINTFILE) $(basename $(CINTFILE)).h
	rm -f $(OLIST) $(CINTOBJ)
	rm -f $(LIBFILE)
	rm -f $(SHLIBFILE) $(ROOTMAP)
	rm -f $(STATICLIBFILE)

cleanbin :
	rm -f $(addprefix $(OBJDIR),$(patsubst %.cxx,%.o,$(MAIN)))
	rm -f $(MAINEXE)

$(HTMLDOC)/index.html : $(SHLIBFILE)
	@echo "Making HTML documentation in $(HTMLDOC)"
	@( echo 'gSystem->Load("lib$(LIBNAME)");'; \
	   echo 'THtml h;';                        \
	   echo 'h.SetProductName("$(PACKAGE)");'; \
	   echo 'h.SetInputDir("$(SRCDIR)");';     \
	   echo 'h.SetOutputDir("$(HTMLDOC)");';   \
	   echo 'h.MakeAll();';                    \
	   echo '.q' )                             \
	 | root -l -b

html : $(HTMLDOC)/index.html

.PHONY : include shlib lib bin default clean cleanbin html

ifneq ($(DLIST),)
-include $(DLIST)
endif
