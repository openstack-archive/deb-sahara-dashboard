# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 Mirantis Inc.
#
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

from horizon import tabs

from savannadashboard.utils import importutils
nova = importutils.import_any('openstack_dashboard.api.nova',
                              'horizon.api.nova')


from savannadashboard.api import client as savannaclient

LOG = logging.getLogger(__name__)


class GeneralTab(tabs.Tab):
    name = _("General Info")
    slug = "cluster_details_tab"
    template_name = ("clusters/_details.html")

    def get_context_data(self, request):
        cluster_id = self.tab_group.kwargs['cluster_id']
        savanna = savannaclient.Client(request)
        cluster = savanna.clusters.get(cluster_id)
        return {"cluster": cluster}


class NodeGroupsTab(tabs.Tab):
    name = _("Node Groups")
    slug = "cluster_nodegroups_tab"
    template_name = ("clusters/_nodegroups_details.html")

    def get_context_data(self, request):
        cluster_id = self.tab_group.kwargs['cluster_id']
        savanna = savannaclient.Client(request)
        cluster = savanna.clusters.get(cluster_id)
        for ng in cluster.node_groups:
            if not ng["flavor_id"]:
                continue
            ng["flavor_name"] = nova.flavor_get(request, ng["flavor_id"]).name
        return {"cluster": cluster}


class ClusterDetailsTabs(tabs.TabGroup):
    slug = "cluster_details"
    tabs = (GeneralTab, NodeGroupsTab, )
    sticky = True
