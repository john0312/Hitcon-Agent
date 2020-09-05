#!/bin/bash

# Prepare the disk image and and dom XML.
disk_path="${TMPIMAGEDIR}/${VMID}.qcow2"
agent_path="${IMAGEDIR}/${VMNAME}.agent.sqfs"
cp "${IMAGEDIR}/${VMNAME}.qcow2" "${disk_path}"
xml_path="${TMPIMAGEDIR}/${VMID}.xml"
# WARNING: Make sure VMID and disk_path is sanitized from the python side.
cat "${VMDIR}/dom.xml" | sed "s#__VMID__#${VMID}#g" | sed "s#__DISKIMG__#${disk_path}#g" | sed "s#__VMNAME__#${VMNAME}#g" | sed "s#__AGENT_IMG__#${agent_path}#g" > ${xml_path}

sudo virsh define "${xml_path}"
