#!/bin/bash

# Arguments
APR_EXEC=$1  # Path to Apriori executable
FP_EXEC=$2   # Path to FP-tree executable
DATASET=$3   # Path to dataset
OUT_DIR=$4   # Output directory

chmod +x "$APR_EXEC"
chmod +x "$FP_EXEC"
# Ensure output directory exists
mkdir -p "$OUT_DIR"

# Support thresholds
THRESHOLDS=(90 50 25 10 5)

# Runtime log file
RUNTIME_LOG="$OUT_DIR/runtime.log"
> "$RUNTIME_LOG"  # Clear previous log

# Run Apriori and FP-tree for each support threshold
# Run Apriori and FP-tree for each support threshold in parallel
for S in "${THRESHOLDS[@]}"; do

    echo "Running FP-tree with support $S%..."
    touch "$OUT_DIR/fp$S"
    FP_TIME=$(timeout 3600 /usr/bin/time -f "%e" "$FP_EXEC" -s$S -v"%a %S" "$DATASET" "$OUT_DIR/fp$S" 2>&1 | tail -n 1)

    # Check if timeout occurred
    if [ $? -eq 124 ]; then
        echo "fp$S TIMEOUT" >> "$RUNTIME_LOG"
    else
        echo "fp$S $FP_TIME" >> "$RUNTIME_LOG"
    fi
    
    echo "Running Apriori with support $S%..."
    touch "$OUT_DIR/ap$S"
    APR_TIME=$(timeout 3600 /usr/bin/time -f "%e" "$APR_EXEC" -s$S -v"%a %S" "$DATASET" "$OUT_DIR/ap$S" 2>&1 | tail -n 1)
    
    # Check if timeout occurred
    if [ $? -eq 124 ]; then
        echo "ap$S TIMEOUT" >> "$RUNTIME_LOG"
    else
        echo "ap$S $APR_TIME" >> "$RUNTIME_LOG"
    fi
done


# Wait for all background processes to finish

# Plot results using Python
python3 plot.py "$OUT_DIR/runtime.log"

