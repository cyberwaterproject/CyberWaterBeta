# first build
ARCHIVE_FILE=packed.tar
RESULT_FILE=agent_results.zip
RUN_FILE=./run.sh
echo "Driver: started, current time:"
date
if [ -f $ARCHIVE_FILE ]; then
  tar -xf $ARCHIVE_FILE
  echo "archive is extracted, current folder:"
  ls | sed -e 's/^/   /'
else
  >&2 echo "$ARCHIVE_FILE not found"
fi

if [ -f $RUN_FILE ]; then
  echo "run.sh contents:"
  sed -e 's/^/   /' $RUN_FILE

  dos2unix $RUN_FILE
  sh $RUN_FILE
  echo "Done, creating results archive (${RESULT_FILE})"
  zip -r  ${RESULT_FILE} .


  echo "Driver: finished"
else
  echo "ERR: run.sh not found"
fi
