#!/usr/bin/env python3
from pathlib import Path
import re

PARAMS_DEFAULT = {
    "d": "128",  # <int>  IO Depth, default 128
    "s": "32",  # <int>  Batch submit, default 32
    "c": "32",  # <int>  Batch complete, default 32
    "b": "512",  # <int>  Block size, default 4096
    "p": "1",  # <bool> Polled IO, default 1
    "B": "1",  # <bool> Fixed buffers, default 1
    "D": "0",  # <bool> DMA map fixed buffers, default 0
    "F": "1",  # <bool> Register files, default 1
    "n": "1",  # <int>  Number of threads, default 1
    "O": "1",  # <bool> Use O_DIRECT, default 1
    "N": "0",  # <bool> Perform just no-op requests, default 0
    "t": "0",  # <bool> Track IO latencies, default 0
    "T": "0",  # <int>  TSC rate in HZ
    "r": "0",  # <int>  Runtime in seconds, default unlimited
    "R": "1",  # <bool> Use random IO, default 1
    "a": "0",  # <bool> Use legacy aio, default 0
    "S": "0",  # <bool> Use sync IO (preadv2), default 0
    "X": "0",  # <bool> Use registered ring 1
    "P": "0",  # <bool> Automatically place on device home node 0
    "u": "0",  # <bool> Use nvme-passthrough I/O, default 0
}


def main(args, cijoe, step):

    mode = step.get("with", {}).get("mode", "default")
    io_mechanism = step.get("with", {}).get("io_mechanism", "io_uring")
    runtime = str(step.get("with", {}).get("runtime", 10))
    t_io_uring_bin = step.get("with", {}).get("bin", "/opt/t_io_uring/io_uring")

    # str(Path(fio_repos) / "t" / "io_uring")

    fio_repos = (
        cijoe.config.options.get("fio", {}).get("repository", {}).get("path", None)
    )
    if not fio_repos:
        return 0

    handles = []
    for device_info in cijoe.config.options.get("duts"):
        params = PARAMS_DEFAULT.copy()

        params["r"] = 10

        handle = f"/dev/nvme{device_info['os']}"
        if io_mechanism == "io_uring_cmd":
            handle = f"/dev/ng{device_info['os']}"
            params["u"] = "1"
            params["O"] = "0"

        handles.append(handle)

        taskset = "taskset -c 0,1"
        if mode == "default":  # Default: n threads for n devices
            params["n"] = len(handles)
        elif mode == "tweak_n1":  # Tweak: 1 thread for n devices
            params["n"] = "1"
        elif mode == "tweak_n2":  # Tweak: 2 threads for n devices
            params["n"] = "2"
        elif mode == "tweak_n2_batch":  # Tweak: 2 threads for n devices + reduce batch
            params["n"] = "2"
            params["c"] = "16"
            params["s"] = "16"
        elif mode == "tweak_n1_sqpoll":
            params["n"] = "1"
            params["c"] = "16"
            params["s"] = "16"
            taskset = "taskset -c 0"
        elif mode == "tweak_n2_nopoll":
            params["n"] = "2"
            params["c"] = "16"
            params["s"] = "16"
            params["p"] = "0"
        elif mode == "tweak_n2_nopnob":
            params["n"] = "2"
            params["c"] = "1"
            params["s"] = "1"
            params["p"] = "0"

        cmd = " ".join(
            [
                taskset,
                t_io_uring_bin,
                " ".join([f"-{k}{v}" for k, v in params.items()]),
                " ".join(handles),
            ]
        )

        iops = []
        for _ in range(3):
            err, state = cijoe.run(cmd)
            output = state.output()

            match = re.match(".*IOPS=(?P<iops>.*)M.*", output, re.MULTILINE | re.DOTALL)
            if match:
                iops.append(float(match.group("iops")))

        cijoe.run(
            f'echo "mode({mode}), #ndevices({len(handles)}), best of three({max(iops)}) "'
        )

    return 0
