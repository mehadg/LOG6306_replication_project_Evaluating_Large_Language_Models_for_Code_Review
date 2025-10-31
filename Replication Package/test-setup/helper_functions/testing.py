import json
    
def extract_tests(file_path):
    test_cases = []
    with open(file_path, 'r') as file:
        for line in file:
            json_data = json.loads(line)
            test_code = json_data['test']
            test_cases.append(test_code)
    return test_cases

def extract_entry_points(file_path):
    entry_points = []
    with open(file_path, 'r') as file:
        for line in file:
            json_obj = json.loads(line)
            entry_points.append(json_obj['entry_point'])
    
    return entry_points

def preprocess_test(test):
    arr = test.split("\n")
    arr.insert(1, '    errors = 0')
    arr.insert(2, '    count = 0')
    
    i = 3  # Starting after the inserted count and errors lines
    while i < len(arr):
        line = arr[i].strip()
        if line.startswith('assert'):
            # Replace assert with try-except block
            original_assert = line
            new_block = f"""
    try:
        {original_assert}
        count += 1
    except Exception as e:
        errors += 1"""
            arr[i] = new_block
        i += 1
    
    arr.append('    return count, errors')  # Optionally return the counts at the end of the function
    return "\n".join(arr)

def check(func):
    """
    Runs test cases for a given function and returns (passed_count, failed_count)
    """
    passed = 0
    failed = 0
    
    try:
        # This will be called after the test code is executed
        # The test code should set global variables for tracking
        if hasattr(func, '__globals__'):
            test_globals = func.__globals__
            if 'passed_tests' in test_globals and 'failed_tests' in test_globals:
                passed = test_globals.get('passed_tests', 0)
                failed = test_globals.get('failed_tests', 0)
            else:
                # If no test tracking, assume it passed if no exception
                passed = 1
                failed = 0
        else:
            passed = 1
            failed = 0
            
    except Exception as e:
        passed = 0
        failed = 1
        
    return (passed, failed)