def add_numbers(a: float, b: float) -> float:
    return a + b


def estimate_vm_memory(
    vm_count: int,
    memory_per_vm_gb: float,
    overhead_percent: float = 15,
) -> dict:
    raw_gb = vm_count * memory_per_vm_gb
    overhead_gb = raw_gb * overhead_percent / 100

    return {
        "raw_gb": raw_gb,
        "overhead_gb": overhead_gb,
        "total_gb": raw_gb + overhead_gb,
    }