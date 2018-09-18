#!/bin/bash
if [ $# -eq 0 ]
  then
    echo "Call this script with an environment json file path"
    exit 1
fi
FILES=collections/*.json
TEST_RESULTS_DIR=test_results_summary
mkdir -p $TEST_RESULTS_DIR
rm -rf $TEST_RESULTS_DIR/*.*
for f in $FILES
do
    echo "Processing $f file..."
    file_name=$(basename $f .json)
    echo $file_name
    newman run $f -e $1 -r cli,html --reporter-html-export $TEST_RESULTS_DIR/$file_name.html
    exit_code=$?
    echo "Exit code from newman is: $exit_code"
    if [ $exit_code != 0 ]
    then
        echo "Exit is not clean. $f collection failed"
        exit $exit_code
    else
        echo "$f collection passed"
    fi
done
