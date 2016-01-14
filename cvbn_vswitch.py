### Copyright (c) Cisco Systems Inc. 2016 -
### Author Arkadiusz Kaliwoda <akaliwod@cisco.com>

"""
.. module:: cvbn_vswitch
    :synopsis: CVBN vSwitch control class

.. moduleauthor:: Arkadiusz Kaliwoda <akaliwod@cisco.com>

Module implementing 'vswitch' class that controls all interactions with CVBN vSwitch instance

"""

import json
import sys
from cvbx_rpc_tools.method import (
    RpcMethodFactory, RpcMethodError
)
import time

class CvbnApiFailure(Exception):
    """Exception raised when REST API execution fails
    """
    pass

class vswitch(object):
    """Python class that controls all interactions with CVBN vSwitch instance
    """
    def __init__(self, server, host):
    """.. function:: init(server, host)

    Setup communication channel for CRUD operations against cvbn-switch-agent via CvBB/CvBN.
    CvBB - HTTP protocol and REST syntax with default CvBB port (8280)
    CvBN - HTTP protocol and RPC specific syntax with default CvBN port (26265)

    Autodiscovery of CvBB vs. CvBN

    There is no authentication.

    :param server: FQDN/IP of the server CvBB/CvBN
    :param host: if 'server' is CvBB, then 'host' must be UUID of the CvBN server. Otherwise it can be anything

    >>> import cvbn_vswitch
    >>> vswitch = cvbn_vswitch.vswitch("localhost","none")

    """

    port = self._determine_rpc_port(server)
        factory = RpcMethodFactory.factory(
            '{}:{}'.format(server, str(port)) 
        )
        self._get_method = factory.method('get')
        self._walk_method = factory.method('walk')
        self._set_method = factory.method('set')
        self._delete_method = factory.method('delete')
    self.agent = host + '/cvbn-switch-agent'
    self.cid = 'magic'

    @staticmethod
    def _determine_rpc_port(server):
        '''check for qvbb rest interface present or not'''
        factory = RpcMethodFactory.factory('{}:26265'.format(server))
        try:
            factory.method('get').invoke(
                'cvbn-service-agent', 'magic', {
                    'tid': 'website',
                    'name': 'qvbb-rest-interface',
                })
        except (RpcMethodError):
            return 26265
        else:
            return 8280

    def getSwitches(self):
    """.. function:: getSwitches()

    Get the list of switches defined on the server with *id* and *name* attributes

    :returns: List of switches defined on the server (JSON)
    :raises: CvbnApiFailure

    >>> print vswitch.getSwitches()
    [{u'tid': u'compute.vswitch', u'id': u'7ee373eb-8aa7-4a24-8c76-c4fa52022624', u'name': u'demo'}]

    """

    params = {'tid':'compute.vswitch'}
    try:
        result = self._walk_method.invoke(self.agent, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")
    return result['children']

    def getSwitchName(self, switchName):
    """.. function:: getSwitchName(switchName)

    Get the switch details by name.

    If switch *name* attribute value is not unique, and this is not enforced by data model, then the first found switch instance is returned.

    :returns: Switch instances or None if switch name does not exist
    :raises: CvbnApiFailure

    >>> print vswitch.getSwitchName("demo")
    {u'tid': u'compute.vswitch', u'id': u'ea2db47c-1cbe-4846-9ba6-141c3ac59508', u'name': u'demo'}
    >>> print vswitch.getSwitchName("wrong")
    None

    """

    params = {'tid':'compute.vswitch'}
    try:
        result = self._walk_method.invoke(self.agent, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    for instances in result['children']:
        if instances['name'] == switchName:
            return instances
    return None

    def getSwitchDomain(self, domainName):
    """.. function:: getSwitchDomain(domainName)

    Get the switch details by name.

    If switch *name* attribute value is not unique, and this is not enforced by data model, then the first found switch instance is returned.

    :param domainName: domain name to be found
    :type domainName: string
    :returns: Switch instances details that has domain or None if domain is not found
    :raises: CvbnApiFailure

    >>> print vswitch.getSwitchDomain("user1")
    {u'tid': u'compute.vswitch', u'id': u'ea2db47c-1cbe-4846-9ba6-141c3ac59508', u'name': u'demo'}
    >>> print vswitch.getSwitchDomain("user2")
    None

    """

    params = {'tid':'compute.vswitch'}
    try:
        result = self._walk_method.invoke(self.agent, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    for instances in result['children']:
        if not (self.getDomainName(instances['id'], domainName) == None):
            return instances

    return None

    def isSwitch(self, uuid):
    """.. function:: isSwitch(uuid)

    Checks if switch instance *uuid* is defined

    :param uuid: Switch instance id
    :type uuid: string
    :returns: True if defined, False if not defined
    :raises: CvbnApiFailure

    >>> print vswitch.isSwitch("wrong")
    False
    >>> print vswitch.isSwitch("7ee373eb-8aa7-4a24-8c76-c4fa52022624")
    True

    """

        params = {'tid':'compute.vswitch'}
        try:
                result = self._walk_method.invoke(self.agent, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")
        for instances in result['children']:
                if instances['id'] == uuid:
            return True
        return False

    def addSwitch(self, name):
    """.. function:: addSwitch(name)

    Add the switch with *name*

    The data model does not enforce *name* to be unique. Neither does *addSwitch* method.

    :param name: Switch instance name
    :type name: string
    :returns: *uuid* reference value for Switch instance or None
    :raises: CvbnApiFailure

    >>> print vswitch.addSwitch("demo")
    7ee373eb-8aa7-4a24-8c76-c4fa52022624

    """

    params = {'tid':'compute.vswitch','name':name}
    try:
        result = self._set_method.invoke(self.agent, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")
    return result['id']

    def deleteSwitch(self, uuid):
    """.. function:: deleteSwitch(uuid)

    Delete the switch by *uuid*

    :param uuid: Switch instance id
    :type uuid: string
    :returns: True if deleted, False if switch is running or not defined
    :raises: CvbnApiFailure

    >>> print vswitch.deleteSwitch("wrong")
    False
    >>> print vswitch.deleteSwitch("7ee373eb-8aa7-4a24-8c76-c4fa52022624")
    True
    >>> print vswitch.getSwitches()
    []

    """

    if not self.isSwitch(uuid):
        return False

    if self.isRunning(uuid):
        if not self.stopSwitch(uuid):
            return False

    for domain in self.getDomains(uuid):
        if not self.deleteDomain(uuid, domain['id']):
            return False

    params = {'tid':'compute.vswitch','id':uuid}
    try:
        result = self._delete_method.invoke(self.agent, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return True

    def startSwitch(self, uuid, maxWait = 10):
    """.. function:: startSwitch(uuid, maxWait = 10)

    Start the switch instance *uuid*. If *uuid* is not defined, then *False* is returned.
    Default max. 10 seconds of waiting for the switch to start.

    :param uuid: Switch instance id
    :type uuid: string
    :param maxWait: Optional waiting time in seconds for switch connection to cvbn-mux. Default 10
    :type maxWait: integer
    :returns: *True* if switch started correctly, *False* if not started or switch not defined or switch already running
    :raises: CvbnApiFailure

    >>> print vswitch.startSwitch("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    True
    >>> print vswitch.startSwitch("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    False
    >>> print vswitch.startSwitch("wrong")
    False

    """

    if not self.isSwitch(uuid):
        return False

    if self.isRunning(uuid):
        return False

        config = {}
        config['tid'] = 'compute.vswitch'
        config['id'] = uuid
        params = {'tid':'compute.server','configuration':config}
        try:
                result = self._set_method.invoke(self.agent, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    counter = 0
    connected = False
        while True:
                if self.isConnectedToMux(uuid):
            connected = True
                        break
                time.sleep(1)
        counter = counter + 1
        if counter > maxWait:
            break
    if not connected:
        return False

        params = {'tid':'networking.vswitch'}
        try:
                result = self._set_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return True

    def stopSwitch(self, uuid):
    """.. function: stopSwitch(uuid)

    Stop the running switch instance *uuid*

    :param uuid: Switch instance id
    :type uuid: string
    :returns: True if stopped, False if not defined or not running
    :raises: CvbnApiFailure

    >>> print vswitch.stopSwitch("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    True
    >>> print vswitch.stopSwitch("wrong")
    False

    """

    runId = self.getRunId(uuid)
    if runId == None:
        return False

        params = {'tid':'compute.server','id':runId}
        try:
                result = self._delete_method.invoke(self.agent, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return True

    def getRunId(self, uuid):
    """.. function: getRunId(uuid)

    Get the running instance's *id*

    :param uuid: Switch instance id
    :type uuid: string
    :returns: *id* value if vSwitch is running and is defined. *None* otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.getRunId("wrong")
    None
    >>> print vswitch.getRunId("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    2eec5b9a-2ba4-4a2f-8c7b-be9b2bb63787

    """

    if not self.isSwitch(uuid):
        return None

        params = {'tid':'compute.server'}
        try:
                result = self._walk_method.invoke(self.agent, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")
        for instances in result['children']:
                if instances['configuration']['id'] == uuid:
            return instances['id']
        return None

    def getNetworkingId(self, uuid):
    """.. function:: getNetworkingId(uuid)

    Get networking.vswich object id related to switch instance

    :param uuid: Switch instance id
    :type uuid: string
    :returns: networking.switch object id, None if switch not running
    :raises: CvbnApiFailure

    >>> print vswitch.getNetworkingId("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    {u'tid': u'networking.vswitch', u'id': u'69970943-8ad6-45ec-820d-58dca4d3ca82'}
    >>> print vswitch.getNetworkingId("wrong")
    None

    """

    if self.getRunId(uuid) == None:
        return None

    params = {'tid':'networking.vswitch'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")
    return result['children'][0]

    def isRunning(self, uuid):
    """.. function:: isRunning(uuid)

    Check if the switch *uuid* is running. If the switch is not even defined, it does not run.
    No check is made if the switch is defined.

    :param uuid: Switch instance id
    :type uuid: string
    :returns: True if running, False if not running
    :raises: CvbnApiFailure

    >>> print vswitch.isRunning("wrong")
    False
    >>> print vswitch.isRunning("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    True

    """

    if self.getRunId(uuid) == None:
        return False
    return True

    def isConnectedToMux(self, uuid):
    """.. function:: isConnectedToMux(uuid)

    Check if the running vSwitch instances connected to cvbn-mux i.e. is the switch instance ready to be configured.

    :param uuid: Switch instance id
    :type uuid: string
    :returns: True if connected, False if not connected
    :raises: CvbnApiFailure

    """

        params = {'tid':'connection'}
        try:
                result = self._walk_method.invoke('0', self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")
        for instances in result['children']:
                if instances['name'] == uuid:
                        return True
        return False

    def getNetworks(self,uuid):
    """.. function:: getNetworks(self, uuid)

    Get the list of associate networks created on the switch *uuid*

    :param uuid: Switch instance id
    :type uuid: string
    :returns: List of associate networks or None if switch is not running
    :raises: CvbnApiFailure

    >>> print vswitch.getNetworks("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    []
    >>> print vswitch.getNetworks("wrong")
    None
    >>> print vswitch.getNetworks("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    [{u'subnets': [], u'name': u'pcpe', u'host_interface': u'eth1', u'network_type': u'associate', u'tid': u'networking.network', u'id': u'09c357c1-adf4-4071-b267-3b7cd8815860'}, {u'subnets': [], u'name': u'pcpe', u'host_interface': u'eth1', u'network_type': u'associate', u'tid': u'networking.network', u'id': u'85da5f09-2291-4961-bf7b-acf05fa116ee'}, {u'tid': u'networking.network', u'subnets': [u'c4e3dfcd-9aa9-422c-959e-885f11db8d36'], u'id': u'cce575af-0b1e-4193-a5ce-1118ea86308e', u'network_type': u'associate', u'name': u'vm'}]

    """

    runId = self.getRunId(uuid)
    if runId == None:
        return None

    params = {'tid':'networking.network'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return result['children']

    def getNetworkId(self, uuid, networkId):
    """.. function:: isNetworkid(uuid, networkId)

    Get associate network by id

    :param uuid: Switch instance id
    :type uuid: string
    :param networkId: Network id
    :type networkId: string
    :returns: Network details if exists, None otherwise (switch not defined, not running, network id not exist)
    :raises: CvbnApiFailure

    >>> print vswitch.getNetworkId("ea2db47c-1cbe-4846-9ba6-141c3ac59508","wrong")
    None
    >>> print vswitch.getNetworkId("ea2db47c-1cbe-4846-9ba6-141c3ac59508","cce575af-0b1e-4193-a5ce-1118ea86308e")
    {u'tid': u'networking.network', u'subnets': [u'c4e3dfcd-9aa9-422c-959e-885f11db8d36'], u'id': u'cce575af-0b1e-4193-a5ce-1118ea86308e', u'network_type': u'associate', u'name': u'vm'}

    """

    runId = self.getRunId(uuid)
    if runId == None:
        return None

    params = {'tid':'networking.network'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

        for instances in result['children']:
                if instances['id'] == networkId:
                        return instances
        return None

    def getNetworkName(self, uuid, networkName):
    """.. function:: getNetworkName(uuid, networkName)

    Get details of network by name

    :param uuid: Switch instance id
    :type uuid: string
    :param networkName: Network name
    :type networkName: string
    :returns: Network details if exists, None otherwise (switch not defined, not running, network id not exist)
    :raises: CvbnApiFailure

    >>> print vswitch.getNetworkName("ea2db47c-1cbe-4846-9ba6-141c3ac59508","wrong")
    None
    >>> print vswitch.getNetworkName("ea2db47c-1cbe-4846-9ba6-141c3ac59508","vm")
    {u'tid': u'networking.network', u'subnets': [u'c4e3dfcd-9aa9-422c-959e-885f11db8d36'], u'id': u'cce575af-0b1e-4193-a5ce-1118ea86308e', u'network_type': u'associate', u'name': u'vm'}

    """

    runId = self.getRunId(uuid)
    if runId == None:
        return None

    params = {'tid':'networking.network'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

        for instances in result['children']:
                if instances['name'] == networkName:
                        return instances
        return None

    def addNetwork(self, uuid, networkName, hostInterface, ipv4Subnet):
    """.. function:: addNetwork(uuid, networkName, hostInterface, ipv4Subnet)

    Add associate network to switch *uuid* with the attribute values as parameters.

    ipv4Subnet can be *None* else it has to be proper notation of CIDR (a.b.c.d/n)

    :param uuid: Switch instance id
    :type uuid: string
    :param networkName: Network name
    :type networkName: string
    :param hostInterface: Host interface name
    :type hostInterface: string
    :param ipv4Subnet: IPv4 subnet of the network
    :type ipv4Subnet: string
    :returns: network *id* if operation was successful, None otherwise (switch not defined, not running)
    :raises: CvbnApiFailure

    >>> print vswitch.addNetwork("ea2db47c-1cbe-4846-9ba6-141c3ac59508","pcpe","eth1","None")
    33b97119-3d45-4790-b888-eb9e5e1c6430
    >>> print vswitch.addNetwork("ea2db47c-1cbe-4846-9ba6-141c3ac59508","vm","lo","192.168.30.0/24")
    fd07cb98-4030-45cc-b4ba-183f110ce10d
    >>> print vswitch.getNetworks("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    [{u'subnets': [], u'name': u'pcpe', u'host_interface': u'eth1', u'network_type': u'associate', u'tid': u'networking.network', u'id': u'33b97119-3d45-4790-b888-eb9e5e1c6430'}, {u'tid': u'networking.network', u'subnets': [u'e67d8e96-f887-4217-9ca6-ccb52d101d92'], u'id': u'fd07cb98-4030-45cc-b4ba-183f110ce10d', u'network_type': u'associate', u'name': u'vm'}]

    """

    runId = self.getRunId(uuid)
    if runId == None:
        return None

    params = {'tid':'networking.network','network_type':'associate','name':networkName,'host_interface':hostInterface}
    try:
        result = self._set_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")
    networkId = result['id']

    if not ipv4Subnet == "None":
        if not self.addSubnet(uuid, networkId, ipv4Subnet):
            self.deleteNetwork(uuid, networkId)
            return None

    return networkId

    def deleteNetwork(self, uuid, networkId):
    """.. function:: deleteNetwork(uuid, networkId)

    Delete network by *networkId*. Associated subnets (if any) are deleted too

    :param uuid: Switch instance id
    :type uuid: string
    :param networkId: Network id
    :type networkId: string
    :returns: True if operation was successful, False otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.getNetworks("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    [{u'tid': u'networking.network', u'subnets': [u'c4e3dfcd-9aa9-422c-959e-885f11db8d36'], u'id': u'cce575af-0b1e-4193-a5ce-1118ea86308e', u'network_type': u'associate', u'name': u'vm'}]
    >>> print vswitch.deleteNetwork("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "cce575af-0b1e-4193-a5ce-1118ea86308e")
    True
    >>> print vswitch.getNetworks("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    []

    """

    if self.getRunId(uuid) == None:
        return False

    networkDetails = self.getNetworkId(uuid, networkId)
    if networkDetails == None:
        return False

    for subnetId in networkDetails['subnets']:
        if not self.deleteSubnet(uuid, subnetId):
            return False

    params = {'tid':'networking.network','id':networkId}
    try:
        result = self._delete_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return True

    def addSubnet(self, uuid, networkId, ipv4Subnet):
    """.. function:: addSubnet(uuid, networkId, ipv4Subnet)

    Add IPv4 Subnet and associate it with the network *networkId*

    :param uuid: Switch instance id
    :type uuid: string
    :param networkId: Network id
    :type networkId: string
    :param ipv4Subnet: IPv4 subnet of the network
    :type ipv4Subnet: string
    :returns: subnet *id* if operation was successful, None otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.addSubnet("ea2db47c-1cbe-4846-9ba6-141c3ac59508","33b97119-3d45-4790-b888-eb9e5e1c6430","192.168.40.0/24")
    23c978ac-8d7f-4a56-9a62-21d11b90ddc9

    """

    if self.getRunId(uuid) == None:
        return None

    if self.getNetworkId(uuid, networkId) == None:
        return None

    params = {'tid':'networking.subnet', 'network_id':networkId, 'cidr':ipv4Subnet}
    try:
        result = self._set_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return result['id']

    def getSubnets(self, uuid):
    """.. function:: getSubnets(self, uuid)

    Get the list of subnets created on the switch *uuid*

    :param uuid: Switch instance id
    :type uuid: string
    :returns: array of subnets or None if switch not running
    :raises: CvbnApiFailure

    >>> print vswitch.getSubnets("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    []
    >>> print vswitch.getSubnets("wrong")
    None
    >>> print vswitch.getSubnets("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    [{u'network_id': u'cce575af-0b1e-4193-a5ce-1118ea86308e', u'ip_version': 4, u'allocation_pools': [{u'start': u'192.168.30.2', u'end': u'192.168.30.254'}], u'gateway_ip': u'192.168.30.1', u'tid': u'networking.subnet', u'cidr': u'192.168.30.0/24', u'id': u'c4e3dfcd-9aa9-422c-959e-885f11db8d36'}]

    """

    if self.getRunId(uuid) == None:
        return None

    params = {'tid':'networking.subnet'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return result['children']

    def getSubnetId(self, uuid, subnetId):
    """.. function:: isSubnetId(uuid, subnetId)

    Get subnet details by *subnetId* for switch *uuid*

    :param uuid: Switch instance id
    :type uuid: string
    :param subnetId: subnet id
    :type subnetId: string
    :returns: Subnet details if exists, None otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.getSubnetId("ea2db47c-1cbe-4846-9ba6-141c3ac59508","23c978ac-8d7f-4a56-9a62-21d11b90ddc9")
    {u'network_id': u'33b97119-3d45-4790-b888-eb9e5e1c6430', u'ip_version': 4, u'allocation_pools': [{u'start': u'192.168.40.2', u'end': u'192.168.40.254'}], u'gateway_ip': u'192.168.40.1', u'tid': u'networking.subnet', u'cidr': u'192.168.40.0/24', u'id': u'23c978ac-8d7f-4a56-9a62-21d11b90ddc9'}
    >>> print vswitch.getSubnetId("ea2db47c-1cbe-4846-9ba6-141c3ac59508","wrong")
    None

    """

    if self.getRunId(uuid) == None:
        return None

    params = {'tid':'networking.subnet'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

        for instances in result['children']:
                if instances['id'] == subnetId:
                        return instances
        return None

    def deleteSubnet(self, uuid, subnetId):
    """.. function:: deleteSubnet(uuid, subnetId):

    Delete subnet by *subnetId* on switch *uuid*

    :param uuid: Switch instance id
    :type uuid: string
    :param subnetId: subnet id
    :type subnetId: string
    :returns: True if operation successful, False otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.deleteSubnet("ea2db47c-1cbe-4846-9ba6-141c3ac59508","23c978ac-8d7f-4a56-9a62-21d11b90ddc9")
    True
    >>> print vswitch.deleteSubnet("ea2db47c-1cbe-4846-9ba6-141c3ac59508","wrong")
    False

    """

    if self.getRunId(uuid) == None:
        return False

    if self.getSubnetId(uuid, subnetId) == None:
        return False

    params = {'tid':'networking.subnet','id':subnetId}
    try:
        result = self._delete_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return True

    def addDomain(self, uuid, domainName):
    """.. function:: addDomain(uuid, domainName):

    Add domain to switch. There is no check for domain's name uniqueness

    :param uuid: Switch instance id
    :type uuid: string
    :param domainName: domain's name
    :type domainName: string
    :returns: domain's *id* if operation successful, None otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.addDomain("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "user1")
    bf5f93ea-bf25-4514-bc80-93615a9bb785
    >>> print vswitch.addDomain("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "user1")
    351ae2bf-047e-406e-913e-0215ed91c2d2

    """

    if self.getRunId(uuid) == None:
        return None

    params = {}
    params['tid'] = 'networking.vswitch.domain'
    params['vswitch'] = self.getNetworkingId(uuid)
    params['name'] = domainName
    try:
        result = self._set_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return result['id']

    def getDomains(self, uuid):
    """.. function:: getDomains(uuid):

    Get all domains details on the switch instance

    :param uuid: Switch instance id
    :type uuid: string
    :returns: array of domains details if operation successful, None otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.getDomains("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    []
    >>> print vswitch.getDomains("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    [{u'tid': u'networking.vswitch.domain', u'vswitch': {u'tid': u'networking.vswitch', u'id': u'69970943-8ad6-45ec-820d-58dca4d3ca82'}, u'name': u'user1', u'id': u'bf5f93ea-bf25-4514-bc80-93615a9bb785'}]

    """

    if self.getRunId(uuid) == None:
        return None

    params = {'tid':'networking.vswitch.domain'}
    try:
            result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return result['children']

    def getDomainId(self, uuid, domainId):
    """.. function:: getDomainId(uuid, domainId):

    Get domain's details by domain id.

    :param uuid: Switch instance id
    :type uuid: string
    :param domainId: domain's id
    :type domainId: string
    :returns: domain's details if operation successful, None otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.getDomainId("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "bf5f93ea-bf25-4514-bc80-93615a9bb785")
    {u'tid': u'networking.vswitch.domain', u'vswitch': {u'tid': u'networking.vswitch', u'id': u'69970943-8ad6-45ec-820d-58dca4d3ca82'}, u'name': u'user1', u'id': u'bf5f93ea-bf25-4514-bc80-93615a9bb785'}
    >>> print vswitch.getDomainId("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "wrong")
    None

    """
    if self.getRunId(uuid) == None:
        return None

    params = {'tid':'networking.vswitch.domain'}
    try:
            result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    for instances in result['children']:
        if instances['id'] == domainId:
            return instances
    return None

    def getDomainName(self, uuid, domainName):
    """.. function:: getDomainName(uuid, domainName):

    Get domain's details by domain name.

    Domain name is not enforced to be unique in the data model. The first found object is returned.

    :param uuid: Switch instance id
    :type uuid: string
    :param domainName: domain's name
    :type domainName: string
    :returns: domain's details if operation successful, None otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.getDomainName("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "user1")
    {u'tid': u'networking.vswitch.domain', u'vswitch': {u'tid': u'networking.vswitch', u'id': u'69970943-8ad6-45ec-820d-58dca4d3ca82'}, u'name': u'user1', u'id': u'bf5f93ea-bf25-4514-bc80-93615a9bb785'}
    >>> print vswitch.getDomainName("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "wrong")
    None

    """
    if self.getRunId(uuid) == None:
        return None

    params = {'tid':'networking.vswitch.domain'}
    try:
            result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    for instances in result['children']:
        if instances['name'] == domainName:
            return instances
    return None

    def deleteDomain(self, uuid, domainId):	
    """.. function:: deleteDomain(uuid, domainId):

    Delete domain defined on the switch with all dependencies

    :param uuid: Switch instance id
    :type uuid: string
    :param domainId: domain's id
    :type domainId: string
    :returns: True if operation successful, False otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.deleteDomain("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "351ae2bf-047e-406e-913e-0215ed91c2d2")
    True
    >>> print vswitch.deleteDomain("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "wrong")
    False

    """
    if self.getRunId(uuid) == None:
        return False

    if self.getDomainId(uuid, domainId) == None:
        return False

    if not self.deleteDomainPorts(uuid, domainId):
        return False

    params = {'tid':'networking.vswitch.domain','id':domainId}
    try:
        result = self._delete_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")
    return True

    def deleteDomainPorts(self, uuid, domainId):
    """.. function:: deleteDomainPorts(uuid, domainId):

    Delete all port objects associated with domain defined on the switch

    :param uuid: Switch instance id
    :type uuid: string
    :param domainId: domain's id
    :type domainId: string
    :returns: True if operation successful, False otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.deleteDomainPorts("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "bf5f93ea-bf25-4514-bc80-93615a9bb785")
    True

    """
    if self.getRunId(uuid) == None:
        return False

    if self.getDomainId(uuid, domainId) == None:
        return False

    params = {'tid':'networking.vswitch.domain.ports'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    for instances in result['children']:
        if instances['domain']['id'] == domainId:
            if instances['port']['tid'] == "networking.port.gre":
                self.deletePortGreDomain(uuid, domainId, instances['port']['id'])
                self.deletePortGre(uuid, instances['port']['id'])
            if instances['port']['tid'] == "networking.port.raw":
                self.deletePortVlanDomain(uuid, domainId, instances['port']['id'])
                self.deletePortVlan(uuid, instances['port']['id'])

    return True

    def addPortGreDomain(self, uuid, domainId, portId):
    """.. function:: addPortGreDomain(uuid, domainId, portId):

    Add GRE port to domain

    :param uuid: Switch instance id
    :type uuid: string
    :param domainId: domain's id
    :type domainId: string
    :param portId: port's id
    :type portId: string
    :returns: True if operation successful, False otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.addPortGreDomain("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "bf5f93ea-bf25-4514-bc80-93615a9bb785","f1739786-38e0-4158-b337-9fd25aae3eb8")
    True

    """
    if self.getRunId(uuid) == None:
        return False

    if self.getDomainId(uuid, domainId) == None:
        return False

    if self.getPortGreId(uuid, portId) == None:
        return False

    if self.isPortGreDomain(uuid, domainId, portId):
        return False

    params = {}
    params['tid'] = "networking.vswitch.domain.ports"
    params['domain'] = {'tid':'networking.vswitch.domain','id':domainId}
    params['port'] = {'tid':'networking.port.gre','id':portId}
    try:
        result = self._set_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return True

    def isPortGreDomain(self, uuid, domainId, portId):
    """.. function:: isPortGreDomain(uuid, domainId, portId):

    Check if GRE port is member of domain

    :param uuid: Switch instance id
    :type uuid: string
    :param domainId: domain's id
    :type domainId: string
    :param portId: port's id
    :type portId: string
    :returns: True if GRE port is member of domain, False otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.isPortGreDomain("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "bf5f93ea-bf25-4514-bc80-93615a9bb785","f1739786-38e0-4158-b337-9fd25aae3eb8")
    True

    """
    if self.getRunId(uuid) == None:
        return False

    if self.getDomainId(uuid, domainId) == None:
        return False

    if self.getPortGreId(uuid, portId) == None:
        return False

    params = {'tid':'networking.vswitch.domain.ports'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    for instances in result['children']:
        if instances['domain']['id'] == domainId:
            if instances['port']['tid'] == "networking.port.gre":
                if instances['port']['id'] == portId:
                    return True

    return False

    def deletePortGreDomain(self,uuid,domainId,portId):
    """.. function:: deletePortGreDomain(uuid, domainId, portId):

    Delete GRE port from domain

    :param uuid: Switch instance id
    :type uuid: string
    :param domainId: domain's id
    :type domainId: string
    :param portId: port's id
    :type portId: string
    :returns: True if operation successful, False otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.deletePortGreDomain("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "bf5f93ea-bf25-4514-bc80-93615a9bb785","f1739786-38e0-4158-b337-9fd25aae3eb8")
    True

    """
    if self.getRunId(uuid) == None:
        return False

    if self.getDomainId(uuid, domainId) == None:
        return False

    if not self.isPortGreDomain(uuid, domainId, portId):
        return False

    params = {}
    params['tid'] = "networking.vswitch.domain.ports"
    params['domain'] = {'tid':'networking.vswitch.domain','id':domainId}
    params['port'] = {'tid':'networking.port.gre','id':portId}
    try:
        result = self._delete_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return True

    def addPortVlanDomain(self, uuid, domainId, portId):
    """.. function:: addPortVlanDomain(uuid, domainId, portId):

    Add VLAN port to domain.

    :param uuid: Switch instance id
    :type uuid: string
    :param domainId: domain's id
    :type domainId: string
    :param portId: port's id
    :type portId: string
    :returns: True if operation successful, False otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.addPortVlanDomain("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "bf5f93ea-bf25-4514-bc80-93615a9bb785", "e07cc20e-75f2-4738-abd3-a4dd6ae172d7")
    True

    """
    if self.getRunId(uuid) == None:
        return False

    if self.getDomainId(uuid, domainId) == None:
        return False

    if self.getPortVlanId(uuid, portId) == None:
        return False

    if self.isPortVlanDomain(uuid, domainId, portId):
        return False

    params = {}
    params['tid'] = 'networking.vswitch.domain.ports'
    params['domain'] = {'tid':'networking.vswitch.domain','id':domainId}
    params['port'] = {'tid':'networking.port.raw','id':portId}
    try:
        result = self._set_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return True

    def isPortVlanDomain(self, uuid, domainId, portId):
    """.. function:: isPortVlanDomain(uuid, domainId, portId):

    Check if VLAN port is member of domain

    :param uuid: Switch instance id
    :type uuid: string
    :param domainId: domain's id
    :type domainId: string
    :param portId: port's id
    :type portId: string
    :returns: True if GRE port is member of domain, False otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.isPortVlanDomain("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "bf5f93ea-bf25-4514-bc80-93615a9bb785", "e07cc20e-75f2-4738-abd3-a4dd6ae172d7")
    True

    """
    if self.getRunId(uuid) == None:
        return False

    if self.getDomainId(uuid, domainId) == None:
        return False

    if self.getPortVlanId(uuid, portId) == None:
        return False

    params = {'tid':'networking.vswitch.domain.ports'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    for instances in result['children']:
        if instances['domain']['id'] == domainId:
            if instances['port']['tid'] == "networking.port.raw":
                if instances['port']['id'] == portId:
                    return True

    return False

    def deletePortVlanDomain(self,uuid,domainId,portId):
    """.. function:: deletePortVlanDomain(uuid, domainId, portId):

    Delete VLAN port from domain

    :param uuid: Switch instance id
    :type uuid: string
    :param domainId: domain's id
    :type domainId: string
    :param portId: port's id
    :type portId: string
    :returns: True if operation successful, False otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.deletePortVlanDomain("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "bf5f93ea-bf25-4514-bc80-93615a9bb785", "e07cc20e-75f2-4738-abd3-a4dd6ae172d7")
    True
    >>> print vswitch.deletePortVlanDomain("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "bf5f93ea-bf25-4514-bc80-93615a9bb785", "wrong")
    False

    """
    if self.getRunId(uuid) == None:
        return False

    if self.getDomainId(uuid, domainId) == None:
        return False

    if not self.isPortVlanDomain(uuid, domainId, portId):
        return False

    params = {}
    params['tid'] = "networking.vswitch.domain.ports"
    params['domain'] = {'tid':'networking.vswitch.domain','id':domainId}
    params['port'] = {'tid':'networking.port.raw','id':portId}
    try:
        result = self._delete_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return True

    def addPortGre(self, uuid, subnetId, portName, local_ip = None, remote_ip = None, checksum = False, seqnum = False):
    """.. function:: addPortGre(uuid, subnetId, portName, local_ip = None, remote_ip = None, checksum = False, seqnum = False):

    Add port GRE to switch.

    :param uuid: Switch instance id
    :type uuid: string
    :param subnetId: subnet id
    :type subnetId: string
    :param portName: port's name
    :type portName: string
    :local_ip: local (on the switch) IP end of GRE tunnel
    :type local_ip: string
    :remote_ip: remote (on the pCPE or VM) IP end of GRE tunnel
    :type remote_ip: string
    :param checksum: is checksum enabled in GRE header
    :type checksum: boolean (True, False)
    :param seqnum: is sequence numbers enabled in GRE header
    :type seqnum: boolean (True, False)
    :returns: port's *id* if operation successful, None otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.addPortGre("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "e67d8e96-f887-4217-9ca6-ccb52d101d92", "gre10", local_ip = "192.168.30.10", remote_ip = None, checksum = False, seqnum = False)
    f1739786-38e0-4158-b337-9fd25aae3eb8
    >>> print vswitch.addPortGre("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "e67d8e96-f887-4217-9ca6-ccb52d101d92", "gre10", local_ip = "192.168.30.10", remote_ip = None, checksum = False, seqnum = False)
    ['']
    inconsistent port usage
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "cvbn_vswitch.py", line 1400, in addPortGre
        raise CvbnApiFailure(err)
    cvbn_vswitch.CvbnApiFailure: ['']
    inconsistent port usage
    >>> print vswitch.addPortGre("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "e67d8e96-f887-4217-9ca6-ccb52d101d92", "gre10", local_ip = "192.168.32.10", remote_ip = None, checksum = False, seqnum = False)
    ['']
    192.168.32.10 is not in available subnet address range
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "cvbn_vswitch.py", line 1400, in addPortGre
        raise CvbnApiFailure(err)
    cvbn_vswitch.CvbnApiFailure: ['']
    192.168.32.10 is not in available subnet address range
    >>> print vswitch.addPortGre("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "wrong", "gre10", local_ip = "192.168.30.10", remote_ip = None, checksum = False, seqnum = False)
    None

    """
    if self.getRunId(uuid) == None:
        return None

    if self.getSubnetId(uuid, subnetId) == None:
        return None

    params = {}
    params['tid'] = 'networking.port.gre'
    params['name'] = portName
    params['local_subnet'] = subnetId
    if local_ip == None:
        params['local_endpoint'] = {}
    else:
        params['local_endpoint'] = {"ip_address":local_ip}
    if remote_ip == None:
        params['remote_endpoint'] = {}
    else:
        params['remote_endpoint'] = {"ip_address":remote_ip}
    params['checksum_present'] = checksum
    params['seq_num_present'] = seqnum
    try:
        result = self._set_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return result['id']

    def getPortsGre(self, uuid):
    """.. function:: getPortsGre(uuid):

    Get all GRE ports on the switch *uuid*

    :param uuid: Switch instance id
    :type uuid: string
    :returns: array of ports details if operation successful, None otherwise
    :raises: CvbnApiFailure

    >>> vswitch.getPortsGre("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    []
    >>> print vswitch.getPortsGre("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    [{u'name': u'gre10', u'local_subnet': u'e67d8e96-f887-4217-9ca6-ccb52d101d92', u'checksum_present': False, u'local_endpoint': {u'ip_address': u'192.168.30.10'}, u'seq_num_present': False, u'mac_address': u'3a:26:2d:9c:84:4a', u'tid': u'networking.port.gre', u'id': u'f1739786-38e0-4158-b337-9fd25aae3eb8', u'remote_endpoint': {}}]

    """
    if self.getRunId(uuid) == None:
        return None

    params = {'tid':'networking.port.gre'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return result['children']

    def getPortGreId(self, uuid, portId):
    """.. function:: getPortGreId(uuid, portId):

    Get port GRE details by id

    :param uuid: Switch instance id
    :type uuid: string
    :param portId: port's id
    :type portId: string
    :returns: port's details if operation successful, None otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.getPortGreId("ea2db47c-1cbe-4846-9ba6-141c3ac59508","f1739786-38e0-4158-b337-9fd25aae3eb8")
    {u'name': u'gre10', u'local_subnet': u'e67d8e96-f887-4217-9ca6-ccb52d101d92', u'checksum_present': False, u'local_endpoint': {u'ip_address': u'192.168.30.10'}, u'seq_num_present': False, u'mac_address': u'3a:26:2d:9c:84:4a', u'tid': u'networking.port.gre', u'id': u'f1739786-38e0-4158-b337-9fd25aae3eb8', u'remote_endpoint': {}}
    >>> print vswitch.getPortGreId("ea2db47c-1cbe-4846-9ba6-141c3ac59508","wrong")
    None

    """
    if self.getRunId(uuid) == None:
        return None

    params = {'tid':'networking.port.gre'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    for instances in result['children']:
        if instances['id'] == portId:
            return instances

    return None

    def getPortGreName(self, uuid, portName):
    """.. function:: getPortGreName(uuid, portName):

    Get port GRE details by port name

    :param uuid: Switch instance id
    :type uuid: string
    :param portName: port's name
    :type portName: string
    :returns: port's details if operation successful, None otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.getPortGreName("ea2db47c-1cbe-4846-9ba6-141c3ac59508","gre10")
    {u'name': u'gre10', u'local_subnet': u'e67d8e96-f887-4217-9ca6-ccb52d101d92', u'checksum_present': False, u'local_endpoint': {u'ip_address': u'192.168.30.10'}, u'seq_num_present': False, u'mac_address': u'3a:26:2d:9c:84:4a', u'tid': u'networking.port.gre', u'id': u'f1739786-38e0-4158-b337-9fd25aae3eb8', u'remote_endpoint': {}}
    >>> print vswitch.getPortGreName("ea2db47c-1cbe-4846-9ba6-141c3ac59508","wrong")
    None

    """
    if self.getRunId(uuid) == None:
        return None

    params = {'tid':'networking.port.gre'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    for instances in result['children']:
        if instances['name'] == portName:
            return instances

    return None

    def isPortGreDomain(self, uuid, portId, domainId):
    """.. function:: isPortGreDomain(uuid, portId, domainId):

    Check if port GRE is member of domain

    :param uuid: Switch instance id
    :type uuid: string
    :param portId: port's id
    :type portId: string
    :param domainId: domain's id
    :type domainId: string
    :returns: True if yes, False otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.isPortGreDomain("ea2db47c-1cbe-4846-9ba6-141c3ac59508","57da5612-1f87-4dc8-a7c4-8c70f732e2b2","bf5f93ea-bf25-4514-bc80-93615a9bb785")
    True

    """
    if self.getRunId(uuid) == None:
        return False

    params = {'tid':'networking.vswitch.domain.ports'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    for instances in result['children']:
        if instances['domain']['id'] == domainId:
            if instances['port']['tid'] == "networking.port.gre":
                if instances['port']['id'] == portId:
                    return True

    return False

    def isPortGreAnyDomain(self, uuid, portId):
    """.. function:: isPortGreAnyDomain(uuid, portId):

    Check if port GRE is member of any domain

    :param uuid: Switch instance id
    :type uuid: string
    :param portId: port's id
    :type portId: string
    :returns: True if yes, False otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.isPortGreAnyDomain("ea2db47c-1cbe-4846-9ba6-141c3ac59508","57da5612-1f87-4dc8-a7c4-8c70f732e2b2")
    True

    """
    if self.getRunId(uuid) == None:
        return False

    for domain in self.getDomains(uuid):
        if self.isPortGreDomain(uuid, portId, domain['id']):
            return True

    return False

    def deletePortGre(self, uuid, portId):
    """.. function:: deletePortGre(uuid, portId):

    Delete port GRE

    If port GRE is member of domain, the delete operation should fail.

    :param uuid: Switch instance id
    :type uuid: string
    :param portId: port's id
    :type portId: string
    :returns: True if operation successful, False otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.deletePortGre("ea2db47c-1cbe-4846-9ba6-141c3ac59508","57da5612-1f87-4dc8-a7c4-8c70f732e2b2")
    True

    """
    if self.getRunId(uuid) == None:
        return False

    if self.getPortGreId(uuid, portId) == None:
        return False

    if self.isPortGreAnyDomain(uuid, portId):
        return False

    params = {'tid':'networking.port.gre','id':portId}
    try:
        result = self._delete_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return True

    def addPortVlan(self, uuid, networkId, portName, vlan):
    """.. function:: addPortVlan(uuid, networkId, portName, vlan):

    Add port VLAN to switch.

    If VLAN is already defined on the target interface, the API should fail (CvbnApiFailure)

    :param uuid: Switch instance id
    :type uuid: string
    :param networkId: network id
    :type networkId: string
    :param portName: port's name
    :type portName: string
    :param vlan: vlan value
    :type vlan: string
    :returns: port's *id* if operation successful, None otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.addPortVlan("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "33b97119-3d45-4790-b888-eb9e5e1c6430", "vlan666", "666")
    45233226-f003-4aa6-9553-5cbfe6424626
    >>> print vswitch.addPortVlan("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "wrong", "vlan666", "666")
    None

    # ip addr
    5: eth1.666@eth1: <BROADCAST,MULTICAST,PROMISC,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default link/ether 00:50:56:b4:a1:3a brd ff:ff:ff:ff:ff:ff

    """

    if self.getRunId(uuid) == None:
        return None

    if self.getNetworkId(uuid, networkId) == None:
        return None

    params = {}
    params['tid'] = 'networking.port.raw'
    params['name'] = portName
    params['network_id'] = networkId
    params['vlan_ids'] = [vlan]
    try:
        result = self._set_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return result['id']

    def getPortsVlan(self, uuid):
    """.. function:: getPortsVlan(uuid):

    Get all VLAN ports created on vSwitch *uuid*

    :param uuid: Switch instance id
    :type uuid: string
    :returns: array of ports if operation successful, None otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.getPortsVlan("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    []
    >>> print vswitch.getPortsVlan("ea2db47c-1cbe-4846-9ba6-141c3ac59508")
    [{u'name': u'vlan666', u'network_id': u'33b97119-3d45-4790-b888-eb9e5e1c6430', u'host_interface': u'eth1.666', u'vlan_id': [666], u'mac_address': u'02:1e:69:02:e6:a9', u'tid': u'networking.port.raw', u'id': u'45233226-f003-4aa6-9553-5cbfe644626'}]

    """
    if self.getRunId(uuid) == None:
        return None

    params = {'tid':'networking.port.raw'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return result['children']

    def getPortVlanId(self, uuid, portId):
    """.. function:: getPortVlanId(uuid, portId):

    Get port VLAN details by id

    :param uuid: Switch instance id
    :type uuid: string
    :param portId: port's id
    :type portId: string
    :returns: port's details if operation successful, None otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.getPortVlanId("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "45233226-f003-4aa6-9553-5cbfe6424626")
    {u'name': u'vlan666', u'network_id': u'33b97119-3d45-4790-b888-eb9e5e1c6430', u'host_interface': u'eth1.666', u'vlan_ids': [666], u'mac_address': u'02:1e:69:02:e6:a9', u'tid': u'networking.port.raw', u'id': u'45233226-f003-4aa6-9553-5cbfe6424626'}

    # ip addr
    5: eth1.666@eth1: <BROADCAST,MULTICAST,PROMISC,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default link/ether 00:50:56:b4:a1:3a brd ff:ff:ff:ff:ff:ff

    """
    if self.getRunId(uuid) == None:
        return None

    params = {'tid':'networking.port.raw'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    for instances in result['children']:
        if instances['id'] == portId:
            return instances

    return None

    def getPortVlanName(self, uuid, portName):
    """.. function:: getPortVlanName(uuid, portName):

    Get port VLAN details by port name

    :param uuid: Switch instance id
    :type uuid: string
    :param portName: port's name
    :type portName: string
    :returns: port's details if operation successful, None otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.getPortVlanName("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "vlan666")
    {u'name': u'vlan666', u'network_id': u'33b97119-3d45-4790-b888-eb9e5e1c6430', u'host_interface': u'eth1.666', u'vlan_ids': [666], u'mac_address': u'02:1e:69:02:e6:a9', u'tid': u'networking.port.raw', u'id': u'45233226-f003-4aa6-9553-5cbfe6424626'}
    >>> print vswitch.getPortVlanName("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "wrong")
    None

    """
    if self.getRunId(uuid) == None:
        return None

    params = {'tid':'networking.port.raw'}
    try:
        result = self._walk_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    for instances in result['children']:
        if instances['name'] == portName:
            return instances

    return None

    def deletePortVlan(self, uuid, portId):
    """.. function:: deletePortVlan(uuid, portId):

    Delete port VLAN

    :param uuid: Switch instance id
    :type uuid: string
    :param portId: port's id
    :type portId: string
    :returns: True if operation successful, False otherwise
    :raises: CvbnApiFailure

    >>> print vswitch.deletePortVlan("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "45233226-f003-4aa6-9553-5cbfe6424626")
    True
    >>> print vswitch.deletePortVlan("ea2db47c-1cbe-4846-9ba6-141c3ac59508", "wrong")
    False

    """
    if self.getRunId(uuid) == None:
        return False

    if self.getPortVlanId(uuid, portId) == None:
        return False

    params = {'tid':'networking.port.raw','id':portId}
    try:
        result = self._delete_method.invoke(uuid, self.cid, params)
    except RpcMethodError as error:
            err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        raise CvbnApiFailure(err)
    except:
        err = "Unknown reason for CVBN API execution failure"
        print >> sys.stderr, err
        raise CvbnApiFailure("reason unknown")

    return True


