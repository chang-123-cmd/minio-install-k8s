#!/usr/bin/env bash

set -e

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd ${SCRIPT_PATH}

umask 0022

exclude_record=excludes
touch ${exclude_record}

execution_time_record=time.log
echo "-----------------------------" >> ${execution_time_record}
multi_script=1
if [[ $(find bin -maxdepth 1 -type l -name "[0-9]*_*.sh" -not -path "bin/00_debug.sh" -print | sort | wc -l) -eq 1 ]];then
  multi_script=0
fi

# shellcheck disable=SC2044
for script_name in $(find bin -maxdepth 1 -type l -name "[0-9]*_*.sh" -not -path "bin/00_debug.sh" -print | sort); do
  echo "${script_name}"
  step_name=${script_name}
  if [[ ${multi_script} -eq 1 ]] && grep -q "${step_name}" ${exclude_record}; then
    echo "    ${step_name} excluded, skipping"
  else
    SECONDS=0
    echo "$(date +"%Y-%m-%d %H:%M:%S") ${step_name} start" >> ${execution_time_record}
    ./${script_name}
    echo "${step_name}" >>${exclude_record}
    {
      echo "$(date +"%Y-%m-%d %H:%M:%S") ${step_name} end"
      echo "${SECONDS} seconds elapsed."
      echo ""
    } >> ${execution_time_record}
  fi
done
echo "" >> ${execution_time_record}
