#!/bin/sh

filename="cvslog.html"

usage()
{
  echo "Usage:"
  echo "$0 -d date [-u user -f filename -a]"
  echo "Date: the start date of the changes (i.e. 20080215)"
  echo "User: the user who has checked in"
  echo "Filename: the file to which to log (default $filename)"
  echo "-a: for all users"
}

while getopts u:d:f:ah option
do
  case "$option" in
    u)  user="$OPTARG";;
    d)  date="$OPTARG";;
    f)  filename="$OPTARG";;
    a)  allusers='yes';;
    h|?)  usage; exit 1;;
  esac
done
shift $(($OPTIND - 1))

# check that we have arguments
usercmd=''
if [ $allusers ]; then
  usercmd='-a '
elif [ $user ]; then
  usercmd='-u '$user
fi
if [ -z "$date" ]; then
  usage;
  exit;
fi

echo '<html><body><table>' > $filename
cvs history -c $usercmd -D $date . | gawk '{ baseAddr="http://embedded-kjk.cisco.com/cgi-bin/cvsweb.cgi/"$8"/"$7;print "<tr><td>"$2"</td><td><a href=\""baseAddr"?rev="$6"\">"$7"</a></td><td>";split ($6, a, ".");v1=""; if (a[4] == 1){v1=a[1]"."a[2]; v2=a[1]"."a[2]"."a[3]"."a[4]} else if (a[4] == 0) {v1=a[1]"."a[2]-1; v2=a[1]"."a[2]} else {v1=a[1]"."a[2]"."a[3]"."a[4]-1; v2=a[1]"."a[2]"."a[3]"."a[4]}; if (v1 != "") print "\t<a href=\""baseAddr".diff?r1="v1";r2="v2";f=H\">Diff "v1" - "v2"</a>" ; print "</td></tr>"; }' >> $filename
echo '</table></body></html>' >> $filename

#print info
echo 'view log with:'
echo 'firefox '$filename
