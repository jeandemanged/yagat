#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
from enum import StrEnum


class BusView(StrEnum):
    BUS_BREAKER = 'BUS_BREAKER'
    BUS_BRANCH = 'BUS_BRANCH'
