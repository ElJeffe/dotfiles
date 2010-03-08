#/bin/bash
# Process the batch output of top and prints the date, cpu and mem usage of the process.
# it will also be written to a file
# usage: top -b -p thePid | ./process_top.sh -l logfile

while getopts l:h option
do
  case "$option" in
    l)  logfile="$OPTARG";;
    p|?)  echo "usage: top -b -p thePid | ./process_top.sh -l logfile";exit 1;;
  esac
done
shift $(($OPTIND - 1))

# clear logfile
if [ "$logfile" ]; then echo "" > $logfile; echo "Logging to $logfile"; fi

log() {
  if [ "$1" ]; then
    echo -e "$1"
    if [ "$logfile" ]; then echo -e "$1" >> $logfile; fi
  fi
}

print_next_line=false
time=0
log "Time    \tCPU\t%Mem\tVMem"
while read line; do
  if $print_next_line; then
    cpu_load=$(echo "$line" | awk '{print $9,"\t",$10,"\t",$5}')
    log "$time\t$cpu_load"
    print_next_line=false
  else
    tmp_time=$(echo "$line" | awk '{if ($1 == "top")print $3}')
    if [ ${#tmp_time} != 0 ]; then
      time=$tmp_time
    fi
    print_next_line=$(echo "$line" | awk '{if ($1 == "PID") print "true"; else print "false"}')
  fi
done
