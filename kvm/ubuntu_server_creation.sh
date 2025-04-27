virt-install \
  --name ubuntu_server_base \
  --ram 2048 \
  --disk path=/var/lib/libvirt/images/ubuntu_server_base.qcow2,size=6 \
  --vcpus 2 \
  --os-variant ubuntu24.04 \
  --console pty,target_type=serial \
  --bridge=br0 \
  --cdrom ~/Documents/iso_files/ubuntu-24.04.2-live-server-amd64.iso
