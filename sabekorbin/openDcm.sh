#!/bin/sh

echo "Disable firewall rules for $DCM_IP"
ssh root@$DCM_IP "debug_ports enable"
