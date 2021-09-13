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

import requests

# pylint: disable=no-name-in-module
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QSpinBox,
)

from ..util import make_api_put_request
from .node import StreamDirection
from .ui import GroupHeader

class StreamEditDialog(QDialog):

    # The daemon/kernal advertises 128 channels, however only
    # the first 8 are usable (for some reason).
    # Attempting to attach to channel 9+ causes a HTTP 400
    STREAM_CHANNEL_LIMIT = 8

    def __init__(self, direction, plugin, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._direction = direction
        self._plugin = plugin
        self._editing_id = None

        self.setLayout(QFormLayout())

        # Audio Channel Bits
        self._channels_label = GroupHeader()
        self._channels_label.setText("ALSA Channels")

        self._channel_count = QSpinBox()
        self._channel_count.setRange(1, self.STREAM_CHANNEL_LIMIT)
        self._channel_count.valueChanged.connect(self._on_channel_count_change)

        self._channel_start = QSpinBox()
        self._channel_start.setRange(1, self.STREAM_CHANNEL_LIMIT)
        self._channel_start.valueChanged.connect(self._on_channel_start_change)

        self._channel_list = QLabel()

        # Buttons
        self._button_box = QDialogButtonBox()
        self._button_box.setStandardButtons(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self._button_box.accepted.connect(self.submit)
        self._button_box.rejected.connect(self.reject)

    def _place_channel_widgets(self):
        self.layout().addRow(self._channels_label)
        self.layout().addRow("Channel Count:", self._channel_count)
        self.layout().addRow("Start Channel:", self._channel_start)
        self.layout().addRow("Mapped Channels:", self._channel_list)

    def _on_channel_count_change(self, value):
        value -= 1
        self._channel_start.setMaximum(self.STREAM_CHANNEL_LIMIT - value)
        self._update_channel_message()

    def _on_channel_start_change(self, value):
        value -= 1
        self._channel_count.setMaximum(self.STREAM_CHANNEL_LIMIT - value)
        self._update_channel_message()

    def _update_channel_message(self):
        start = self._channel_start.value()
        self._channel_list.setText(
            ", ".join([str(i + start) for i in range(self._channel_count.value())])
        )

    def clear(self):
        self._editing_id = None
        self._channel_start.setValue(1)
        self._channel_count.setValue(2)

    def deserialise(self, stream_definition):
        self._editing_id = stream_definition['id']

        # Update channel mapping
        self._channel_start.setValue(1)
        self._channel_count.setValue(len(stream_definition['map']))
        self._channel_start.setValue(stream_definition['map'][0] + 1)

    def submit(self):
        if self._editing_id is not None:
            stream_id = self._editing_id
        else:
            stream_id = max(self.parent().local_stream_ids()) + 1

        reply = make_api_put_request(
            requests,
            self._plugin.address,
            'sink_edit' if self._direction == StreamDirection.SINK else 'source_edit',
            stream_id,
            self.serialise()
        )

        if reply:
            self.close()
        else:
            # todo: Implement error checking/messages
            print(reply)
