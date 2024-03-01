#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
from typing import Dict, List, Optional

import yagat.networkstructure as ns


class Substation:
    def __init__(self, network_structure: 'ns.NetworkStructure', substation_id: str, name: Optional[str] = None):
        self._network_structure = network_structure
        self._substation_id = substation_id
        self._name = name
        self._voltage_levels: Dict[str, 'ns.VoltageLevel'] = {}

    @property
    def network_structure(self) -> 'ns.NetworkStructure':
        return self._network_structure

    @property
    def substation_id(self) -> str:
        return self._substation_id

    @property
    def name(self) -> str:
        if self._name:
            return self._name
        return self._substation_id

    @property
    def voltage_levels(self) -> List['ns.VoltageLevel']:
        return sorted(self._voltage_levels.values(), key=lambda vl: vl.get_data().nominal_v, reverse=True)

    def get_voltage_level(self, voltage_level_id: str) -> Optional['ns.VoltageLevel']:
        if voltage_level_id in self._voltage_levels:
            return self._voltage_levels[voltage_level_id]
        return None

    def add_voltage_level(self, voltage_level: 'ns.VoltageLevel') -> None:
        self._voltage_levels[voltage_level.voltage_level_id] = voltage_level
