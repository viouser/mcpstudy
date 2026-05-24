from fastmcp import FastMCP

mcp = FastMCP("special-tasks")


@mcp.tool()
def summarize_log(log_text: str) -> str:
    """
    Summarize a log file and identify likely errors.
    """
    lines = log_text.splitlines()

    errors = [
        line for line in lines
        if "error" in line.lower()
        or "failed" in line.lower()
        or "exception" in line.lower()
    ]

    if not errors:
        return "No obvious errors found."

    return "Potential issues:\n" + "\n".join(errors[:25])


@mcp.tool()
def calculate_vm_memory(
    vms: int,
    memory_per_vm_gb: float,
    overhead_percent: float = 15,
) -> dict:
    """
    Estimate total memory required for a number of VMs.
    """
    raw_gb = vms * memory_per_vm_gb
    overhead_gb = raw_gb * overhead_percent / 100

    return {
        "raw_gb": raw_gb,
        "overhead_gb": overhead_gb,
        "total_gb": raw_gb + overhead_gb,
    }


@mcp.tool()
def estimate_gpu_vram_capacity(
    gpu_count: int,
    vram_per_gpu_gb: float,
    model_size_gb: float,
    utilization_target_percent: float = 85,
) -> dict:
    """
    Estimate usable GPU VRAM capacity for local AI workloads.
    """
    total_vram_gb = gpu_count * vram_per_gpu_gb
    usable_vram_gb = total_vram_gb * utilization_target_percent / 100
    remaining_gb = usable_vram_gb - model_size_gb

    return {
        "total_vram_gb": total_vram_gb,
        "usable_vram_gb": usable_vram_gb,
        "model_size_gb": model_size_gb,
        "remaining_gb": remaining_gb,
        "fits": remaining_gb >= 0,
    }


if __name__ == "__main__":
    mcp.run()