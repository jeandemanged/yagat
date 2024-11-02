#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import math
from typing import Optional

import pandas as pd

import yagat.networkstructure as ns


class Connection:
    def __init__(self, network_structure: 'ns.NetworkStructure', voltage_level: 'ns.VoltageLevel', equipment_id: str,
                 equipment_type: 'ns.EquipmentType',
                 side: Optional[int] = None, name: Optional[str] = None):
        self._network_structure = network_structure
        self._voltage_level = voltage_level
        self._equipment_id = equipment_id
        self._name = name
        self._equipment_type = equipment_type
        self._side = side

    @property
    def equipment_id(self) -> str:
        return self._equipment_id

    @property
    def name(self) -> str:
        if self._name:
            return self._name
        return self._equipment_id

    @property
    def equipment_type(self) -> 'ns.EquipmentType':
        return self._equipment_type

    @property
    def side(self) -> int:
        return self._side

    @property
    def voltage_level(self) -> 'ns.VoltageLevel':
        return self._voltage_level

    @property
    def substation(self) -> 'Optional[ns.Substation]':
        return self._voltage_level.substation

    @property
    def network_structure(self) -> 'ns.NetworkStructure':
        return self._network_structure

    def _side_char(self):
        if not self.side:
            return ''
        return f'{self.side}'

    def get_bus_id(self, bus_view: 'ns.BusView') -> str:
        if self.equipment_type == ns.EquipmentType.SWITCH:
            if bus_view == ns.BusView.BUS_BRANCH:
                return ''
            elif bus_view == ns.BusView.BUS_BREAKER:
                if self.network_structure.is_retained(self):
                    # omg
                    return self.network_structure.network.get_bus_breaker_topology(self.voltage_level.voltage_level_id).switches.loc[self.equipment_id][f'bus{self._side_char()}_id']
                else:
                    return ''
        prefix = ''
        if bus_view == ns.BusView.BUS_BREAKER:
            prefix = 'bus_breaker_'
        return self.get_data()[f'{prefix}bus{self._side_char()}_id']

    def get_p(self) -> float:
        if self.equipment_type == ns.EquipmentType.SWITCH:
            return math.nan
        return self.get_data()[f'p{self._side_char()}']

    def get_q(self) -> float:
        if self.equipment_type == ns.EquipmentType.SWITCH:
            return math.nan
        return self.get_data()[f'q{self._side_char()}']

    def get_i(self) -> float:
        if self.equipment_type == ns.EquipmentType.SWITCH:
            return math.nan
        return self.get_data()[f'i{self._side_char()}']

    def get_connected(self) -> bool:
        if self.equipment_type == ns.EquipmentType.SWITCH:
            return True
        return self.get_data()[f'connected{self._side_char()}']

    def get_data(self) -> pd.Series:
        return self.network_structure.get_connection_data(self.equipment_id, self.side)
