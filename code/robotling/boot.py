# ----------------------------------------------------------------------------
# Copyright [2017] [Mauro Riva <lemariva@mail.com> <lemariva.com>]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# boot.py -- run on boot-up
# ----------------------------------------------------------------------------
# Disable debugging information
try:
  import esp
  esp.osdebug(None)
except ImportError:
  pass

# WLAN access
try:
  from NETWORK import my_ssid, my_wp2_pwd
except ImportError:
  pass

def do_connect():
  import network
  sta_if = network.WLAN(network.STA_IF)
  if not sta_if.isconnected():
    print('Connecting to network...')
    sta_if.active(True)
    sta_if.connect(my_ssid, my_wp2_pwd)
    while not sta_if.isconnected():
      pass
    print('Network config:', sta_if.ifconfig())

# REPL via WLAN
"""
do_connect()
import webrepl
webrepl.start()
"""
# ----------------------------------------------------------------------------
