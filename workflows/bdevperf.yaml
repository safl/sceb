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

- name: bdevperf
  uses: bdevperf
  with:
    repetitions: 3
    iosizes: ['4K']
    iodepths: [1, 2, 4, 8]
