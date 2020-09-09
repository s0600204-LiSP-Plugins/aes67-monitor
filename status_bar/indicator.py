# This file is a derivation of work on - and as such shares the same
# licence as - Linux Show Player
#
# Linux Show Player:
#   Copyright 2012-2020 Francesco Ceruti <ceppofrancy@gmail.com>
#
# This file:
#   Copyright 2020 s0600204
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

import logging

import requests

# pylint: disable=import-error
from lisp.ui.mainwindow import MainStatusBar

from ..util import StatusEnum, make_api_get_request
from .widget import StatusBarWidget

logger = logging.getLogger(__name__) # pylint: disable=invalid-name

SINK_FLAGS = {
    "rtp_seq_id_error": {
        'status': StatusEnum.ERROR,
        'tooltip': "Incorrect RTP sequence",
    },
    "rtp_ssrc_error": {
        'status': StatusEnum.ERROR,
        'tooltip': "Received data from unexpected source",
    },
    "rtp_payload_type_error": {
        'status': StatusEnum.ERROR,
        'tooltip': "Unexpected payload type",
    },
    "rtp_sac_error": {
        'status': StatusEnum.ERROR,
        'tooltip': "Packet with invalid timestamp",
    },
    "receiving_rtp_packet": {
        'status': StatusEnum.NORMAL,
        'tooltip': "Receiving Audio",
    },
    "some_muted": {
        'status': StatusEnum.DEBUG,
        'tooltip': "Unused flag",
    },
    "all_muted": {
        'status': StatusEnum.DEBUG,
        'tooltip': "Unused flag",
    },
    "muted": {
        'status': StatusEnum.NORMAL,
        'tooltip': "Audio stream muted",
    },
}


class StatusBarIndicator:

    def __init__(self, plugin):
        self._plugin = plugin
        self._widget = None

    def show(self):
        if not self._widget:
            self._widget = StatusBarWidget()
        self._plugin.poller.add_callback('ptp_status', self.update_ptp)
        self._plugin.poller.add_callback('streams', self.update_sinks)

        # MainWindow > .statusBar > MainStatusBar
        status_bar = self._plugin.app.window.statusBar().findChild(MainStatusBar)
        status_layout = status_bar.layout()
        status_layout.layout().insertWidget(status_layout.count() - 2, self._widget)

    def hide(self):
        if not self._widget:
            return
        self._plugin.poller.remove_callback('ptp_status', self.update_ptp)
        self._plugin.poller.remove_callback('streams', self.update_sinks)

        status_bar = self._plugin.app.window.statusBar().findChild(MainStatusBar)
        status_layout = status_bar.layout()
        status_layout.layout().removeWidget(self._widget)

    def update_ptp(self, json):
        if not json:
            self._widget.clear()
            return

        self._widget.update_ptp_status({
            'locked': {
                'status': StatusEnum.NORMAL,
                'tooltip': "Locked",
            },
            'unlocked': {
                'status': StatusEnum.ERROR,
                'tooltip': "None",
            },
            'locking': {
                'status': StatusEnum.WARNING,
                'tooltip': "Connecting...",
            },
        }.get(json['status']))

    def update_sinks(self, json):
        if not json:
            return

        overall_status = StatusEnum.NORMAL
        overall_tooltip = ""

        # @todo: reuse from poller (somehow)
        session = requests.session()
        address = self._plugin.address

        for sink in json['sinks']:
            sink_reply = make_api_get_request(session, address, 'sink_status', sink['id'])
            sink_tooltip = f"\n#{sink['id']}: {sink['name']}"

            for flag_name, flag_value in sink_reply.json()['sink_flags'].items():
                level = SINK_FLAGS.get(flag_name, StatusEnum.UNKNOWN)

                if level == StatusEnum.UNKNOWN:
                    logger.debug(f"Unrecognised flag '{flag_name}' (on Sink #{sink['id']} '{sink['name']}')")
                    continue

                if not flag_value:
                    continue

                sink_tooltip += f"\n    • {level['tooltip']}"

                if level['status'] == StatusEnum.NORMAL:
                    continue

                if level['status'] == StatusEnum.ERROR:
                    # .warning instead of .error, as the latter causes a dialog box to appear
                    logger.warning(f"{level['tooltip']} on Sink #{sink['id']} ('{sink['name']}') [{flag_name}]")
                    overall_status = StatusEnum.ERROR

                elif level['status'] == StatusEnum.WARNING:
                    logger.warning(f"{level['tooltip']} on Sink #{sink['id']} ('{sink['name']}') [{flag_name}]")
                    if overall_status != StatusEnum.ERROR:
                        overall_status = StatusEnum.WARNING

                elif level['status'] == StatusEnum.DEBUG:
                    logger.debug(f"{level['tooltip']} on Sink #{sink['id']} ('{sink['name']}') [{flag_name}]")

            overall_tooltip += sink_tooltip

        self._widget.update_sinks_status({
            'status': overall_status,
            'tooltip': overall_tooltip,
        })
