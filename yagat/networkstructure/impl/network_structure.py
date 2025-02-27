#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import logging
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import pypowsybl.loadflow as lf
import pypowsybl.network as pn

import yagat.networkstructure as ns


class NetworkStructure:
    def __init__(self, network: pn.Network):
        self._network: pn.Network = network
        self._substations: Dict[str, ns.Substation] = {}
        self._voltage_levels: Dict[str, ns.VoltageLevel] = {}
        self._connections: Dict[Tuple[str, Optional[int]], ns.Connection] = {}

        self._areas_df: pd.DataFrame = pd.DataFrame()
        self._areas_boundaries_df: pd.DataFrame = pd.DataFrame()
        self._substations_df: pd.DataFrame = pd.DataFrame()
        self._voltage_levels_df: pd.DataFrame = pd.DataFrame()

        self._injections_df: Dict[ns.EquipmentType, pd.DataFrame] = {}
        self._branches_df: Dict[ns.EquipmentType, pd.DataFrame] = {}
        self._three_windings_transformers_df: pd.DataFrame = pd.DataFrame()
        self._tie_lines_df: pd.DataFrame = pd.DataFrame()
        self._buses_df: pd.DataFrame = pd.DataFrame()
        self._buses_bus_breaker_view_df: pd.DataFrame = pd.DataFrame()
        self._switches_df: pd.DataFrame = pd.DataFrame()
        self._hvdc_lines_df: pd.DataFrame = pd.DataFrame()

        self._linear_shunt_compensator_sections_df: pd.DataFrame = pd.DataFrame()
        self._non_linear_shunt_compensator_sections_df: pd.DataFrame = pd.DataFrame()

        self._components_df: pd.DataFrame = pd.DataFrame()
        self._lf_components_results: list[lf.ComponentResult] = []

        self._bus_breaker_topology_cache: Dict[str, pn.BusBreakerTopology] = {}

        self.refresh()

        for substation_idx, substation_s in self._substations_df.iterrows():
            substation_id = str(substation_idx)
            self._substations[substation_id] = ns.Substation(self, substation_id, str(substation_s['name']))

        for voltage_level_idx, voltage_level_s in self._voltage_levels_df.iterrows():
            voltage_level_id = str(voltage_level_idx)
            substation_id = voltage_level_s.substation_id
            substation = None
            if substation_id in self._substations:
                substation = self._substations[substation_id]
            voltage_level = ns.VoltageLevel(self, substation, voltage_level_id, str(voltage_level_s['name']))
            self._voltage_levels[voltage_level_id] = voltage_level
            if substation:
                substation.add_voltage_level(voltage_level)

        for typ in ns.EquipmentType.branch_types():
            self.__process_branches(self._branches_df[typ], typ)

        for typ in ns.EquipmentType.injection_types():
            self.__process_injection(self._injections_df[typ], typ)

        for three_windings_xf_idx, three_windings_xf_s in self._three_windings_transformers_df.iterrows():
            three_windings_xf_id = str(three_windings_xf_idx)
            voltage_level1_id = three_windings_xf_s.voltage_level1_id
            voltage_level2_id = three_windings_xf_s.voltage_level2_id
            voltage_level3_id = three_windings_xf_s.voltage_level3_id
            voltage_level1 = self._voltage_levels[voltage_level1_id]
            voltage_level2 = self._voltage_levels[voltage_level2_id]
            voltage_level3 = self._voltage_levels[voltage_level3_id]
            c1 = ns.Connection(self, voltage_level1, three_windings_xf_id, ns.EquipmentType.THREE_WINDINGS_TRANSFORMER,
                               1,
                               str(three_windings_xf_s['name']))
            c2 = ns.Connection(self, voltage_level2, three_windings_xf_id, ns.EquipmentType.THREE_WINDINGS_TRANSFORMER,
                               2,
                               str(three_windings_xf_s['name']))
            c3 = ns.Connection(self, voltage_level3, three_windings_xf_id, ns.EquipmentType.THREE_WINDINGS_TRANSFORMER,
                               3,
                               str(three_windings_xf_s['name']))
            voltage_level1.add_connection(c1)
            voltage_level2.add_connection(c2)
            voltage_level3.add_connection(c3)
            self._connections[(c1.equipment_id, c1.side)] = c1
            self._connections[(c2.equipment_id, c2.side)] = c2
            self._connections[(c3.equipment_id, c3.side)] = c3

        for switch_idx, switch_s in self._switches_df.iterrows():
            switch_id = str(switch_idx)
            voltage_level_id = switch_s.voltage_level_id
            voltage_level = self._voltage_levels[voltage_level_id]
            c1 = ns.Connection(self, voltage_level, switch_id, ns.EquipmentType.SWITCH,
                               1,
                               str(switch_s['name']))
            c2 = ns.Connection(self, voltage_level, switch_id, ns.EquipmentType.SWITCH,
                               2,
                               str(switch_s['name']))
            voltage_level.add_connection(c1)
            voltage_level.add_connection(c2)
            self._connections[(c1.equipment_id, c1.side)] = c1
            self._connections[(c2.equipment_id, c2.side)] = c2

    @property
    def network(self) -> pn.Network:
        return self._network

    @property
    def lf_components_results(self) -> list[lf.ComponentResult]:
        return self._lf_components_results

    @lf_components_results.setter
    def lf_components_results(self, value: list[lf.ComponentResult]) -> None:
        self._lf_components_results = value

    @property
    def areas(self) -> pd.DataFrame:
        return self._areas_df

    @property
    def areas_boundaries(self) -> pd.DataFrame:
        return self._areas_boundaries_df

    @property
    def buses(self) -> pd.DataFrame:
        return self._buses_df

    @property
    def buses_bus_breaker_view(self) -> pd.DataFrame:
        return self._buses_bus_breaker_view_df

    @property
    def generators(self) -> pd.DataFrame:
        return self._injections_df[ns.EquipmentType.GENERATOR]

    @property
    def loads(self) -> pd.DataFrame:
        return self._injections_df[ns.EquipmentType.LOAD]

    @property
    def lines(self) -> pd.DataFrame:
        return self._branches_df[ns.EquipmentType.LINE]

    @property
    def two_windings_transformers(self) -> pd.DataFrame:
        return self._branches_df[ns.EquipmentType.TWO_WINDINGS_TRANSFORMER]

    @property
    def dangling_lines(self) -> pd.DataFrame:
        return self._injections_df[ns.EquipmentType.DANGLING_LINE]

    @property
    def shunt_compensators(self) -> pd.DataFrame:
        return self._injections_df[ns.EquipmentType.SHUNT_COMPENSATOR]

    @property
    def static_var_compensators(self) -> pd.DataFrame:
        return self._injections_df[ns.EquipmentType.STATIC_VAR_COMPENSATOR]

    @property
    def lcc_hvdc(self) -> pd.DataFrame:
        return self._injections_df[ns.EquipmentType.LCC_CONVERTER_STATION]

    @property
    def vsc_hvdc(self) -> pd.DataFrame:
        return self._injections_df[ns.EquipmentType.VSC_CONVERTER_STATION]

    @property
    def three_windings_transformers(self) -> pd.DataFrame:
        return self._three_windings_transformers_df

    @property
    def switches(self) -> pd.DataFrame:
        return self._switches_df

    @property
    def tie_lines(self) -> pd.DataFrame:
        return self._tie_lines_df

    @property
    def hvdc_lines(self) -> pd.DataFrame:
        return self._hvdc_lines_df

    @property
    def components(self) -> pd.DataFrame:
        return self._components_df

    def refresh(self):
        logging.info('refresh start')

        self._bus_breaker_topology_cache = {}

        logging.info('get_areas...')
        self._areas_df = self._network.get_areas(all_attributes=True)

        logging.info('get_areas_boundaries...')
        self._areas_boundaries_df = self._network.get_areas_boundaries(all_attributes=True)

        logging.info('get_substations...')
        self._substations_df = self._network.get_substations(all_attributes=True)

        logging.info('get_voltage_levels...')
        tmp = self._substations_df[['name', 'country']].rename(columns={'name': 'substation_name'})
        self._voltage_levels_df = (self._network.get_voltage_levels(
            attributes=['substation_id', 'name', 'nominal_v', 'low_voltage_limit', 'high_voltage_limit',
                        'topology_kind'])
                                   .reset_index()
                                   .merge(tmp, left_on='substation_id', right_on='id', how='left')
                                   .set_index('id'))[
            ['name', 'country', 'substation_id', 'substation_name', 'nominal_v', 'low_voltage_limit',
             'high_voltage_limit', 'topology_kind']]

        logging.info('get_buses')
        tmp = self._voltage_levels_df[
            ['name', 'country', 'substation_id', 'substation_name', 'nominal_v', 'low_voltage_limit',
             'high_voltage_limit']].rename(columns={'name': 'voltage_level_name'})
        self._buses_df = (self._network.get_buses()
                          .reset_index()
                          .merge(tmp, left_on='voltage_level_id', right_on='id', how='left')
                          .set_index('id'))

        logging.info('building components ...')
        components = list(zip(self._buses_df.connected_component, self._buses_df.synchronous_component))
        components.sort()
        components = [f'CC{connected_component} SC{synchronous_component}'
                      for (connected_component, synchronous_component) in components]
        df = pd.DataFrame(index=components)
        df = df[~df.index.duplicated(keep='first')]
        new_columns = {'status': [''] * len(df),
                       'status_text': [''] * len(df),
                       'iteration_count': [np.nan] * len(df),
                       'reference_bus_id': [''] * len(df),
                       'slack_buses_ids': [''] * len(df),
                       'active_power_mismatch': [np.nan] * len(df),
                       'distributed_active_power': [np.nan] * len(df),
                       }
        self._components_df = df.assign(**new_columns)

        for cr in self._lf_components_results:
            cid = f'CC{cr.connected_component_num} SC{cr.synchronous_component_num}'
            self._components_df.loc[cid, 'status'] = cr.status.name
            self._components_df.loc[cid, 'status_text'] = cr.status_text
            self._components_df.loc[cid, 'iteration_count'] = cr.iteration_count
            self._components_df.loc[cid, 'reference_bus_id'] = cr.reference_bus_id
            self._components_df.loc[cid, 'slack_buses_ids'] = ','.join([sbr.id for sbr in cr.slack_bus_results])
            self._components_df.loc[cid, 'active_power_mismatch'] = (
                sum(sbr.active_power_mismatch for sbr in cr.slack_bus_results)
            )
            self._components_df.loc[cid, 'distributed_active_power'] = cr.distributed_active_power

        logging.info('get_bus_breaker_view_buses')
        self._buses_bus_breaker_view_df = (self._network.get_bus_breaker_view_buses()
                                           .reset_index()
                                           .merge(tmp, left_on='voltage_level_id', right_on='id', how='left')
                                           .set_index('id'))

        logging.info('get_lines')
        self._branches_df[ns.EquipmentType.LINE] = self._network.get_lines(
            attributes=['name', 'connected1', 'connected2', 'p1', 'q1', 'i1', 'p2', 'q2', 'i2', 'bus1_id',
                        'bus_breaker_bus1_id', 'voltage_level1_id', 'bus2_id', 'bus_breaker_bus2_id',
                        'voltage_level2_id'])

        logging.info('get_2_windings_transformers')
        self._branches_df[ns.EquipmentType.TWO_WINDINGS_TRANSFORMER] = self._network.get_2_windings_transformers(
            attributes=['name', 'connected1', 'connected2', 'p1', 'q1', 'i1', 'p2', 'q2', 'i2', 'bus1_id',
                        'bus_breaker_bus1_id', 'voltage_level1_id', 'bus2_id', 'bus_breaker_bus2_id',
                        'voltage_level2_id'])

        logging.info('get_3_windings_transformers...')
        self._three_windings_transformers_df = self._network.get_3_windings_transformers(
            attributes=['name', 'connected1', 'connected2', 'connected3', 'p1', 'q1', 'i1', 'p2', 'q2', 'i2', 'p3',
                        'q3', 'i3', 'bus1_id', 'bus_breaker_bus1_id', 'voltage_level1_id', 'bus2_id',
                        'bus_breaker_bus2_id', 'voltage_level2_id', 'bus3_id', 'bus_breaker_bus3_id',
                        'voltage_level3_id'])

        logging.info('get_tie_lines...')
        self._tie_lines_df = self._network.get_tie_lines(all_attributes=True)

        logging.info('get_switches...')
        self._switches_df = self._network.get_switches(
            attributes=['name', 'kind', 'open', 'retained',
                        'bus_breaker_bus1_id', 'bus_breaker_bus2_id', 'voltage_level_id', 'fictitious'])

        logging.info('get_loads...')
        self._injections_df[ns.EquipmentType.LOAD] = self._network.get_loads(
            attributes=['name', 'connected', 'type', 'p0', 'q0', 'p', 'q', 'i',
                        'bus_id', 'bus_breaker_bus_id', 'voltage_level_id', 'fictitious'])

        logging.info('get_generators...')
        self._injections_df[ns.EquipmentType.GENERATOR] = self._network.get_generators(
            attributes=['name', 'connected', 'energy_source', 'target_p', 'min_p', 'max_p',
                        'voltage_regulator_on', 'target_q', 'target_v', 'p', 'q', 'i',
                        'bus_id', 'bus_breaker_bus_id', 'voltage_level_id', 'fictitious'])

        logging.info('get_dangling_lines...')
        self._injections_df[ns.EquipmentType.DANGLING_LINE] = self._network.get_dangling_lines(
            attributes=['name', 'connected', 'p0', 'q0', 'p', 'q', 'i', 'boundary_p', 'boundary_q', 'boundary_v_mag',
                        'boundary_v_angle', 'bus_id', 'bus_breaker_bus_id', 'voltage_level_id', 'pairing_key', 'paired',
                        'tie_line_id', 'fictitious'])

        logging.info('get_shunt_compensators...')
        self._injections_df[ns.EquipmentType.SHUNT_COMPENSATOR] = self._network.get_shunt_compensators(
            attributes=['name', 'connected', 'model_type', 'section_count', 'max_section_count',
                        'voltage_regulation_on', 'target_v', 'target_deadband', 'p', 'q', 'i',
                        'bus_id', 'bus_breaker_bus_id', 'voltage_level_id', 'fictitious'])

        logging.info('get_static_var_compensators...')
        self._injections_df[ns.EquipmentType.STATIC_VAR_COMPENSATOR] = self._network.get_static_var_compensators(
            all_attributes=True)

        logging.info('get_lcc_converter_stations...')
        self._injections_df[ns.EquipmentType.LCC_CONVERTER_STATION] = self._network.get_lcc_converter_stations(
            all_attributes=True)

        logging.info('get_vsc_converter_stations...')
        self._injections_df[ns.EquipmentType.VSC_CONVERTER_STATION] = self._network.get_vsc_converter_stations(
            all_attributes=True)

        logging.info('get_linear_shunt_compensator_sections')
        self._linear_shunt_compensator_sections_df = self._network.get_linear_shunt_compensator_sections(
            all_attributes=True)

        logging.info('get_non_linear_shunt_compensator_sections')
        self._non_linear_shunt_compensator_sections_df = self._network.get_non_linear_shunt_compensator_sections(
            all_attributes=True)

        logging.info('get_hvdc_lines')
        self._hvdc_lines_df = self._network.get_hvdc_lines(all_attributes=True)

        logging.info('refresh end')

    def __process_injection(self, injections_df, injection_type: ns.EquipmentType) -> None:
        for injection_idx, injection_s in injections_df.iterrows():
            injection_id = str(injection_idx)
            voltage_level_id = injection_s.voltage_level_id
            voltage_level = self._voltage_levels[voltage_level_id]
            c1 = ns.Connection(self, voltage_level, injection_id, injection_type, None, injection_s['name'])
            voltage_level.add_connection(c1)
            self._connections[(c1.equipment_id, c1.side)] = c1

    def __process_branches(self, branches_df, branch_type: ns.EquipmentType) -> None:
        for branch_idx, branches_s in branches_df.iterrows():
            branch_id = str(branch_idx)
            voltage_level1_id = branches_s.voltage_level1_id
            voltage_level2_id = branches_s.voltage_level2_id
            voltage_level1 = self._voltage_levels[voltage_level1_id]
            voltage_level2 = self._voltage_levels[voltage_level2_id]
            c1 = ns.Connection(self, voltage_level1, branch_id, branch_type, 1, branches_s['name'])
            c2 = ns.Connection(self, voltage_level2, branch_id, branch_type, 2, branches_s['name'])
            voltage_level1.add_connection(c1)
            voltage_level2.add_connection(c2)
            self._connections[(c1.equipment_id, c1.side)] = c1
            self._connections[(c2.equipment_id, c2.side)] = c2

    @property
    def substations(self) -> 'List[ns.Substation]':
        return sorted(self._substations.values(), key=lambda s: s.name)

    @property
    def voltage_levels(self) -> 'List[ns.VoltageLevel]':
        return sorted(self._voltage_levels.values(), key=lambda vl: (-vl.get_data().nominal_v, vl.name))

    def get_substation(self, substation_id: str) -> 'Optional[ns.Substation]':
        if substation_id in self._substations:
            return self._substations[substation_id]
        return None

    def get_voltage_level(self, voltage_level_id: str) -> 'Optional[ns.VoltageLevel]':
        if voltage_level_id in self._voltage_levels:
            return self._voltage_levels[voltage_level_id]
        return None

    def get_substation_or_voltage_level(self, object_id: str) -> 'Union[ns.Substation, ns.VoltageLevel]':
        substation = self.get_substation(object_id)
        if substation:
            return substation
        voltage_level = self.get_voltage_level(object_id)
        if voltage_level:
            return voltage_level
        raise RuntimeError(f'{object_id} is not a known Substation or VoltageLevel')

    def get_connection(self, connection_id: str, side: Optional[int]) -> 'Optional[ns.Connection]':
        if (connection_id, side) in self._connections:
            return self._connections[(connection_id, side)]
        return None

    def get_voltage_level_data(self, voltage_level: 'ns.VoltageLevel') -> pd.DataFrame:
        return self._voltage_levels_df.loc[voltage_level.voltage_level_id]

    def get_connection_data(self, connection_id: str, side: Optional[int]) -> pd.DataFrame:
        connection = self._connections[(connection_id, side)]
        if not connection:
            return pd.Series()
        typ = connection.equipment_type
        if typ in ns.EquipmentType.branch_types():
            df = self._branches_df[typ]
        elif typ in ns.EquipmentType.injection_types():
            df = self._injections_df[typ]
        elif typ == ns.EquipmentType.THREE_WINDINGS_TRANSFORMER:
            df = self._three_windings_transformers_df
        else:
            raise RuntimeError(f'No dataframe for connection {connection_id} of type {typ}')

        return df.loc[connection.equipment_id]

    def get_shunt_compensator_type(self, connection: ns.Connection) -> 'ns.ShuntCompensatorType':
        if connection.equipment_type != ns.EquipmentType.SHUNT_COMPENSATOR:
            raise RuntimeError('Not a shunt compensator')
        model_type = self._injections_df[ns.EquipmentType.SHUNT_COMPENSATOR].loc[connection.equipment_id]['model_type']
        if model_type == 'LINEAR':
            b = self._linear_shunt_compensator_sections_df.loc[connection.equipment_id]['b_per_section']
        else:
            # just take the first section. it is not supposed to be a different sign across sections.
            b = self._non_linear_shunt_compensator_sections_df.loc[(connection.equipment_id, 0)]['b']
        if b > 0:
            return ns.ShuntCompensatorType.CAPACITOR
        return ns.ShuntCompensatorType.REACTOR

    def is_retained(self, connection: ns.Connection) -> bool:
        if connection.equipment_type != ns.EquipmentType.SWITCH:
            raise RuntimeError('Not a switch')
        return bool(self._switches_df.loc[connection.equipment_id]['retained'])

    def is_open(self, connection: ns.Connection) -> bool:
        if connection.equipment_type != ns.EquipmentType.SWITCH:
            raise RuntimeError('Not a switch')
        return bool(self._switches_df.loc[connection.equipment_id]['open'])

    def get_other_sides(self, connection: ns.Connection) -> List[ns.Connection]:
        if connection.equipment_type in ns.EquipmentType.branch_types() or connection.equipment_type == ns.EquipmentType.SWITCH:
            other_side_num = 1 if connection.side == 2 else 2
            return [self._connections[(connection.equipment_id, other_side_num)]]
        elif connection.equipment_type == ns.EquipmentType.THREE_WINDINGS_TRANSFORMER:
            other_sides = []
            for i in range(1, 4):
                if i != connection.side and (connection.equipment_id, i) in self._connections:
                    other_sides.append(self._connections[(connection.equipment_id, i)])
            return other_sides
        elif connection.equipment_type == ns.EquipmentType.DANGLING_LINE:
            return self._get_other_side_from_df(connection, self._tie_lines_df, 'dangling_line1_id',
                                                'dangling_line2_id')
        elif connection.equipment_type in [ns.EquipmentType.LCC_CONVERTER_STATION,
                                           ns.EquipmentType.VSC_CONVERTER_STATION]:
            return self._get_other_side_from_df(connection, self._hvdc_lines_df, 'converter_station1_id',
                                                'converter_station2_id')
        return []

    def _get_other_side_from_df(self, connection: ns.Connection, data_frame: pd.DataFrame, col1: str, col2: str) -> \
            List[ns.Connection]:
        for _, series in data_frame.iterrows():
            eq1 = str(series[col1])
            eq2 = str(series[col2])
            if connection.equipment_id == eq1:
                return [self._connections[(eq2, None)]]
            elif connection.equipment_id == eq2:
                return [self._connections[(eq1, None)]]
        return []

    def get_bus_breaker_topology(self, voltage_level: 'ns.VoltageLevel') -> pn.BusBreakerTopology:
        voltage_level_id: str = voltage_level.voltage_level_id
        if voltage_level_id in self._bus_breaker_topology_cache:
            return self._bus_breaker_topology_cache[voltage_level_id]
        topo = self.network.get_bus_breaker_topology(voltage_level_id)
        self._bus_breaker_topology_cache[voltage_level_id] = topo
        return topo
