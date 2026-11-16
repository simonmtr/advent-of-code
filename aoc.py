"""Helper CLI for Advent of Code: create a day from the template, fetch its input, run and test it.

Usage:
    python aoc.py new YEAR DAY
    python aoc.py fetch YEAR DAY
    python aoc.py run YEAR DAY [--example]
    python aoc.py test YEAR DAY
"""

import argparse
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_DIRECTORY = Path(__file__).resolve().parent
TEMPLATE_DIRECTORY = REPO_DIRECTORY / 'template'
TEMPLATE_FILE_NAMES = ('solution.py', 'test_solution.py')
SESSION_FILE_PATH = Path.home() / '.config' / 'advent-of-code' / 'session'
SESSION_ENVIRONMENT_VARIABLE = 'AOC_SESSION'
USER_AGENT = 'github.com/simonmtr/advent-of-code by 12691887+simonmtr@users.noreply.github.com'
PUZZLE_UNLOCK_TIME_ZONE = ZoneInfo('America/New_York')
FIRST_YEAR = 2015
FIRST_YEAR_WITH_TWELVE_DAYS = 2025
REQUEST_TIMEOUT_SECONDS = 30


class AocError(Exception):
    """An error with a message meant for the user; printed without a traceback."""


@dataclass(frozen=True)
class PuzzleDay:
    year: int
    day: int

    def __post_init__(self) -> None:
        if self.year < FIRST_YEAR:
            raise AocError(f'Advent of Code starts in {FIRST_YEAR}, got year {self.year}.')
        last_day = 12 if self.year >= FIRST_YEAR_WITH_TWELVE_DAYS else 25
        if not 1 <= self.day <= last_day:
            raise AocError(f'Day must be between 1 and {last_day} for {self.year}, got {self.day}.')

    @property
    def directory(self) -> Path:
        return REPO_DIRECTORY / str(self.year) / f'day{self.day:02d}'

    @property
    def input_url(self) -> str:
        return f'https://adventofcode.com/{self.year}/day/{self.day}/input'

    @property
    def unlock_time(self) -> datetime:
        return datetime(self.year, 12, self.day, tzinfo=PUZZLE_UNLOCK_TIME_ZONE)

    def is_unlocked(self) -> bool:
        return datetime.now(UTC) >= self.unlock_time


def read_session_cookie() -> str:
    session_cookie = os.environ.get(SESSION_ENVIRONMENT_VARIABLE, '').strip()
    if not session_cookie and SESSION_FILE_PATH.is_file():
        session_cookie = SESSION_FILE_PATH.read_text().strip()
    if not session_cookie:
        raise AocError(
            'No session cookie found.\n'
            f'Set the {SESSION_ENVIRONMENT_VARIABLE} environment variable, or put the cookie in '
            f'{SESSION_FILE_PATH}.\n'
            'To get it: log in at https://adventofcode.com, open the browser dev tools, and copy '
            'the value of the "session" cookie (Application/Storage tab, Cookies).'
        )
    return session_cookie


def download_input_text(puzzle_day: PuzzleDay, session_cookie: str) -> str:
    request = urllib.request.Request(
        puzzle_day.input_url,
        headers={'Cookie': f'session={session_cookie}', 'User-Agent': USER_AGENT},
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.read().decode()
    except urllib.error.HTTPError as error:
        if error.code in (400, 404):
            raise AocError(
                f'Advent of Code answered {error.code} for {puzzle_day.input_url}: the session '
                'cookie is wrong or expired, or the puzzle is not unlocked yet.'
            ) from error
        raise AocError(
            f'Advent of Code answered {error.code} {error.reason} for {puzzle_day.input_url}.'
        ) from error
    except urllib.error.URLError as error:
        raise AocError(f'Network error while fetching the input: {error.reason}') from error
    except TimeoutError as error:
        raise AocError(
            f'Timed out after {REQUEST_TIMEOUT_SECONDS} s fetching the input.'
        ) from error


def fetch_input(puzzle_day: PuzzleDay) -> None:
    input_path = puzzle_day.directory / 'input.txt'
    if input_path.exists():
        print(f'{input_path.relative_to(REPO_DIRECTORY)} already exists, not fetching it again.')
        return
    if not puzzle_day.is_unlocked():
        unlock_time_local = puzzle_day.unlock_time.astimezone()
        raise AocError(
            f'{puzzle_day.year} day {puzzle_day.day} unlocks at '
            f'{unlock_time_local:%Y-%m-%d %H:%M %Z} (midnight US Eastern). Not fetching yet.'
        )
    session_cookie = read_session_cookie()
    input_text = download_input_text(puzzle_day, session_cookie)
    puzzle_day.directory.mkdir(parents=True, exist_ok=True)
    temporary_path = input_path.with_name('input.txt.part')
    temporary_path.write_text(input_text)
    temporary_path.replace(input_path)
    print(f'Saved input to {input_path.relative_to(REPO_DIRECTORY)}.')


def create_day_from_template(puzzle_day: PuzzleDay) -> None:
    if puzzle_day.directory.exists():
        raise AocError(f'{puzzle_day.directory.relative_to(REPO_DIRECTORY)} already exists.')
    puzzle_day.directory.mkdir(parents=True)
    for file_name in TEMPLATE_FILE_NAMES:
        shutil.copyfile(TEMPLATE_DIRECTORY / file_name, puzzle_day.directory / file_name)
    (puzzle_day.directory / 'example.txt').touch()
    print(f'Created {puzzle_day.directory.relative_to(REPO_DIRECTORY)}.')
    if puzzle_day.is_unlocked():
        fetch_input(puzzle_day)
    else:
        print('Puzzle not unlocked yet; run `fetch` once it is.')


def require_day_directory(puzzle_day: PuzzleDay) -> Path:
    if not puzzle_day.directory.is_dir():
        raise AocError(
            f'{puzzle_day.directory.relative_to(REPO_DIRECTORY)} does not exist; '
            f'run `python aoc.py new {puzzle_day.year} {puzzle_day.day}` first.'
        )
    return puzzle_day.directory


def run_solution(puzzle_day: PuzzleDay, use_example: bool) -> int:
    day_directory = require_day_directory(puzzle_day)
    input_path = day_directory / ('example.txt' if use_example else 'input.txt')
    command = [sys.executable, str(day_directory / 'solution.py'), str(input_path)]
    return subprocess.run(command, check=False).returncode


def run_tests(puzzle_day: PuzzleDay) -> int:
    day_directory = require_day_directory(puzzle_day)
    command = [sys.executable, '-m', 'pytest', '-rs', str(day_directory)]
    return subprocess.run(command, cwd=REPO_DIRECTORY, check=False).returncode


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Advent of Code helper.')
    subparsers = parser.add_subparsers(dest='command', required=True)
    for command, help_text in (
        ('new', 'create YEAR/dayDD from the template, then fetch the input if unlocked'),
        ('fetch', 'download the input to YEAR/dayDD/input.txt'),
        ('run', "run the day's solution"),
        ('test', "run pytest on the day's folder"),
    ):
        subparser = subparsers.add_parser(command, help=help_text)
        subparser.add_argument('year', type=int)
        subparser.add_argument('day', type=int)
        if command == 'run':
            subparser.add_argument(
                '--example', action='store_true', help='use example.txt instead of input.txt'
            )
    return parser


def main() -> None:
    arguments = build_argument_parser().parse_args()
    try:
        puzzle_day = PuzzleDay(arguments.year, arguments.day)
        match arguments.command:
            case 'new':
                create_day_from_template(puzzle_day)
            case 'fetch':
                fetch_input(puzzle_day)
            case 'run':
                sys.exit(run_solution(puzzle_day, arguments.example))
            case 'test':
                sys.exit(run_tests(puzzle_day))
            case _:
                raise AssertionError(f'Unhandled command: {arguments.command}')
    except AocError as error:
        sys.exit(f'Error: {error}')


if __name__ == '__main__':
    main()
