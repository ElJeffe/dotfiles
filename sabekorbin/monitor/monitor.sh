progname=DCM_IO
delay=1

while getopts n:d:p:h option
do
  case "$option" in
    n)  progname="$OPTARG";;
    p)  pid="$OPTARG";;
    d)  delay="$OPTARG";;
    h|?)  echo "Usage: monitor.sh [-n programName|-p pid] [-d delay]"; exit 1;;
  esac
done
shift $(($OPTIND - 1))

if [ -z "$pid" ]; then
  pid=$( echo $(pidof "$progname") | awk '{ print $1 }' )
else
  progname=
fi


echo "ProgName $progname PID $pid Delay $delay"

if [ -z "$pid" ]; then
  echo "The pid is empty"
  exit 1
fi

if [ -n "$progname" ]; then
  logfile="$progname.cpulog"
else
  logfile="$pid.cpulog"
fi

top -b -d $delay -p $pid | ./process_top.sh -l "$logfile"

