from fastmcp import FastMCP

mcp = FastMCP("vsphere-tools")


@mcp.tool()
def estimate_cluster_memory_capacity(
    host_count: int,
    memory_per_host_gb: float,
    reserved_percent: float = 20,
) -> dict:
    """
    Estimate usable vSphere cluster memory after HA or operational reserve.
    """
    raw_capacity_gb = host_count * memory_per_host_gb
    reserved_gb = raw_capacity_gb * reserved_percent / 100
    usable_capacity_gb = raw_capacity_gb - reserved_gb

    return {
        "host_count": host_count,
        "raw_capacity_gb": raw_capacity_gb,
        "reserved_gb": reserved_gb,
        "usable_capacity_gb": usable_capacity_gb,
    }


@mcp.tool()
def estimate_gpu_cluster_vram(
    host_count: int,
    gpus_per_host: int,
    vram_per_gpu_gb: float,
    fragmentation_reserve_percent: float = 15,
) -> dict:
    """
    Estimate usable GPU VRAM after reserving capacity for fragmentation.
    """
    total_gpus = host_count * gpus_per_host
    raw_vram_gb = total_gpus * vram_per_gpu_gb
    reserve_gb = raw_vram_gb * fragmentation_reserve_percent / 100
    usable_vram_gb = raw_vram_gb - reserve_gb

    return {
        "total_gpus": total_gpus,
        "raw_vram_gb": raw_vram_gb,
        "fragmentation_reserve_gb": reserve_gb,
        "usable_vram_gb": usable_vram_gb,
    }


if __name__ == "__main__":
    mcp.run()