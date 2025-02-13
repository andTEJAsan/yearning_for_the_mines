def check_gaston_format(file_path):
    with open(file_path, 'r') as file:
        vertices = set()
        line_number = 0
        for line in file:
            line_number += 1
            parts = line.strip().split()
            if not parts:
                continue

            if parts[0] == 't':  # Graph transaction
                if len(parts) != 3 or parts[1] != '#' or not parts[2].isdigit():
                    print(f"❌ [Line {line_number}] Invalid graph transaction format: {line.strip()}")
                vertices.clear()

            elif parts[0] == 'v':  # Vertex definition
                if len(parts) != 3 or not parts[1].isdigit():
                    print(f"❌ [Line {line_number}] Invalid vertex format: {line.strip()}")
                else:
                    vertices.add(parts[1])

            elif parts[0] == 'e':  # Edge definition
                if len(parts) != 4 or not (parts[1] in vertices and parts[2] in vertices):
                    print(f"❌ [Line {line_number}] Edge references unknown vertex: {line.strip()}")

            else:
                print(f"❌ [Line {line_number}] Unrecognized line format: {line.strip()}")

    print("✅ Validation complete!")

# Run it with:
check_gaston_format("tiny_test.txt")