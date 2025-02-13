#!/usr/bin/env python3

import argparse
import pickle
import networkx as nx
import gspan_mining.gspan as gspan
from scipy.stats import chi2_contingency
from networkx.algorithms import isomorphism
import numpy as np
from tqdm import tqdm


def parse_graphs(file_path):
    graphs = []
    current_graph = nx.Graph()
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#'):  # New graph indicator
                if current_graph.number_of_nodes() > 0:
                    graphs.append(current_graph)
                    current_graph = nx.Graph()
                continue
            if line.startswith('v'):
                # Format: v node_id label
                parts = line.split()
                node_id, label = parts[1], parts[2]
                current_graph.add_node(int(node_id), label=label)
            elif line.startswith('e'):
                # Format: e node1 node2 label
                parts = line.split()
                u, v, label = int(parts[1]), int(parts[2]), parts[3]
                current_graph.add_edge(u, v, label=label)
        # Append last graph if exists
        if current_graph.number_of_nodes() > 0:
            graphs.append(current_graph)
    return graphs


def gspan_mining(file_path, min_support=2, min_num_vertices=1):
    with open('tmp_graph.txt', 'w') as outfile:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):  # New graph indicator
                    outfile.write('\nt # \n')
                else:
                    outfile.write(line + '\n')

    # Run gSpan
    gs = gspan.gSpan('tmp_graph.txt', min_support,  min_num_vertices, verbose = False)
    gs.run()

    return gs._frequent_subgraphs


def convert_gspan_to_nx(gspan_graph : gspan.Graph):
    graph = nx.Graph()
    gspan_graph = gspan_graph.to_graph()
    for node in gspan_graph.vertices:
        graph.add_node(gspan_graph.vertices[node].vid, label=gspan_graph.vertices[node].vlb)
    for frm in gspan_graph.vertices:
        edges = gspan_graph.vertices[frm].edges
        for to in edges:
            graph.add_edge(frm, to, label=edges[to].elb)
    return graph


def check_subgraph_presence(main_graph, subgraph):
    """
    Check if 'subgraph' is isomorphic to any subgraph of 'main_graph' using VF2.
    """
    gm = isomorphism.GraphMatcher(
        main_graph, subgraph,
        node_match=lambda n1, n2: n1['label'] == n2['label'],
        edge_match=lambda e1, e2: e1['label'] == e2['label']
    )
    return gm.subgraph_is_isomorphic()


def select_discriminative_subgraphs(candidate_subgraphs, graphs, labels, max_features=100):
    chi_scores = []

    for subgraph in tqdm(candidate_subgraphs):
        presence_positive = 0  # Subgraph present in class 1
        absence_positive = 0   # Subgraph absent in class 1
        presence_negative = 0  # Subgraph present in class 0
        absence_negative = 0   # Subgraph absent in class 0

        for i, graph in enumerate(graphs):
            present = check_subgraph_presence(graph, subgraph)
            if labels[i] == 1:
                if present:
                    presence_positive += 1
                else:
                    absence_positive += 1
            elif present:
                presence_negative += 1
            else:
                absence_negative += 1

        # Construct contingency table
        contingency_table = np.array([
            [presence_positive, absence_positive],
            [presence_negative, absence_negative]
        ])

        # Perform Chi-Square test
        chi2, p_value, _, _ = chi2_contingency(contingency_table)

        # Store results
        chi_scores.append((subgraph, chi2))

    # Sort subgraphs by chi-square score (higher is better)
    chi_scores.sort(key=lambda x: x[1], reverse=True)

    # Select top max_features subgraphs
    return [x[0] for x in chi_scores[:max_features]]


def load_labels(label_file):
    labels = []
    with open(label_file, 'r') as f:
        for line in f:
            if line := line.strip():
                labels.append(int(line))
    return labels


def main(args):
    print("Parsing training graphs...")
    graphs = parse_graphs(args.graphs)
    labels = load_labels(args.labels)
    import math
    print("Mining candidate subgraphs using gSpan...")
    candidates = gspan_mining(args.graphs, min_support=math.ceil(0.5*len(labels)), min_num_vertices=2)
    print(f"Found {len(candidates)} candidate subgraphs.")

    print("Converting candidate subgraphs to NetworkX format...")
    nx_candidates = [convert_gspan_to_nx(c) for c in candidates]
    print("Converted candidate subgraphs to NetworkX format.")

    print("Selecting discriminative subgraphs...")
    discriminative_subgraphs = select_discriminative_subgraphs(nx_candidates, graphs, labels, max_features=args.max_features)
    print(f"Selected {len(discriminative_subgraphs)} discriminative subgraphs.")
    

    print("Saving discriminative subgraphs...")
    with open(args.output, 'wb') as f:
        pickle.dump(discriminative_subgraphs, f)
    print(f"Discriminative subgraphs saved to {args.output}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discriminative Subgraph Mining")
    parser.add_argument("--graphs", type=str, required=True, help="Path to the training graphs file")
    parser.add_argument("--labels", type=str, required=True, help="Path to the labels file")
    parser.add_argument("--output", type=str, default="subgraphs.pkl", help="Output file for selected subgraphs")
    parser.add_argument("--max_features", type=int, default=100, help="Maximum number of discriminative subgraphs to select")
    args = parser.parse_args()
    main(args)

