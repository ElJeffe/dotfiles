#!/bin/zsh


konsolePid=0
# find the pid of the current konsole
findKonsolePid()
{
  curPid=$$
  while [[ $curPid != 0 ]]; do
    curPid=$( ps -f | awk -v pid="$curPid" ' $2 == pid { print $3 } ')
    isKonsole=$( ps -p $curPid | grep konsole )
    if [[ ! -z "$isKonsole" ]]; then
     konsolePid=$curPid
     return
   fi 
  done
}

# maketab: make a new tab with a title, and send text to it
makeTab()
{
  if [ -z $1 ]; then
    echo "makeTab requires at least one argument!"
    return 1
  fi

  title=$1
  cmdList=($@[2,$#])

  konsole_version=$( konsole -v| gawk '{if ($1 ~ /Konsole/) print $2;}' )
  if [[ $konsole_version =~ "1.*" ]]; then
    # Find the current console or create a new one
    if [[ "${KONSOLE_DCOP:-}" != "" ]] ; then
      konsole=$(echo "${KONSOLE_DCOP:-}" | sed -e 's/DCOPRef(\(.*\),.*/\1/')
    else
      konsole=$(dcopstart konsole-script --script)
    fi
    # Create a new session
    session=$(dcop $konsole konsole newSession)
    if [ "$session" = "" ] ; then
      echo "'dcop $konsole konsole newSession' failed, exiting"
      exit 1
    fi
    
    dcop $konsole $session renameSession "$title" || exit 1
    for cmd in $cmdList; do
      dcop $konsole $session sendSession "$cmd"
      sleep 0.1
    done
    #sleep 2
    #dcop $konsole $session sendSession "source /app/init"
    #dcop $konsole $session sendSession "history -r /app/histCmds"
  elif [[ $konsole_version =~ "2\.(.*).*" ]]; then
    sub_version=$match
    
    # create a new session
#    if [[ $sub_version -lt 5 ]]; then
#      dbus_kons="org.kde.konsole"
#    else
#      findKonsolePid
#      dbus_kons="org.kde.konsole-$konsolePid"
#    fi
    dbus_kons="org.kde.konsole"
    session_num=$(qdbus $dbus_kons /Konsole newSession)
    sleep 0.5
    # set title
    qdbus $dbus_kons /Sessions/$session_num setTitle 0 "$title" >/dev/null
    sleep 0.1
    qdbus $dbus_kons /Sessions/$session_num setTitle 1 "$title" >/dev/null
    sleep 0.1
    # send commands
    for cmd in $cmdList; do
      qdbus $dbus_kons /Sessions/$session_num sendText "$cmd" >/dev/null
      sleep 0.1
      qdbus $dbus_kons /Sessions/$session_num sendText $'\n' >/dev/null
      sleep 0.1
    done
  else
   echo "unknown version $konsole_version"    
  
  fi;
}

