import os
from openclaw_core.engine import OpenClawEngine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASTRA_PATH = os.path.join(BASE_DIR, "astra-runtime")

if "OPENAI_API_KEY" not in os.environ:
    raise EnvironmentError(
        "OPENAI_API_KEY not set. Export it before running Astra."
    )

engine = OpenClawEngine(ASTRA_PATH)

print("ASTRA online. Type 'exit' to quit.\n")

while True:
    user_input = input("ASTRA > ")
    if user_input.lower() == "exit":
        break

    try:
        response = engine.run(user_input)
        print("\n" + response + "\n")
    except Exception as e:
        print(f"\nError: {e}\n")
