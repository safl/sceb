#!/usr/bin/env python3
"""
build fio
=========

Build fio in fio.repository.path, using prefix fio.build.prefix.

Retargetable: True
------------------
"""
from pathlib import Path


def main(args, cijoe, step):
    """Install qemu"""

    commands = [
        "git rev-parse --short HEAD",
        "make clean",
        f"./configure --prefix={ cijoe.config.options['fio']['build']['prefix'] }",
        # f"./configure --prefix={ cijoe.config.options['fio']['build']['prefix'] }",
        "make -j $(nproc)",
        "make install",
    ]
    for cmd in commands:
        err, _ = cijoe.run(
            cmd, cwd=Path(cijoe.config.options["fio"]["repository"]["path"])
        )
        if err:
            return err

    return err
