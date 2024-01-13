import logging
import psutil
import platform
import GPUtil


# Import logger
log = logging.getLogger(__name__)


def get_system_profile():
    """
    Get system profile
    Returns dictionary with the following keys:
        - os
        - system_name
        - os_release
        - os_version
        - processor_arch
        - processor_type
        - physical_cores
        - logical_cores
    """

    # Platform information
    my_platform = platform.uname()

    # Initialize the output dictionary
    output_dict = dict()

    # Add the os type; Windows or Linux
    output_dict['os'] = my_platform.system

    # Add the system name
    output_dict['system_name'] = my_platform.node

    # Add the release number of the os; 10(Windows) or 5.4.0-72-generic(linux)
    output_dict['os_release'] = my_platform.release

    # Add the version number of the os
    output_dict['os_version'] = my_platform.version

    # Add the processor architecture of the machine; can be AMD64 or x86-64
    output_dict['processor_arch'] = my_platform.machine

    # Add the processor type; Intel64 Family 6 or x86_64
    output_dict['processor_type'] = my_platform.processor

    # Add the number of physical cores
    output_dict['physical_cores'] = psutil.cpu_count(logical=False)

    # Add the number of logical cores
    output_dict['logical_cores'] = psutil.cpu_count(logical=True)

    return output_dict


def get_cpu_stats():
    """
    Get CPU statistics
    Returns dictionary with the following keys:
        - max_cpu_freq_ghz
        - min_cpu_freq_ghz
        - current_cpu_freq_ghz
        - cpu_usage_percent
    """

    # CPU frequencies
    cpufreq = psutil.cpu_freq()

    # Initialize the output dictionary
    output_dict = dict()

    # Add maximum CPU frequency
    output_dict['max_cpu_freq_ghz'] = round(cpufreq.max/1000, 1)

    # Add minimum CPU frequency
    output_dict['min_cpu_freq_ghz'] = round(cpufreq.min/1000, 1)

    # Add current CPU frequency
    output_dict['current_cpu_freq_ghz'] = round(cpufreq.current/1000, 1)

    # Add current CPU usage percentage
    output_dict['cpu_usage_percent'] = round(
        psutil.cpu_percent(interval=1, percpu=False),
        2  # Two digits after the decimal points
    )

    return output_dict


def _convert_memory_size(input_memory, input_unit, output_unit):
    """
    Convert memory size

    Inputs:
        input_memory: The input memory size
        input_unit: The unit of the input memory size
        output_unit: The unit of the desired output memory size.

    Returns:
        Output memory size
    """

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    # Set the base factor
    factor = 1024

    # Get the index of the input unit
    input_unit_index = units.index(input_unit)

    # Get the index of the output unit
    output_unit_index = units.index(output_unit)

    # Get the difference between the two indices
    factor_multiplier = abs(output_unit_index - input_unit_index)

    # Check if the input unit is smaller than the output unit
    if input_unit_index < output_unit_index:
        output_memory = input_memory / (factor**factor_multiplier)
    else:
        output_memory = input_memory * (factor**factor_multiplier)

    return round(output_memory, 2)


def get_ram_stats():
    """
    Get RAM statistics
    Returns dictionary with the following keys:
        - total_ram_gb
        - free_ram_gb
        - free_ram_gb
        - ram_usage_percent
        - total_swap_gb
        - free_swap_gb
        - used_swap_gb
        - swap_usage_percent
    """

    # Get virtual memory information
    virtual_memory = psutil.virtual_memory()

    # Initialize the output dictionary
    output_dict = dict()

    # Add total RAM memory
    output_dict['total_ram_gb'] = round(
        _convert_memory_size(
            input_memory=virtual_memory.total,
            input_unit='B',
            output_unit='GB'
        ),
        2  # Two digits after the decimal points
    )

    # Add available RAM memory
    output_dict['free_ram_gb'] = round(
        _convert_memory_size(
            input_memory=virtual_memory.available,
            input_unit='B',
            output_unit='GB'
        ),
        2  # Two digits after the decimal points
    )

    # Add used RAM memory
    output_dict['used_ram_gb'] = round(
        _convert_memory_size(
            input_memory=virtual_memory.used,
            input_unit='B',
            output_unit='GB'
        ),
        2  # Two di gits after the decimal points
    )

    # Add RAM memory utilization percentage
    output_dict['ram_usage_percent'] = round(
        virtual_memory.percent,
        2  # Two di gits after the decimal points
    )

    # Get swap memory information if exist
    swap_memory = psutil.swap_memory()

    # Add total swap memory
    output_dict['total_swap_gb'] = round(
        _convert_memory_size(
            input_memory=swap_memory.total,
            input_unit='B',
            output_unit='GB'
        ),
        2  # Two digits after the decimal points
    )

    # Add available swap memory
    output_dict['free_swap_gb'] = round(
        _convert_memory_size(
            input_memory=swap_memory.free,
            input_unit='B',
            output_unit='GB'
        ),
        2  # Two digits after the decimal points
    )

    # Add used swap memory
    output_dict['used_swap_gb'] = round(
        _convert_memory_size(
            input_memory=swap_memory.used,
            input_unit='B',
            output_unit='GB'
        ),
        2  # Two di gits after the decimal points
    )

    # Add swap memory utilization percentage
    output_dict['swap_usage_percent'] = round(
        swap_memory.percent,
        2  # Two di gits after the decimal points
    )

    return output_dict


def get_disk_stats():
    """
    Get storage disk statistics
    Returns dictionary with the following keys:
        - partitions_list: Includes a dictionary of each partition with the
            following keys:
                - partition_name
                - partition_mountpoint
                - partition_fstype
                - partition_total_gb
                - partition_used_gb
                - partition_free_gb
                - partition_percentage
        - total_storage_gb
        - used_storage_gb
        - free_storage_gb
        - storage_usage_percent
    """

    # Initialize full disk storage
    total_storage = 0

    # Initialize used disk usage storage
    used_storage = 0

    # Initialize free disk usage storage
    free_storage = 0

    # Initialize the output dictionary
    output_dict = dict()

    # Initialize the partitions list
    partitions_list = []

    # Get partitions data
    partitions = psutil.disk_partitions()

    # Loop over the partitions
    for partition in partitions:

        # Initialize the partition dictionary
        partition_dict = dict()

        # Add the partition name
        partition_dict['partition_name'] = partition.device

        # Add the partition Mountpoint
        partition_dict['partition_mountpoint'] = partition.device

        # Add the partition file system type
        partition_dict['partition_fstype'] = partition.fstype

        # Get the disk usage of the partition
        partition_disk = psutil.disk_usage(partition.mountpoint)

        # Add the partition total size
        total_partition_size = partition_disk.total
        total_storage += total_partition_size
        partition_dict['partition_total_gb'] = round(
            _convert_memory_size(
                input_memory=total_partition_size,
                input_unit='B',
                output_unit='GB'
            ),
            2  # Two di gits after the decimal points
        )

        # Add the partition used size
        used_partition_size = partition_disk.used
        used_storage += used_partition_size
        partition_dict['partition_used_gb'] = round(
            _convert_memory_size(
                input_memory=used_partition_size,
                input_unit='B',
                output_unit='GB'
            ),
            2  # Two di gits after the decimal points
        )

        # Add the partition free size
        free_partition_size = partition_disk.free
        free_storage += free_partition_size
        partition_dict['partition_free_gb'] = round(
            _convert_memory_size(
                input_memory=free_partition_size,
                input_unit='B',
                output_unit='GB'
            ),
            2  # Two di gits after the decimal points
        )

        # Add the partition usage percentage
        partition_dict['partition_percentage'] = partition_disk.percent

        # Add the partition dictionary to the partitions list
        partitions_list.append(partition_dict)

    # Append the partitions list to the output dictionary
    output_dict['partitions_list'] = partitions_list

    # Append the count of partitions to the output dictionary
    output_dict['partitions_count'] = len(partitions_list)

    # Add total storage size in GB
    output_dict['total_storage_gb'] = round(
        _convert_memory_size(
            input_memory=total_storage,
            input_unit='B',
            output_unit='GB'
        ),
        2  # Two di gits after the decimal points
    )

    # Add used storage size in GB
    output_dict['used_storage_gb'] = round(
        _convert_memory_size(
            input_memory=used_storage,
            input_unit='B',
            output_unit='GB'
        ),
        2  # Two di gits after the decimal points
    )

    # Add free storage size in GB
    output_dict['free_storage_gb'] = round(
        _convert_memory_size(
            input_memory=free_storage,
            input_unit='B',
            output_unit='GB'
        ),
        2  # Two di gits after the decimal points
    )

    # Add used storage percentage
    if total_storage != 0:
        output_dict['storage_usage_percent'] = round(
            (used_storage/total_storage)*100,
            2  # Two di gits after the decimal points
        )
    else:
        output_dict['storage_usage_percent'] = 0

    return output_dict


def get_gpu_stats():
    """
    Get GPU statistics
    Returns dictionary with the following keys:
        - gpus_list: Includes a dictionary of each GPU with the
            following keys:
                - partition_name
                - partition_mountpoint
                - partition_fstype
                - partition_total_gb
                - partition_used_gb
                - partition_free_gb
                - partition_percentage
        - total_storage_gb
        - used_storage_gb
        - free_storage_gb
        - storage_usage_percent
    """

    # Initialize the output dictionary
    output_dict = dict()

    # Initialize total GPUs memeory
    total_gpu_memory = 0

    # Initialize used GPUs memeory
    used_gpu_memory = 0

    # Initialize free GPUs memeory
    free_gpu_memory = 0

    # Initialize max GPU temperature
    max_gpu_temperature = 0

    # Initialize GPUs count
    gpus_count = 0

    gpus = GPUtil.getGPUs()

    gpus_list = []

    # Loop over the available GPUs
    for gpu in gpus:

        gpu_dict = dict()

        # Add GPU name
        gpu_dict['name'] = gpu.name

        # Add GPU ID
        gpu_dict['id'] = gpu.id

        # Add GPU total memory
        total_gpu_memory += gpu.memoryTotal
        gpu_dict['total_memory_gb'] = round(
            _convert_memory_size(
                input_memory=gpu.memoryTotal,
                input_unit='MB',
                output_unit='GB'
            ),
            2  # Two di gits after the decimal points
        )

        # Add GPU used memory
        used_gpu_memory += gpu.memoryUsed  # MB
        gpu_dict['used_memory_gb'] = round(
            _convert_memory_size(
                input_memory=gpu.memoryUsed,
                input_unit='MB',
                output_unit='GB'
            ),
            2  # Two di gits after the decimal points
        )

        # Add GPU free memory
        free_gpu_memory += gpu.memoryFree  # MB
        gpu_dict['free_memory_gb'] = round(
            _convert_memory_size(
                input_memory=gpu.memoryFree,
                input_unit='MB',
                output_unit='GB'
            ),
            2  # Two di gits after the decimal points
        )

        # Add GPU usage percentage
        gpu_dict['usage_percentage'] = gpu.memoryUtil * 100

        # Add GPU temperature
        gpu_dict['temperature'] = gpu.temperature  # C degrees
        if float(gpu_dict['temperature']) > float(max_gpu_temperature):
            max_gpu_temperature = gpu_dict['temperature']

        # Add current GPU dictionary to the GPUs list
        gpus_list.append(gpu_dict)

    # Add GPUs list to the output dict
    output_dict['gpus_list'] = gpus_list

    # Append the count of GPUs to the output dictionary
    output_dict['gpus_count'] = len(gpus_list)

    # Append the max temperature of all GPUs to the output dictionary
    output_dict['gpu_temperature'] = max_gpu_temperature

    # Add total GPU memory
    output_dict['total_gpu_gb'] = round(
        _convert_memory_size(
            input_memory=total_gpu_memory,
            input_unit='MB',
            output_unit='GB'
        ),
        2  # Two di gits after the decimal points
    )

    # Add total used GPU memory
    output_dict['total_used_gpu_gb'] = round(
        _convert_memory_size(
            input_memory=used_gpu_memory,
            input_unit='MB',
            output_unit='GB'
        ),
        2  # Two di gits after the decimal points
    )

    # Add total free GPU memory
    output_dict['total_free_gpu_gb'] = round(
        _convert_memory_size(
            input_memory=free_gpu_memory,
            input_unit='MB',
            output_unit='GB'
        ),
        2  # Two di gits after the decimal points
    )

    # Add total GPU usage percentage
    if total_gpu_memory != 0:
        output_dict['gpu_usage_percentage'] = round(
            (used_gpu_memory/total_gpu_memory)*100,
            2
        )
    else:
        output_dict['gpu_usage_percentage'] = 0

    return output_dict


if __name__ == '__main__':

    # Get system profile
    system_profile_dict = get_system_profile()
    print(system_profile_dict)

    # Get CPU stats
    cpu_stats_dict = get_cpu_stats()
    print(cpu_stats_dict)

    # Get RAM stats
    ram_stats_dict = get_ram_stats()
    print(ram_stats_dict)

    # Get storage disk stats
    disk_stats_dict = get_disk_stats()
    print(disk_stats_dict)

    # Get GPU stats
    gpu_stats_dict = get_gpu_stats()
    print(gpu_stats_dict)
