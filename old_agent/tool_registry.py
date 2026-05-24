from tools.native_tools import add_numbers, estimate_vm_memory


class Tool:
    def __init__(self, name, description, function):
        self.name = name
        self.description = description
        self.function = function

    def run(self, **kwargs):
        return self.function(**kwargs)


def load_native_tools() -> dict:
    return {
        "add_numbers": Tool(
            name="add_numbers",
            description="Add two numbers together.",
            function=add_numbers,
        ),
        "estimate_vm_memory": Tool(
            name="estimate_vm_memory",
            description="Estimate VM memory capacity with overhead.",
            function=estimate_vm_memory,
        ),
    }