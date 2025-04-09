#!/bin/sh
# shellcheck shell=sh enable=all

if [ "${OB_VERBOSE:-0}" = 1 ]; then
	set -x
fi

if [ $# -ge 3 ] && [ "${2%%/*}" = localhost ] && [ -f "$3" ]; then
	SHA1=$(sha1sum "$3" | awk '{print $1}')
	ID=$("$1" image ls -q -f "reference=$2" -f "label=io.github.openbar.sha1=${SHA1}")
	if [ -n "${ID}" ]; then
		echo ok
	elif "$1" inspect "$2" >/dev/null 2>&1; then
		echo newer
	else
		echo missing
	fi
elif [ $# -eq 2 ] && [ "${2%%/*}" != localhost ]; then
	if "$1" inspect "$2" >/dev/null 2>&1; then
		echo ok
	else
		echo missing
	fi
else
	echo invalid
fi
