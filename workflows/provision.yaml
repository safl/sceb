---
doc: |
  Produce, transform and plot fio-output
  ======================================

  This workflow assumes that the 'prep.workflow' has completed.
  The comparison and plots consists of

    * bandwidth in KiB / seconds
    * latency is mean and in nano-seconds
    * IOPS are 'raw' / base-unit

  The above in a bar-plot at iodepth=1, and a line-plot as a function of iodepth.

  See Artifacts for the generated plots

steps:
- name: kill
  uses: qemu.guest_kill

- name: initialize
  uses: qemu.guest_bootimg

- name: start
  uses: qemu.guest_start_nvme

- name: check
  run: |
    hostname

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

- name: fio
  uses: fioe
  with:
    repetitions: 1
    iosizes: ['4K']
    iodepths: [1]

- name: plot
  uses: plot
  with:
    path: cijoe-output
