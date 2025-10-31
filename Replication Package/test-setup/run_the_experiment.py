# run_the_experiment.py (minimal, import-only orchestrator)
import os, sys

HERE = os.path.abspath(os.path.dirname(__file__))
PART = os.path.dirname(HERE)
HF_DIR = os.path.join(HERE, "helper_functions")

for p in (HERE, PART, HF_DIR):
    if p not in sys.path:
        sys.path.append(p)

# 1) Generate prompts (modules usually generate on import)
import helper_functions.generate_prompts  # side effects: writes prompts

# 2) Generate responses (reads prompts, calls prompt_to_api.get_response)
import helper_functions.generate_responses

print("All tasks completed.")


