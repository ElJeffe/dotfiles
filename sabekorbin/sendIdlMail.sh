#/bin/zsh

BASEDIR=/home/steelj99/Projects/checkIdls
RESULTS_FILE=/tmp/checkIdlResults-$USER
# Set update to 1, if the code should be updated from CVS
UPDATE=1
# set clean to 1, if all checked out code should be deleted at the end
CLEAN=1

IDL_RESP=steelj99@cisco.com
DOXY_RESP=pschiepe@cisco.com
#DOXY_RESP=steelj99@cisco.com

log()
{
  echo "$(date +%H:%M:%S) - $@"
}

# remove RESULTS_FILE if it exists
if [[ -a $RESULTS_FILE ]] ; then
  rm $RESULTS_FILE
fi

# update all code
if [[ $UPDATE -ne 0 ]] ; then
  log "Updating DCM_IDL"
  cd $BASEDIR/DCM_IDL
  cvs update -d > /dev/null 2>&1

  for proj in DCM_IO DCM_MB DCM_TR
  do
    log "Updating $proj"
    cd $BASEDIR/$proj
    cvs update default.conf > /dev/null 2>&1
    /usr/local/bin/dcm-update > /dev/null 2>&1
  done
fi

# check idls and add them to the results file
for proj in DCM_IO DCM_MB DCM_TR
do
  log "Check IDL calls in $proj"
  echo "IDL check in $proj" >> $RESULTS_FILE
  echo "#######################" >> $RESULTS_FILE
  BRANCH=$(head -n1 $BASEDIR/$proj/CVS/Tag)
  echo "Branch: $BRANCH" >> $RESULTS_FILE
  cat $BASEDIR/$proj/CVS/Tag >> $RESULTS_FILE
  echo " ----------------------" >> $RESULTS_FILE
  cd $BASEDIR/DCM_IDL
  ./checkIfIdlCallsDocumented.py -i . -c $BASEDIR/$proj >> $RESULTS_FILE
  echo " " >> $RESULTS_FILE
done

log "Results written to $RESULTS_FILE"

# send mail of results file
cat $RESULTS_FILE | mail -s "IDL checks" $IDL_RESP

# check doxygen errors
log "Check doxygen errors"
cd $BASEDIR/DCM_IDL
./makePdf > /dev/null 2>&1
echo "" | mail -s "Doxygen warnings" -a DoxygenWarnings.csv $DOXY_RESP

# remove all checked out code, since otherwise my disk quote is exceeded
if [[ $CLEAN -ne 0 ]] ; then
  for proj in DCM_IDL DCM_IO DCM_MB DCM_TR
  do
    cd $BASEDIR/$proj
    /home/steelj99/bin/clearcvs
  done
fi
