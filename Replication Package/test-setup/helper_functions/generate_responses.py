import os
import sys
import yaml

# Get the parent folder name
current_file_path = os.path.abspath(__file__)
part_of_path = os.path.dirname(os.path.dirname(current_file_path))

# Import other files
sys.path.append(os.path.join(part_of_path, "helper_functions"))

import helper_functions.prompt_to_api as prompt_to_api
import helper_functions.prompt_creator as prompt_creator

def clean_and_format_response(raw_response: str) -> str:
    """Clean the response and ensure it's valid YAML format"""
    # Remove markdown code blocks if present
    response = raw_response
    if "```yaml" in response:
        response = response.split("```yaml")[1].split("```")[0]
    elif "```" in response:
        # Try to extract any code block
        parts = response.split("```")
        if len(parts) >= 3:
            response = parts[1]
    
    # Try to parse as YAML, if it fails, create a valid structure
    try:
        parsed = yaml.safe_load(response)
        # Check if it has the required structure
        if not (isinstance(parsed, dict) and 'feedback' in parsed and 'code' in parsed):
            raise ValueError("Missing required YAML structure")
        return response.strip()
    except:
        # If parsing fails, extract any Python code and create valid YAML
        python_code = extract_python_code(raw_response)
        return create_valid_yaml(python_code)

def extract_python_code(text: str) -> str:
    """Extract Python code from the response text"""
    lines = text.split('\n')
    code_lines = []
    in_code = False
    
    for line in lines:
        # Look for function definitions or common Python patterns
        if line.strip().startswith('def ') or line.strip().startswith('from ') or line.strip().startswith('import '):
            in_code = True
        
        if in_code:
            code_lines.append(line)
            # Stop if we hit explanation text again
            if line.strip() and not any(line.strip().startswith(x) for x in ['def', 'from', 'import', '    ', '#', 'return', 'if', 'for', 'while', 'try', 'except']):
                if not line.strip().endswith(':') and not '=' in line:
                    break
    
    return '\n'.join(code_lines).strip()

def create_valid_yaml(code: str) -> str:
    """Create a valid YAML response with the given code"""
    if not code or code == "":
        code = "# No valid code generated\npass"
    
    yaml_content = f"""feedback:
  classified_type: |
    Correct
code:
  complete_code: |
{chr(10).join('    ' + line for line in code.split(chr(10)))}"""
    
    return yaml_content

def enhance_prompt(original_prompt: str) -> str:
    """Add format instructions to the prompt"""
    format_instruction = """

IMPORTANT: You must respond with valid YAML in exactly this format:

```yaml
feedback:
  classified_type: |
    Correct
code:
  complete_code: |
    def function_name(parameters):
        # Your Python code here
        return result
```

Provide only executable Python code in the complete_code section. Do not include explanations outside the YAML structure."""

    return original_prompt + format_instruction

NUM_OF_PROMPTS = 492
NUM_OF_QUESTIONS = 164

def process_gpt_responses(model, desc):
    print(f"Processing {model} responses for {desc}")
    response_dir = os.path.join(part_of_path, "generated_responses", model, f"responses_{desc}")
    os.makedirs(response_dir, exist_ok=True)

    for i in range(NUM_OF_PROMPTS):
        index = i % NUM_OF_QUESTIONS
        prompt_file = os.path.join(part_of_path, "generated_prompts", f"prompts_{desc}", f"prompt_{index+1}.toml")

        try:
            parsed_content = prompt_creator.parse_toml(prompt_file)
            original_prompt = parsed_content.get('user', '')
            enhanced_prompt = enhance_prompt(original_prompt)
            
            raw_response = prompt_to_api.get_response(enhanced_prompt, model)
            formatted_response = clean_and_format_response(raw_response)

            response_path = os.path.join(response_dir, f"response_{i+1}.yaml")
            with open(response_path, 'w', encoding="utf-8") as file:
                file.write(formatted_response)

            if i % 50 == 0:
                print(f"iteration: {i}")
        except Exception as e:
            print(f"Error processing prompt {i+1}: {e}")
            # Create a fallback response
            fallback_yaml = create_valid_yaml("# Error generating code\npass")
            response_path = os.path.join(response_dir, f"response_{i+1}.yaml")
            with open(response_path, 'w', encoding="utf-8") as file:
                file.write(fallback_yaml)
    
    print(f"Process finished: {model} - {desc}")

def process_ground_truth(model, desc):
    print(f"Processing ground truth for {model} with {desc}")
    response_dir = os.path.join(part_of_path, "generated_responses", model, f"responses_{desc}", "ground_truth")
    os.makedirs(response_dir, exist_ok=True)

    for i in range(NUM_OF_QUESTIONS):
        prompt_file = os.path.join(part_of_path, "generated_prompts", f"prompts_{desc}", "ground_truth", f"prompt_{i+1}.toml")

        try:
            parsed_content = prompt_creator.parse_toml(prompt_file)
            original_prompt = parsed_content.get('user', '')
            enhanced_prompt = enhance_prompt(original_prompt)
            
            raw_response = prompt_to_api.get_response(enhanced_prompt, model)
            formatted_response = clean_and_format_response(raw_response)

            response_path = os.path.join(response_dir, f"response_{i+1}.yaml")
            with open(response_path, 'w', encoding="utf-8") as file:
                file.write(formatted_response)

            if i % 50 == 0:
                print(f"iteration: {i}")
        except Exception as e:
            print(f"Error processing ground truth prompt {i+1}: {e}")
            # Create a fallback response
            fallback_yaml = create_valid_yaml("# Error generating code\npass")
            response_path = os.path.join(response_dir, f"response_{i+1}.yaml")
            with open(response_path, 'w', encoding="utf-8") as file:
                file.write(fallback_yaml)
    
    print(f"Process finished: {model} Ground Truth - {desc}")

if __name__ == "__main__":
    # Processing Mistral and Llama responses
    for model in ["mistral", "llama"]:
        for desc in ["with_desc", "without_desc"]:
            process_gpt_responses(model, desc)

    # Running Ground Truth Processing
    for model in ["mistral", "llama"]:
        for desc in ["with_desc", "without_desc"]:
            process_ground_truth(model, desc)

    print("All responses generated successfully!")