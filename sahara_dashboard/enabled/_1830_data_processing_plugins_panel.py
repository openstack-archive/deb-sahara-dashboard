# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from sahara_dashboard import exceptions

# The slug of the panel to be added to HORIZON_CONFIG. Required.
PANEL = 'data_processing.data_plugins'
# The slug of the dashboard the PANEL associated with. Required.
PANEL_DASHBOARD = 'project'
# The slug of the panel group the PANEL is associated with.
PANEL_GROUP = 'data_processing'

# Python panel class of the PANEL to be added.
ADD_PANEL = \
    ('sahara_dashboard.'
     'content.data_processing.data_plugins.panel.PluginsPanel')

ADD_INSTALLED_APPS = \
    ["sahara_dashboard.content.data_processing.data_plugins", ]

ADD_EXCEPTIONS = {
    'recoverable': exceptions.RECOVERABLE
}
