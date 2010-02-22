#!/bin/sh
if [ $# -eq 0 ] ; then
    echo Usage: 
    echo $0 ip-addr 0
    echo to connect to the mainbord or
    echo $0 ip-addr boardnr
    echo to connect to an io-board
    echo $0 ip-addr tr boardnr
    echo to connect to a transrater board
    exit
fi;  
ip=$1;
#put object first in title, most of the time you only work with one DCM
#and an icon only show the first n characters of the title..
if [ $# -eq 1 ] ; then
    title="mainbord ($ip)"
    logfile="mainboard"
    port=22;
elif [ $# -eq 2 ] ; then
    board=$2;
    title="io$board ($ip)"
    logfile="board$board"
    port=$((1001+100*$board));
else 
    [ $2 != "tr" ] && echo "unknown destination" && exit 1;
    board=$3;
    title="tr$board ($ip)"
    logfile="transrater"
    port=$((1001+100*$board+50));    
fi;

init_cmd="rm ~/.bash_profile"

init_cmd="rm ~/.bash_profile; echo \"LS_COLORS='no=00:fi=00:di=00;34:ln=00;36:pi=40;33:so=00;35:do=00;35:bd=40;33;01:cd=40;33;01:or=41;33;01:ex=00;32:'
export LS_COLORS
alias ls='ls --color=auto -F'
alias s='/app/startdcm'
alias k='/app/killdcm'
touch /app/once
cd /app\" > ~/.bash_profile;
echo 'tcpdump -i eth2 -w /app/tcpdump.cap -s0 port 5003' >> ~/.bash_history
echo 'tail -fn1000 /var/log/$logfile' >> ~/.bash_history"

# some global stuff
addSshKey.sh root@$ip -p $port
ssh root@$ip -p $port "$init_cmd" 

konsole_version=$( konsole -v| gawk '{if ($1 ~ /Konsole/) split($2, version, "."); print version[1];}' )
if [ $konsole_version == 1 ]; then
  # Find the current console or create a new one
  if [ "${KONSOLE_DCOP:-}" != "" ] ; then
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
  dcop $konsole $session sendSession "ssh root@$ip -p $port;exit" || echo "Did you start the konsole with the --script option?"
  #sleep 2
  #dcop $konsole $session sendSession "source /app/init"
  #dcop $konsole $session sendSession "history -r /app/histCmds"
elif [ $konsole_version == 2 ]; then
  # create a new session
  session_num=$(qdbus org.kde.konsole /Konsole newSession)
  sleep 0.5
  # set title
  qdbus org.kde.konsole /Sessions/$session_num setTitle 0 "$title"
  sleep 0.1
  qdbus org.kde.konsole /Sessions/$session_num setTitle 1 "$title"
  sleep 0.1
  # send command
  qdbus org.kde.konsole /Sessions/$session_num sendText "ssh root@$ip -p $port;exit"
  sleep 0.1
  qdbus org.kde.konsole /Sessions/$session_num sendText $'\n'

fi;
