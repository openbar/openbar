hello:
	say_hello

OB_MANUAL_TARGETS += clean
clean:
	${RM} -r ${OB_BUILD_DIR}
