import argparse
import asyncio
from pathlib import Path

import dotenv
import yaml
from pydantic import BaseModel, Field, TypeAdapter


import manual_tester


class TestCase(BaseModel):
    """Description of a test case as specified in YAML."""

    task_statement: str = Field(description="What the agent should attempt to do.")
    success_criteria: str = Field(description="What makes the agent's task successful.")


def parse_test_cases(yaml_path: Path) -> list[TestCase]:
    """Parse an array of TestCase objects from a YAML file."""
    try:
        with open(yaml_path) as f:
            content = f.read()
    except FileNotFoundError:
        raise SystemExit(f"Error: File not found: {yaml_path}")
    except PermissionError:
        raise SystemExit(f"Error: Permission denied reading file: {yaml_path}")
    except OSError as e:
        raise SystemExit(f"Error: Failed to read file '{yaml_path}': {e}")

    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise SystemExit(f"Error: Invalid YAML in '{yaml_path}': {e}")

    if data is None:
        raise SystemExit(f"Error: YAML file '{yaml_path}' is empty")

    try:
        adapter = TypeAdapter(list[TestCase])
        return adapter.validate_python(data)
    except Exception as e:
        raise SystemExit(f"Error: Invalid test case format in '{yaml_path}': {e}")


async def main():
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(description="Run test cases from a YAML file.")
    parser.add_argument("yaml_file", type=Path, help="Path to the YAML file containing test cases.")
    args = parser.parse_args()

    test_cases = parse_test_cases(args.yaml_file)
    print(f"Loaded {len(test_cases)} test cases")
    
    results = []
    for i, tc in enumerate(test_cases, 1):
        print(f"  {i}. {tc.task_statement[:50]}...")
        result = await manual_tester.process_test_case(tc.task_statement, tc.success_criteria, i)
        results.append(result)
    
    manual_tester.print_summary(results)


if __name__ == "__main__":
    asyncio.run(main())
