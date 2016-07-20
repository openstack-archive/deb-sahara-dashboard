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

from horizon import exceptions
from horizon import forms
from horizon import workflows

from django.utils.translation import ugettext_lazy as _
from saharaclient.api import base as api_base

from openstack_dashboard.api import nova

from sahara_dashboard.content.data_processing.utils \
    import acl as acl_utils
from sahara_dashboard.content.data_processing.utils import neutron_support
import sahara_dashboard.content.data_processing.utils. \
    workflow_helpers as whelpers
from sahara_dashboard.api import sahara as saharaclient
import sahara_dashboard.content.data_processing.clusters. \
    cluster_templates.workflows.create as t_flows


KEYPAIR_IMPORT_URL = "horizon:project:access_and_security:keypairs:import"
BASE_IMAGE_URL = "horizon:project:data_processing.clusters:register"
TEMPLATE_UPLOAD_URL = (
    "horizon:project:data_processing.clusters:upload_file")


class SelectPluginAction(t_flows.SelectPluginAction):
    class Meta(object):
        name = _("Select plugin and hadoop version for cluster")
        help_text_template = "clusters/_create_general_help.html"


class SelectPlugin(t_flows.SelectPlugin):
    action_class = SelectPluginAction


class CreateCluster(t_flows.CreateClusterTemplate):
    slug = "create_cluster"
    name = _("Launch Cluster")
    success_url = "horizon:project:data_processing.clusters:clusters-tab"
    default_steps = (SelectPlugin,)


class GeneralConfigAction(workflows.Action):
    populate_neutron_management_network_choices = \
        neutron_support.populate_neutron_management_network_choices

    hidden_configure_field = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"class": "hidden_configure_field"}))

    hidden_to_delete_field = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"class": "hidden_to_delete_field"}))

    cluster_name = forms.CharField(label=_("Cluster Name"))

    description = forms.CharField(label=_("Description"),
                                  required=False,
                                  widget=forms.Textarea(attrs={'rows': 4}))
    cluster_template = forms.DynamicChoiceField(label=_("Cluster Template"),
                                                initial=(None, "None"),
                                                add_item_link=
                                                TEMPLATE_UPLOAD_URL)

    cluster_count = forms.IntegerField(min_value=1,
                                       label=_("Cluster Count"),
                                       initial=1,
                                       help_text=(
                                           _("Number of clusters to launch.")))

    image = forms.DynamicChoiceField(label=_("Base Image"),
                                     add_item_link=BASE_IMAGE_URL)

    keypair = forms.DynamicChoiceField(
        label=_("Keypair"),
        required=False,
        help_text=_("Which keypair to use for authentication."),
        add_item_link=KEYPAIR_IMPORT_URL)

    def __init__(self, request, *args, **kwargs):
        super(GeneralConfigAction, self).__init__(request, *args, **kwargs)

        plugin, hadoop_version = whelpers.\
            get_plugin_and_hadoop_version(request)

        if saharaclient.base.is_service_enabled(request, 'network'):
            self.fields["neutron_management_network"] = forms.ChoiceField(
                label=_("Neutron Management Network"),
                choices=self.populate_neutron_management_network_choices(
                    request, {})
            )

        self.fields['is_public'] = acl_utils.get_is_public_form(
            _("cluster"))
        self.fields['is_protected'] = acl_utils.get_is_protected_form(
            _("cluster"))

        self.fields["plugin_name"] = forms.CharField(
            widget=forms.HiddenInput(),
            initial=plugin
        )
        self.fields["hadoop_version"] = forms.CharField(
            widget=forms.HiddenInput(),
            initial=hadoop_version
        )

    def populate_image_choices(self, request, context):
        return whelpers.populate_image_choices(self, request, context)

    def populate_keypair_choices(self, request, context):
        try:
            keypairs = nova.keypair_list(request)
        except Exception:
            keypairs = []
            exceptions.handle(request,
                              _("Unable to fetch keypair choices."))
        keypair_list = [(kp.name, kp.name) for kp in keypairs]
        keypair_list.insert(0, ("", _("No keypair")))

        return keypair_list

    def populate_cluster_template_choices(self, request, context):
        templates = saharaclient.cluster_template_list(request)

        plugin, hadoop_version = whelpers.\
            get_plugin_and_hadoop_version(request)

        choices = [(template.id, template.name)
                   for template in templates
                   if (template.hadoop_version == hadoop_version and
                       template.plugin_name == plugin)]

        if not choices:
            choices.append(("", _("No Templates Available")))
        # cluster_template_id comes from cluster templates table, when
        # Create Cluster from template is clicked there
        selected_template_name = None
        req = request.GET or request.POST
        if req.get("cluster_template_name"):
            selected_template_name = (
                req.get("cluster_template_name"))
        if selected_template_name:
            for template in templates:
                if template.name == selected_template_name:
                    selected_template_id = template.id
                    break
        else:
            selected_template_id = (
                req.get("cluster_template_id", None))

        for template in templates:
            if template.id == selected_template_id:
                self.fields['cluster_template'].initial = template.id

        return choices

    def get_help_text(self):
        extra = dict()
        plugin, hadoop_version = whelpers.\
            get_plugin_and_hadoop_version(self.request)
        extra["plugin_name"] = plugin
        extra["hadoop_version"] = hadoop_version
        return super(GeneralConfigAction, self).get_help_text(extra)

    def clean(self):
        cleaned_data = super(GeneralConfigAction, self).clean()
        if cleaned_data.get("hidden_configure_field", None) \
                == "create_nodegroup":
            self._errors = dict()
        return cleaned_data

    class Meta(object):
        name = _("Configure Cluster")
        help_text_template = "clusters/_configure_general_help.html"


class GeneralConfig(workflows.Step):
    action_class = GeneralConfigAction
    contributes = ("hidden_configure_field", )

    def contribute(self, data, context):
        for k, v in data.items():
            context["general_" + k] = v

        return context


class ConfigureCluster(whelpers.StatusFormatMixin, workflows.Workflow):
    slug = "configure_cluster"
    name = _("Launch Cluster")
    finalize_button_name = _("Launch")
    success_message = _("Launched Cluster %s")
    name_property = "general_cluster_name"
    success_url = "horizon:project:data_processing.clusters:clusters-tab"
    default_steps = (GeneralConfig, )

    def handle(self, request, context):
        try:
            # TODO(nkonovalov) Implement AJAX Node Groups.
            node_groups = None

            plugin, hadoop_version = whelpers.\
                get_plugin_and_hadoop_version(request)

            cluster_template_id = context["general_cluster_template"] or None
            user_keypair = context["general_keypair"] or None
            image_id = context["general_image"] or None
            saharaclient.cluster_create(
                request,
                context["general_cluster_name"],
                plugin, hadoop_version,
                cluster_template_id=cluster_template_id,
                default_image_id=image_id,
                description=context["general_description"],
                node_groups=node_groups,
                user_keypair_id=user_keypair,
                count=context['general_cluster_count'],
                net_id=context.get("general_neutron_management_network", None),
                is_public=context['general_is_public'],
                is_protected=context['general_is_protected']
            )
            return True
        except api_base.APIException as e:
            self.error_description = str(e)
            return False
        except Exception:
            exceptions.handle(request,
                              _('Unable to create the cluster'))
            return False
