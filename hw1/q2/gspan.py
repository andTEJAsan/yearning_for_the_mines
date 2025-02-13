import sys
import subprocess
import time
import os
import matplotlib.pyplot as plt
from math import ceil


runtimes = {
    'gaston': {
        95: 0.762342,
        50: 8.355292,
        25: 14.387408,
        10: 45.914243,
        5: 139.708704,
    },
    'gspan': {
        95: 4.404190,
        50: 92.643192,
        25: 252.273981,
        10: 1025.084215,
        5: 2473.581923
    },
    'fsg': {
        95: 19.825265,
        50: 116.981214,
        25: 337.632542,
        10: 1218.239290,
        5: 3572.427569
    }
}
MIN_SUPS = [5]


def convert_dataset(dataset_path, output_path):
    """Converts dataset format using convert_format.py (done only once)."""
    gspan = os.path.join(output_path, "data_gspan")
    convert_script = os.path.join(os.path.dirname(__file__), "convert_format.py")
    command = ["python3", convert_script, dataset_path, gspan]
    subprocess.run(command, check=True)
    
    gaston = os.path.join(output_path, "data_gaston")
    convert_script = os.path.join(os.path.dirname(__file__), "convert_format.py")
    command = ["python3", convert_script, dataset_path, gaston]
    subprocess.run(command, check=True)
    
    fsg = os.path.join(output_path, "data_fsg")
    convert_script = os.path.join(os.path.dirname(__file__), "convert_format_fsg.py")
    command = ["python3", convert_script, dataset_path, fsg]
    subprocess.run(command, check=True)


def run_algorithm(executable, output_path):
    prev_min_sup = -1
    for min_sup in MIN_SUPS:
        for algorithm_name in executable.keys():
            if min_sup == MIN_SUPS[0]:
                converted_dataset = os.path.join(output_path, f"data_{algorithm_name}")
            else:
                converted_dataset = os.path.join(output_path, f"{algorithm_name}{prev_min_sup}")
        
            os.rename(converted_dataset, os.path.join(output_path, f"{algorithm_name}{min_sup}"))
        
            converted_dataset = os.path.join(output_path, f"{algorithm_name}{min_sup}")
            output_file = os.path.join(output_path, f"{algorithm_name.lower()}{min_sup}_stdout")
            
            if algorithm_name == "gaston":
                command = [executable[algorithm_name], str(ceil(641.09*min_sup)), converted_dataset, f"{algorithm_name}{min_sup}"]
            elif algorithm_name == "gspan":
                command = [executable[algorithm_name], "-f", converted_dataset, "-s", str(min_sup/100), "-o"]
            elif algorithm_name == "fsg":
                command = [executable[algorithm_name], "-s", str(min_sup), converted_dataset]
            else:
                continue

            print(f"Executing: {' '.join(command)}")

            start_time = time.time()
            try:
                with open(output_file, "w") as outfile:
                    subprocess.run(command, stdout=outfile, stderr=subprocess.PIPE, check=True, timeout=3600)
                print(f"Finished {algorithm_name} for min_sup={min_sup}")
            except subprocess.CalledProcessError as e:
                print(f"Error: {algorithm_name} failed for min_sup={min_sup} with exit code {e.returncode}")
                print("STDERR Output:\n", e.stderr.decode())
            except subprocess.TimeoutExpired:
                print("Process took too long and was terminated.")
            except Exception as e:
                print(f"Unexpected error: {e}")
            end_time = time.time()

            execution_time = end_time - start_time

            print(f"{algorithm_name} min_sup={min_sup} -> {execution_time:.6f} sec")

            with open(f'time_{algorithm_name}_{min_sup}', 'w') as f:
                f.write(f'{execution_time:.6f} sec')

            runtimes[algorithm_name][min_sup] = execution_time
        prev_min_sup = min_sup


def plot_results(output_path):
    """Generates and saves the runtime comparison plot."""
    min_sups = [95, 50, 25, 10, 5]
    gaston_runtimes = runtimes['gaston']
    gspan_runtimes = runtimes['gspan']
    fsg_runtimes = runtimes['fsg']

    gaston_values = [gaston_runtimes.get(ms, 3600) for ms in min_sups]
    gspan_values = [gspan_runtimes.get(ms, 3600) for ms in min_sups]
    fsg_values = [fsg_runtimes.get(ms, 3600) for ms in min_sups]

    print("\n--- Extracted Runtime Values (Scaled) ---")
    print("Gaston:", gaston_values)
    print("gSpan:", gspan_values)
    print("FSG:", fsg_values)
    print("-----------------------------------------\n")

    if max(gaston_values + gspan_values + fsg_values) == 0:
        print("Error: No valid runtime data available for plotting.")
        return

    plt.figure(figsize=(10, 6))

    plt.plot(min_sups, gaston_values, marker='s', linestyle='-', label='Gaston', linewidth=2)
    plt.plot(min_sups, gspan_values, marker='s', linestyle='-', label='gSpan', linewidth=2)
    plt.plot(min_sups, fsg_values, marker='s', linestyle='-', label='FSG', linewidth=2)

    plt.xlabel("Minimum Support (%)", fontsize=12)
    plt.ylabel("Runtime (seconds)", fontsize=12)
    plt.title("Runtime of Gaston, gSpan, and FSG vs Minimum Support", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle="--", linewidth=0.5)

    plt.ylim(0, max(gaston_values + gspan_values + fsg_values) * 1.2)

    plot_path = os.path.join(output_path, "plot.png")
    plt.savefig(plot_path, dpi=300)
    print(f"Plot saved successfully at: {plot_path}")


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

    run_algorithm({
        # 'gaston': gaston_exec,
        'gspan': gspan_exec,
        # 'fsg': fsg_exec
    },
    output_path)
    
    plot_results(output_path)