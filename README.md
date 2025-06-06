# Zarr to HDF5 Converter

This repository contains tools for converting Zarr format files to HDF5 format, with a focus on handling large multidimensional image data using distributed processing with Dask.

## Overview

The converter efficiently transforms hierarchical data stored in Zarr format to HDF5 format, maintaining the nested group structure while leveraging Dask for parallel processing. This is particularly useful for scientific imaging data that needs to be converted between these two formats.

## Features

- Parallel conversion using Dask distributed computing
- Preserves hierarchical structure (groups and arrays)
- Configurable compression for output HDF5 files
- Chunked data handling for large datasets
- Support for local processing

## Requirements

- Python 3.12+
- Dependencies listed in pyproject.toml, including:
  - dask and related packages
  - zarr
  - h5py
  - numpy

## Getting Started

1. Clone the repository
2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## Usage

### Local Notebook Pipeline

The repository includes a Jupyter notebook (local_pipeline.ipynb) that demonstrates converting Zarr data to HDF5 format:

1. Place your Zarr data in fused.zarr
2. Run the notebook to convert data to HDF5 (outputs to `local_testing/output/output.h5`)

Example usage from the notebook:

```python
import dask.array as da
import h5py
from dask.distributed import Client, LocalCluster
import zarr
import time

# Setup Dask cluster
cluster = LocalCluster(n_workers=2, threads_per_worker=2, memory_limit="8GB")
client = Client(cluster)

# Open Zarr data and define output path
zarr_group = zarr.open("local_testing/data/fused.zarr", mode="r")
output_path = "local_testing/output/output.h5"

# Convert from Zarr to HDF5
with h5py.File(output_path, "w") as h5f:
    for group_name in zarr_group.group_keys():
        subgroup = zarr_group[group_name]
        h5_subgroup = h5f.create_group(group_name)
        for array_name in subgroup.array_keys():
            z = subgroup[array_name]
            dask_arr = da.from_zarr(z)
            h5_subgroup.create_dataset(
                array_name,
                data=dask_arr,
                shape=dask_arr.shape,
                dtype=dask_arr.dtype,
                chunks=True,
                compression="gzip"
            )
```

### Local Script Pipeline

The repository includes a python script (main.py) that converts Zarr data to HDF5 format:

1. Place your Zarr data in fused.zarr 
2. Give command line inputs in this format:
  - `uv run <path/to/main.py> -i <path/to/input/data> -o <path/to/output/file> -n <number_of_workers> -t <number_of_threads_per_worker> -m <memory_limit_with_units>`
  - `-n`, `-t`, `-m` are optional and a default of 2 workers, 2 threads per worker and 8GB of memory will be selected otherwise

## Project Structure

```
.
├── local_pipeline.ipynb      # Jupyter notebook with local conversion example
├── local_testing/            # Directory for test data and outputs
│   ├── data/                 # Input Zarr data directory
│   └── output/               # Output HDF5 files directory
├── main.py                   # Main script which converst Zarr to HDF5
├── pyproject.toml            # Project dependencies and configuration
├── README.md                 # This documentation
└── src/                      # Source code directory
```

## License

MIT License

## Acknowledgments

[Add any acknowledgments here]
