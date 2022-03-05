# Do not use make's built-in rules and variables.
# Disable printing of the working directory.
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --no-builtin-variables
MAKEFLAGS += --no-print-directory

# That's our default target when none is given on the command line.
.PHONY: all
all:

# Keep the openbar silent if requested.
ifeq (${VERBOSE}, 0)
  MAKEFLAGS += --silent
  QUIET := >/dev/null
endif

# Useful variables for make's $(subst) function.
EMPTY       :=
COMMA       := ,
SPACE       := ${EMPTY} ${EMPTY}
VERTICALTAB := ${EMPTY}${EMPTY}

define NEWLINE


endef

# The configuration file.
CONFIG := ${REPO_DIR}/.config

# Yocto requires the use of bash(1).
SHELL := /bin/bash

## foreach-eval <list> <function>
# For each unique element of the <list>, evaluate the specified <function> call.
foreach-eval = $(foreach element,$(sort ${1}),$(eval $(call ${2},${element})))

# To interpret and analyze the configuration file, it is read as a makefile
# and its database (the resulting variables and targets) is printed (option -p).
# The same approach is used by /usr/share/bash-completion/completions/make.
#
# The $(shell) function is used to make the call. But the $(shell) invoked does
# not inherit the internal environment. And therefore, is not able to see the
# internal variables (like REPO_DIR).
#
# So each variables which needs to be exported have to be added in the command
# line. The CONFIG_EXPORT_VARIABLES variable lists all the variables that will
# be exported to the configuration file. This variable can be appended by the
# user.
CONFIG_MAKE := ${MAKE}

override CONFIG_EXPORT_VARIABLES += REPO_DIR BUILD_DIR VERBOSE
override CONFIG_EXPORT_VARIABLES += DEFCONFIG_DIR DOCKER_DIR OE_INIT_BUILD_ENV
override CONFIG_EXPORT_VARIABLES += DL_DIR SSTATE_DIR DISTRO MACHINE

define config-export-variable
  ifdef ${1}
    CONFIG_MAKE += ${1}=${${1}}
  endif
endef

$(call foreach-eval,${CONFIG_EXPORT_VARIABLES},config-export-variable)

## config-parse <script>
# Parse the configuration file using a specified <script>.
#
# The output uses the makefile format so it can be evaluated directly.
#
# By default the $(shell) function replaces newline characters with spaces.
# So the script is using vertical tabs as separators, that are replaced by
# newlines later.
config-parse = $(subst ${VERTICALTAB},${NEWLINE},\
	$(shell ${CONFIG_MAKE} -npqf ${CONFIG} 2>&1 | awk -f ${1}))

## config-load-variables
# Load the variables from the configuration (and not the targets).
#
# The ALL_TARGETS list the available targets from the configuration. The
# internal "shell" target is added manually.
#
# The MANUAL_TARGETS is a user configurable variable. The AUTO_TARGETS is
# automatically deducted from the previous *_TARGETS variables.
#
# The AUTO_TARGETS are added as dependencies of the "all" target.
define config-load-variables-noeval
  $(call config-parse,${OPENBAR_DIR}/scripts/config-variables.awk)

  ALL_TARGETS += shell
  MANUAL_TARGETS += shell

  AUTO_TARGETS := $$(filter-out $${MANUAL_TARGETS},$${ALL_TARGETS})

  .PHONY: $${ALL_TARGETS}

  all: $${AUTO_TARGETS}
endef

config-load-variables = $(eval $(call config-load-variables-noeval))

## config-load-targets
# Load the targets from the configuration (and not the variables).
define config-load-targets-noeval
  $(call config-parse,${OPENBAR_DIR}/scripts/config-targets.awk)
endef

config-load-targets = $(eval $(call config-load-targets-noeval))