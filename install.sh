#!/bin/bash

if [[ $USER != root ]]; then
	echo "Must be root to install this script."
	exit 1
fi

PLATFORM="$( python3 -c 'import platform; print(platform.system())' )"


chmod +x hijack.py

if [[ "$PLATFORM" == "Linux" ]]; then
	cp -f hijack.py /usr/bin/hj
else
	cp -f hijack.py /usr/local/bin/hj
fi


