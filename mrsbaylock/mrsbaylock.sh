#!/usr/bin/env bash

set -e

echo
echo "------------------------------------------"
echo "  I am here to protect thee "
echo "------------------------------------------"
echo

echo 'Pick a browser. Enter 1 or 2, but do not pick Firefox for now. '

browser_options=("chrome" "firefox")

select opt in "${browser_options[@]}"; do
  case ${opt} in
  "chrome")
    browser="chrome"
    break
    ;;
  "firefox")
    browser="firefox"
    break
    ;;
  *)
    echo "The devil made you say that, try again"
    exit 1
    ;;
  esac
done

headless_options=("regular" "headless")

select opt in "${headless_options[@]}"; do
  case ${opt} in
  "headless")
    headless=true
    break
    ;;
  "regular")
    headless=false
    break
    ;;
  *)
    echo "The devil made you say that, try again"
    exit 1
    ;;
  esac
done

echo
echo "Enter name of test file you want to run (e.g., 'user_authentication' will run 'test_user_authentication.py')"
echo -n "    > "

read test_suite

echo
echo "Enter your username"
echo
printf "    > "

read username

echo
echo "Enter your password"
echo
printf "    > "

read -s password

echo
echo "Running tests matching ${test_suite}"

USERNAME="${username}" PASSWORD="${password}" pytest tests/test_${test_suite}.py --browser ${browser} --headless ${headless}

exit 0
