#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
from typing import Any

import pandas as pd

from yagat.app_context import AppContext
from yagat.frames.impl.base_list_view import BaseListView, BaseColumnFormat


class AreaBoundariesListView(BaseListView):

    def __init__(self, parent, context: AppContext, *args, **kwargs):
        BaseListView.__init__(self, parent, context, *args, **kwargs)

    @property
    def tab_name(self) -> str:
        return 'Areas Boundaries'

    @property
    def tab_group_name(self) -> str:
        return 'Areas List'

    def get_data_frame(self) -> pd.DataFrame:
        return self.context.network_structure.areas_boundaries

    def get_column_formats(self) -> dict[str, BaseColumnFormat]:
        return super().get_column_formats()

    def on_entry(self, ident: str, column_name: str, new_value: Any):
        raise RuntimeError('Area Boundaries do not support update')

    def filter_data_frame(self, df: pd.DataFrame, voltage_levels: list[str]) -> pd.DataFrame:
        return df
