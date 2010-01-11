#!/bin/sh
DCM=0
if [ $1 == "DCM" ]; then
  echo "permanently adding to DCM"
  DCM=1
  shift
fi

pub_key=$( cat ~/.ssh/id_dsa.pub )
cmd="gr=\$(grep \"$pub_key\" ~/.ssh/authorized_keys2)
if [ -z \"\$gr\" ]; then
  echo \"$pub_key\" >> ~/.ssh/authorized_keys2;"
  if [ $DCM -eq 1 ]; then
    cmd="$cmd
  echo \"$pub_key\" >> /app/authorized_keys2;"
fi
cmd="$cmd
fi"

#echo "$cmd"
ssh $* "$cmd"
