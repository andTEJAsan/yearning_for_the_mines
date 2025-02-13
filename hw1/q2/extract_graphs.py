
import sys
import re

def extract_graphs(input_file, output_file, num_graphs):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        lines = infile.readlines()
        index = 0
        count = -1

        while index < len(lines) and count < num_graphs:
            # Identify start of a graph
            if lines[index].startswith('#'):
                count += 1
                if count >= num_graphs:
                    break
            outfile.write(lines[index])
            index += 1
    
    print(f"Successfully written {count} graphs to {output_file}.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python extract_graphs.py <input_file> <output_file> <num_graphs>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    num_graphs = int(sys.argv[3])
    
    extract_graphs(input_file, output_file, num_graphs)