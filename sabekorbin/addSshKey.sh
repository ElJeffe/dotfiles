#!/bin/sh
# Add the public SSH key to a device, so subsequent logins are passwordless


usage()
{
  echo "Usage:"
  echo "$0 [DCM] device"
  echo "DCM: On a DCM, the keyfile is removed after every reboot. By enabling this option,"
  echo "     the key will be stored permanently on the DCM"
  echo "device: The IP address or name of the device where the key should be added to"
}

if [ $# == 0 ]; then
  usage;
  exit 1;
fi

if [ $1 == "-h" ]; then
  usage;
  exit 1;
fi

DCM=0
if [ $1 == "DCM" ]; then
  echo "permanently adding to DCM"
  DCM=1
  shift
fi
if [ -f ~/.ssh/id_dsa.pub ]
then
  pub_key=$( cat ~/.ssh/id_dsa.pub )
elif [ -f ~/.ssh/id_rsa.pub ]
then
  pub_key=$( cat ~/.ssh/id_rsa.pub )
else
  echo "could not find RSA or DSA public key"
  exit 1;
fi

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
