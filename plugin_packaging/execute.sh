#!/bin/sh
COMMAND="python3.5 ${1}/main.py --db-database ${4} --db-hostname ${5} --db-port ${6} --project-name ${8} --mailingurl ${9} --backend ${10} --output ${15}"

if [ ! -z ${2+x} ] && [ ${2} != "None" ]; then
COMMAND="$COMMAND --db-user ${2}"
fi

if [ ! -z ${3+x} ] && [ ${3} != "None" ]; then
COMMAND="$COMMAND --db-password ${3}"
fi

if [ ! -z ${7+x} ] && [ ${7} != "None" ]; then
COMMAND="$COMMAND --db-authentication ${7}"
fi

if [ ! -z ${11+x} ] && [ ${11} != "None" ]; then
COMMAND="$COMMAND --proxy-host ${11}"
fi

if [ ! -z ${12+x} ] && [ ${12} != "None" ]; then
COMMAND="$COMMAND --proxy-port ${12}"
fi

if [ ! -z ${13+x} ] && [ ${13} != "None" ]; then
COMMAND="$COMMAND --proxy-user ${13}"
fi

if [ ! -z ${14+x} ] && [ ${14} != "None" ]; then
COMMAND="$COMMAND --proxy-password ${14}"
fi

if [ ! -z ${16+x} ] && [ ${16} != "None" ]; then
COMMAND="$COMMAND --debug ${16}"
fi

$COMMAND