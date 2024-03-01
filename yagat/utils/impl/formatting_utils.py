#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
def format_v_mag(value: float):
    return _repl_nan(f'{value:.2f}')


def format_v_angle(value: float):
    return _repl_nan(f'{value:.3f}')


def format_power(value: float):
    return _repl_nan(f'{value:.1f}')


def _repl_nan(value: str):
    return value.replace('nan', '-')
