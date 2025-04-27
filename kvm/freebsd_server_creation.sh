virt-install \
  --name freebsd_server_base \
  --ram 2048 \
  --disk path=/var/lib/libvirt/images/freebsd_server_base.qcow2,size=6 \
  --vcpus 2 \
  --os-variant freebsd14.0 \
  --console pty,target_type=serial \
  --bridge=br0 \
  --cdrom ~/Documents/iso_files/FreeBSD-14.2-RELEASE-amd64-disc1.iso
