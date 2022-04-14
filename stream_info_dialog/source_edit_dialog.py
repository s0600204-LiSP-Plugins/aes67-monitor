# This file is a derivation of work on - and as such shares the same
# licence as - Linux Show Player
#
# Linux Show Player:
#   Copyright 2012-2022 Francesco Ceruti <ceppofrancy@gmail.com>
#
# This file:
#   Copyright 2022 s0600204
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
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLineEdit,
    QSpinBox,
)

from .node import StreamDirection
from .stream_edit_dialog import StreamEditDialog
from .ui import GroupHeader


class SourceEditDialog(StreamEditDialog):

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

    def __init__(self, *args, **kwargs):
        super().__init__(StreamDirection.SOURCE, *args, **kwargs)

        self.setMinimumWidth(350)

        # Meta
        self._meta_header = GroupHeader()
        self._meta_header.setText("Source")
        self.layout().addRow(self._meta_header)

        self._stream_name = QLineEdit()
        self.layout().addRow("Source Name:", self._stream_name)

        self._source_enabled = QCheckBox()
        self.layout().addRow("Source Enabled:", self._source_enabled)

        # Channels
        self._place_channel_widgets()

        # Audio Specification
        self._spec_header = GroupHeader()
        self._spec_header.setText("Audio Specification")
        self.layout().addRow(self._spec_header)

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
        self.layout().addRow(self._button_box)

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

    def clear(self):
        super().clear()
        self.setWindowTitle("Creating New Source")

        self._stream_name.setText("New Source")
        self._source_enabled.setChecked(True)

        self._spec_preset.setCurrentIndex(0)
        self._samples_per_packet.setCurrentIndex(0)
        self._ptp_traceable.setChecked(False)

    def deserialise(self, stream_definition):
        super().deserialise(stream_definition)
        self.setWindowTitle(f"Editing Source '{stream_definition['name']}'")

        # First, determine sound protocol
        if self._compare_preset(stream_definition, self._aes67_base):
            self._spec_preset.setCurrentIndex(0)
        elif self._compare_preset(stream_definition, self._dante_base):
            self._spec_preset.setCurrentIndex(1)
        else:
            self._spec_preset.setCurrentIndex(self._spec_preset.count() - 1)
            self._codec.setCurrentText(self._codecs[stream_definition['codec']])
            self._dscp.setCurrentText(self._dscp_values[stream_definition['dscp']])
            self._payload_type.setValue(stream_definition['payload_type'])
            self._ttl.setValue(stream_definition['ttl'])

        # Second, populate things
        self._source_enabled.setChecked(stream_definition['enabled'])
        self._stream_name.setText(stream_definition['name'])
        self._samples_per_packet.setCurrentText(str(stream_definition['max_samples_per_packet']))
        self._ptp_traceable.setChecked(stream_definition['refclk_ptp_traceable'])

    def serialise(self):
        start = self._channel_start.value() - 1
        return {
            "enabled": self._source_enabled.isChecked(),
            "name": self._stream_name.text(),
            "io": "Audio Device",
            "codec": self._codec.currentData(),
            "max_samples_per_packet": int(self._samples_per_packet.currentText()),
            "ttl": self._ttl.value(),
            "payload_type": self._payload_type.value(),
            "dscp": self._dscp.currentData(),
            "refclk_ptp_traceable": self._ptp_traceable.isChecked(),
            "map": [i + start for i in range(self._channel_count.value())],
        }

    def _compare_preset(self, stream_definition, compare_with):
        for key, value in compare_with.items():
            if stream_definition[key] != value:
                return False
        return True
