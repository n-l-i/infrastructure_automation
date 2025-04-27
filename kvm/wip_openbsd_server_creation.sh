virt-install \
  --name=openbsd_server_base \
  --ram=2048 \
  --vcpus=2 \
  --os-variant=openbsd7.5 \
  --cdrom ~/Documents/iso_files/install76.iso \
  --bridge=br0 \
  --disk path=/var/lib/libvirt/images/openbsd_server_base.qcow2,size=6 \
  --input=type=keyboard,bus=usb
