# Copyright 2015 FUJITSU LIMITED
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
from networking_fujitsu.ml2.drivers.fujitsu.common import utils as fj_util
from neutron.i18n import _LE
from neutron.plugins.common import constants as p_const
from neutron.plugins.ml2.common import exceptions as ml2_exc
from neutron.plugins.ml2 import driver_api
from oslo_log import helpers as log_helpers
from oslo_log import log as logging


LOG = logging.getLogger(__name__)
ISM_DRIVER = 'networking_fujitsu.ml2.drivers.fujitsu.ism.ism_base'


class FujitsuIsmDriver(driver_api.MechanismDriver):
    """Ml2 Mechanism driver for Fujitsu ISM. """

    def __init__(self):
        self._driver = None
        self.initialize()

    def initialize(self):
        self._driver = ISM_DRIVER

    @classmethod
    def create_ism_base(self, network_type, segmentation_id):

        if (network_type == p_const.TYPE_VLAN):
            ism = self._driver.IsmVlanBase(network_type, segmentation_id)
            return ism
        elif (network_type == p_const.TYPE_VXLAN):
            ism = self._driver.IsmVxlanBase(network_type, segmentation_id)
            return ism

    @log_helpers.log_method_call
    def create_port_postcommit(self, context):
        """Call ISM API to set VLAN configuration."""

        port = context.current
        if not fj_util.is_baremetal_deploy(port):
            LOG.warning("This plugin is doing nothing before ironic-neutron\
                      integration will be merged.")
            return
        net_type, seg_id = fj_util.get_network_segments(port.network)
        phy_connections = fj_util.get_physical_connectivity(port)

        # TODO(yushiro) Call LAG setup function of ISM

        for phy_con in phy_connections:
            try:
                ism = FujitsuIsmDriver.create_ism_base(net_type, seg_id)
                current = ism.get_current_config(phy_con)
                req_param = ism.generate_req_param_for_port(current)
                ism.setup_for_port(req_param, phy_con)
            except Exception as er:
                LOG.exception(
                    _LE("failed to setup %(net_type)s. detail=%(er)s"),
                    {'net_type': net_type, 'er': er})
                raise ml2_exc.MechanismDriverError(method="%s" % __name__)
        return

    @log_helpers.log_method_call
    def update_port_postcommit(self, context):
        """Call ISM API to set VLAN configuration."""

        port = context.current
        if not fj_util.is_baremetal_deploy(port):
            LOG.warning("This plugin is doing nothing before ironic-neutron\
                      integration will be merged.")
            return

        net_type, seg_id = fj_util.get_network_segments(port.network)
        phy_connections = fj_util.get_physical_connectivity(port)

        for phy_con in phy_connections:
            try:
                ism = FujitsuIsmDriver.create_ism_base(net_type, seg_id)
                current = ism.get_current_config(phy_con)
                req_param = ism.generate_req_param_for_port(current)
                ism.setup_for_port(req_param, phy_con)
            except Exception as er:
                LOG.exception(
                    _LE("failed to setup %(net_type)s. detail=%(er)s"),
                    {'net_type': net_type, 'er': er})
                raise ml2_exc.MechanismDriverError(method="%s" % __name__)
        return

    @log_helpers.log_method_call
    def delete_port_postcommit(self, context):
        """Call ISM API to reset VLAN configuration."""

        port = context.current
        if not fj_util.is_baremetal_deploy(port):
            LOG.warning("This plugin is doing nothing before ironic-neutron\
                      integration will be merged.")
            return
        net_type, seg_id = fj_util.get_network_segments(port.network)
        phy_connections = fj_util.get_physical_connectivity(port)

        # TODO(yushiro) Call LAG un-setup function of ISM

        for phy_con in phy_connections:
            # TODO(yushiro): Consider try position
            try:
                ism = self.create_ism_base(net_type, '')
                current = ism.get_current_config(phy_con)
                req_param = ism.generate_req_param_for_port(current)
                ism.setup_for_port(req_param, phy_con)
            except Exception as er:
                LOG.exception(
                    _LE("failed to setup %(net_type)s. detail=%(er)s"),
                    {'net_type': net_type, 'er': er})
                raise ml2_exc.MechanismDriverError(method="%s" % __name__)
