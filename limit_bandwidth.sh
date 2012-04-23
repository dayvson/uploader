#!/bin/bash

usage() {
        echo "Usage: sudo ./limit-bandwidth.sh <action> [width]
                action                 {add|remove}
                width (when adding)    Ex: 25KByte/s" >&2
	echo ""
        exit 1
}

echo ""
case "$1" in
  add)
	if [ -z $2 ]
	then
	  usuage
	fi
	BANDWIDTH=$2
        echo "Adding bandwidth limitor ${BANDWIDTH} to ports 80 and 1935 and 8888"
	sudo ipfw pipe 1 config bw $BANDWIDTH        
        sudo ipfw add 1 pipe 1 src-port 80
        sudo ipfw add 2 pipe 1 src-port 1935
        sudo ipfw add 3 pipe 1 src-port 8888
        ;;
  remove)
	echo "Removing bandwidth limitor ${BANDWIDTH} to ports 80 and 1935 and 8888"
	sudo ipfw delete 1
	sudo ipfw delete 2        	
	sudo ipfw delete 3        	
	;;
  *)
        usage
	;;
esac

exit 0