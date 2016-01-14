### Copyright (c) Cisco Systems Inc. 2015 -
### Author Arkadiusz Kaliwoda <akaliwod@cisco.com>

"""
.. module:: cvbn_server
        :synopsis: CVBN server control class

.. moduleauthor:: Arkadiusz Kaliwoda <akaliwod@cisco.com>

Module implementing 'vbn' class that controls all interactions with CVBN server

"""

import json
import sys
from cvbx_rpc_tools.method import (
        RpcMethodFactory, RpcMethodError
)

class CvbnApiFailure(Exception):
    """Exception raised when REST API execution fails
    """
    pass

class vbn(object):
    def __init__(self, server, host):
        """.. function:: init(server, host)

        Setup communication channel for CRUD operations against cvbn-guest-agent via CvBB/CvBN.
        CvBB - HTTP protocol and REST syntax with default CvBB port (8280)
        CvBN - HTTP protocol and RPC specific syntax with default CvBN port (26265)

        Autodiscovery of CvBB vs. CvBN

        There is no authentication.

        :param server: FQDN/IP of the server CvBB/CvBN
        :param host: if 'server' is CvBB, then 'host' must be UUID of the CvBN server. Otherwise it can be anything

	>>> import cvbn_server
	>>> server=cvbn_server.vbn("localhost","none")

        """
        port = self._determine_rpc_port(server)
        factory = RpcMethodFactory.factory(
                '{}:{}'.format(server, str(port))
        )
        self._walk_method = factory.method('walk')
        self._get_method = factory.method('get')
        self._set_method = factory.method('set')
        self._delete_method = factory.method('delete')
        self.agent = host + '/cvbn-guest-agent'
        self.cid = 'magic'

    @staticmethod
    def _determine_rpc_port(server):
        '''check for qvbb rest interface present or not'''
        factory = RpcMethodFactory.factory('{}:26265'.format(server))
        try:
            factory.method('get').invoke(
                    'cvbn-service-agent', 'magic', {
                        'tid': 'website',
                        'name': 'cvbb-rest-interface',
                    })
        except (RpcMethodError):
            return 26265
        else:
            return 8280

    def create_network(self, prefix, network_type, interface):
        ''' Creates networking object '''

    params = {}
    params['tid'] = 'networking.network'
    params['name'] = prefix
    params['network_type'] = network_type
    params['host_interface'] = interface
    try:
        result = self._set_method.invoke(self.agent, self.cid, params)
    except RpcMethodError as error:
        err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        sys.exit(1)


def is_networking(self):
    ''' Check if there is any networking object created '''
    params = {'tid': 'networking.network'}
    try:
        result = self._walk_method.invoke(self.agent, self.cid, params)
    except RpcMethodError as error:
        err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        sys.exit(1)
    retValue = False
    for instances in result['children']:
        retValue = True
    return retValue


def find_network_type(self, name):
    if name == "overlay":
        return self.find_network("overlay-network")
    if name == "vlan":
        return self.find_network("vlan-network")
    if name == "tap":
        return self.find_network("wan-network")
    return None


def find_network(self, name):
    ''' Find networking.network object with name '''
    params = {'tid': 'networking.network'}
    try:
        result = self._walk_method.invoke(self.agent, self.cid, params)
    except RpcMethodError as error:
        err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        sys.exit(1)
    for instances in result['children']:
        if instances['name'] == name:
            return instances['id']
    return None


def del_network(self, name):
    ''' Delete network by name '''
    uuid = self.find_network(name)
    if not uuid == None:
        self.del_network_uuid(uuid)


def del_network_uuid(self, uuid):
    ''' Delete network by uuid '''
    params = {'tid': 'networking.network', 'id': uuid}
    try:
        result = self._delete_method.invoke(self.agent, self.cid, params)
    except RpcMethodError as error:
        err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        sys.exit(1)


def info_network(self):
    params = {'tid': 'networking.network'}
    try:
        result = self._walk_method.invoke(self.agent, self.cid, params)
    except RpcMethodError as error:
        err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        sys.exit(1)
    return json.dumps(result)


def addSubnet(self, prefix, cidr, defgw, network, pool_start, pool_end):
    ''' Create subnet object '''
    params = {}
    params['tid'] = 'networking.subnet'
    params['name'] = prefix
    params['cidr'] = cidr
    params['network_id'] = network
    if pool_start != 'none':
        params['allocation_pools'] = [{'start': pool_start, 'end': pool_end}]
    if not defgw == 'none':
        params['gateway_ip'] = defgw
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


def getSubnets(self):
    """
>>> print server.getSubnets()
[]
	"""
    params = {'tid': 'networking.subnet'}
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


def getSubnetId(self, subnetId):
    params = {'tid': 'networking.subnet'}
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
        if instances['id'] == subnetId:
            return instances

    return None


def getSubnetName(self, subnetName):
    params = {'tid': 'networking.subnet'}
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
        if instances['name'] == subnetName:
            return instances

    return None


def get_network_subnet(self, uuid):
    ''' Get first subnet for network 'uuid' '''
    params = {'tid': 'networking.network', 'id': uuid}
    try:
        result = self._get_method.invoke(self.agent, self.cid, params)
    except RpcMethodError as error:
        err = '{}\n{}'.format(sys.argv, error)
        print >> sys.stderr, err
        sys.exit(1)
    return result['subnets'][0]


def del_subnet(self, name):
    ''' Delete subnet by name '''
    uuid = self.find_subnet(name)
    if not uuid == None:
        self.del_subnet_uuid(uuid)


def deleteSubnet(self, subnetId):
    if self.getSubnetId(subnetId) == None:
        return False

    params = {'tid': 'networking.subnet', 'id': subnetId}
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


def enableNat(self, natInterface, subnetId):
    """.. function:: enableNat(natInterface, natSubnet)

	Enable NAT on the server

        :param natInterface: interface where NAT should be enabled
        :type natInterface: string
	:param subnetId: subnet id
	:type subnetId: string
        :returns: NAT id if enabled, None otherwise
        :raises: CvbnApiFailure

	>>> TODO

        """

    if not (self.getNat() == None):
        return None

    if self.getSubnetId(subnetId) == None:
        return None

    params = {}
    params['tid'] = 'host.nat'
    params['out_interface'] = natInterface
    params['subnet_id'] = subnetId
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

    return None


def getNat(self):
    """
	>>> print server.getNat()
	None
	"""
    params = {'tid': 'host.nat'}
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
        return instances

    return None


def disableNat(self):
    natInfo = self.getNat()
    if natInfo == None:
        return False

    params = {'tid': 'host.nat', 'id': natInfo['id']}
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
