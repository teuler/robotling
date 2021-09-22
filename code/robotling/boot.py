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

import gc
gc.collect()
print("{0} of {1} bytes heap RAM used".format(gc.mem_alloc(), gc.mem_free()))
# ----------------------------------------------------------------------------
