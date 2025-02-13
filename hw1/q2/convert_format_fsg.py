import sys

def convert_formatA_to_formatB(formatA_file, formatB_file):
    int_to_str = ['Br', 'C', 'Cl', 'F', 'H', 'I', 'N', 'O', 'P', 'S', 'Si']
    str_to_int = {v: k for k, v in enumerate(int_to_str)}
    
    with open(formatA_file, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    output_lines = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#"):  # Graph ID
            graph_id = lines[i][1:].strip()
            output_lines.append(f"t # {graph_id}")
            i += 1
            
            num_nodes = int(lines[i].strip())
            i += 1
            node_labels = []
            
            for node_id in range(num_nodes):
                label_str = lines[i].strip()
                if label_str not in str_to_int:
                    print(f"Warning: Unrecognized node label '{label_str}' at line {i+1}")
                    label_int = -1  # Assign a default invalid value
                else:
                    label_int = str_to_int[label_str]
                output_lines.append(f"v {node_id} {label_int}")
                node_labels.append(label_int)
                i += 1
            
            num_edges = int(lines[i].strip())
            i += 1
            
            for _ in range(num_edges):
                edge_parts = lines[i].strip().split()
                if len(edge_parts) != 3:
                    print(f"Warning: Skipping invalid edge line '{lines[i]}' at line {i+1}")
                else:
                    src, dest, edge_label = edge_parts
                    output_lines.append(f"u {src} {dest} {edge_label}")
                i += 1
                
    with open(formatB_file, 'w') as f:
        f.write('\n'.join(output_lines).strip())

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_formatA_file> <output_formatB_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_formatA_to_formatB(input_file, output_file)
