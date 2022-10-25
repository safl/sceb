---
doc: |
  Prepare a machine for SPDK Summit 2022
  ======================================

  This clones the required repositories, builds and installs

steps:
- name: prep_repos
  uses: core.repository_prep

- name: packages
  run: |
    cd /root/git/xnvme/ && ./toolbox/pkgs/debian-bullseye.sh

- name: prep_fio
  uses: prep_fio

- name: prep_xnvme
  uses: prep_xnvme

- name: prep_spdk
  uses: prep_spdk

- name: prep_driver
  run: |
    xnvme-driver || true
    xnvme-driver reset || true

- name: info
  uses: linux.sysinfo
