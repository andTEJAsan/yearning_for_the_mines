#!/bin/bash

# Ensure correct number of arguments
if [ "$#" -ne 5 ]; then
    echo "Usage: bash q2.sh <path_gspan_executable> <path_fsg_executable> <path_gaston_executable> <path_dataset> <path_out>"
    exit 1
fi

# Assign input arguments
GSPAN_EXEC="$1"
FSG_EXEC="$2"
GASTON_EXEC="$3"
DATASET_PATH="$4"
OUTPUT_PATH="$5"

# Print the received arguments for debugging
echo "Running gspan.py with the following arguments:"
echo "  GSpan Executable: $GSPAN_EXEC"
echo "  FSG Executable:   $FSG_EXEC"
echo "  Gaston Executable: $GASTON_EXEC"
echo "  Dataset Path: $DATASET_PATH"
echo "  Output Path: $OUTPUT_PATH"

# Run the Python script
python3 gspan.py "$GSPAN_EXEC" "$FSG_EXEC" "$GASTON_EXEC" "$DATASET_PATH" "$OUTPUT_PATH"

# Print completion message
echo "✅ gspan.py execution completed."