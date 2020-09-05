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

import enum
import logging

import requests

# pylint: disable=import-error
from lisp.core.clock import Clock
from lisp.core.plugin import Plugin
from lisp.core.util import compose_url
from lisp.ui.mainwindow import MainStatusBar

from .status_bar_widget import StatusBarWidget
from .util import StatusEnum

logger = logging.getLogger(__name__) # pylint: disable=invalid-name

SCHEME = "http"

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

class Aes67Monitor(Plugin):
    """Provides the ability to monitor AES67 connections"""

    Name = 'AES67 Daemon Monitor'
    Authors = ('s0600204',)
    Depends = ()
    Description = 'Monitors a running AES67 Daemon'

    def __init__(self, app):
        super().__init__(app)

        self.interval = Clock(2000)
        self.ip = "127.0.0.1"
        self.port = 8080

        self.status_bar_widget = None

        self.add_status_bar_widget()
        self.interval.add_callback(self.run_status_update)

    def add_status_bar_widget(self):
        # MainWindow > .statusBar > MainStatusBar
        status_bar = self.app.window.statusBar().findChild(MainStatusBar)
        status_layout = status_bar.layout()
        self.status_bar_widget = StatusBarWidget(status_bar)
        status_layout.layout().insertWidget(status_layout.count() - 2, self.status_bar_widget)

    def run_status_update(self):
        with requests.Session() as session:

            ptp = self.fetch_ptp_status(session)

            if not ptp:
                self.status_bar_widget.clear()
                return

            sinks = self.fetch_sink_status(session)

            self.status_bar_widget.update(ptp=ptp, sinks=sinks)

    def fetch_ptp_status(self, session):
        url = compose_url(SCHEME, self.ip, self.port, "/api/ptp/status")
        try:
            reply = session.get(url)
        except requests.ConnectionError:
            return False

        return {
            'locked': StatusEnum.NORMAL,
            'unlocked': StatusEnum.ERROR,
            'locking': StatusEnum.WARNING,
        }.get(reply.json()['status'])

    def fetch_sink_status(self, session):
        url = compose_url(SCHEME, self.ip, self.port, "/api/sinks")
        try:
            reply = session.get(url)
        except requests.ConnectionError:
            return False

        overall_status = StatusEnum.NORMAL
        sinks = reply.json()['sinks']
        for sink in sinks:
            sink_url = compose_url(SCHEME, self.ip, self.port, f"/api/sink/status/{sink['id']}")
            sink_reply = session.get(sink_url)

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
