"""Advent of Code solution. Run: python solution.py [INPUT_PATH] (defaults to input.txt here)."""

import sys
import time
from collections.abc import Callable
from pathlib import Path


def parse(text: str) -> list[str]:
    return text.splitlines()


def part1(text: str) -> int | str:
    raise NotImplementedError


def part2(text: str) -> int | str:
    raise NotImplementedError


def print_part_answer_with_run_time(
    label: str, solve_part: Callable[[str], int | str], text: str
) -> None:
    start_seconds = time.perf_counter()
    try:
        answer = solve_part(text)
    except NotImplementedError:
        print(f'{label}: not solved yet')
        return
    elapsed_milliseconds = (time.perf_counter() - start_seconds) * 1000
    print(f'{label}: {answer}  ({elapsed_milliseconds:.1f} ms)')


def main() -> None:
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('input.txt')
    if not input_path.is_file():
        sys.exit(f'Input file not found: {input_path}')
    text = input_path.read_text()
    print_part_answer_with_run_time('Part 1', part1, text)
    print_part_answer_with_run_time('Part 2', part2, text)


if __name__ == '__main__':
    main()
