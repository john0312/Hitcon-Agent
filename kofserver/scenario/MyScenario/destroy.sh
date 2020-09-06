#!/bin/bash

sudo virsh shutdown "${VMID}"
sudo virsh destroy "${VMID}"
sudo virsh undefine "${VMID}"

disk_path="${TMPIMAGEDIR}/${VMID}.qcow2"
xml_path="${TMPIMAGEDIR}/${VMID}.xml"

#rm -f "${disk_path}"
#rm -f "${xml_path}"

exit 0
