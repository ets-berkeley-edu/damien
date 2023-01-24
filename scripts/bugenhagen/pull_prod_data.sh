#!/bin/bash

# Fail the entire script when one of the commands in it fails
set -e

echo_usage() {
  echo "SYNOPSIS"
  echo "     ${0} -d db_connection"; echo
  echo "DESCRIPTION"
  echo "Available options"
  echo "     -d      Database connection information in the form 'host:port:database:username'"
}

while getopts "d:" arg; do
  case ${arg} in
    d)
      # shellcheck disable=SC2206
      db_params=(${OPTARG//:/ })
      db_host=${db_params[0]}
      db_port=${db_params[1]}
      db_database=${db_params[2]}
      db_username=${db_params[3]}
      db_password=${db_params[4]}
      ;;
    *) ;;
  esac
done

# Validation
[[ "${db_host}" && "${db_port}" && "${db_database}" && "${db_username}" ]] || {
  echo "[ERROR] You must specify complete database connection information."; echo
  echo_usage
  exit 1
}

if ! [[ "${db_password}" ]]; then
  echo -n "Enter database password: "
  read -s db_password; echo; echo
fi

echo

SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
CSV_HOME_DIRECTORY="${SCRIPT_DIR}/csv_files"

# Delete old CSVs
rm -Rf "${CSV_HOME_DIRECTORY}"
mkdir -p "${CSV_HOME_DIRECTORY}"

output_csv() {
  # Connect to the source database and pipe the results of a supplied query to a CSV file in the local directory.
  echo "Copying ${1} from database..."
  PGPASSWORD=${db_password} psql -h "${db_host}" -p "${db_port}" -d "${db_database}" --username "${db_username}" \
  -c "COPY (${2}) TO STDOUT WITH (FORMAT CSV, HEADER TRUE, FORCE_QUOTE *, DELIMITER '|')" > "${CSV_HOME_DIRECTORY}/${1}.csv"
}

# Query each table except for exports (whose records point to environment-specific S3 locations).

output_csv "department_catalog_listings" "SELECT * FROM department_catalog_listings"
output_csv "department_forms" "SELECT * FROM department_forms"
output_csv "department_members" "SELECT * FROM department_members"
output_csv "department_notes" "SELECT * FROM department_notes"
output_csv "departments" "SELECT * FROM departments"
output_csv "evaluation_types" "SELECT * FROM evaluation_types"
output_csv "evaluations" "SELECT * FROM evaluations"
output_csv "evaluation_terms" "SELECT * FROM evaluation_terms"
output_csv "json_cache" "SELECT * FROM json_cache"
output_csv "supplemental_instructors" "SELECT * FROM supplemental_instructors"
output_csv "supplemental_sections" "SELECT * FROM supplemental_sections"
output_csv "tool_settings" "SELECT * FROM tool_settings"
output_csv "user_department_forms" "SELECT * FROM user_department_forms"
output_csv "users" "SELECT * FROM users"

echo "Done."

exit 0
