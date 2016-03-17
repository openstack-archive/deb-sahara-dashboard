from django.utils.translation import ugettext_lazy as _

# The slug of the panel group to be added to HORIZON_CONFIG. Required.
PANEL_GROUP = 'data_processing'
# The display name of the PANEL_GROUP. Required.
PANEL_GROUP_NAME = _('Data Processing')
# The slug of the dashboard the PANEL_GROUP associated with. Required.
PANEL_GROUP_DASHBOARD = 'project'

ADD_INSTALLED_APPS = ['sahara_dashboard']
