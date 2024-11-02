#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
from typing import Dict, List, Optional

import pandas as pd

import yagat.networkstructure as ns


class VoltageLevel:
    def __init__(self, network_structure: 'ns.NetworkStructure', substation: 'Optional[ns.Substation]',
                 voltage_level_id: str, name: Optional[str] = None):
        self._network_structure = network_structure
        self._substation = substation
        self._voltage_level_id = voltage_level_id
        self._name = name
        self._connections: Dict[(str, Optional[int]), 'ns.Connection'] = {}

    @property
    def voltage_level_id(self) -> str:
        return self._voltage_level_id

    @property
    def name(self) -> str:
        if self._name:
            return self._name
        return self._voltage_level_id

    @property
    def substation(self) -> 'Optional[ns.Substation]':
        return self._substation

    @property
    def network_structure(self) -> 'ns.NetworkStructure':
        return self._network_structure

    def add_connection(self, connection: 'ns.Connection'):
        self._connections[(connection.equipment_id, connection.side)] = connection

    @property
    def connections(self) -> List['ns.Connection']:
        return list(self._connections.values())

    def get_buses(self, bus_view: 'ns.BusView') -> pd.DataFrame:
        bus_branch_buses = self.network_structure.get_buses(self)
        match bus_view:
            case ns.BusView.BUS_BRANCH:
                return bus_branch_buses
            case ns.BusView.BUS_BREAKER:
                return self.network_structure.network.get_bus_breaker_topology(self.voltage_level_id).buses.join(bus_branch_buses, on='bus_id', rsuffix='_ignore')


    def get_bus_connections(self, bus_view: 'ns.BusView', bus_id: str) -> List['ns.Connection']:
        bus_connections = [c for c in self._connections.values() if c.get_bus_id(bus_view) == bus_id]
        return bus_connections

    def get_connection(self, connection_id: str, side: Optional[int] = None) -> Optional['ns.Connection']:
        if (connection_id, side) in self._connections:
            return self._connections[(connection_id, side)]
        return None

    def get_data(self) -> pd.Series:
        return self.network_structure.get_voltage_level_data(self)
