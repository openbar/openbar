## container-volume <string>
# Format the volume string to be container compliant.
container-volume = $(shell echo ${1} | awk -f ${OPENBAR_DIR}/scripts/container-volume.awk)

## container-volume-hostdir <string>
# Get the host directory from a container volume string.
container-volume-hostdir = $(firstword $(subst ${COLON},${SPACE},${1}))

## container-status [<file>]
#
container-status = $(filter-out invalid ${1},$(shell OB_VERBOSE=${OB_VERBOSE} ${OPENBAR_DIR}/scripts/container-status.sh ${OB_CONTAINER_ENGINE} ${CONTAINER_TAG} ${2}))

# Choose whether to build or pull the container.
ifeq (${OB_CONTAINER_DIR},)
  CONTAINER_COMMAND := pull
else ifeq (${OB_CONTAINER_IMAGE},)
  CONTAINER_COMMAND := build
else
  CONTAINER_COMMAND := pull
endif

# The default container configuration.
OB_CONTAINER_POLICY     ?= newer
ifeq (${CONTAINER_COMMAND},pull)
  OB_CONTAINER_IMAGE    ?= ghcr.io/openbar/openbar:latest
else
  OB_CONTAINER          ?= default
  OB_CONTAINER_FILENAME ?= Dockerfile
  OB_CONTAINER_CONTEXT  ?= ${OB_CONTAINER_DIR}/${OB_CONTAINER}
  OB_CONTAINER_FILE     ?= ${OB_CONTAINER_CONTEXT}/${OB_CONTAINER_FILENAME}
endif

# The generated container variables.
ifeq (${CONTAINER_COMMAND},pull)
  CONTAINER_TAG         := ${OB_CONTAINER_IMAGE}
  CONTAINER_IMAGE       := $(firstword $(subst :,${SPACE},${CONTAINER_TAG}))
  CONTAINER_HOSTNAME    := $(subst /,-,${CONTAINER_IMAGE})
else
  CONTAINER_SHA1        := $(firstword $(shell sha1sum ${OB_CONTAINER_FILE}))
  CONTAINER_ID          := $(lastword $(subst /,${SPACE},${OB_CONTAINER_FILE:%/Dockerfile=%}))
  CONTAINER_TAG         := localhost/openbar/${OB_PROJECT_ID}/${CONTAINER_ID}:latest
  CONTAINER_HOSTNAME    := $(subst /,-,${OB_CONTAINER})
endif

# Add all exported variables inside the container.
CONTAINER_ENV_ARGS :=

define container-env-args
  ifdef ${1}
    CONTAINER_ENV_ARGS += -e ${1}="$(call unquote,${${1}})"
  endif
endef

$(call foreach-eval,OB_EXPORT ${OB_EXPORT},container-env-args)

# Mount the required volumes if not already done.
override OB_CONTAINER_VOLUMES += ${OPENBAR_DIR} ${OB_BUILD_DIR}

# Add OE/Yocto related volumes to the mount list.
ifeq (${OB_TYPE},yocto)
  override OB_CONTAINER_VOLUMES += ${DEPLOY_DIR} ${DL_DIR} ${SSTATE_DIR}
endif

CONTAINER_VOLUME_ARGS :=
CONTAINER_VOLUME_HOSTDIRS :=

define container-volume-args
  CONTAINER_VOLUME_ARGS += -v $(call container-volume,${1})
  CONTAINER_VOLUME_HOSTDIRS += $(call container-volume-hostdir,${1})
endef

$(call foreach-eval,${OB_CONTAINER_VOLUMES},container-volume-args)

# The container volumes directories are created manually so that
# the owner is not root.
${CONTAINER_VOLUME_HOSTDIRS}:
	mkdir -p $@

# Container build default arguments.
CONTAINER_BUILD_ARGS := -t ${CONTAINER_TAG}
CONTAINER_BUILD_ARGS += -f ${OB_CONTAINER_FILE}

ifeq (${OB_VERBOSE},0)
  CONTAINER_BUILD_ARGS += --quiet
endif

CONTAINER_BUILD_ARGS += --label io.github.openbar.project_id=${OB_PROJECT_ID}
CONTAINER_BUILD_ARGS += --label io.github.openbar.container_id=${CONTAINER_ID}
CONTAINER_BUILD_ARGS += --label io.github.openbar.sha1=${CONTAINER_SHA1}

CONTAINER_BUILD_ARGS += ${OB_CONTAINER_BUILD_EXTRA_ARGS}

# Container pull default arguments.
CONTAINER_PULL_ARGS :=

ifeq (${OB_VERBOSE},0)
  CONTAINER_PULL_ARGS += --quiet
endif

# Container run default arguments.
CONTAINER_RUN_ARGS := --rm			# Never save the running container.
CONTAINER_RUN_ARGS += --log-driver=none		# Disables any logging for the container.
CONTAINER_RUN_ARGS += --privileged		# Allow access to devices.

# Never pull when running.
CONTAINER_RUN_ARGS += --pull never

# Allow to run interactive commands.
ifeq ($(shell tty >/dev/null && echo interactive),interactive)
  CONTAINER_RUN_ARGS += --interactive --tty -e TERM=${TERM}
endif

# Set the hostname to be identifiable.
CONTAINER_RUN_ARGS += --hostname ${CONTAINER_HOSTNAME}
CONTAINER_RUN_ARGS += --add-host ${CONTAINER_HOSTNAME}:127.0.0.1

# Bind the local ssh configuration and authentication.
ifneq ($(wildcard ${HOME}/.ssh),)
  CONTAINER_RUN_ARGS += -v ${HOME}/.ssh:${OB_CONTAINER_HOME}/.ssh:ro
endif

ifdef SSH_AUTH_SOCK
  ifneq ($(wildcard ${SSH_AUTH_SOCK}),)
    CONTAINER_RUN_ARGS += -v ${SSH_AUTH_SOCK}:${OB_CONTAINER_HOME}/ssh.socket:ro
    CONTAINER_RUN_ARGS += -e SSH_AUTH_SOCK=${OB_CONTAINER_HOME}/ssh.socket
  endif
endif

# Also bind the local netrc file.
ifneq ($(wildcard ${HOME}/.netrc),)
  CONTAINER_RUN_ARGS += -v ${HOME}/.netrc:${OB_CONTAINER_HOME}/.netrc:ro
endif

# Mount the root directory as working directory.
CONTAINER_RUN_ARGS += -w ${OB_ROOT_DIR}
CONTAINER_RUN_ARGS += -v ${OB_ROOT_DIR}:${OB_ROOT_DIR}

# Mount the required volumes.
CONTAINER_RUN_ARGS += ${CONTAINER_VOLUME_ARGS}

# Export the required environment variables.
CONTAINER_RUN_ARGS += ${CONTAINER_ENV_ARGS}

# Add optional extra arguments.
CONTAINER_RUN_ARGS += ${OB_CONTAINER_RUN_EXTRA_ARGS}
