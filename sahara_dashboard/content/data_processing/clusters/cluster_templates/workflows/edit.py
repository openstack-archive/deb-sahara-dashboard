# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms

from sahara_dashboard.api import sahara as saharaclient
import sahara_dashboard.content.data_processing.clusters. \
    cluster_templates.workflows.create as create_flow
import sahara_dashboard.content.data_processing.clusters. \
    cluster_templates.workflows.copy as copy_flow
import sahara_dashboard.content.data_processing. \
    utils.workflow_helpers as whelpers
from sahara_dashboard import utils


class EditClusterTemplate(copy_flow.CopyClusterTemplate):
    success_message = _("Cluster Template %s updated")
    entry_point = "generalconfigaction"
    finalize_button_name = _("Update")
    name = _("Edit Cluster Template")

    def __init__(self, request, context_seed, entry_point, *args, **kwargs):
        try:
            super(EditClusterTemplate, self).__init__(request, context_seed,
                                                      entry_point, *args,
                                                      **kwargs)

            for step in self.steps:
                if isinstance(step, create_flow.GeneralConfig):
                    fields = step.action.fields
                    fields["cluster_template_name"].initial = (
                        self.template.name)
                    fields["cluster_template_id"] = forms.CharField(
                        widget=forms.HiddenInput(),
                        initial=self.cluster_template_id)
                elif isinstance(step, create_flow.SelectDnsDomains):
                    fields = step.action.fields
                    fields["domain_name"].initial = self.template.domain_name
        except Exception:
            exceptions.handle(request,
                              _("Unable to fetch template to edit."))

    def handle(self, request, context):
        try:
            node_groups = []
            configs_dict = whelpers.parse_configs_from_context(context,
                                                               self.defaults)
            ids = json.loads(context['ng_forms_ids'])
            for id in ids:
                name = context['ng_group_name_' + str(id)]
                template_id = context['ng_template_id_' + str(id)]
                count = context['ng_count_' + str(id)]

                raw_ng = context.get("ng_serialized_" + str(id))

                if raw_ng and raw_ng != 'null':
                    ng = json.loads(utils.deserialize(str(raw_ng)))
                else:
                    ng = dict()
                ng["name"] = name
                ng["count"] = count
                if template_id and template_id != u'None':
                    ng["node_group_template_id"] = template_id
                node_groups.append(ng)

            plugin, hadoop_version = whelpers. \
                get_plugin_and_hadoop_version(request)

            ct_shares = []
            if "ct_shares" in context:
                ct_shares = context["ct_shares"]

            domain = context.get('dns_domain_name', None)
            if domain == 'None':
                domain = None

            saharaclient.cluster_template_update(
                request=request,
                ct_id=self.cluster_template_id,
                name=context["general_cluster_template_name"],
                plugin_name=plugin,
                hadoop_version=hadoop_version,
                description=context["general_description"],
                cluster_configs=configs_dict,
                node_groups=node_groups,
                anti_affinity=context["anti_affinity_info"],
                use_autoconfig=context['general_use_autoconfig'],
                shares=ct_shares,
                is_public=context['general_is_public'],
                is_protected=context['general_is_protected'],
                domain_name=domain
            )
            return True
        except exceptions.Conflict as e:
            self.error_description = str(e)
            return False
        except Exception:
            exceptions.handle(request,
                              _("Cluster template update failed"))
            return False
