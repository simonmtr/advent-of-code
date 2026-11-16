# advent-of-code

My [Advent of Code](https://adventofcode.com) solutions in Python, starting with 2026 (12 puzzles, 1–12 December).

## Setup

- Python 3.12 or newer.
- Dev tools (`pytest`, `ruff`): `uv sync`, or `python -m venv .venv && .venv/bin/pip install --group dev` (pip ≥ 25.1). Then activate the venv (`source .venv/bin/activate`) or prefix commands with `uv run`.
- Session cookie: log in at adventofcode.com, copy the `session` cookie from the browser's dev tools, and put it in `~/.config/advent-of-code/session` (or the `AOC_SESSION` environment variable).
- Enable the pre-commit hook, which blocks committing `input*.txt` and `example*.txt`: `git config core.hooksPath .githooks`.

## Daily use

```sh
python aoc.py new 2026 1     # create 2026/day01 from template/, fetch the input once unlocked
# write part1/part2 in 2026/day01/solution.py; paste the example into example.txt
# and set EXPECTED_PART1/EXPECTED_PART2 in test_solution.py
python aoc.py test 2026 1    # run the tests on the example
python aoc.py run 2026 1     # run on input.txt (--example for example.txt)
```

Puzzles unlock at midnight US Eastern. `python aoc.py fetch 2026 1` downloads an input on its own; it never re-downloads one already on disk. Answers are submitted by hand.

Puzzle inputs and puzzle text are not in this repo, at the request of Advent of Code's author: see https://adventofcode.com.
