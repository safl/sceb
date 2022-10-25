#!/usr/bin/env python3
"""
init zram
=========

Initialize zram block devices

Retargetable: True
------------------
"""
from pathlib import Path


def main(args, cijoe, step):
    """Install qemu"""

    commands = [
        "modprobe zram num_devices=4",
        "echo 512M > /sys/block/zram0/disksize",
    ]
    for cmd in commands:
        err, _ = cijoe.run(
            cmd, cwd=Path(cijoe.config.options["fio"]["repository"]["path"])
        )
        if err:
            return err

    return err
