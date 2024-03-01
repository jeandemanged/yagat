#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import pypowsybl.network as pn
import pypowsybl.loadflow as lf
import pytest
import numpy as np

import yagat.networkstructure as ns


class TestNetworkStructureIeee9:

    @pytest.fixture
    def setup(self):
        network = pn.create_ieee9()
        structure = ns.NetworkStructure(network)
        yield network, structure

    def test_structure(self, setup):
        _, structure = setup
        assert len(structure.substations) == 6
        assert len(structure.voltage_levels) == 6
        assert structure.get_substation('not exists s') is None
        assert structure.get_voltage_level('not exists vl') is None
        s1 = structure.get_substation('S1')
        assert s1 is not None
        assert isinstance(s1, ns.Substation)
        vl1 = structure.get_voltage_level('VL1')
        assert vl1 is not None
        assert isinstance(vl1, ns.VoltageLevel)
        s2 = structure.get_substation_or_voltage_level('S2')
        assert s2 is not None
        assert isinstance(s2, ns.Substation)
        vl2 = structure.get_substation_or_voltage_level('VL2')
        assert vl2 is not None
        assert isinstance(vl2, ns.VoltageLevel)
        with pytest.raises(RuntimeError):
            structure.get_substation_or_voltage_level('not_exists')

    def test_substation(self, setup):
        _, structure = setup
        s1 = structure.get_substation('S1')
        assert s1.network_structure == structure
        assert s1.substation_id == 'S1'
        assert s1.name == 'S1'
        assert len(s1.voltage_levels) == 1
        vl1 = s1.get_voltage_level('VL1')
        assert vl1 is not None
        assert isinstance(vl1, ns.VoltageLevel)
        assert s1.get_voltage_level('not exists vl') is None

    def test_voltage_level(self, setup):
        _, structure = setup
        s1 = structure.get_substation('S1')
        vl1 = structure.get_voltage_level('VL1')
        assert vl1.network_structure == structure
        assert vl1.substation == s1
        assert vl1.voltage_level_id == 'VL1'
        assert vl1.name == 'VL1'
        assert len(vl1.connections) == 5
        l540 = vl1.get_connection('L5-4-0', 2)
        assert l540 is not None
        assert isinstance(l540, ns.Connection)
        assert vl1.get_connection('not exists c') is None

    def test_voltage_level_buses(self, setup):
        _, structure = setup
        vl1 = structure.get_voltage_level('VL1')
        vl1_buses = vl1.get_buses(ns.BusView.BUS_BRANCH)
        vl2 = structure.get_voltage_level('VL2')
        vl2_buses = vl2.get_buses(ns.BusView.BUS_BRANCH)
        assert len(vl1_buses) == 2
        assert len(vl2_buses) == 2
        assert 'VL1_0' in vl1_buses.index
        assert 'VL1_1' in vl1_buses.index
        assert 'VL2_0' in vl2_buses.index
        assert 'VL2_1' in vl2_buses.index
        assert 'VL2_0' not in vl1_buses.index
        assert 'VL1_0' not in vl2_buses.index
        vl1_0_connections = vl1.get_bus_connections(ns.BusView.BUS_BRANCH, 'VL1_0')
        assert len(vl1_0_connections) == 2

    def test_connection(self, setup):
        _, structure = setup
        s1 = structure.get_substation('S1')
        vl1 = structure.get_voltage_level('VL1')

        l540 = vl1.get_connection('L5-4-0', 2)
        assert l540.substation == s1
        assert l540.voltage_level == vl1
        assert l540.network_structure == structure
        assert l540.equipment_id == 'L5-4-0'
        assert l540.name == 'L5-4-0'
        assert l540.equipment_type == 'LINE'
        assert l540.side == 2

        t410 = vl1.get_connection('T4-1-0', 1)
        assert t410.equipment_id == 'T4-1-0'
        assert t410.name == 'T4-1-0'
        assert t410.equipment_type == ns.EquipmentType.TWO_WINDINGS_TRANSFORMER
        assert t410.side == 1

        b1g = vl1.get_connection('B1-G')
        assert b1g.equipment_id == 'B1-G'
        assert b1g.name == 'B1-G'
        assert b1g.equipment_type == ns.EquipmentType.GENERATOR
        assert b1g.side is None

    def test_connection_data(self, setup):
        network, structure = setup
        connection_data = structure.get_connection_data('L5-4-0', 2)
        assert np.isnan(connection_data.p1)
        lf.run_ac(network)
        structure.refresh()
        connection_data = structure.get_connection_data('L5-4-0', 2)
        assert connection_data.p1 == pytest.approx(-40.7, 0.1)

    def test_connection_from_structure(self, setup):
        _, structure = setup
        t410_1 = structure.get_connection('T4-1-0', 1)
        t410_2 = structure.get_connection('T4-1-0', 2)
        assert t410_1.voltage_level.voltage_level_id == 'VL1'
        assert t410_2.voltage_level.voltage_level_id == 'VL1'


class TestNetworkStructureMicroGridBe:

    @pytest.fixture
    def setup(self):
        network = pn.create_micro_grid_be_network()
        structure = ns.NetworkStructure(network)
        yield network, structure

    def test_structure(self, setup):
        _, structure = setup
        assert len(structure.substations) == 2
        assert len(structure.voltage_levels) == 6

        anvers = structure.get_substation('87f7002b-056f-4a6a-a872-1744eea757e3')
        assert anvers.name == 'Anvers'
        assert len(anvers.voltage_levels) == 1

        brussels = structure.get_substation('37e14a0f-5e34-4647-a062-8bfd9305fa9d')
        assert brussels.name == 'PP_Brussels'
        assert len(brussels.voltage_levels) == 5

        brussels_380 = structure.get_voltage_level('469df5f7-058f-4451-a998-57a48e8a56fe')
        assert brussels_380.name == '380.0'
        assert len(brussels_380.connections) == 6
        tr3 = brussels_380.get_connection('84ed55f4-61f5-4d9d-8755-bba7b877a246', 1)
        assert tr3.name == 'BE-TR3_1'
        assert tr3.equipment_type == ns.EquipmentType.THREE_WINDINGS_TRANSFORMER
        dangling_line3 = brussels_380.get_connection('78736387-5f60-4832-b3fe-d50daf81b0a6')
        assert dangling_line3.name == 'BE-Line_3'
        assert dangling_line3.equipment_type == ns.EquipmentType.DANGLING_LINE

        brussels_110 = structure.get_voltage_level('8bbd7e74-ae20-4dce-8780-c20f8e18c2e0')
        assert brussels_110.name == '110.0'
        assert len(brussels_110.connections) == 5
        s1 = brussels_110.get_connection('d771118f-36e9-4115-a128-cc3d9ce3e3da')
        assert s1.name == 'BE_S1'
        assert s1.equipment_type == ns.EquipmentType.SHUNT_COMPENSATOR
