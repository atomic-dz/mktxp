# coding=utf8
## Copyright (c) 2020 Arseniy Kuznetsov
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

import re
from datetime import timedelta
from mktxp.collectors.base_collector import BaseCollector
from mktxp.router_metric import RouterMetric


class SystemResourceCollector(BaseCollector):
    ''' System Resource Metrics collector
    '''        
    @staticmethod
    def collect(router_metric):
        resource_labels = ['uptime', 'version', 'free_memory', 'total_memory', 
                           'cpu', 'cpu_count', 'cpu_frequency', 'cpu_load', 
                           'free_hdd_space', 'total_hdd_space', 
                           'architecture_name', 'board_name']
        resource_records = router_metric.system_resource_records(resource_labels)
        if not resource_records:
            return

        # translate records to appropriate values
        translated_fields = ['uptime']        
        for resource_record in resource_records:
            for translated_field in translated_fields:
                value = resource_record.get(translated_field, None)    
                if value:            
                    resource_record[translated_field] = SystemResourceCollector._translated_values(translated_field, value)

        uptime_metrics = BaseCollector.gauge_collector('uptime', 'Time interval since boot-up', resource_records, 'uptime', ['version', 'board_name', 'cpu', 'architecture_name'])
        yield uptime_metrics

        free_memory_metrics = BaseCollector.gauge_collector('free_memory', 'Unused amount of RAM', resource_records, 'free_memory', ['version', 'board_name', 'cpu', 'architecture_name'])
        yield free_memory_metrics

        total_memory_metrics = BaseCollector.gauge_collector('total_memory', 'Amount of installed RAM', resource_records, 'total_memory', ['version', 'board_name', 'cpu', 'architecture_name'])
        yield total_memory_metrics

        free_hdd_metrics = BaseCollector.gauge_collector('free_hdd_space', 'Free space on hard drive or NAND', resource_records, 'free_hdd_space', ['version', 'board_name', 'cpu', 'architecture_name'])
        yield free_hdd_metrics

        total_hdd_metrics = BaseCollector.gauge_collector('total_hdd_space', 'Size of the hard drive or NAND', resource_records, 'total_hdd_space', ['version', 'board_name', 'cpu', 'architecture_name'])
        yield total_hdd_metrics

        cpu_load_metrics = BaseCollector.gauge_collector('cpu_load', 'Percentage of used CPU resources', resource_records, 'cpu_load', ['version', 'board_name', 'cpu', 'architecture_name'])
        yield cpu_load_metrics

        cpu_count_metrics = BaseCollector.gauge_collector('cpu_count', 'Number of CPUs present on the system', resource_records, 'cpu_count', ['version', 'board_name', 'cpu', 'architecture_name'])
        yield cpu_count_metrics

        cpu_frequency_metrics = BaseCollector.gauge_collector('cpu_frequency', 'Current CPU frequency', resource_records, 'cpu_frequency', ['version', 'board_name', 'cpu', 'architecture_name'])
        yield cpu_frequency_metrics


    # Helpers
    @staticmethod
    def _translated_values(translated_field, value):
        return {
                'uptime': lambda value: SystemResourceCollector._parse_uptime(value)
                }[translated_field](value)

    @staticmethod
    def _parse_uptime(time):
        time_dict = re.match(r'((?P<weeks>\d+)w)?((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?', time).groupdict()
        return timedelta(**{key: int(value) for key, value in time_dict.items() if value}).total_seconds()
