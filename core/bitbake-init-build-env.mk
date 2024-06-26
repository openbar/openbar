# The oe-init-build-env layer.
#
# The oe-init-build-env layer is responsible for:
# - exporting the required variables to bitbake.
# - cleaning the bitbake layer configuration.
# - initializing the bitbake environment.

# The openbar directory. This must be done before any includes.
OPENBAR_DIR := $(realpath $(dir $(lastword ${MAKEFILE_LIST}))/..)

# Include the common makefiles.
include ${OPENBAR_DIR}/includes/verify-environment.mk
include ${OPENBAR_DIR}/includes/common.mk

# Load the configuration variables and targets.
ifeq ($(realpath ${CONFIG}),)
  $(error Configuration file not found)
else
  $(call config-load-variables)
endif

# The bitbake variable used to export environment variables to bitbake.
OB_BB_EXPORT_LIST_VARIABLE ?= BB_ENV_PASSTHROUGH_ADDITIONS

# Export the required variables to bitbake.
override OB_BB_EXPORT_VARIABLES += OB_ROOT_DIR OB_BUILD_DIR OB_VERBOSE
override OB_BB_EXPORT_VARIABLES += DEPLOY_DIR DL_DIR SSTATE_DIR DISTRO MACHINE

define export-variable
  ifdef ${1}
    export ${1}
    export ${OB_BB_EXPORT_LIST_VARIABLE} += ${1}
  endif
endef

$(call foreach-eval,${OB_BB_EXPORT_VARIABLES},export-variable)

# All targets are forwarded to the bitbake-layers layer.
${OB_ALL_TARGETS}: .forward

.PHONY: .forward
.forward: .clean-bblayers
	${QUIET} . ${OB_BB_INIT_BUILD_ENV} ${OB_BUILD_DIR} \
		&& ${MAKE} -f ${OPENBAR_DIR}/core/bitbake-layers.mk ${MAKECMDGOALS}

# The configuration of the bitbake layers must be removed. It will then be
# rebuilt each time by the following bitbake-layers layer.
.PHONY: .clean-bblayers
.clean-bblayers:
	rm -f ${OB_BUILD_DIR}/conf/bblayers.conf
