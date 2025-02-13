import argparse
from sklearn.model_selection import train_test_split
from identify import parse_graphs, load_labels
import subprocess


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="Path to the data file.")
    parser.add_argument("--labels", type=str, required=True, help="Path to the labels file.")

    args = parser.parse_args()
    DATA_PATH = args.data
    LABELS_PATH = args.labels

    # Load the data and labels
    data = parse_graphs(DATA_PATH)
    labels = load_labels(LABELS_PATH)

    # Split the data into training and testing sets
    data_train, data_test, labels_train, labels_test = train_test_split(data, labels, test_size=0.2, random_state=0)

    # Save train
    f = 'train.txt'
    with open(f, 'w') as f:
        for g in data_train:
            f.write("#\n")
            # g = nx.graph.Graph(g)
            for node in g.nodes:
                f.write(f"v {node} {g.nodes[node]['label']}\n")
            for edge in g.edges:
                f.write(f"e {edge[0]} {edge[1]} {g.edges[edge]['label']}\n")
    print(f"Train data saved to {f}")
    
    f = 'train_labels.txt'
    with open(f, 'w') as f:
        for l in labels_train:
            f.write(f"{l}\n")
    print(f"Train labels saved to {f}")

    # Save test
    f = 'test.txt'
    with open(f, 'w') as f:
        for g in data_test:
            f.write("#\n")
            # g = nx.graph.Graph(g)
            for node in g.nodes:
                f.write(f"v {node} {g.nodes[node]['label']}\n")
            for edge in g.edges:
                f.write(f"e {edge[0]} {edge[1]} {g.edges[edge]['label']}\n")
    print(f"Test data saved to {f}")

    f = 'test_labels.txt'
    with open(f, 'w') as f:
        for l in labels_test:
            f.write(f"{l}\n")
    
    print(f"Test labels saved to {f}")
    
    command = [
        "python3", "identify.py",
        "--graphs", "./train.txt",
        "--labels", "./train_labels.txt",   
    ]
    subprocess.run(command)

    command = [
        "python3", "convert.py",
        "--graphs", "./train.txt",
        "--output", "./train_features.npy",
    ]
    subprocess.run(command)

    command = [
        "python3", "convert.py",
        "--graphs", "./test.txt",
        "--output", "./test_features.npy",
    ]
    subprocess.run(command)

    command = [
        "python3", "classify.py",
        "--ftrain", "./train_features.npy",
        "--ftest", "./test_features.npy",
        "--ltrain", "./train_labels.txt",
        "--ltest", "./test_labels.txt",
        "--proba", "./proba.npy",
    ]
    subprocess.run(command)
