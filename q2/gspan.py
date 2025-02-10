
import sys
import subprocess
import time
import os
import multiprocessing
import matplotlib.pyplot as plt

def convert_dataset(dataset_path, output_path):
    """Converts dataset format using convert_format.py (done only once)."""
    global converted_dataset
    converted_dataset = os.path.join(output_path, "converted_dataset.txt")
    convert_script = os.path.join(os.path.dirname(__file__), "convert_format.py")

    # Print command
    command = ["python3", convert_script, dataset_path, converted_dataset]
    print("Executing:", " ".join(command))
    
    subprocess.run(command, check=True)
    print("✅ Dataset converted successfully.")

def run_algorithm(executable, min_sup, output_path, result_dict, algorithm_name):
    """Runs a given algorithm for a specific min_sup and stores execution time."""
    output_file = os.path.join(output_path, f"{algorithm_name.lower()}{min_sup}")

    if algorithm_name == "Gaston":
        command = [executable, str(min_sup), converted_dataset]
    elif algorithm_name == "gSpan":
        command = [executable, "-f", converted_dataset, "-s", str(min_sup/100)]
    else:  # FSG
        command = [executable, "-s", str(min_sup / 100), converted_dataset]

    print(f"Executing: {' '.join(command)}")

    start_time = time.time()
    try:
        with open(output_file, "w") as outfile:
            subprocess.run(command, stdout=outfile, stderr=subprocess.PIPE, check=True)
        print(f"✅ Finished {algorithm_name} for min_sup={min_sup}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {algorithm_name} failed for min_sup={min_sup} with exit code {e.returncode}")
        print("STDERR Output:\n", e.stderr.decode())
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    end_time = time.time()

    execution_time = end_time - start_time

    # Update shared dictionary safely
    result_dict[min_sup] = execution_time
    print(f"✅ {algorithm_name} min_sup={min_sup} -> {execution_time:.6f} sec (Stored in Shared Dict)")

def execute_algorithm(executable, output_path, algorithm_name, result_dict):
    """Runs Gaston, gSpan, or FSG in parallel for different min_support values using a shared dictionary."""
    min_sups = [95, 50, 25, 10, 5]
    num_cores = max(1, multiprocessing.cpu_count())  # Limit CPU usage

    processes = []

    for min_sup in min_sups:
        p = multiprocessing.Process(target=run_algorithm, args=(executable, min_sup, output_path, result_dict, algorithm_name))
        processes.append(p)
        p.start()

        if len(processes) >= num_cores:
            for p in processes:
                p.join()
            processes.clear()

    for p in processes:
        p.join()

def plot_results(output_path, gaston_runtimes, gspan_runtimes, fsg_runtimes):
    """Generates and saves the runtime comparison plot."""
    min_sups = [95, 50, 25, 10, 5]

    gaston_values = [gaston_runtimes.get(ms, 0) * 100 for ms in min_sups]
    gspan_values = [gspan_runtimes.get(ms, 0) * 100 for ms in min_sups]
    fsg_values = [fsg_runtimes.get(ms, 0) * 100 for ms in min_sups]

    print("\n--- Extracted Runtime Values (Scaled) ---")
    print("Gaston:", gaston_values)
    print("gSpan:", gspan_values)
    print("FSG:", fsg_values)
    print("-----------------------------------------\n")

    if max(gaston_values + gspan_values + fsg_values) == 0:
        print("❌ Error: No valid runtime data available for plotting.")
        return

    plt.figure(figsize=(10, 6))

    plt.plot(min_sups, gaston_values, marker='s', linestyle='-', label='Gaston', linewidth=2)
    plt.plot(min_sups, gspan_values, marker='s', linestyle='-', label='gSpan', linewidth=2)
    plt.plot(min_sups, fsg_values, marker='s', linestyle='-', label='FSG', linewidth=2)

    plt.xlabel("Minimum Support (%)", fontsize=12)
    plt.ylabel("Runtime (seconds) × 100", fontsize=12)
    plt.title("Runtime of Gaston, gSpan, and FSG vs Minimum Support", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle="--", linewidth=0.5)

    plt.ylim(0, max(gaston_values + gspan_values + fsg_values) * 1.2)

    plot_path = os.path.join(output_path, "plot.png")
    plt.savefig(plot_path, dpi=300)
    print(f"✅ Plot saved successfully at: {plot_path}")

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python script.py <path_gspan_executable> <path_fsg_executable> <path_gaston_executable> <path_dataset> <path_out>")
        sys.exit(1)

    gspan_exec = sys.argv[1]
    fsg_exec = sys.argv[2]
    gaston_exec = sys.argv[3]
    dataset_path = sys.argv[4]
    output_path = sys.argv[5]

    os.makedirs(output_path, exist_ok=True)

    convert_dataset(dataset_path, output_path)

    with multiprocessing.Manager() as manager:
        gaston_runtimes = manager.dict()
        gspan_runtimes = manager.dict()
        fsg_runtimes = manager.dict()

        gaston_process = multiprocessing.Process(target=execute_algorithm, args=(gaston_exec, output_path, "Gaston", gaston_runtimes))
        gspan_process = multiprocessing.Process(target=execute_algorithm, args=(gspan_exec, output_path, "gSpan", gspan_runtimes))
        fsg_process = multiprocessing.Process(target=execute_algorithm, args=(fsg_exec, output_path, "FSG", fsg_runtimes))

        gaston_process.start()
        gaston_process.join()

        fsg_process.start()
        fsg_process.join()

        gspan_process.start()
        gspan_process.join()


        print("\n--- Stored Execution Times ---")
        print("Gaston Runtimes:", dict(gaston_runtimes))
        print("gSpan Runtimes:", dict(gspan_runtimes))
        print("FSG Runtimes:", dict(fsg_runtimes))
        print("--------------------------------\n")


        plot_results(output_path, gaston_runtimes, gspan_runtimes, fsg_runtimes)