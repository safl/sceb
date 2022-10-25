#!/usr/bin/env python3
"""
Build xNVMe from source
=======================

Step Args
---------

step.with.xnvme_source:  path to xNVMe source (default: config.options.repository.path)

Retargetable: True
------------------
"""
import errno
from pathlib import Path


def main(args, cijoe, step):
    """Build xNVMe"""

    conf = cijoe.config.options.get("xnvme", None)
    if not conf:
        return errno.EINVAL

    xnvme_source = step.get("with", {}).get("xnvme_source", conf["repository"]["path"])

    commands = [
        "git rev-parse --short HEAD",
        "rm -r builddir || true",
        "meson setup builddir -Dwith-spdk=false",
        "cd builddir && meson compile",
        "cd builddir && meson install",
        "cd builddir && meson --internal uninstall",
        "cd builddir && meson install",
        "cat builddir/meson-logs/meson-log.txt",
    ]
    first_err = 0
    for cmd in commands:
        err, _ = cijoe.run(
            cmd,
            cwd=xnvme_source,
        )
        if err and not first_err:
            first_err = err

    return first_err
