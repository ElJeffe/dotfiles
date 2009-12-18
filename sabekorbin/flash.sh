#!/bin/bash

#GOEMANB

#configure ip address

usage ()
{
    echo "usage:"
    echo $0 [-d] [-b] [-k] [file]
    echo "-d to copy a non-stripped version"
    echo "-b to copy both stripped and non-stripped versions"
    echo "by default only a stripped version is copied"
    echo "file to explicit specify an executable to strip/copy"
    echo "(specifying a file should not be necessary , script should find it itself)"
}
std_execs="DCM_IO DCM_MB DCM_SNMP DCM_TR"
exec=;
debug=0;
stripped=1;
#user=$(whoami)
if [ $# -ge 1 ] ; then
    if [ $1 == '-d' ] ; then
        debug=1;
        stripped=0;
        shift;
    elif [ $1 == '-b' ] ; then
        debug=1;
        stripped=1;
        shift;
    elif [ $1 == '-h' ] ; then
        usage;
        exit;
    elif [ $1 == '--help' ] ; then
        usage;
        exit;
    fi;
fi;

#now we should have no arguments or one filename
if [ $# -gt 1 ] ;then
    echo "too many/invalid arguments"
    usage;
    exit;
fi;

if [ $# == 1 ] ; then
#executable is specified, check if it exists
    exec=$1;
    if [ ! -f $exec ] ; then
        echo "$exec not found"
        usage;
        exit;
    fi;
else 
#search standard list for executable.
    for i in $std_execs; do 
        if [ -f $i ] ; then
            exec=$i;
            echo using $exec
            break;
        fi;
    done;
fi;
#check if we found a "standard" executable
if [ -z $exec ] ; then
    usage;
    exit;
fi;
#determine target name
suffix=${exec#*.} #name upto first dot
dbgsuffix=""
if [ "$suffix" == "$exec" ] ; then
#no suffix
    target=${exec}
else
    prefix=${exec%%.*} #everything after fist dot
    target=${prefix}.${suffix}
fi;
tgtdir="/app/bin"
if [ $suffix == "o" ] ; then
    echo "assuming kernel module, putting it in /app/kernel"
    debug=1
    stripped=0
    dbgsuffix=""
    tgtdir=/app/kernel
elif [ $suffix == "ffs" ] ; then
    echo "assuming fpga code, putting it in /app/fpga"
    debug=1
    stripped=0
    dbgsuffix=""
    tgtdir=/app/fpga
fi;
#now start copying...
localFile=""
trgetFile=""
if [ $debug -eq 1 ] ; then
    localFile=$exec
    targetFile=${target}${dbgsuffix}
fi;
if [ $stripped -eq 1 ] ; then
    ppc_440-strip $exec -o ${target}_s
    localFile=${target}_s
    targetFile=${target}
fi;

ssh root@$DCM_IP "rm $tgtdir/$targetFile"
scp $localFile root@$DCM_IP:$tgtdir/$targetFile
NOW=$(date +%Hh%M)
echo "Flashing of $localFile to $targetFile on $DCM_IP finished on $NOW"
chksum=$(md5sum $localFile)
echo "md5sum: $chksum"
