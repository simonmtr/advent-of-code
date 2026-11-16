"""Checks part1/part2 on example.txt. A test skips until its expected value is filled in."""

import importlib.util
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

EXPECTED_PART1: int | str | None = None
EXPECTED_PART2: int | str | None = None

DAY_DIRECTORY = Path(__file__).parent


def load_solution_module() -> ModuleType:
    # Loaded by path under a unique name, so the solution.py files of different days never collide.
    solution_path = DAY_DIRECTORY / 'solution.py'
    module_name = f'aoc_solution_{DAY_DIRECTORY.parent.name}_{DAY_DIRECTORY.name}'
    spec = importlib.util.spec_from_file_location(module_name, solution_path)
    if spec is None or spec.loader is None:
        raise ImportError(f'Cannot load {solution_path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_example_text_or_skip() -> str:
    example_path = DAY_DIRECTORY / 'example.txt'
    if not example_path.is_file() or not example_path.read_text().strip():
        pytest.skip('example.txt is missing or empty')
    return example_path.read_text()


def check_part_on_example(part_name: str, expected_answer: int | str | None) -> None:
    if expected_answer is None:
        pytest.skip(f'expected value for {part_name} not set')
    example_text = read_example_text_or_skip()
    solve_part: Callable[[str], int | str] = getattr(load_solution_module(), part_name)
    assert solve_part(example_text) == expected_answer


def test_part1_on_example() -> None:
    check_part_on_example('part1', EXPECTED_PART1)


def test_part2_on_example() -> None:
    check_part_on_example('part2', EXPECTED_PART2)
