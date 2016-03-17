# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from sahara_dashboard.api import sahara as saharaclient
from sahara_dashboard.content.data_processing.jobs.data_sources \
    import tables as data_source_tables
from sahara_dashboard.content.data_processing \
    import tabs as sahara_tabs

LOG = logging.getLogger(__name__)


class DataSourcesTab(sahara_tabs.SaharaTableTab):
    table_classes = (data_source_tables.DataSourcesTable, )
    name = _("Data Sources")
    slug = "data_sources_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_data_sources_data(self):
        try:
            data_sources = saharaclient.data_source_list(self.request)
        except Exception:
            data_sources = []
            exceptions.handle(self.request,
                              _("Unable to fetch data source list"))
        return data_sources


class GeneralTab(tabs.Tab):
    name = _("General Info")
    slug = "data_source_details_tab"
    template_name = "data_sources/_details.html"

    def get_context_data(self, request):
        data_source_id = self.tab_group.kwargs['data_source_id']
        try:
            data_source = saharaclient.data_source_get(request, data_source_id)
        except Exception as e:
            data_source = {}
            LOG.error("Unable to fetch data source details: %s" % str(e))

        return {"data_source": data_source}


class DataSourceDetailsTabs(tabs.TabGroup):
    slug = "data_source_details"
    tabs = (GeneralTab,)
    sticky = True
