# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 OpenStack Foundation
# Copyright 2012 Nebula, Inc.
# Copyright (c) 2012 X.commerce, a business unit of eBay Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import absolute_import
import logging

from django.conf import settings
from manilaclient.v1 import client as manila_client

from horizon import exceptions
from horizon.utils.memoized import memoized  # noqa
from openstack_dashboard.api import base

LOG = logging.getLogger(__name__)


# API static values
SHARE_STATE_AVAILABLE = "available"
DEFAULT_QUOTA_NAME = 'default'


def manilaclient(request):
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)
    try:
        manila_url = base.url_for(request, 'share')
    except exceptions.ServiceCatalogException:
        LOG.debug('no share service configured.')
        return None
    c = manila_client.Client(request.user.username,
                             input_auth_token=request.user.token.id,
                             project_id=request.user.tenant_id,
                             service_catalog_url=manila_url,
                             insecure=insecure,
                             cacert=cacert,
                             http_log_debug=settings.DEBUG)
    c.client.auth_token = request.user.token.id
    c.client.management_url = manila_url
    return c


def share_list(request, search_opts=None):
    return manilaclient(request).shares.list(search_opts=search_opts)


def share_get(request, share_id):
    return manilaclient(request).shares.get(share_id)
