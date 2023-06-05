import sys
import itertools

if len(sys.argv) != 2:
    print("Usage: {} <number of columns>".format(sys.argv[0]))
    sys.exit(1)

cols = int(sys.argv[1])
rows = [[] for _ in range(cols)]

lines = [line.strip() for line in sys.stdin.readlines()]

print(".. list-table::")
print()

while lines:
    for i in range(cols):
        item = lines.pop(0) if lines else ""
        if(i == 0):
            print("   * - {}".format(item))
        else:
            print("     - {}".format(item))

