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

# pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QAction

# pylint: disable=import-error
from lisp.core.plugin import Plugin
from lisp.core.util import compose_url
from lisp.ui.settings.app_configuration import AppConfigurationDialog

from aes67_monitor.poller import DaemonPoller
from aes67_monitor.settings_page import Aes67Settings
from aes67_monitor.stream_info_dialog.dialog import StreamInfoDialog
from aes67_monitor.status_bar.indicator import StatusBarIndicator

class Aes67Monitor(Plugin):
    """Provides the ability to monitor AES67 connections"""

    Name = 'AES67 Daemon Monitor'
    Authors = ('s0600204',)
    Depends = ()
    Description = 'Monitors a running AES67 Daemon'

    SCHEME = "http"

    def __init__(self, app):
        super().__init__(app)

        self._daemon_name = None

        # Register the settings widget
        AppConfigurationDialog.registerSettingsPage(
            'plugins.aes67_monitor', Aes67Settings, Aes67Monitor.Config)

        self.poller = DaemonPoller(self)
        self.poller.add_callback('config', self._update_daemon_name)

        self.indicator = StatusBarIndicator(self)
        self.indicator.show()

        self._info_dialog = None

        self._info_menu_action = QAction('AES67 Audio Streams', self.app.window)
        self._info_menu_action.triggered.connect(self._open_info_dialog)
        self.app.window.menuTools.addAction(self._info_menu_action)

    @property
    def address(self):
        return compose_url(self.SCHEME, self.Config["daemon_ip"], self.Config["daemon_port"])

    @property
    def ip(self):
        return self.Config["daemon_ip"]

    @property
    def daemon_name(self):
        return self._daemon_name

    def _update_daemon_name(self, config_json):
        self._daemon_name = config_json['node_id'] if config_json else None

    def _open_info_dialog(self):
        if not self._info_dialog:
            self._info_dialog = StreamInfoDialog(self)
        self._info_dialog.open()
