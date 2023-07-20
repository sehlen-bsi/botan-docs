import os
import sys

if len(sys.argv) != 2 or not os.path.isfile(sys.argv[1]):
    print(f"Usage: {sys.argv[0]} <path to .env file>")
    sys.exit(1)

def is_relevant(line: str) -> bool:
    comment = line.startswith("#")
    empty = line.startswith("\n")
    return not comment and not empty

with open(sys.argv[1], encoding='utf-8') as env_file:
    [print(line.strip()) for line in env_file.readlines() if is_relevant(line)]
