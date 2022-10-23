#!/usr/bin/env bash

readonly SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${SCRIPT_ROOT}"

TARGET_DIR=bin
mkdir -p ${TARGET_DIR}

# shellcheck disable=SC2044
for script_name in $(find ${TARGET_DIR} -maxdepth 1 -type l -name "[0-9]*_*.sh" -print | sort); do
  echo "Removing link ${script_name}"
  rm -f ${script_name}
done
echo

for playbook in $(find playbooks -mindepth 1 -maxdepth 1 -type f -print | sort)
do
  playbook_file=$(basename ${playbook})
  playbook_name=${playbook_file%.*}
  playbook_runner=${TARGET_DIR}/${playbook_name}.sh
  [[ -f ${playbook_runner} ]] && rm -f ${playbook_runner}
  echo "Creating Link: ${playbook_runner} --> playbook.sh"
  ln -s ../playbook.sh ${playbook_runner}
done
