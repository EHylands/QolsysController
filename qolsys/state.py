#MIT License
#
#Copyright (c) 2021 Raphaël Beamonte <raphael.beamonte@gmail.com>

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import logging

from qolsys.event import QolsysEventInfoSummary
from qolsys.exceptions import QolsysException
from qolsys.observable import QolsysObservable
from qolsys.partition import QolsysPartition

LOGGER = logging.getLogger(__name__)

class QolsysState(QolsysObservable):
    NOTIFY_UPDATE_PARTITIONS = 'update_partitions'
    NOTIFY_UPDATE_ERROR = 'update_error'

    def __init__(self, event: QolsysEventInfoSummary = None):
        super().__init__()

        self._last_exception = None

        self._partitions = {}
        
        if event:
            self.update(event)

        QolsysException.STATE = self

    @property
    def last_exception(self):
        return self._last_exception

    @last_exception.setter
    def last_exception(self, value):
        prev_value = self._last_exception
        self._last_exception = value

        self.notify(change=self.NOTIFY_UPDATE_ERROR,
                    prev_value=prev_value,
                    new_value=value)

    @property
    def partitions(self):
        return self._partitions.values()

    def partition(self, partition_id):
        return self._partitions.get(int(partition_id))

    def update(self, event: QolsysEventInfoSummary):
        prev_partitions = self.partitions

        self._partitions = {}
        for partition in event.partitions:
            self._partitions[int(partition.id)] = partition

        self.notify(change=self.NOTIFY_UPDATE_PARTITIONS,
                    prev_value=prev_partitions,
                    new_value=self.partitions)
        
    def update(self,partitions):
        prev_partitions = self.partitions
        
        self._partitions = {}

        for partition in partitions:
            self._partitions[int(partition.id)] = partition

        self.notify(change=self.NOTIFY_UPDATE_PARTITIONS,
                    prev_value=prev_partitions,
                   new_value=self.partitions)
        
    def zone(self, zone_id):
        for partition in self.partitions:
            zone = partition.zone(zone_id)
            if zone is not None:
                return zone

    def sensor(self, sensor_id):
        for partition in self.partitions:
            sensor = partition.sensor(sensor_id)
            if sensor is not None:
                return sensor

    def zone_update(self, sensor):
        # Find where the zone is currently at
        current_zone = self.zone(sensor.zone_id)
        if current_zone is None:
            raise Exception(f'Zone not found for zone update: {sensor}, '
                            'we might not be sync-ed anymore')  # TODO: make it a better exception

        if current_zone.partition_id == sensor.partition_id:
            self._partitions[sensor.partition_id].update_sensor(sensor)
        else:
            self._partitions[current_zone.partition_id].remove_zone(sensor.zone_id)
            self._partitions[sensor.partition_id].add_sensor(sensor)

    def zone_add(self, sensor):
        partition = self._partitions.get(sensor.partition_id)
        if partition is None:
            raise Exception(f'Partition not found for zone add: {sensor},'
                            'we might not be sync-ed anymore')  # TODO: make it a better exception

        self._partitions[sensor.partition_id].add_sensor(sensor)

    def zone_delete(self,sensor):
        partition = self._partitions.get(sensor.partition_id)
        
        if partition is None:
            raise Exception(f'Partition not found for zone add: {sensor},'
                            'we might not be sync-ed anymore')  # TODO: make it a better exception
        
        self._partitions[sensor.partition_id].remove_sensor(sensor)

    def zone_open(self, zone_id):
        for partition in self.partitions:
            zone = partition.zone(zone_id)
            if zone is not None:
                zone.open()

    def zone_closed(self, zone_id):
        for partition in self.partitions:
            zone = partition.zone(zone_id)
            if zone is not None:
                zone.closed()


    def dump(self):
        LOGGER.debug(f'*** Information ***')

        for partition in self.partitions:  
            LOGGER.debug(f"Partition{partition._id} ({partition._name}) - {partition._status}")
            
        for sensor in partition.sensors:
            LOGGER.debug(f"Zone{sensor._zone_id} ({sensor._name}) - {sensor._status}")
            
        for zwave in partition.zwave_devices:
            LOGGER.debug(f"Z-Wave{zwave._id} ({zwave._node_name}) - {zwave._node_type}")            
