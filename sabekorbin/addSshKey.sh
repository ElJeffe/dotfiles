#!/bin/sh

pub_key=$( cat ~/.ssh/id_dsa.pub )
cmd="gr=\$(grep \"$pub_key\" ~/.ssh/authorized_keys2)
if [ -z \"\$gr\" ]; then
  echo \"$pub_key\" >> ~/.ssh/authorized_keys2 
fi"
ssh $* "$cmd"
