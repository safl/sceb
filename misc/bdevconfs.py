#!/usr/bin/env python3
import argparse
from cijoe.core.resources import dict_from_yamlfile
from pathlib import Path
import pprint
import json
import os


IOPATHS = {
    "driver": {
        "bdev_name": "bdev_nvme",
        "io_mechanism": "spdk_nvme",
        "method": "bdev_nvme_attach_controller",
    },
    "aio": {
        "bdev_name": "bdev_aio",
        "io_mechanism": "libaio",
        "method": "bdev_aio_create",
    },
    "uring": {
        "bdev_name": "bdev_uring",
        "io_mechanism": "io_uring",
        "method": "bdev_uring_create",
    },
    "xnvme_libaio": {
        "bdev_name": "bdev_xnvme",
        "io_mechanism": "libaio",
        "conserve_cpu": False,
        "method": "bdev_xnvme_create",
    },
    "xnvme_libaio_conserve_cpu": {
        "bdev_name": "bdev_xnvme",
        "io_mechanism": "libaio",
        "conserve_cpu": True,
        "method": "bdev_xnvme_create",
    },
    "xnvme_io_uring": {
        "bdev_name": "bdev_xnvme",
        "io_mechanism": "io_uring",
        "conserve_cpu": False,
        "method": "bdev_xnvme_create",
    },
    "xnvme_io_uring_conserve_cpu": {
        "bdev_name": "bdev_xnvme",
        "io_mechanism": "io_uring",
        "conserve_cpu": True,
        "method": "bdev_xnvme_create",
    },
    "xnvme_io_uring_cmd": {
        "bdev_name": "bdev_xnvme",
        "io_mechanism": "io_uring_cmd",
        "conserve_cpu": False,
        "method": "bdev_xnvme_create",
    },
    "xnvme_io_uring_cmd_conserve_cpu": {
        "bdev_name": "bdev_xnvme",
        "io_mechanism": "io_uring_cmd",
        "conserve_cpu": True,
        "method": "bdev_xnvme_create",
    },
}


def gen_bdev_confs(args):

    config = dict_from_yamlfile(args.config)

    for iopath_label, iopath in IOPATHS.items():
        conf = {"subsystems": []}
        for count, dev_info in enumerate(config.get("duts"), 1):
            bdevs = {
                "subsystem": "bdev",
                "config": [],
            }

            # Parameters, first the device "handle"
            params = {}
            if "driver" in iopath_label:
                params["trtype"] = "PCIe"
                params["traddr"] = f"{dev_info['pcie']}"
            elif "io_uring_cmd" in iopath_label:
                params["filename"] = f"/dev/ng{dev_info['os']}"
            else:
                params["filename"] = f"/dev/nvme{dev_info['os']}"

            # Parameters, then an instance name
            params["name"] = "_".join(
                [
                    f"{iopath['bdev_name']}",
                    f"{iopath['io_mechanism']}",
                    f"device{dev_info['os']}",
                ]
            )

            # Parameters, for xNVMe
            if "xnvme" in iopath_label:
                params["io_mechanism"] = f"{iopath['io_mechanism']}"
                params["conserve_cpu"] = iopath['conserve_cpu']

            bdevs["config"].append(
                {
                    "params": params,
                    "method": iopath["method"],
                }
            )
            conf["subsystems"].append(bdevs)

            output_dir = args.output
            os.makedirs(output_dir, exist_ok=True)

            filename = output_dir / "_".join(
                [
                    f"{iopath['bdev_name']}",
                    f"{iopath['io_mechanism']}",
                    "conserve_cpu" if "xnvme" in iopath_label and iopath["conserve_cpu"] else "", 
                    f"{count}.conf",
                ]
            )

            with filename.open("w") as cfile:
                json.dump(conf, cfile, indent=2, sort_keys=False)


def parse_args():

    parser = argparse.ArgumentParser(
        prog="stuff", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to CIJOE config",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default="/tmp",
        help="Path to the Configuration file.",
    )

    return parser.parse_args()


def main():

    args = parse_args()

    gen_bdev_confs(args)


if __name__ == "__main__":
    main()
