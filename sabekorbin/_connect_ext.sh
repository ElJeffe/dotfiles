#!/bin/zsh

source $(dirname $0)/_tabs.sh

if [[ $# -eq 0 ]] ; then
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
short_ip=$ip;
if [[ $ip =~ "10\.48\.(.*)" ]]
then
  short_ip=$match
fi
#put object first in title, most of the time you only work with one DCM
#and an icon only show the first n characters of the title..
if [[ $# -eq 1 ]] ; then
    title="mainbord ($short_ip)"
    logfile="mainboard"
    port=22;
elif [[ $# -eq 2 ]] ; then
    board=$2;
    title="io$board ($short_ip)"
    logfile="board$board"
    port=$((1001+100*$board));
else 
    [[ $2 != "tr" ]] && echo "unknown destination" && exit 1;
    board=$3;
    title="tr$board ($short_ip)"
    logfile="transrater"
    port=$((1001+100*$board+50));    
fi;

# open debug ports if necessary
if [[ $(ssh $ip -p $port "echo 2>&1" 2>&1) =~ "refused" ]]; then
  openDcm.sh $ip
fi

init_cmd="rm ~/.bash_profile; echo \"LS_COLORS='no=00:fi=00:di=00;34:ln=00;36:pi=40;33:so=00;35:do=00;35:bd=40;33;01:cd=40;33;01:or=41;33;01:ex=00;32:'
export LS_COLORS
alias ls='ls --color=auto -F'
alias s='/app/startdcm'
alias k='/app/killdcm'
touch /app/once
cd /app\" > ~/.bash_profile;
echo 'tcpdump -i eth2 -w /app/tcpdump.cap -s0 port 5003' >> ~/.bash_history
echo 'watch /app/myetime' >> ~/.bash_history
echo 'date; rebootdcm -i; watch /app/myetime' >> ~/.bash_history
echo 'date; rebootdcm -ci; watch /app/myetime' >> ~/.bash_history
echo 'tail -fn1000 /var/log/$logfile' >> ~/.bash_history"

# some global stuff
#addSshKey.sh root@$ip -p $port
ssh root@$ip -p $port "$init_cmd" 

# create the tab
makeTab "$title" "ssh root@$ip -p $port; exit"

