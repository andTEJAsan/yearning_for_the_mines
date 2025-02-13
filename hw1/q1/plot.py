import sys
import matplotlib.pyplot as plt

def read_times(file_name):
    # Initialize dictionaries to store times
    apriori_times = {}
    fp_times = {}

    # Read the file
    with open(file_name, 'r') as file:
        lines = file.readlines()

    # Process each line
    for line in lines:
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        
        algo_support, time = parts
        time = float(time)

        # Extract algorithm and support value
        algo = algo_support[:2]  # 'ap' or 'fp'
        support = int(algo_support[2:])  # e.g., 90, 50, 25, 10
        
        # Store the time in the corresponding dictionary
        if algo == 'ap':
            apriori_times[support] = time
        elif algo == 'fp':
            fp_times[support] = time

    return apriori_times, fp_times

def plot_times(apriori_times, fp_times):
    # Sort by support
    supports = sorted(list(apriori_times.keys()))

    # Extract times
    apriori_plot = [apriori_times[s] for s in supports]
    fp_plot = [fp_times[s] for s in supports]

    # Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(supports, apriori_plot, marker='o', label='Apriori', color='blue')
    plt.plot(supports, fp_plot, marker='x', label='FP-tree', color='red')
    plt.xlabel('Support (%)')
    plt.ylabel('Time (s)')
    plt.title('Runtime of Apriori vs FP-tree')
    plt.legend()
    plt.grid(True)
    
    # Save the plot to a file
    plt.savefig('plot.png')

    # Display the plot
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python plot_from_times.py <times_file>")
        sys.exit(1)

    times_file = sys.argv[1]
    apriori_times, fp_times = read_times(times_file)
    plot_times(apriori_times, fp_times)
