import os
import yaml
import json
import traceback
from dotenv import load_dotenv
from packages.file import file
from packages.logger import logger
from packages.system import system
from packages.postgredb import postgredb
from packages.datetimetools import datetimetools


# Initiate logger
log = logger.get(app_name='logs', enable_logs_file=False)

# Load environment variables from the specified file
dotenv_path = '/server-monitor/env_vars.txt'
load_dotenv(dotenv_path)


def main():

    log.info('Start program execution')
    project_abs_path = file.caller_dir_path()

    # Import configurations
    config_path = os.path.join(project_abs_path, 'config.yaml')
    with open(config_path) as config_file:
        config = yaml.safe_load(config_file)
    # Create a database instance
    db = postgredb.PostgreSQLDB(
        host = os.getenv('DB_HOSTNAME'),
        db_name = os.getenv('DB_NAME'),
        username = os.getenv('DB_USERNAME'),
        password = os.getenv('DB_PASSWORD')
    )

    log.info('start creating database\'s tables')

    # Create all tables if not already exist
    # Loop over all queries paths
    for query_path in config['queries']['create_tables_paths']:

        # Read query
        query = file.read(os.path.join(project_abs_path, query_path))

        # Execute query
        db.run_query(query=query)

        # Commit the transaction
        db.commit()

    log.info('finished creating database\'s tables')

    # Get current timestamp
    current_timestamp = datetimetools.get_current_timestamp()

    log.info('start system profile')

    system_profile_dict = system.get_system_profile()
    log.info(system_profile_dict)

    # Insert into the database
    profile_insert_query = file.read(
        path=os.path.join(
            project_abs_path, 'data/input/queries/insert/system_profile.txt'
        )
    )
    values_list = [
        current_timestamp,
        system_profile_dict['os'],
        system_profile_dict['system_name'],
        system_profile_dict['os_release'],
        system_profile_dict['os_version'],
        system_profile_dict['processor_arch'],
        system_profile_dict['processor_type'],
        system_profile_dict['physical_cores'],
        system_profile_dict['logical_cores']
    ]
    log.info('start inserting system profile data into the database')
    db.insert(insert_query=profile_insert_query, values_list=values_list)

    log.info('finished system profile')

    log.info('start CPU stats')

    cpu_stats_dict = system.get_cpu_stats()
    log.info(cpu_stats_dict)

    # Insert into the database
    cpu_insert_query = file.read(
        path=os.path.join(
            project_abs_path, 'data/input/queries/insert/cpu_stats.txt'
        )
    )
    cpu_values_list = [
        current_timestamp,
        cpu_stats_dict['current_cpu_freq_ghz'],
        cpu_stats_dict['cpu_usage_percent']
    ]
    log.info('start inserting CPU stats data into the database')
    db.insert(insert_query=cpu_insert_query, values_list=cpu_values_list)

    log.info('finished CPU stats')

    log.info('start RAM memory stats')

    ram_stats_dict = system.get_ram_stats()
    log.info(ram_stats_dict)

    # Insert into the database
    ram_insert_query = file.read(
        path=os.path.join(
            project_abs_path, 'data/input/queries/insert/ram_stats.txt'
        )
    )
    ram_values_list = [
        current_timestamp,
        ram_stats_dict['total_ram_gb'],
        ram_stats_dict['free_ram_gb'],
        ram_stats_dict['used_ram_gb'],
        ram_stats_dict['ram_usage_percent'],
        ram_stats_dict['total_swap_gb'],
        ram_stats_dict['free_swap_gb'],
        ram_stats_dict['used_swap_gb'],
        ram_stats_dict['swap_usage_percent']
    ]
    log.info('start inserting RAM memory data into the database')
    db.insert(insert_query=ram_insert_query, values_list=ram_values_list)

    log.info('finished RAM memory stats')

    log.info('start Storage stats stats')

    storage_stats_dict = system.get_disk_stats()
    storage_stats_dict['total_storage_gb'] = storage_stats_dict['partitions_list'][0]['partition_total_gb']
    storage_stats_dict['used_storage_gb'] = storage_stats_dict['partitions_list'][0]['partition_used_gb']
    storage_stats_dict['free_storage_gb'] = storage_stats_dict['partitions_list'][0]['partition_free_gb']
    storage_stats_dict['storage_usage_percent'] = storage_stats_dict['partitions_list'][0]['partition_percentage']
    log.info(storage_stats_dict)

    # Insert into the database
    storage_insert_query = file.read(
        path=os.path.join(
            project_abs_path, 'data/input/queries/insert/storage_stats.txt'
        )
    )
    storage_values_list = [
        current_timestamp,
        storage_stats_dict['total_storage_gb'],
        storage_stats_dict['used_storage_gb'],
        storage_stats_dict['free_storage_gb'],
        storage_stats_dict['storage_usage_percent'],
        storage_stats_dict['partitions_count'],
        json.dumps(storage_stats_dict['partitions_list']),
    ]
    log.info('start inserting Storage stats data into the database')

    db.insert(
        insert_query=storage_insert_query, values_list=storage_values_list
    )

    log.info('finished Storage stats stats')

    log.info('Finished program execution')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e)
        log.error('Error Traceback: \n {0}'.format(traceback.format_exc()))
