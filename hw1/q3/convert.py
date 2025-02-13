#!/usr/bin/env python3
import argparse
import pickle
import numpy as np
import networkx as nx
from networkx.algorithms import isomorphism


def parse_graphs(file_path):
    """
    Parse graphs from the given file.
    Returns a list of NetworkX graph objects.
    """
    graphs = []
    current_graph = nx.Graph()
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                if current_graph.number_of_nodes() > 0:
                    graphs.append(current_graph)
                    current_graph = nx.Graph()
                continue
            if line.startswith('v'):
                parts = line.split()
                node_id, label = parts[1], parts[2]
                current_graph.add_node(int(node_id), label=label)
            elif line.startswith('e'):
                parts = line.split()
                u, v, label = int(parts[1]), int(parts[2]), parts[3]
                current_graph.add_edge(u, v, label=label)
        if current_graph.number_of_nodes() > 0:
            graphs.append(current_graph)
    return graphs


def check_subgraph_presence(main_graph, subgraph):
    """
    Check if 'subgraph' is isomorphic to any subgraph of 'main_graph'.
    Uses the VF2 algorithm provided by NetworkX.
    Returns True if present, False otherwise.
    """
    gm = isomorphism.GraphMatcher(main_graph, subgraph, node_match=lambda n1, n2: n1['label'] == n2['label'],
                                    edge_match=lambda e1, e2: e1['label'] == e2['label'])
    return gm.subgraph_is_isomorphic()


def generate_feature_vector(graph, discriminative_subgraphs):
    """
    For a given graph, generate a binary feature vector indicating the presence (1) or absence (0)
    of each discriminative subgraph.
    """
    feature_vector = []
    for sg in discriminative_subgraphs:
        present = check_subgraph_presence(graph, sg)
        feature_vector.append(1 if present else 0)
    return feature_vector


def main(args):
    print("Loading discriminative subgraphs...")
    with open(args.subgraphs, 'rb') as f:
        discriminative_subgraphs = pickle.load(f)
    print(f"Loaded {len(discriminative_subgraphs)} subgraphs.")

    print("Parsing input graphs...")
    graphs = parse_graphs(args.graphs)
    print(f"Parsed {len(graphs)} graphs.")

    print("Generating feature vectors...")
    feature_matrix = []
    for idx, graph in enumerate(graphs):
        fv = generate_feature_vector(graph, discriminative_subgraphs)
        feature_matrix.append(fv)
        if idx % 10 == 0:
            print(f"Processed graph {idx+1}/{len(graphs)}")
    
    feature_matrix = np.array(feature_matrix)
    print(f"Feature matrix shape: {feature_matrix.shape}")

    # Save the feature matrix as a .npy file.
    np.save(args.output, feature_matrix)
    print(f"Feature matrix saved to {args.output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Graph to Feature Vector Converter")
    parser.add_argument("--graphs", type=str, required=True, help="Path to the graphs file (training or test)")
    parser.add_argument("--subgraphs", type=str, default="subgraphs.pkl", help="Path to the discriminative subgraphs file")
    parser.add_argument("--output", type=str, default="features.npy", help="Output file for the feature matrix (NumPy array)")
    args = parser.parse_args()
    main(args)
