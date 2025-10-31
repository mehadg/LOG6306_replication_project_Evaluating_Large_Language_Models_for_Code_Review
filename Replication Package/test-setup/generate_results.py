import math
import yaml
import os
import json
import re
import io
import sys
import signal
import queue
from threading import Thread

# Get the parent folder name
current_file_path = os.path.abspath(__file__)
part_of_path = os.path.dirname(os.path.dirname(current_file_path))

# Import other files
sys.path.append(f'{part_of_path}/helper_functions')
import helper_functions.testing as testing

test_files = ["r_mistral_w_desc.jsonl", "r_mistral_wout_desc.jsonl", "r_llama_w_desc.jsonl", "r_llama_wout_desc.jsonl",
              "r_mistral_gt_w_desc.jsonl", "r_mistral_gt_wout_desc.jsonl",
              "r_llama_gt_w_desc.jsonl", "r_llama_gt_wout_desc.jsonl"]

response_paths = [
    os.path.join("mistral", "responses_with_desc"),
    os.path.join("mistral", "responses_without_desc"),
    os.path.join("llama", "responses_with_desc"),
    os.path.join("llama", "responses_without_desc"),
    os.path.join("mistral", "responses_with_desc", "ground_truth"),
    os.path.join("mistral", "responses_without_desc", "ground_truth"),
    os.path.join("llama", "responses_with_desc", "ground_truth"),
    os.path.join("llama", "responses_without_desc", "ground_truth")
]

NUM_OF_PROMPTS = 492

# Get the data
file_path_tests = 'tests.jsonl'
tests = testing.extract_tests(file_path_tests)
entry_points = testing.extract_entry_points(file_path_tests)

# get the previous scores
old_scores = []
old_labels = []
with open("code_snippets.jsonl", "r") as old_scores_file:
    for line in old_scores_file:
        json_obj = json.loads(line)

        if math.isnan(json_obj['score']):
            old_scores.append(-1)
            old_labels.append("Incorrect")
        else:
            old_scores.append(json_obj['score'])

            if json_obj['score'] == 1.0:
                old_labels.append("Correct")
            else:
                old_labels.append("Incorrect")

if not os.path.exists('results'):
    os.makedirs('results')

classified_type = []
for j in range(0,8):
    counts = []
    errors = []
    with open(f'results/{test_files[j]}', "w") as results_file:
        for i in range(NUM_OF_PROMPTS):
            
            invalid_code = False
            test_index = i % 164
            error_info = "none"

            # Extract the code from the response
            try:
                with open(f'generated_responses/{response_paths[j]}/response_{i+1}.yaml', 'r') as file:
                    data = yaml.safe_load(file)
            except Exception as e:
                print(f"Exception in question {i+1}, bad response")
                error_info = "cannot parse the response yaml"
                invalid_code = True

            # Accessing the response contents
            if invalid_code == False:
                try:
                    feedback_keys = list(data['feedback'].keys())
                    code_keys = list(data['code'].keys())

                    first_feedback_key = feedback_keys[0]
                    first_code_key = code_keys[0]

                    classified_type = data['feedback'][first_feedback_key]
                    complete_code = data['code'][first_code_key]
                except Exception as e:
                    print(f"Exception in question {i+1}, invalid suggested code")
                    error_info = "invalid yaml variable value type"
                    invalid_code = True

            if invalid_code:
                counts.append("NaN")
                errors.append("NaN")
            elif complete_code == "infinite loop":
                print("Complete code was not provided by the model for question: ", i+1)
                error_info = "infinite loop"
                counts.append(-1)
                errors.append(-1)
            elif complete_code != "No":
                try:
                    result_queue = queue.Queue()

                    def run_code():
                        try:
                            # Suppress the print functions of generated solutions, if any
                            text_trap = io.StringIO()
                            sys.stdout = text_trap
                            
                            # Execute the generated code
                            exec(complete_code, globals())
                            
                            # Execute the test code
                            testing_code = tests[test_index]
                            exec(testing_code, globals())
                            
                            sys.stdout = sys.__stdout__
                            
                            # If we get here without exception, assume it passed
                            result_queue.put((1, 0))  # (passed, failed)
                            
                        except Exception as inner_e:
                            sys.stdout = sys.__stdout__
                            result_queue.put(inner_e)

                    t = Thread(target=run_code)
                    t.daemon = True
                    t.start()
                    t.join(timeout=5)

                    if t.is_alive():
                        print(f"Timeout in question {i+1}: Code execution exceeded timeout")
                        error_info = "timeout (possible infinite loop)"
                        counts.append(-1)
                        errors.append(-1)
                    else:
                        result = result_queue.get()
                        if isinstance(result, Exception):
                            raise result
                        count, error = result
                        counts.append(count)
                        errors.append(error)
                except Exception as e:
                    sys.stdout = sys.__stdout__
                    print(f"Exception in question {i+1}, cannot run the code: {e}")
                    error_info = str(e)  # Convert to string
                    counts.append("NaN")
                    errors.append("NaN")
            else:
                counts.append("NaN")
                errors.append("NaN")
            
            # Now this should work because counts[i] and errors[i] exist
            is_nan = counts[i] == "NaN" and errors[i] == "NaN"
            if is_nan:
                score = -1.0
            elif counts[i] == -1 and errors[i] == -1:
                score = 0.0
            else:
                score = counts[i] / (counts[i] + errors[i])

            if j >= 4:
                prev_score = 1.0
                prev_label = "Correct"
            else:
                prev_score = old_scores[i]
                prev_label = old_labels[i]
            score_diff = abs(score - prev_score)
            
            if score == 1.0:
                label = "Correct"
            else:
                label = "Incorrect"

            record = {'question': f'question_{i+1}', 
                    'passed_tests': counts[i], 
                    'failed_tests': errors[i], 
                    'score': score,
                    'prev_score': prev_score,
                    'score_diff': score_diff,
                    'suggested_label': classified_type,
                    'label_after_exc': label,
                    'prev_label': prev_label,
                    'error': str(error_info)}
            results_file.write(json.dumps(record) + '\n')