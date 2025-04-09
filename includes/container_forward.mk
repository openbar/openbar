# All targets are forwarded to the next layer inside the container.
${OB_ALL_TARGETS}: .forward

ifeq (${OB_TYPE},simple)
  NEXT_LAYER := type/simple.mk
else
  NEXT_LAYER := type/initenv.mk
endif

.PHONY: .forward
.forward: | ${CONTAINER_VOLUME_HOSTDIRS}
	${CONTAINER_RUN} $(call submake_noenv,${NEXT_LAYER})

.PHONY: .container-build
.container-build:
	@echo "Building ${OB_CONTAINER_ENGINE} image '${CONTAINER_TAG:localhost/%=%}'"
	${QUIET} ${CONTAINER_BUILD}

.PHONY: .container-pull
.container-pull:
	@echo "Pulling ${OB_CONTAINER_ENGINE} image '${CONTAINER_TAG}'"
	${QUIET} ${CONTAINER_PULL}

ifeq (${CONTAINER_COMMAND},pull)
  ifdef OB_CONTAINER_FORCE_PULL
    ifneq (${OB_CONTAINER_FORCE_PULL},0)
      .forward: .container-pull
    endif
  else ifeq ($(filter-out missing newer,${OB_CONTAINER_POLICY}),)
    ifeq ($(call container-status,missing newer),)
      .forward: .container-pull
    endif
  else ifneq (${OB_CONTAINER_POLICY},never)
    .forward: .container-pull
  endif
else
  ifdef OB_CONTAINER_FORCE_BUILD
    ifneq (${OB_CONTAINER_FORCE_BUILD},0)
      .forward: .container-build
    endif
  else ifeq (${OB_CONTAINER_POLICY},newer)
    ifeq ($(call container-status,missing newer,${OB_CONTAINER_FILE}),)
      .forward: .container-build
    endif
  else ifeq (${OB_CONTAINER_POLICY},missing)
    ifeq ($(call container-status,missing,${OB_CONTAINER_FILE}),)
      .forward: .container-build
    endif
  else ifneq (${OB_CONTAINER_POLICY},never)
    .forward: .container-build
  endif
endif
