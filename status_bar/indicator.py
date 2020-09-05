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
from lisp.core.clock import Clock
from lisp.core.util import compose_url
from lisp.ui.mainwindow import MainStatusBar

from ..util import StatusEnum
from .widget import StatusBarWidget

logger = logging.getLogger(__name__) # pylint: disable=invalid-name

UPDATE_INTERVAL = 2000 # milliseconds

SINK_FLAGS = {
    "rtp_seq_id_error": StatusEnum.ERROR,
    "rtp_ssrc_error": StatusEnum.ERROR,
    "rtp_payload_type_error": StatusEnum.ERROR,
    "rtp_sac_error": StatusEnum.ERROR,
    "receiving_rtp_packet": StatusEnum.NORMAL,
    "some_muted": StatusEnum.DEBUG,
    "all_muted": StatusEnum.DEBUG,
    "muted": StatusEnum.NORMAL,
}


class StatusBarIndicator:

    ptp_api_path = "api/ptp/status"
    sinks_api_path = "api/sinks"
    sink_status_api_path = "api/sink/status/"

    def __init__(self, plugin):
        self._plugin = plugin
        self._clock = Clock(UPDATE_INTERVAL)
        self._widget = None

    def show(self):
        if not self._widget:
            self._widget = StatusBarWidget()
        self._clock.add_callback(self.run_update)

        # MainWindow > .statusBar > MainStatusBar
        status_bar = self._plugin.app.window.statusBar().findChild(MainStatusBar)
        status_layout = status_bar.layout()
        status_layout.layout().insertWidget(status_layout.count() - 2, self._widget)

    def hide(self):
        if not self._widget:
            return
        self._clock.remove_callback(self.run_update)

        status_bar = self._plugin.app.window.statusBar().findChild(MainStatusBar)
        status_layout = status_bar.layout()
        status_layout.layout().removeWidget(self._widget)

    def run_update(self):
        with requests.Session() as session:
            address = self._plugin.address
            ptp = self.fetch_ptp_status(session, address)
            if not ptp:
                self._widget.clear()
                return

            self._widget.update(
                ptp=ptp,
                sinks=self.fetch_sink_status(session, address)
            )

    def fetch_ptp_status(self, session, address):
        try:
            reply = session.get(address + self.ptp_api_path)
        except requests.ConnectionError:
            return False

        return {
            'locked': StatusEnum.NORMAL,
            'unlocked': StatusEnum.ERROR,
            'locking': StatusEnum.WARNING,
        }.get(reply.json()['status'])

    def fetch_sink_status(self, session, address):
        try:
            reply = session.get(address + self.sinks_api_path)
        except requests.ConnectionError:
            return False

        overall_status = StatusEnum.NORMAL
        sinks = reply.json()['sinks']
        for sink in sinks:
            sink_reply = session.get(address + self.sink_status_api_path + str(sink['id']))

            for flag_name, flag_value in sink_reply.json()['sink_flags'].items():
                level = SINK_FLAGS.get(flag_name, StatusEnum.UNKNOWN)

                if level == StatusEnum.UNKNOWN:
                    logger.debug(f"Unrecognised flag: {flag_name}")
                    continue

                if not flag_value or level == StatusEnum.NORMAL:
                    continue

                if level == StatusEnum.ERROR:
                    # .warning instead of .error, as the latter causes a dialog box to appear
                    logger.warning(f"{sink['id']} ({sink['name']}) : {flag_name}")
                    overall_status = StatusEnum.ERROR

                elif level == StatusEnum.WARNING:
                    logger.warning(f"{sink['id']} ({sink['name']}) : {flag_name}")
                    if overall_status != StatusEnum.ERROR:
                        overall_status = StatusEnum.WARNING

                elif level == StatusEnum.DEBUG:
                    logger.debug(f"{sink['id']} ({sink['name']}) : {flag_name}")

        return overall_status

