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

import requests

# pylint: disable=no-name-in-module
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
)

from ..util import make_api_put_request
from .node import StreamDirection


class SourceEditDialog(QDialog):

    _aes67_base = {
        "codec": "L24",
        "dscp": 34,
        "payload_type": 98,
        "ttl": 15,
    }

    _dante_base = {
        "codec": "L16",
        "dscp": 46,
        "payload_type": 98,
        "ttl": 15,
    }

    # The daemon/kernal advertises 128 channels, however only
    # the first 8 are usable (for some reason).
    # Attempting to attach to channel 9+ causes a HTTP 400
    _channel_limit = 8

    _codecs = {
        "L16": "L16",
        "L24": "L24",
        "AM824": "L32 / AM824",
    }
    _dscp_values = {
        46: "46 (EF)",
        34: "34 (AF41)",
        26: "26 (AF31)",
        0:  "0 (BE)",
    }
    _packet_sample_sizes = [12, 16, 48, 96, 192]

    def __init__(self, plugin, **kwargs):
        super().__init__(**kwargs)
        self._plugin = plugin
        self._editing_id = None

        self.setMinimumWidth(350)
        self.setLayout(QFormLayout())

        # Meta
        self._meta_label = QLabel()
        self._meta_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._meta_label.setIndent(2)
        self._meta_label.setMargin(2)
        self._meta_label.setText("Source")
        self.layout().addRow(self._meta_label)

        self._source_name = QLineEdit()
        self.layout().addRow("Source Name:", self._source_name)

        self._source_enabled = QCheckBox()
        self.layout().addRow("Source Enabled:", self._source_enabled)

        # Channels
        self._channels_label = QLabel()
        self._channels_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._channels_label.setIndent(4)
        self._channels_label.setMargin(2)
        self._channels_label.setText("ALSA Channels")
        self.layout().addRow(self._channels_label)

        self._channel_count = QSpinBox()
        self._channel_count.setRange(1, self._channel_limit)
        self._channel_count.valueChanged.connect(self._on_channel_count_change)
        self.layout().addRow("Channel Count:", self._channel_count)

        self._channel_start = QSpinBox()
        self._channel_start.setRange(1, self._channel_limit)
        self._channel_start.valueChanged.connect(self._on_channel_start_change)
        self.layout().addRow("Start Channel:", self._channel_start)

        self._channel_list = QLabel()
        self.layout().addRow("Mapped Channels:", self._channel_list)

        # Audio Specification
        self._spec_label = QLabel()
        self._spec_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._spec_label.setIndent(4)
        self._spec_label.setMargin(2)
        self._spec_label.setText("Audio Specification")
        self.layout().addRow(self._spec_label)

        self._spec_preset = QComboBox()
        self._spec_preset.addItem("AES67")
        self._spec_preset.addItem("Dante")
        self._spec_preset.addItem("Custom...")
        self._spec_preset.setCurrentIndex(-1)
        self._spec_preset.setDisabled(True)
        self._spec_preset.currentIndexChanged.connect(self._on_spec_idx_change)
        self.layout().addRow("Presets:", self._spec_preset)

        self._samples_per_packet = QComboBox()
        for sample in self._packet_sample_sizes:
            self._samples_per_packet.addItem(str(sample))
        self.layout().addRow("Max Samples per Packet:", self._samples_per_packet)

        self._ptp_traceable = QCheckBox()
        self.layout().addRow("PTP Traceable:", self._ptp_traceable)

        self._codec = QComboBox()
        for codec, caption in self._codecs.items():
            self._codec.addItem(caption, codec)
        self.layout().addRow("Codec:", self._codec)

        self._dscp = QComboBox()
        for dscp, caption in self._dscp_values.items():
            self._dscp.addItem(caption, dscp)
        self.layout().addRow("DSCP:", self._dscp)

        self._payload_type = QSpinBox()
        self._payload_type.setRange(77, 127)
        self.layout().addRow("Payload Type:", self._payload_type)

        self._ttl = QSpinBox()
        self._ttl.setMinimum(1)
        self.layout().addRow("TTL:", self._ttl)

        # Buttons
        self._button_box = QDialogButtonBox()
        self._button_box.setStandardButtons(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self._button_box.accepted.connect(self.submit)
        self._button_box.rejected.connect(self.reject)
        self.layout().addRow(self._button_box)

    def _on_channel_count_change(self, value):
        value -= 1
        self._channel_start.setMaximum(self._channel_limit - value)
        self._update_channel_message()

    def _on_channel_start_change(self, value):
        value -= 1
        self._channel_count.setMaximum(self._channel_limit - value)
        self._update_channel_message()

    def _update_channel_message(self):
        start = self._channel_start.value()
        self._channel_list.setText(
            ", ".join([str(i + start) for i in range(self._channel_count.value())])
        )

    def _on_spec_idx_change(self, idx):
        is_custom = idx == self._spec_preset.count() - 1
        self._codec.setEnabled(is_custom)
        self._dscp.setEnabled(is_custom)
        self._payload_type.setEnabled(is_custom)
        self._ttl.setEnabled(is_custom)
        if is_custom:
            return

        preset = self._aes67_base
        if self._spec_preset.currentText() == "Dante": # todo: Don't compare on the text.
            preset = self._dante_base

        self._codec.setCurrentText(self._codecs[preset['codec']])
        self._dscp.setCurrentText(self._dscp_values[preset['dscp']])
        self._payload_type.setValue(preset['payload_type'])
        self._ttl.setValue(preset['ttl'])

    def submit(self):
        if self._editing_id is not None:
            stream_id = self._editing_id
        else:
            stream_id = max(self.parent().local_stream_ids(StreamDirection.SOURCE)) + 1

        reply = make_api_put_request(
            requests,
            self._plugin.address,
            'source_edit',
            stream_id,
            self.serialise()
        )

        if reply:
            self.close()
        else:
            # todo: Implement error checking/messages
            print(reply)

    def clear(self):
        self._editing_id = None
        self.setWindowTitle("Creating New Source")

        self._source_name.setText("New Source")
        self._source_enabled.setChecked(True)

        self._channel_start.setValue(1)
        self._channel_count.setValue(2)

        self._spec_preset.setCurrentIndex(0)
        self._samples_per_packet.setCurrentIndex(0)
        self._ptp_traceable.setChecked(False)

    def deserialise(self, source_json):
        self._editing_id = source_json['id']
        self.setWindowTitle(f"Editing Source '{source_json['name']}'")

        # First, determine sound protocol
        if self._compare_preset(source_json, self._aes67_base):
            self._spec_preset.setCurrentIndex(0)
        elif self._compare_preset(source_json, self._dante_base):
            self._spec_preset.setCurrentIndex(1)
        else:
            self._spec_preset.setCurrentIndex(self._spec_preset.count() - 1)
            self._codec.setCurrentText(self._codecs[source_json['codec']])
            self._dscp.setCurrentText(self._dscp_values[source_json['dscp']])
            self._payload_type.setValue(source_json['payload_type'])
            self._ttl.setValue(source_json['ttl'])

        # Second, populate things
        self._source_enabled.setChecked(source_json['enabled'])
        self._source_name.setText(source_json['name'])
        self._samples_per_packet.setCurrentText(str(source_json['max_samples_per_packet']))
        self._ptp_traceable.setChecked(source_json['refclk_ptp_traceable'])

        # Third, update channel mapping
        self._channel_start.setValue(1)
        self._channel_count.setValue(len(source_json['map']))
        self._channel_start.setValue(source_json['map'][0] + 1)

    def serialise(self):
        start = self._channel_start.value() - 1
        return {
            "enabled": self._source_enabled.isChecked(),
            "name": self._source_name.text(),
            "io": "Audio Device",
            "codec": self._codec.currentData(),
            "max_samples_per_packet": int(self._samples_per_packet.currentText()),
            "ttl": self._ttl.value(),
            "payload_type": self._payload_type.value(),
            "dscp": self._dscp.currentData(),
            "refclk_ptp_traceable": self._ptp_traceable.isChecked(),
            "map": [i + start for i in range(self._channel_count.value())],
        }

    def _compare_preset(self, json_data, compare_with):
        for key, value in compare_with.items():
            if json_data[key] != value:
                return False
        return True
