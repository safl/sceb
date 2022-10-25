#!/usr/bin/env python
"""
    Run fio...
"""
from itertools import product
from pathlib import Path

from cijoe.fio.wrapper import fio_fancy


def main(args, cijoe, step):

    repetitions = step.get("with", {}).get("repetitions", 3)
    iosizes = step.get("with", {}).get("iosizes", ["4K"])
    iodepths = step.get("with", {}).get("iodepths", [1, 2, 4, 8])
    cmd_prefix = step.get("with", {}).get("cmd_prefix", "")

    cdev = {"uri": "/dev/ng0n1", "nsid": 1, "labels": ["cdev"]}
    bdev = {"uri": "/dev/nvme0n1", "nsid": 1, "labels": ["bdev"]}
    pcie = {"uri": "0000:01:00.0", "nsid": 1, "labels": ["pcie"]}

    impl_io_uring_cmd = {
        "io_uring_cmd-reference": {
            "engine": "io_uring_cmd",
            "device": cdev,
            "xnvme_opts": {},
            "spdk_opts": {},
        },
        "io_uring_cmd-xnvme": {
            "engine": "xnvme",
            "device": cdev,
            "xnvme_opts": {
                "be": "linux",
                "async": "io_uring_cmd",
                "sync": "nvme",
                "admin": "nvme",
            },
            "spdk_opts": {},
        },
        "io_uring_cmd-bdev_xnvme": {
            "engine": "spdk_bdev",
            "device": cdev,
            "xnvme_opts": {},
            "spdk_opts": {
                "bdev": "xnvme",
                "params": {
                    "filename": cdev["uri"],
                    "name": "Nvme0n1",
                    "io_mechanism": "io_uring_cmd",
                    # "conserve_cpu": False,
                    # "conserve_cpu": True,
                },
            },
        },
    }

    impl_io_uring = {
        "io_uring-reference": {
            "engine": "io_uring",
            "device": bdev,
            "xnvme_opts": {},
            "spdk_opts": {},
        },
        "io_uring-bdev_uring": {
            "engine": "spdk_bdev",
            "device": bdev,
            "xnvme_opts": {},
            "spdk_opts": {
                "bdev": "uring",
                "params": {"filename": bdev["uri"], "name": "Nvme0n1"},
            },
        },
        "io_uring-bdev_xnvme": {
            "engine": "spdk_bdev",
            "device": bdev,
            "xnvme_opts": {},
            "spdk_opts": {
                "bdev": "xnvme",
                "params": {
                    "filename": bdev["uri"],
                    "name": "Nvme0n1",
                    "io_mechanism": "io_uring",
                    # "conserve_cpu": False,
                    # "conserve_cpu": True,
                },
            },
        },
        "io_uring-xnvme": {
            "engine": "xnvme",
            "device": bdev,
            "xnvme_opts": {
                "be": "linux",
                "async": "io_uring",
                "sync": "nvme",
                "admin": "nvme",
            },
            "spdk_opts": {},
        },
    }

    impl_libaio = {
        "libaio-reference": {
            "engine": "libaio",
            "device": bdev,
            "xnvme_opts": {},
            "spdk_opts": {},
        },
        "libaio-bdev_aio": {
            "engine": "spdk_bdev",
            "device": bdev,
            "xnvme_opts": {},
            "spdk_opts": {
                "bdev": "aio",
                "params": {"filename": bdev["uri"], "name": "Nvme0n1"},
            },
        },
        "libaio-bdev_xnvme": {
            "engine": "spdk_bdev",
            "device": bdev,
            "xnvme_opts": {},
            "spdk_opts": {
                "bdev": "xnvme",
                "params": {
                    "filename": bdev["uri"],
                    "name": "Nvme0n1",
                    "io_mechanism": "libaio",
                    # "conserve_cpu": False,
                    # "conserve_cpu": True,
                },
            },
        },
        "libaio-xnvme": {
            "engine": "xnvme",
            "device": bdev,
            "xnvme_opts": {
                "be": "linux",
                "async": "libaio",
                "sync": "nvme",
                "admin": "nvme",
            },
            "spdk_opts": {},
        },
    }

    impl_ioctl = {
        "ioctl-xnvme": {
            "engine": "xnvme",
            "device": cdev,
            "xnvme_opts": {
                "be": "linux",
                "async": "thrpool",
                "sync": "nvme",
                "admin": "nvme",
            },
            "spdk_opts": {},
        },
    }

    implementation = {}
    implementation.update(impl_io_uring_cmd)
    implementation.update(impl_io_uring)
    implementation.update(impl_libaio)
    implementation.update(impl_ioctl)

    err = 0
    try:
        for (bs, iodepth, (label, params), rep) in product(
            iosizes, iodepths, implementation.items(), range(repetitions)
        ):
            fio_output_path = Path(f"/tmp/fio-output_{bs}_{iodepth}_{label}_{rep}.txt")
            err, state = fio_fancy(
                cijoe,
                fio_output_path,
                "compare",
                params["engine"],
                params["device"],
                xnvme_opts=params["xnvme_opts"],
                spdk_opts=params["spdk_opts"],
                aux={
                    "bs": str(bs),
                    "iodepth": str(iodepth),
                    "name": label,
                    "cpus_allowed": "1",
                },
            )
    except Exception as exc:
        log.error(f"Something failed({exc})")
        log.error("".join(traceback.format_exception(None, exc, exc.__traceback__)))
        print(
            type(exc).__name__,  # TypeError
            __file__,  # /tmp/example.py
            exc.__traceback__.tb_lineno,  # 2
        )

    return err
