#!/bin/bash

sudo virsh shutdown "${VMID}"
# TODO: Wait for it to shutdown?
sleep 3
sudo virsh destroy "${VMID}"

exit 0


