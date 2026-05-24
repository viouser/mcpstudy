import ollama

MODEL = "llama3.1:8b"

messages = [
    {
        "role": "system",
        "content": (
            "You are a local assistant. Be concise, practical, and ask before "
            "performing risky actions."
        ),
    }
]

while True:
    user_input = input("\nYou: ")

    if user_input.lower() in {"exit", "quit"}:
        break

    messages.append({"role": "user", "content": user_input})

    response = ollama.chat(
        model=MODEL,
        messages=messages,
    )

    assistant_message = response["message"]["content"]
    print(f"\nAgent: {assistant_message}")

    messages.append({"role": "assistant", "content": assistant_message})