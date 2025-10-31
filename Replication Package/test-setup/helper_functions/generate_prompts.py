import os
import sys
import json

# Get the parent folder name
current_file_path = os.path.abspath(__file__)
part_of_path = os.path.dirname(os.path.dirname(current_file_path))

# Import other files
sys.path.append(os.path.join(part_of_path, "helper_functions"))
import helper_functions.prompt_creator as prompt_creator

NUM_OF_QUESTIONS = 164

# Get the data
file_path_solutions = os.path.join(part_of_path, "code_snippets.jsonl")
docstrings, solutions = prompt_creator.extract_generated_solutions(file_path_solutions)

# Define output directories (corrected paths)
output_dir_with_desc = os.path.join(part_of_path, "generated_prompts", "prompts_with_desc")
output_dir_without_desc = os.path.join(part_of_path, "generated_prompts", "prompts_without_desc")
ground_truth_dir_with_desc = os.path.join(output_dir_with_desc, "ground_truth")
ground_truth_dir_without_desc = os.path.join(output_dir_without_desc, "ground_truth")

# Ensure directories exist
os.makedirs(output_dir_with_desc, exist_ok=True)
os.makedirs(output_dir_without_desc, exist_ok=True)
os.makedirs(ground_truth_dir_with_desc, exist_ok=True)
os.makedirs(ground_truth_dir_without_desc, exist_ok=True)

# Function to check if the job is done
def is_job_done(directory, ground_truth=False):
    prefix = "gt_" if ground_truth else "prompt_"
    expected_files = [os.path.join(directory, f"{prefix}{i+1}.toml") for i in range(NUM_OF_QUESTIONS)]
    
    missing_files = [f for f in expected_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"Missing files in {directory}: {len(missing_files)} files are missing.")
        return False
    else:
        print(f"All expected files exist in {directory}. Skipping...")
        return True

# Creating prompts with descriptions
if not is_job_done(output_dir_with_desc):
    print("Creating prompts with descriptions...")
    for i in range(NUM_OF_QUESTIONS):
        prompt_creator.create_prompt_with_desc(
            os.path.join(part_of_path, "prompt_templates", "prompt_with_desc.toml"),
            "\"" + docstrings[i] + "\"",
            prompt_creator.add_plus_after_newline(solutions[i]),
            i + 1,
            ground_truth=False
        )
    print("Prompts with descriptions complete.")
else:
    print("Prompts with descriptions already exist. Skipping...")

# Creating prompts without descriptions
if not is_job_done(output_dir_without_desc):
    print("Creating prompts without descriptions...")
    for i in range(NUM_OF_QUESTIONS):
        prompt_creator.create_prompt_without_desc(
            os.path.join(part_of_path, "prompt_templates", "prompt_without_desc.toml"),
            prompt_creator.add_plus_after_newline(solutions[i]),
            i + 1,
            ground_truth=False
        )
    print("Prompts without descriptions complete.")
else:
    print("Prompts without descriptions already exist. Skipping...")

# Creating ground truth prompts
if not is_job_done(ground_truth_dir_with_desc, ground_truth=True) or not is_job_done(ground_truth_dir_without_desc, ground_truth=True):
    print("Creating ground truth prompts...")
    with open(os.path.join(part_of_path, "HumanEval.jsonl"), 'r') as file:
        i = 0
        for line in file:
            json_obj = json.loads(line)

            func_def_list = solutions[i].split("\n")
            func_def = next((element for element in func_def_list if element.startswith("def ")), "")
            ground_truth = func_def + "\n" + json_obj['canonical_solution']

            prompt_creator.create_prompt_with_desc(
                os.path.join(part_of_path, "prompt_templates", "prompt_with_desc.toml"),
                "\"" + docstrings[i] + "\"",
                prompt_creator.add_plus_after_newline(ground_truth),
                i + 1,
                ground_truth=True
            )
            prompt_creator.create_prompt_without_desc(
                os.path.join(part_of_path, "prompt_templates", "prompt_without_desc.toml"),
                prompt_creator.add_plus_after_newline(ground_truth),
                i + 1,
                ground_truth=True
            )
            i += 1
    print("Ground truth prompts complete.")
else:
    print("Ground truth prompts already exist. Skipping...")

print("All tasks completed.")

if __name__ == "__main__":
    # Put all the execution code here
    # (The code that actually runs when imported)
    pass
