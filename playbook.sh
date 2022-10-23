#!/usr/bin/env bash

set -e

umask 0022

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd ${SCRIPT_DIR}/..
if [[ "$(basename ${BASH_SOURCE[0]})" == "playbook.sh" ]];then
  echo "DO NOT run playbook.sh directly!"
  exit 1
fi

ANSIBLE_BIN_PATH=/usr/local/miniconda3/bin
if [[ -d ${ANSIBLE_BIN_PATH} ]];then
    PATH=${ANSIBLE_BIN_PATH}:${PATH}
    export PATH
fi
# detect python executable
# shellcheck disable=SC2015
[[ -f /usr/libexec/platform-python ]] && export PYTHON_EXEC=/usr/libexec/platform-python || true

# detect local YARN
# shellcheck disable=SC2015
[[ -d /opt/rdx/hadoop/etc/hadoop ]] && export LOCAL_YARN=/opt/rdx/hadoop/etc/hadoop || true

FILE_NAME=$(basename "${BASH_SOURCE[0]}")
PLAYBOOK_NAME=${FILE_NAME%.*}
PLAYBOOK_FILE=playbooks/${PLAYBOOK_NAME}.yml
HOST_FILE=hosts.ini
if [[ -f hosts-debug.ini ]];then
  HOST_FILE=hosts-debug.ini
  echo "Using ${HOST_FILE}"
fi

if [[ -f ${PLAYBOOK_FILE} ]];then
  ansible-playbook -i ${HOST_FILE} ${PLAYBOOK_FILE}
else
  echo "Playbook ${PLAYBOOK_FILE} not found." && exit 1
fi
