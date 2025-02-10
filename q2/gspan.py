
import sys
import subprocess
import time
import os
import multiprocessing

# Global dictionaries to store execution times
gaston_runtimes = {}
gspan_runtimes = {}

# Global variable for converted dataset path
converted_dataset = ""

def convert_dataset(dataset_path, output_path):
    """Converts dataset format using convert_format.py (done only once)."""
    global converted_dataset
    converted_dataset = os.path.join(output_path, "converted_dataset.txt")
    convert_script = os.path.join(os.path.dirname(__file__), "convert_format.py")

    # Print command
    command = ["python3", convert_script, dataset_path, converted_dataset]
    print("Executing:", " ".join(command))
    
    subprocess.run(command, check=True)
    print("Dataset converted successfully.")

def run_gaston(gaston_exec, min_sup, output_path, result_queue):
    """Runs Gaston for a specific min_sup and stores execution time."""
    gaston_output = os.path.join(output_path, f"gaston{min_sup}")
    command = [gaston_exec, str(min_sup), converted_dataset]

    # Print command
    print("Executing:", " ".join(command))

    start_time = time.time()
    with open(gaston_output, "w") as outfile:
        subprocess.run(command, stdout=outfile, stderr=subprocess.PIPE, check=True)
    end_time = time.time()

    print(f"Finished Gaston for min_sup={min_sup}")
    execution_time = end_time - start_time
    result_queue.put(("Gaston", min_sup, execution_time))  # Send results back to main process

def run_gspan(gspan_exec, min_sup, output_path, result_queue):
    """Runs gSpan for a specific min_sup and stores execution time."""
    gspan_output = os.path.join(output_path, f"gspan{min_sup}")
    min_sup_fraction = min_sup / 100  # Convert percentage to fraction
    command = [gspan_exec, "-f", converted_dataset, "-s", str(min_sup_fraction), "-d 15"]

    # Print command
    print("Executing:", " ".join(command))

    start_time = time.time()
    try:
        with open(gspan_output, "w") as outfile:
            subprocess.run(command, stdout=outfile, stderr=subprocess.PIPE, check=True)
        print(f"Finished gSpan for min_sup={min_sup}")
    except subprocess.CalledProcessError as e:
        print(f"Error: gSpan failed for min_sup={min_sup} with exit code {e.returncode}")
        print("STDERR Output:\n", e.stderr.decode())  # Log full error output
    except Exception as e:
        print(f"Unexpected error: {e}")
    end_time = time.time()

    execution_time = end_time - start_time
    result_queue.put(("gSpan", min_sup, execution_time))  # Send results back to main process

def execute_gaston(gaston_exec, output_path):
    """Runs Gaston in parallel for different min_support values."""
    global gaston_runtimes
    min_sups = [5, 10, 25, 50, 95]
    num_cores = max(1, multiprocessing.cpu_count() // 2)  # Limit CPU usage

    result_queue = multiprocessing.Queue()
    processes = []

    for min_sup in min_sups:
        p = multiprocessing.Process(target=run_gaston, args=(gaston_exec, min_sup, output_path, result_queue))
        processes.append(p)
        p.start()

        if len(processes) >= num_cores:
            for p in processes:
                p.join()
            processes.clear()

    for p in processes:
        p.join()

    while not result_queue.empty():
        _, min_sup, exec_time = result_queue.get()
        gaston_runtimes[min_sup] = exec_time

    print("Execution times for Gaston:", gaston_runtimes)

def execute_gspan(gspan_exec, output_path):
    """Runs gSpan in parallel for different min_support values."""
    global gspan_runtimes
    min_sups = [5, 10, 25, 50, 95]
    num_cores = max(1, multiprocessing.cpu_count() // 2)  # Limit CPU usage

    result_queue = multiprocessing.Queue()
    processes = []

    for min_sup in min_sups:
        p = multiprocessing.Process(target=run_gspan, args=(gspan_exec, min_sup, output_path, result_queue))
        processes.append(p)
        p.start()

        if len(processes) >= num_cores:
            for p in processes:
                p.join()
            processes.clear()

    for p in processes:
        p.join()

    while not result_queue.empty():
        _, min_sup, exec_time = result_queue.get()
        gspan_runtimes[min_sup] = exec_time

    print("Execution times for gSpan:", gspan_runtimes)

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

    # Convert dataset once
    convert_dataset(dataset_path, output_path)

    # Run Gaston in parallel
    # gaston_process = multiprocessing.Process(target=execute_gaston, args=(gaston_exec, output_path))
    # gaston_process.start()
    # gaston_process.join()
    # Run gSpan in parallel
    gspan_process = multiprocessing.Process(target=execute_gspan, args=(gspan_exec, output_path))
    gspan_process.start()

    # Wait for both to finish
    gspan_process.join()