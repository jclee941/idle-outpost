from __future__ import annotations

import logging
import shlex
import subprocess
from dataclasses import dataclass

LOGGER = logging.getLogger(__name__)

_KEYWORDS = ("outpost", "idleoutpost", "appquantum")


@dataclass(frozen=True)
class CandidatePackage:
    package: str
    main_activity: str | None


def _adb(args: list[str], device: str | None = None) -> str:
    cmd = ["adb"]
    if device:
        cmd += ["-s", device]
    cmd += args
    LOGGER.debug("adb: %s", shlex.join(cmd))
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)


def list_packages(device: str | None = None) -> list[str]:
    output = _adb(["shell", "pm", "list", "packages"], device)
    return sorted(
        line.replace("package:", "").strip()
        for line in output.splitlines()
        if line.startswith("package:")
    )


def find_outpost_packages(device: str | None = None) -> list[str]:
    return [pkg for pkg in list_packages(device) if any(kw in pkg.lower() for kw in _KEYWORDS)]


def get_main_activity(package: str, device: str | None = None) -> str | None:
    try:
        out = _adb(
            ["shell", "cmd", "package", "resolve-activity", "--brief", package], device
        )
    except subprocess.CalledProcessError as exc:
        LOGGER.warning("resolve-activity failed for %s: %s", package, exc.output)
        return None
    for line in out.splitlines():
        line = line.strip()
        if "/" in line and line.startswith(package + "/"):
            return line.split("/", 1)[1]
    return None


def discover(device: str | None = None) -> list[CandidatePackage]:
    candidates: list[CandidatePackage] = []
    for pkg in find_outpost_packages(device):
        candidates.append(CandidatePackage(package=pkg, main_activity=get_main_activity(pkg, device)))
    return candidates
