"""Platform and GPU detection utilities for inference tracking."""

import platform
import subprocess
from dataclasses import dataclass, field


@dataclass
class GPUInfo:
    """Information about a detected GPU/accelerator."""

    name: str
    vendor: str  # nvidia, amd, intel, apple
    memory_mb: int | None = None
    driver_version: str | None = None


@dataclass
class PlatformInfo:
    """Complete platform information for inference tracking."""

    os_name: str
    os_version: str
    python_version: str
    accelerators: list[GPUInfo] = field(default_factory=list)
    compute_backend: str | None = None  # cuda, rocm, mps, oneapi, cpu

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "os_name": self.os_name,
            "os_version": self.os_version,
            "python_version": self.python_version,
            "accelerators": [
                {
                    "name": gpu.name,
                    "vendor": gpu.vendor,
                    "memory_mb": gpu.memory_mb,
                    "driver_version": gpu.driver_version,
                }
                for gpu in self.accelerators
            ],
            "compute_backend": self.compute_backend,
        }


def _detect_nvidia_gpus() -> list[GPUInfo]:
    """Detect NVIDIA GPUs using nvidia-smi."""
    gpus = []
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 3:
                        gpus.append(
                            GPUInfo(
                                name=parts[0],
                                vendor="nvidia",
                                memory_mb=int(float(parts[1])) if parts[1] else None,
                                driver_version=parts[2] if parts[2] else None,
                            )
                        )
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    return gpus


def _detect_amd_gpus() -> list[GPUInfo]:
    """Detect AMD GPUs using rocm-smi."""
    gpus = []
    try:
        # Try rocm-smi for AMD GPUs
        result = subprocess.run(
            ["rocm-smi", "--showproductname", "--showmeminfo", "vram", "--csv"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 2:
                        gpus.append(
                            GPUInfo(
                                name=parts[1] if len(parts) > 1 else "AMD GPU",
                                vendor="amd",
                                memory_mb=None,  # Parse from meminfo if needed
                                driver_version=None,
                            )
                        )
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass

    # Fallback: try lspci for AMD GPUs
    if not gpus:
        try:
            result = subprocess.run(
                ["lspci"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "VGA" in line and ("AMD" in line or "ATI" in line):
                        # Extract GPU name from lspci output
                        name_part = line.split(":")[-1].strip() if ":" in line else "AMD GPU"
                        gpus.append(GPUInfo(name=name_part, vendor="amd"))
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
    return gpus


def _detect_intel_gpus() -> list[GPUInfo]:
    """Detect Intel GPUs."""
    gpus = []
    try:
        # Try lspci for Intel GPUs
        result = subprocess.run(
            ["lspci"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "VGA" in line and "Intel" in line:
                    name_part = line.split(":")[-1].strip() if ":" in line else "Intel GPU"
                    gpus.append(GPUInfo(name=name_part, vendor="intel"))
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    return gpus


def _detect_apple_mps() -> list[GPUInfo]:
    """Detect Apple Silicon MPS availability."""
    gpus = []
    try:
        import torch

        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            # Get chip info from system_profiler on macOS
            try:
                result = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                chip_name = result.stdout.strip() if result.returncode == 0 else "Apple Silicon"
            except Exception:
                chip_name = "Apple Silicon"

            gpus.append(
                GPUInfo(
                    name=chip_name,
                    vendor="apple",
                    memory_mb=None,  # Unified memory, not separately queryable
                    driver_version=None,
                )
            )
    except ImportError:
        pass

    # Fallback for macOS without torch
    if not gpus and platform.system() == "Darwin":
        try:
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and "Apple" in result.stdout:
                gpus.append(GPUInfo(name="Apple GPU", vendor="apple"))
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
    return gpus


def _detect_compute_backend() -> str | None:
    """Detect the primary compute backend available."""
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
    except ImportError:
        pass

    # Check for ROCm
    try:
        result = subprocess.run(
            ["rocm-smi", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return "rocm"
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass

    # Check for Intel oneAPI
    try:
        result = subprocess.run(
            ["sycl-ls"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and "Intel" in result.stdout:
            return "oneapi"
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass

    return "cpu"


def get_platform_info() -> PlatformInfo:
    """Detect and return complete platform information.

    Returns:
        PlatformInfo with OS, Python version, and detected accelerators.
    """
    # Collect all detected GPUs
    accelerators = []

    # Try each detection method
    accelerators.extend(_detect_nvidia_gpus())
    accelerators.extend(_detect_amd_gpus())
    accelerators.extend(_detect_intel_gpus())
    accelerators.extend(_detect_apple_mps())

    # Detect compute backend
    compute_backend = _detect_compute_backend()

    return PlatformInfo(
        os_name=platform.system(),
        os_version=platform.release(),
        python_version=platform.python_version(),
        accelerators=accelerators,
        compute_backend=compute_backend,
    )


def get_platform_summary() -> str:
    """Get a human-readable summary of the platform.

    Returns:
        String summary of detected platform and accelerators.
    """
    info = get_platform_info()

    parts = [f"{info.os_name} {info.os_version}", f"Python {info.python_version}"]

    if info.accelerators:
        gpu_names = [gpu.name for gpu in info.accelerators]
        parts.append(f"GPU: {', '.join(gpu_names)}")
    else:
        parts.append("No GPU detected")

    if info.compute_backend:
        parts.append(f"Backend: {info.compute_backend}")

    return " | ".join(parts)
