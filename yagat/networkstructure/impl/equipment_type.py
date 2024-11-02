#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
from enum import StrEnum


class EquipmentType(StrEnum):
    LOAD = 'LOAD'
    GENERATOR = 'GENERATOR'
    LINE = 'LINE'
    TWO_WINDINGS_TRANSFORMER = 'TWO_WINDINGS_TRANSFORMER'
    THREE_WINDINGS_TRANSFORMER = 'THREE_WINDINGS_TRANSFORMER'
    DANGLING_LINE = 'DANGLING_LINE'
    STATIC_VAR_COMPENSATOR = 'STATIC_VAR_COMPENSATOR'
    SHUNT_COMPENSATOR = 'SHUNT_COMPENSATOR'
    LCC_CONVERTER_STATION = 'LCC_CONVERTER_STATION'
    VSC_CONVERTER_STATION = 'VSC_CONVERTER_STATION'
    SWITCH = 'SWITCH'

    @staticmethod
    def branch_types():
        return [EquipmentType.LINE, EquipmentType.TWO_WINDINGS_TRANSFORMER]

    @staticmethod
    def injection_types():
        return [EquipmentType.LOAD, EquipmentType.GENERATOR, EquipmentType.SHUNT_COMPENSATOR,
                EquipmentType.DANGLING_LINE, EquipmentType.STATIC_VAR_COMPENSATOR, EquipmentType.LCC_CONVERTER_STATION,
                EquipmentType.VSC_CONVERTER_STATION]


class ShuntCompensatorType(StrEnum):
    CAPACITOR = 'CAPACITOR'
    REACTOR = 'REACTOR'
