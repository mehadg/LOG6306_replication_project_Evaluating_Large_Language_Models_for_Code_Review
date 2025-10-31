import json
import toml
import os
import re

# Get the parent folder name
current_file_path = os.path.abspath(__file__)
part_of_path = os.path.dirname(os.path.dirname(current_file_path))

def extract_generated_solutions(file_path):
    solutions = []
    docstrings = []
    with open(file_path, 'r', encoding="utf-8") as file:
        print("Processing JSONL file...")
        for line in file:
            json_obj = json.loads(line)

            if 'generated_solution' in json_obj:
                _, solution = remove_docstring(json_obj['generated_solution'])
                solutions.append(solution)

                explanation, _ = remove_docstring(json_obj['question'])
                docstrings.append(explanation)
            else:
                print("Warning: 'generated_solution' key not found in some entries")

    return docstrings, solutions

def remove_docstring(text):
    """Removes docstrings enclosed in triple quotes and returns both cleaned text and extracted docstring."""
    docstrings = re.findall(r'(\"\"\"(.*?)\"\"\"|\'\'\'(.*?)\'\'\')', text, flags=re.DOTALL)
    extracted_text = ''.join([ds[1] if ds[1] else ds[2] for ds in docstrings])
    
    cleaned_text = re.sub(r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\')', '', text, flags=re.DOTALL)
    return extracted_text.strip(), cleaned_text

def add_plus_after_newline(input_string):
    """Formats the input string by adding '+' at the start of each line."""
    input_string = "+" + input_string
    lines = input_string.split('\n')
    modified_string = '\n+'.join(lines)
    modified_string = f"@@ -0,0 +1,{len(lines)} @@\n" + modified_string
    return modified_string

def create_prompt_with_desc(file_path, explanation, question, i, ground_truth):
    """Creates a prompt with descriptions, replacing placeholders in a TOML template."""
    with open(file_path, 'r', encoding="utf-8") as file:
        lines = file.readlines()

    for j, line in enumerate(lines):
        if "{{desc}}" in line:
            lines[j] = line.replace("{{desc}}", explanation)
        elif "{{diff}}" in line:
            lines[j] = line.replace("{{diff}}", question)

    output_dir = os.path.join(part_of_path, "generated_prompts", "prompts_with_desc")
    if ground_truth:
        output_dir = os.path.join(output_dir, "ground_truth")

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"prompt_{i}.toml")

    with open(output_file, 'w', encoding="utf-8") as file:
        file.writelines(lines)

def create_prompt_without_desc(file_path, question, i, ground_truth):
    """Creates a prompt without descriptions, replacing placeholders in a TOML template."""
    with open(file_path, 'r', encoding="utf-8") as file:
        lines = file.readlines()

    for j, line in enumerate(lines):
        if "{{diff}}" in line:
            lines[j] = line.replace("{{diff}}", question)

    output_dir = os.path.join(part_of_path, "generated_prompts", "prompts_without_desc")
    if ground_truth:
        output_dir = os.path.join(output_dir, "ground_truth")

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"prompt_{i}.toml")

    with open(output_file, 'w', encoding="utf-8") as file:
        file.writelines(lines)

def parse_toml(file_path):
    """Parses TOML files and extracts sections enclosed in triple quotes."""
    content = ""

    with open(file_path, 'r', encoding="utf-8") as file:
        for line in file:
            content += line

    keys = ['user']
    parsed_data = {}

    for key in keys:
        start_index = content.find(f"{key}='''")
        if start_index != -1:
            start_index += len(f"{key}='''")
            end_index = content.find("'''", start_index)
            if end_index != -1:
                parsed_data[key] = content[start_index:end_index].strip()

    return parsed_data
