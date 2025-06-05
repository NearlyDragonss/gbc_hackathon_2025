# To be completed
import dask.array as da
import h5py
from dask.distributed import Client, LocalCluster
import zarr
import time
import sys, getopt

# inputs
def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "i:o:n::t::m::", ["i_file=", "o_file=", "n_work=", "threads=", "mem_lim="])
        n_workers = 2
        threads_per_worker = 2
        memory_limit = "8GB"
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <input_file> -o <output_file> -n <num_workers> -t <num_threads> -m <memory_limit>')
            sys.exit()
        elif opt in ("-i", "--i_file"):
            input_path = arg
        elif opt in ("-o", "--o_file"):
            output_path = arg
        elif opt in("-n", "--n_work"):
            n_workers = int(arg)
        elif opt in("-t", "--threads"):
            threads_per_worker = int(arg)
        elif opt in("-m", "--mem_lim"):
            memory_limit = arg
    print('Input file is ', input_path)
    print('Output file is ', output_path)

    zarr_group = zarr.open(input_path, mode="r")
    cluster = LocalCluster(n_workers=n_workers, threads_per_worker=threads_per_worker, memory_limit=memory_limit)
    client = Client(cluster)
    cluster.get_client()

    start = time.time()
    with h5py.File(output_path, "w") as h5f:
        print("In file")
        # check if there are group keys
        zarr_group_keys = zarr_group.group_keys()
        print(list(zarr_group_keys))
        if list(zarr_group_keys):
            for group_name in zarr_group_keys:
                print("In first for loop")
                subgroup = zarr_group[group_name]
                h5_subgroup = h5f.create_group(group_name)

                # check if there are array keys
                array_keys = subgroup.array_keys()
                print(list(array_keys))
                if list(array_keys):
                    for array_name in subgroup.array_keys():
                        print("In second for loop")
                        z = subgroup[array_name]
                        print(f"Converting {group_name}/{array_name}")
                        dask_arr = da.from_zarr(z)
                        h5_subgroup.create_dataset(
                            array_name,
                            data=dask_arr,
                            shape=dask_arr.shape,
                            dtype=dask_arr.dtype,
                            chunks=True,
                            compression="gzip",
                        )
                else:
                    print("Array keys are empty")
        else:
            print("Group keys are empty")

    end = time.time()
    print(f"Time taken to write data: {end - start} seconds")

if __name__ == "__main__":
   main(sys.argv[1:])