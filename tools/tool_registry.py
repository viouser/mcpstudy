from langchain_core.tools import tool


@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@tool
def estimate_vm_memory(
    vm_count: int,
    memory_per_vm_gb: float,
    overhead_percent: float = 15,
) -> dict:
    """Estimate total VM memory capacity with overhead."""
    raw_gb = vm_count * memory_per_vm_gb
    overhead_gb = raw_gb * overhead_percent / 100

    return {
        "raw_gb": raw_gb,
        "overhead_gb": overhead_gb,
        "total_gb": raw_gb + overhead_gb,
    }


def load_langchain_native_tools():
    return [
        add_numbers,
        estimate_vm_memory,
    ]