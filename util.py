# This file is a derivation of work on - and as such shares the same
# licence as - Linux Show Player
#
# Linux Show Player:
#   Copyright 2012-2021 Francesco Ceruti <ceppofrancy@gmail.com>
#
# This file:
#   Copyright 2021 s0600204
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=missing-docstring

from enum import Enum

import requests


API_PATHS = {
    'config': "api/config",
    'ptp_status': "api/ptp/status",
    'remote_sources': "api/browse/sources/all",
    'sink_edit': "api/sink/",
    'sink_status': "api/sink/status/",
    'source_edit': "api/source/",
    'streams': "api/streams",
}

class StatusEnum(Enum):
    DEBUG = -2
    UNKNOWN = -1
    NORMAL = 0
    WARNING = 1
    ERROR = 2

def make_api_get_request(session, address, what, opt_arg=None):
    path = API_PATHS.get(what)
    if not path:
        return None

    try:
        if opt_arg is not None:
            return session.get(f"{address}{path}{opt_arg}")
        return session.get(f"{address}{path}")
    except requests.ConnectionError:
        return None

def make_api_put_request(session, address, what, arg, json_data):
    if not arg or not json_data:
        return None

    path = API_PATHS.get(what)
    if not path:
        return None

    try:
        return session.put(f"{address}{path}{arg}", json=json_data)
    except requests.ConnectionError:
        return None

def make_api_delete_request(session, address, what, arg):
    if not arg:
        return None

    path = API_PATHS.get(what)
    if not path:
        return None

    try:
        return session.delete(f"{address}{path}{arg}")
    except requests.ConnectionError:
        return None
