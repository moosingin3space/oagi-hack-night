import asyncio
import os
import subprocess
import argparse
import yaml
from typing import List, Dict, Any
import dotenv

# Import the judge function
try:
    from judge import evaluate_ease_of_use
except ImportError:
    print("Error: Could not import 'evaluate_ease_of_use' from 'judge.py'. Make sure it exists in the same directory.")
    exit(1)

def run_oagi_agent(instruction: str, output_file: str):
    """
    Runs the OAGI agent using the CLI.
    """
    cmd = [
        "oagi", "agent", "run",
        instruction,
        "--model", "lux-actor-1",
        "--export", "markdown",
        "--export-file", output_file
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Run the command and wait for it to finish
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing OAGI agent: {e}")
        raise
    except FileNotFoundError:
        # Fallback for when 'oagi' is not in PATH, try local venv
        venv_cmd = ["./.venv/bin/oagi"] + cmd[1:]
        print(f"Command 'oagi' not found, trying: {' '.join(venv_cmd)}")
        try:
            subprocess.run(venv_cmd, check=True)
        except Exception as e:
            print(f"Failed to run OAGI agent: {e}")
            raise

async def process_test_case(task: str, success_criteria: str, index: int):
    """
    Process a single test case: run agent, get logs, evaluate.
    """

    print(f"\n=== Processing Test Case {index} ===")
    print(f"Task: {task}")
    
    # Construct the instruction string
    instruction = f"Task: {task}\n\nSuccess Criteria: {success_criteria}"
    
    log_filename = f"execution_log_{index + 1}.md"
    
    # 1. Run the agent via CLI
    print("Step 1: Running Agent...")
    try:
        run_oagi_agent(instruction, log_filename)
    except Exception:
        print("Skipping evaluation due to execution failure.")
        return

    # 2. Read the log file
    print(f"Step 2: Reading log file '{log_filename}'...")
    if not os.path.exists(log_filename):
        print(f"Error: Log file {log_filename} was not created.")
        return
        
    with open(log_filename, "r") as f:
        log_content = f.read()

    # 3. Evaluate ease of use
    print("Step 3: Evaluating Ease of Use...")
    try:
        evaluation = await evaluate_ease_of_use(log_content)
        print("\n--- Evaluation Result ---")
        print(f"Summary: {evaluation.summary}")
        print(f"Ease Score: {evaluation.ease_score}/10")
        print(f"Justification: {evaluation.justification}")
        print("-------------------------")
    except Exception as e:
        print(f"Error during evaluation: {e}")

async def main():
    dotenv.load_dotenv()
    
    parser = argparse.ArgumentParser(description="Run manual tests from YAML.")
    parser.add_argument("--file", "-f", type=str, default="test_cases.yaml", help="Path to YAML test cases file")
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: Test file '{args.file}' not found.")
        return

    print(f"Loading test cases from {args.file}...")
    with open(args.file, "r") as f:
        try:
            test_cases = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            return
            
    if not isinstance(test_cases, list):
        print("Error: YAML file must contain a list of test cases.")
        return

    for i, test_case in enumerate(test_cases):
        await process_test_case(test_case, i)

if __name__ == "__main__":
    asyncio.run(main())
