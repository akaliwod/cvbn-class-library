"""
.. module:: rcs_module
	:synopsis: RCS control class

.. moduleauthor:: Arkadiusz Kaliwoda <akaliwod@cisco.com>

Module implenting 'rcs' class that controls all interactions with RCS instance

"""

import requests, json

requests.packages.urllib3.disable_warnings()

class GetAuthTokenFailure(Exception):
    """Exception raised when authentication with RCS instances fails
    """
    pass

class RcsDefFailure(Exception):
    """Exception raised when RCS definition is incomplete
    """
    pass

class RcsApiFailure(Exception):
    """Exception raised when REST API execution fails
    """
    pass

class rcs(object):
    """ Python class that controls all interactions with RCS instance.
    """
    def __init__(self, rcs_def):
	""".. function:: init(rcs_def)

	Init authenticates with RCS instances as per rcs_def (dict) parameter. 
	The authentication token is stored in *token* attribute.

	*rcs_def* of *dict* type must have the following keys defined

	:param server: RCS instance FQDN/IP
	:param port: TCP port
	:param client_id: client identifier (e.g. admin)
	:param client_secret: client secret (e.g. pwd)
	:param grant_type: authentication type (e.g. password)
	:param username: username
	:param password: password
	:returns: object reference
	:raises: RcsDefFailure, GetAuthTokenFailure

	>>> import rcs_module
	>>> rcs_def={
	...         "server": "vsaf.rainbow.jungo.com",
	...         "port": "8080",
	...         "username": "admin@cisco.com",
	...         "password": "password",
	...         "client_id": "admin",
	...         "client_secret": "admin_secret",
	...         "grant_type": "password"
	... }
	>>> _rcs=rcs_module.rcs(rcs_def)
	>>>

	"""
	try:
		self.server = rcs_def["server"]
		self.port = rcs_def["port"]
		self.client_id = rcs_def["client_id"]
		self.client_secret = rcs_def["client_secret"]
		self.grant_type = rcs_def["grant_type"]
		self.username = rcs_def["username"]
		self.password = rcs_def["password"]
	except:
		raise RcsDefFailure
	self.token = None
	self._get_authentication_token()
	self.filter = None
	self.url = "http://" + self.server + ":" + self.port

    def _get_authentication_token(self):
	tokenReq = {}
	tokenReq['client_id'] = self.client_id
	tokenReq['client_secret'] = self.client_secret
	tokenReq['grant_type'] = self.grant_type
	tokenReq['username'] = self.username
	tokenReq['password'] = self.password

	url = "https://" + self.server + "/oauth/token"
	try: 
		ret = requests.post(url, tokenReq, verify=False)
	except:
		raise GetAuthTokenFailure
	try:
		# Follow RFC6750 OAuth 2.0 Authorization Bearer Token Usage
		self.token = "Bearer " + ret.json()['access_token']
	except:
		raise GetAuthTokenFailure

    def setFilter(self, filter):
	"""Set Filter"
	"""
	self.filter = filter

    ''' Admin Services '''

    def getAdminServices(self):
	""".. function:: getAdminServices()

	Get the list of /admin/services

	:returns: List of /admin/services (JSON)
	:raises: RcsApiFailure

	>>> _rcs.getAdminServices()
	{u'services': [{u'description': None, u'enabled': True, u'href': u'/admin/services/com:cisco:vsaf:self_care', u'config': {}, u'id': u'com:cisco:vsaf:self_care', u'name': u'self_care'}, {u'description': None, u'enabled': True, u'href': u'/admin/services/com:cisco:vsaf:scr', u'config': {}, u'id': u'com:cisco:vsaf:scr', u'name': u'scr'}, {u'description': None, u'enabled': True, u'href': u'/admin/services/com:cisco:vsaf:management_agent', u'config': {}, u'id': u'com:cisco:vsaf:management_agent', u'name': u'management'}, {u'description': None, u'enabled': False, u'href': u'/admin/services/com:cisco:vsaf:home_monitoring', u'config': {}, u'id': u'com:cisco:vsaf:home_monitoring', u'name': None}, {u'description': None, u'enabled': False, u'href': u'/admin/services/com:cisco:vsaf:signed_url', u'config': {}, u'id': u'com:cisco:vsaf:signed_url', u'name': None}, {u'description': None, u'enabled': False, u'href': u'/admin/services/com:cisco:vsaf:settings', u'config': {}, u'id': u'com:cisco:vsaf:settings', u'name': None}, {u'description': None, u'enabled': False, u'href': u'/admin/services/com:cisco:vsaf:home_master', u'config': {}, u'id': u'com:cisco:vsaf:home_master', u'name': None}, {u'description': None, u'enabled': False, u'href': u'/admin/services/com:cisco:vsaf:home_automation', u'config': {}, u'id': u'com:cisco:vsaf:home_automation', u'name': None}], u'meta': {u'total_count': 8, u'current_page': 1, u'total_pages': 1}}

	"""
	
	url = self.url + "/admin/services"
	hdr = {"Accept-version":"v2","Authorization":self.token}
	try:
		r = requests.get(url, headers = hdr)
	except:
		raise RcsApiFailure
	return r.json()

    ''' End of Admin Services '''

    ''' Admin Devices '''

    def getAdminDevices(self):
	""".. function:: getAdminDevices()

	Get the list of /admin/devices

	:returns: List of /admin/devices (JSON)
	:raises: RcsApiFailure

	>>> _rcs.getAdminDevices()
	{u'meta': {u'total_count': 3, u'current_page': 1, u'total_pages': 1}, u'devices': [{u'name': u'Device #1 for Velcom', u'customer_key': None, u'enabled': True, u'href': u'/admin/devices/d-91ce97d3e866b4a7005f9e6dee3b31c97f2b9a', u'services': [], u'config': None, u'id': u'd-91ce97d3e866b4a7005f9e6dee3b31c97f2b9a', u'uid': u'/C=IL/O=Jungo Ltd/OU=CTO/CN=Velcom-vCPE-1/serialNumber=20151103'}, {u'name': u'Device #2 for Velcom', u'customer_key': None, u'enabled': True, u'href': u'/admin/devices/d-e153bef08890c0e5d059aaa32437827ad229b3', u'services': [], u'config': None, u'id': u'd-e153bef08890c0e5d059aaa32437827ad229b3', u'uid': u'/C=IL/O=Jungo Ltd/OU=CTO/CN=Velcom-vCPE-2/serialNumber=20151103'}, {u'name': u'Jungo Home Gateway with Rainbow Application Framework', u'customer_key': None, u'enabled': True, u'href': u'/admin/devices/d-99fb5cf47a7093160ffbb0225231e0b4237ae4', u'services': [{u'name': u'management', u'service_enabled': True, u'enabled': True, u'device_config': None, u'config': {}, u'id': u'com:cisco:vsaf:management_agent'}, {u'name': None, u'service_enabled': False, u'enabled': True, u'device_config': None, u'config': {}, u'id': u'com:cisco:vsaf:home_monitoring'}, {u'name': None, u'service_enabled': False, u'enabled': True, u'device_config': None, u'config': {}, u'id': u'com:cisco:vsaf:signed_url'}, {u'name': None, u'service_enabled': False, u'enabled': True, u'device_config': None, u'config': {}, u'id': u'com:cisco:vsaf:settings'}, {u'name': None, u'service_enabled': False, u'enabled': True, u'device_config': None, u'config': {}, u'id': u'com:cisco:vsaf:home_master'}, {u'name': None, u'service_enabled': False, u'enabled': True, u'device_config': None, u'config': {}, u'id': u'com:cisco:vsaf:home_automation'}], u'config': None, u'id': u'd-99fb5cf47a7093160ffbb0225231e0b4237ae4', u'uid': u'/C=IL/O=Jungo Ltd/OU=CTO/CN=vVCAF for itay@jungo.com/serialNumber=1'}]}

	"""

	url = self.url + "/admin/devices"
	hdr = {"Accept-version":"v2","Authorization":self.token}
	try:
		r = requests.get(url, headers = hdr)
	except:
		raise RcsApiFailure
	return r.json()

    def getAdminDevice(self, device_id):
	""".. function:: getAdminDevice(device_id)

	Get device details by device UUID

	:param device_id: Device UUID value
	:type device_id: string
	:returns: /admin/device (JSON)
	:raises: RcsApiFailure

	>>> _rcs.getAdminDevice("d-99fb5cf47a7093160ffbb0225231e0b4237ae4")
	{u'device': {u'name': u'Jungo Home Gateway with Rainbow Application Framework', u'customer_key': None, u'enabled': True, u'href': u'/admin/devices/d-99fb5cf47a7093160ffbb0225231e0b4237ae4', u'services': [{u'name': u'management', u'service_enabled': True, u'enabled': True, u'device_config': None, u'config': {}, u'id': u'com:cisco:vsaf:management_agent'}, {u'name': None, u'service_enabled': False, u'enabled': True, u'device_config': None, u'config': {}, u'id': u'com:cisco:vsaf:home_monitoring'}, {u'name': None, u'service_enabled': False, u'enabled': True, u'device_config': None, u'config': {}, u'id': u'com:cisco:vsaf:signed_url'}, {u'name': None, u'service_enabled': False, u'enabled': True, u'device_config': None, u'config': {}, u'id': u'com:cisco:vsaf:settings'}, {u'name': None, u'service_enabled': False, u'enabled': True, u'device_config': None, u'config': {}, u'id': u'com:cisco:vsaf:home_master'}, {u'name': None, u'service_enabled': False, u'enabled': True, u'device_config': None, u'config': {}, u'id': u'com:cisco:vsaf:home_automation'}], u'config': None, u'id': u'd-99fb5cf47a7093160ffbb0225231e0b4237ae4', u'uid': u'/C=IL/O=Jungo Ltd/OU=CTO/CN=vVCAF for itay@jungo.com/serialNumber=1'}}
	>>>
	>>> _rcs.getAdminDevice("wrong")
	{u'errors': u'not found'}

	"""

	url = self.url + "/admin/devices/" + device_id
	hdr = {"Accept-version":"v2","Authorization":self.token}
	try:
		r = requests.get(url, headers = hdr)
	except:
		raise RcsApiFailure
	return r.json()

    # Exact match search for device Id 
    def getAdminDeviceIdByName(self, name):
	""".. function:: getAdminDeviceIdByName(device_name)

	Return device id for *name* key value equal to *device_name*. 
	Return *None* if such device does not exist
	If there is more than one matching device, the first match is returned

	:param device_name: device name
	:type device_name: string
	:returns: device id (string) or None
	:raises: RcsApiFailure

	>>> _rcs.getAdminDeviceIdByName("Jungo Home Gateway with Rainbow Application Framework")
	u'd-99fb5cf47a7093160ffbb0225231e0b4237ae4'
	>>> _rcs.getAdminDeviceIdByName("wrong")
	>>>

	"""
	try:
		devicesList = self.getAdminDevices()['devices']
	except:
		raise RcsApiFailure
	retValue = None
	for device in devicesList:
		if device['name'] == name:
			retValue = device['id']
	return retValue
	
    # Exact match search for device Id 
    def getAdminDeviceIdByUid(self, uid):
	""".. function:: getAdminDeviceIdByUid(device_uid)

	Return device id for *uid* key value equal to *device_uid*. 
	Return *None* if such device does not exist
	If there is more than one matching device, the first match is returned

	:param device_uid: device uid
	:type device_uid: string
	:returns: device id (string) or None
	:raises: RcsApiFailure

	>>> _rcs.getAdminDeviceIdByUid("/C=IL/O=Jungo Ltd/OU=CTO/CN=vVCAF for itay@jungo.com/serialNumber=1")
	u'd-99fb5cf47a7093160ffbb0225231e0b4237ae4'
	>>> _rcs.getAdminDeviceIdByUid("wrong")
	>>>

	"""
	try:
		devicesList = self.getAdminDevices()['devices']
	except:
		raise RcsApiFailure
	retValue = None
	for device in devicesList:
		if device['uid'] == uid:
			retValue = device['id']
	return retValue

    # if device with uid exists, device is updated
    def addAdminDevice(self, uid, name):
	""".. function:: addAdminDevice(device_uid, device_name)

	Add device with *uid* and *name* values.

	:param device_uid: device uid
	:param device_name: device_name
	:returns: JSON-formatted response::

		'added' = True|False
		'status' = HTTP Response code from  RCS
		'description' = Error description if request failed
		'response' = JSON response if request succeeded

	:raises: RcsApiFailure

	.. note::

		If device already exists, function will succeed and new device is not created

	>>> _rcs.addAdminDevice("myUid", "myName")
	{'status': 200, 'added': True, 'response': {u'device': {u'name': u'myName', u'customer_key': None, u'enabled': True, u'href': u'/admin/devices/d-4131b46a5c8cc0515abc24d3a047bde611f6bc', u'services': [], u'config': None, u'id': u'd-4131b46a5c8cc0515abc24d3a047bde611f6bc', u'uid': u'myUid'}}}

	"""

	url = self.url + "/admin/devices/"
	hdr = {"Accept-version":"v2", "Authorization":self.token, "Content-type": "application/json"}
	payload = {}
	payload['device'] = {'uid': uid, 'name': name }
	try:
		r = requests.post(url, json.dumps(payload), headers = hdr)
	except:
		raise RcsApiFailure

	retValue = {}
	if r.status_code == 200:
		retValue['added'] = True
		retValue['status'] = 200
		retValue['response'] = r.json()
	else:
		retValue['added'] = False
		retValue['status'] = r.status_code
		retValue['description'] = ""
		retValue['response'] = ""
		if r.status_code == 400:
			retValue['description'] = "The Content-Type header is either missing or specifies an unsupported MIME type, the request body does not contain a device object, or the object is empty."
		if r.status_code == 406:
			retValue['description'] = "The Accept-Version header is either missing or specifies an API version not supported by the server."
			retValue['response'] = r.json()
		if r.status_code == 422:
			retValue['description'] = "The submitted device object did not pass validation."
			retValue['response'] = r.json()
		if r.status_code == 500:
			retValue['description'] = "The request body could not be parsed because of JSON encoding errors."

	return retValue

    def deleteAdminDevice(self, device_id):
	""".. function:: deleteAdminDevice(device_id)

	Delete device with *id* value equal to *device_id*

	:param device_id: device id
	:returns: JSON-formatted response::

		'deleted' = True|False
		'status' = HTTP Response code from  RCS
		'description' = Error description if request failed
		'response' = JSON response if request succeeded

	:raises: RcsApiFailure

	>>> _rcs.deleteAdminDevice("d-4131b46a5c8cc0515abc24d3a047bde611f6bc")
	{'deleted': True, 'status': 204, 'description': 'The Device resource was successfully deleted.'}
	>>> _rcs.deleteAdminDevice("d-4131b46a5c8cc0515abc24d3a047bde611f6bc")
	{'deleted': False, 'status': 404, 'description': 'The Device resource with the specified deviceId could not be found.', 'response': {u'errors': u'not found'}}

	"""
	url = self.url + "/admin/devices/" + device_id
	hdr = {"Accept-version":"v2", "Authorization":self.token}
	try:
		r = requests.delete(url, headers = hdr)
	except:
		raise RcsApiFailure

	retValue = {}
	if r.status_code >= 200 and r.status_code <= 299:
		retValue['deleted'] = True
		retValue['status'] = r.status_code
		retValue['description'] = ""
		if r.status_code == 204:
			retValue['description'] = "The Device resource was successfully deleted."
	else:
		retValue['deleted'] = False
		retValue['status'] = r.status_code
		retValue['description'] = ""
		retValue['response'] = ""
		if r.status_code == 404:
			retValue['description'] = "The Device resource with the specified deviceId could not be found."
			retValue['response'] = r.json()
		if r.status_code == 406:
			retValue['description'] = "The Accept-Version header is either missing or specifies an API version not supported by the server."
			retValue['response'] = r.json()

	return retValue

    ''' End of Admin Devices '''

    ''' Admin Device Authorization '''	

    def getAdminDeviceAuth(self, device_id):
	""".. function:: getAdminDeviceAuth(device_id)

	Get device authorization details by device UUID

	:param device_id: Device UUID value
	:type device_id: string
	:returns: device authorization details (JSON)
	:raises: RcsApiFailure

	>>> _rcs.getAdminDeviceAuth("d-99fb5cf47a7093160ffbb0225231e0b4237ae4")
	{u'authorizations': [{u'admin_comment': None, u'user_id': u'u-ce5cb1ab58e6578872ea8755c7613bb0a48e68', u'href': u'/admin/devices/d-99fb5cf47a7093160ffbb0225231e0b4237ae4/authorizations/a-f89c2734cbc9b0b124cccfdb245ec72eae01f7', u'device_id': u'd-99fb5cf47a7093160ffbb0225231e0b4237ae4', u'config': {}, u'id': u'a-f89c2734cbc9b0b124cccfdb245ec72eae01f7', u'permissions': {u'owner': True, u'admin': True, u'invite': True}}]}

	"""

	url = self.url + "/admin/devices/" + device_id + "/authorizations"
	hdr = {"Accept-version":"v2","Authorization":self.token}
	try:
		r = requests.get(url, headers = hdr)
	except:
		raise RcsApiFailure
	return r.json()

    def addAdminDeviceAuth(self, device_id, user_id):
	""".. function:: addAdminDeviceAuth(device_id, user_id)

	Add device authorization

	:param device_id: Device UUID value
	:type device_id: string
	:param user_id: User UUID value
	:type user_id: string
	:returns: add device authorization result (JSON)::

		'added' = True|False
		'status' = HTTP Response code from  RCS
		'description' = Error description if request failed
		'response' = JSON response if request succeeded

	:raises: RcsApiFailure

	>>> _rcs.addAdminDeviceAuth("d-99fb5cf47a7093160ffbb0225231e0b4237ae4","u-ce5cb1ab58e6578872ea8755c7613bb0a48e68")
	{'status': 200, 'added': True, 'response': {u'authorization': {u'admin_comment': None, u'user_id': u'u-ce5cb1ab58e6578872ea8755c7613bb0a48e68', u'href': u'/admin/devices/d-99fb5cf47a7093160ffbb0225231e0b4237ae4/authorizations/a-8b55bc89f02c6e17c46706ad64fa5ccad4bec1', u'device_id': u'd-99fb5cf47a7093160ffbb0225231e0b4237ae4', u'config': {}, u'id': u'a-8b55bc89f02c6e17c46706ad64fa5ccad4bec1', u'permissions': {u'owner': True, u'admin': True, u'invite': True}}}}

	"""

	url = self.url + "/admin/devices/" + device_id + "/authorizations"
	hdr = {"Accept-version":"v2", "Authorization":self.token, "Content-type": "application/json"}
	payload = {}
	payload['authorization'] = {'user_id': user_id, 'permissions': {"owner": True, "admin": True, "invite": True} }
	try:
		r = requests.post(url, json.dumps(payload), headers = hdr)
	except:
		raise RcsApiFailure

	retValue = {}
	if r.status_code == 200:
		retValue['added'] = True
		retValue['status'] = 200
		retValue['response'] = r.json()
	else:
		retValue['added'] = False
		retValue['status'] = r.status_code
		retValue['description'] = ""
		retValue['response'] = ""
		if r.status_code == 404:
			retValue['description'] = "The User resource with the specified userId could not be found."
			retValue['response'] = r.json()
		if r.status_code == 406:
			retValue['description'] = "The Accept-Version header is either missing or specifies an API version not supported by the server."
			retValue['response'] = r.json()
		if r.status_code == 422:
			retValue['description'] = "The submitted authorization object did not pass validation."
			retValue['response'] = r.json()
		if r.status_code == 500:
			retValue['description'] = "The request body could not be parsed because of JSON encoding errors."
	return retValue

    def deleteAdminDeviceAuth(self, device_id, auth_id):
	""".. function:: deleteAdminDeviceAuth(device_id, auth_id)

	Delete device authorization

	:param device_id: Device UUID value
	:type device_id: string
	:param auth_id: Authorization UUID value
	:type auth_id: string
	:returns: delete device authorization result (JSON)::

		'deleted' = True|False
		'status' = HTTP Response code from  RCS
		'description' = Error description if request failed
		'response' = JSON response if request succeeded

	:raises: RcsApiFailure

	>>> _rcs.deleteAdminDeviceAuth("d-99fb5cf47a7093160ffbb0225231e0b4237ae4","a-f89c2734cbc9b0b124cccfdb245ec72eae01f7")
	{'deleted': True, 'status': 204, 'description': 'The Authorization resource was successfully deleted.'}
	>>> _rcs.deleteAdminDeviceAuth("d-99fb5cf47a7093160ffbb0225231e0b4237ae4","a-f89c2734cbc9b0b124cccfdb245ec72eae01f7")
	{'deleted': False, 'status': 404, 'description': 'The Device resource with the specified deviceId or the Authorization resource with the specific authorizationId could not be found.', 'response': {u'errors': u'not found'}}

	"""

	url = self.url + "/admin/devices/" + device_id + "/authorizations/" + auth_id
	hdr = {"Accept-version":"v2", "Authorization":self.token}
	try:
		r = requests.delete(url, headers = hdr)
	except:
		raise RcsApiFailure

	retValue = {}
	if r.status_code >= 200 and r.status_code <= 299:
		retValue['deleted'] = True
		retValue['status'] = r.status_code
		retValue['description'] = ""
		if r.status_code == 204:
			retValue['description'] = "The Authorization resource was successfully deleted."
	else:
		retValue['deleted'] = False
		retValue['status'] = r.status_code
		retValue['description'] = ""
		retValue['response'] = ""
		if r.status_code == 404:
			retValue['description'] = "The Device resource with the specified deviceId or the Authorization resource with the specific authorizationId could not be found."
			retValue['response'] = r.json()
		if r.status_code == 406:
			retValue['description'] = "The Accept-Version header is either missing or specifies an API version not supported by the server."
			retValue['response'] = r.json()

	return retValue

    ''' End of Admin Device Authorization '''

    ''' Admin Users '''

    def getAdminUsers(self):
	""".. function:: getAdminUsers()

	Get list of all users

	:returns: list of admin users (JSON)
	:raises: RcsApiFailure

	>>> _rcs.getAdminUsers()
	{u'meta': {u'total_count': 3, u'current_page': 1, u'total_pages': 1}, u'users': [{u'name': None, u'customer_key': None, u'id': u'u-ce5cb1ab58e6578872ea8755c7613bb0a48e68', u'href': u'/admin/users/u-ce5cb1ab58e6578872ea8755c7613bb0a48e68', u'provider': u'local', u'provider_uid': u'demo@cisco.com', u'config': {}, u'email': u'demo@cisco.com'}, {u'name': u'user1 for Velcom PoC', u'customer_key': None, u'id': u'u-cee5668160ccb8f4972033e9a3a4000b21c06c', u'href': u'/admin/users/u-cee5668160ccb8f4972033e9a3a4000b21c06c', u'provider': u'local', u'provider_uid': u'user1@velcom.by', u'config': {}, u'email': u'user1@velcom.by'}, {u'name': u'user2 for Velcom PoC', u'customer_key': None, u'id': u'u-068c80f50233a299bf017fd44034ed7c3c6bd2', u'href': u'/admin/users/u-068c80f50233a299bf017fd44034ed7c3c6bd2', u'provider': u'local', u'provider_uid': u'user2@velcom.by', u'config': {}, u'email': u'user2@velcom.by'}]}

	"""

	url = self.url + "/admin/users"
	hdr = {"Accept-version":"v2","Authorization":self.token}
	try:
		r = requests.get(url, headers = hdr)
	except:
		raise RcsApiFailure

	return r.json()

    def getAdminUser(self, user_id):
	""".. function:: getAdminUser(user_id)

	Get details of admin user by user UUID value

	:param user_id: user UUID
	:type user_id: string
	:returns: details of admin users (JSON)
	:raises: RcsApiFailure

	>>> _rcs.getAdminUser("u-ce5cb1ab58e6578872ea8755c7613bb0a48e68")
	{u'user': {u'name': None, u'customer_key': None, u'id': u'u-ce5cb1ab58e6578872ea8755c7613bb0a48e68', u'href': u'/admin/users/u-ce5cb1ab58e6578872ea8755c7613bb0a48e68', u'provider': u'local', u'provider_uid': u'demo@cisco.com', u'config': {}, u'email': u'demo@cisco.com'}}
	>>> _rcs.getAdminUser("wrong")
	{u'errors': u'not found'}

	"""

	url = self.url + "/admin/users/" + user_id
	hdr = {"Accept-version":"v2","Authorization":self.token}
	try:
		r = requests.get(url, headers = hdr)
	except:
		raise RcsApiFailure
	return r.json()

    # Exact match search for user Id 
    def getAdminUserIdByName(self, name):
	""".. function:: getAdminUser(user_name)

	Get admin user UUID by user name value. None if not found (exact match)

	:param user_name: admin user name to be found
	:type user_name: string
	:returns: admin user uuid
	:raises: RcsApiFailure

	>>> _rcs.getAdminUserIdByName("demo@cisco.com")
	u'u-ce5cb1ab58e6578872ea8755c7613bb0a48e68'
	>>> _rcs.getAdminUserIdByName("wrong")
	>>>

	"""
	
	try:
		usersList = self.getAdminUsers()['users']
	except:
		RcsApiFailure
	retValue = None
	for user in usersList:
		if user['email'] == name:
			retValue = user['id']
	return retValue
	
    def addAdminUser(self, email, name, password):
	""".. function:: addAdminUser(email, name, password)

	Add admin user

	:param email: the same as username
	:type email: string
	:param name: description
	:type name: name
	:param password: password
	:type password: string
	:returns: add user result (JSON)::

		'added' = True|False
		'status' = HTTP Response code from  RCS
		'description' = Error description if request failed
		'response' = JSON response if request succeeded

	:raises: RcsApiFailure

	>>> _rcs.addAdminUser("test@test.com","Test user","123456")
	{'status': 200, 'added': True, 'response': {u'user': {u'name': u'Test user', u'customer_key': None, u'id': u'u-f3455bb4fa37991855bc0a2744f30f53886905', u'href': u'/admin/users/u-f3455bb4fa37991855bc0a2744f30f53886905', u'provider': u'local', u'provider_uid': u'test@test.com', u'config': {}, u'email': u'test@test.com'}}}

	"""

	url = self.url + "/admin/users/"
	hdr = {"Accept-version":"v2", "Authorization":self.token, "Content-type": "application/json"}
	payload = {}
	payload['user'] = {'email': email, 'name': name, 'password': password }
	try:
		r = requests.post(url, json.dumps(payload), headers = hdr)
	except:
		raise RcsApiFailure

	retValue = {}
	if r.status_code == 200:
		retValue['added'] = True
		retValue['status'] = 200
		retValue['response'] = r.json()
	else:
		retValue['added'] = False
		retValue['status'] = r.status_code
		retValue['description'] = ""
		retValue['response'] = ""
		if r.status_code == 500:
			retValue['description'] = "The request body could not be parsed because of JSON encoding errors."

	return retValue

    def deleteAdminUser(self, user_id):
	""".. function:: deleteAdminUser(user_id)

	Delete user by user UUID

	:param user_id: user UUID
	:type user_id: string
	:returns: delete user result (JSON)::

		'deleted' = True|False
		'status' = HTTP Response code from  RCS
		'description' = Error description if request failed
		'response' = JSON response if request succeeded

	:raises: RcsApiFailure

	>>> _rcs.deleteAdminUser("u-f3455bb4fa37991855bc0a2744f30f53886905")
	{'deleted': True, 'status': 204, 'description': 'The User resource was successfully deleted.'}
	>>> _rcs.deleteAdminUser("u-f3455bb4fa37991855bc0a2744f30f53886905")
	{'deleted': False, 'status': 404, 'description': 'The User resource with the specified userId could not be found.', 'response': {u'errors': u'not found'}}

	"""

	url = self.url + "/admin/users/" + user_id
	hdr = {"Accept-version":"v2", "Authorization":self.token}
	try:
		r = requests.delete(url, headers = hdr)
	except:
		raise RcsApiFailure

	retValue = {}
	if r.status_code >= 200 and r.status_code <= 299:
		retValue['deleted'] = True
		retValue['status'] = r.status_code
		retValue['description'] = ""
		if r.status_code == 204:
			retValue['description'] = "The User resource was successfully deleted."
	else:
		retValue['deleted'] = False
		retValue['status'] = r.status_code
		retValue['description'] = ""
		retValue['response'] = ""
		if r.status_code == 404:
			retValue['description'] = "The User resource with the specified userId could not be found."
			retValue['response'] = r.json()

	return retValue

    ''' End of Admin Users '''

    ''' Admin Users Authorization '''

    def getAdminUserAuth(self, user_id):
	""".. function:: getAdminUserAuth(user_id)

	Get device authorization details for user by user UUID

	:param user_id: user UUID
	:type user_id: string
	:returns: device authorization details (JSON)
	:raises: RcsApiFailure

	>>> _rcs.getAdminUserAuth("u-ce5cb1ab58e6578872ea8755c7613bb0a48e68")
	{u'authorizations': [{u'admin_comment': None, u'user_id': u'u-ce5cb1ab58e6578872ea8755c7613bb0a48e68', u'href': u'/admin/devices/d-99fb5cf47a7093160ffbb0225231e0b4237ae4/authorizations/a-8b55bc89f02c6e17c46706ad64fa5ccad4bec1', u'device_id': u'd-99fb5cf47a7093160ffbb0225231e0b4237ae4', u'config': {}, u'id': u'a-8b55bc89f02c6e17c46706ad64fa5ccad4bec1', u'permissions': {u'owner': True, u'admin': True, u'invite': True}}]}
	>>> _rcs.getAdminUserAuth("wrong")
	{u'errors': u'not found'}

	"""

	url = self.url + "/admin/users/" + user_id + "/authorizations"
	hdr = {"Accept-version":"v2","Authorization":self.token}
	try:
		req = requests.get(url, headers = hdr)
	except:
		raise RcsApiFailure
	return req.json()

    def addAdminUserAuth(self, user_id, device_id):
	""".. function:: addAdminUserAuth(user_id, device_id)

	Add device authorization for user by user UUID

	:param user_id: user UUID
	:type user_id: string
	:param device_id: device's uuid value
	:type device_id: string
	:returns: add device authorization result (JSON)::

		'added' = True|False
		'status' = HTTP Response code from  RCS
		'description' = Error description if request failed
		'response' = JSON response if request succeeded

	:raises: RcsApiFailure

	>>> _rcs.addAdminUserAuth("u-8273fbc6dd29883c3be2e334ab535a9e7abf98","d-99fb5cf47a7093160ffbb0225231e0b4237ae4")
	{'status': 200, 'added': True, 'response': {u'authorization': {u'admin_comment': None, u'user_id': u'u-8273fbc6dd29883c3be2e334ab535a9e7abf98', u'href': u'/admin/devices/d-99fb5cf47a7093160ffbb0225231e0b4237ae4/authorizations/a-e24d9ed54302ee51cabd31d4ec6e56632fd9cd', u'device_id': u'd-99fb5cf47a7093160ffbb0225231e0b4237ae4', u'config': {}, u'id': u'a-e24d9ed54302ee51cabd31d4ec6e56632fd9cd', u'permissions': {u'owner': True, u'admin': True, u'invite': True}}}}

	"""
	url = self.url + "/admin/users/" + user_id + "/authorizations"
	hdr = {"Accept-version":"v2", "Authorization":self.token, "Content-type": "application/json"}
	payload = {}
	payload['authorization'] = {'device_id': device_id, 'permissions': {"owner": True, "admin": True, "invite": True} }
	try:
		r = requests.post(url, json.dumps(payload), headers = hdr)
	except:
		raise RcsApiFailure

	retValue = {}
	if r.status_code == 200:
		retValue['added'] = True
		retValue['status'] = 200
		retValue['response'] = r.json()
	else:
		retValue['added'] = False
		retValue['status'] = r.status_code
		retValue['description'] = ""
		retValue['response'] = ""
		if r.status_code == 406:
			retValue['description'] = "The Accept-Version header is either missing or specifies an API version not supported by the server."
			retValue['response'] = r.json()
		if r.status_code == 422:
			retValue['description'] = "The submitted authorization object did not pass validation."
			retValue['response'] = r.json()
		if r.status_code == 500:
			retValue['description'] = "The request body could not be parsed because of JSON encoding errors."
	return retValue

    def deleteAdminUserAuth(self, user_id, auth_id):
	""".. function:: deleteAdminUserAuth(user_id, device_id)

	Delete device authorization for user by user UUID

	:param user_id: user UUID
	:type user_id: string
	:param device_id: device's uuid value
	:type device_id: string
	:returns: delete device authorization result (JSON)::

		'deleted' = True|False
		'status' = HTTP Response code from  RCS
		'description' = Error description if request failed
		'response' = JSON response if request succeeded

	:raises: RcsApiFailure

	>>> _rcs.deleteAdminUserAuth("u-8273fbc6dd29883c3be2e334ab535a9e7abf98", "a-e24d9ed54302ee51cabd31d4ec6e56632fd9cd")
	{'deleted': True, 'status': 204, 'description': 'The Authorization resource was successfully deleted.'}

	"""

	url = self.url + "/admin/users/" + user_id + "/authorizations/" + auth_id
	hdr = {"Accept-version":"v2", "Authorization":self.token}
	try:
		r = requests.delete(url, headers = hdr)
	except:
		raise RcsApiFailure

	retValue = {}
	if r.status_code >= 200 and r.status_code <= 299:
		retValue['deleted'] = True
		retValue['status'] = r.status_code
		retValue['description'] = ""
		if r.status_code == 204:
			retValue['description'] = "The Authorization resource was successfully deleted."
	else:
		retValue['deleted'] = False
		retValue['status'] = r.status_code
		retValue['description'] = ""
		retValue['response'] = ""
		if r.status_code == 404:
			retValue['description'] = "The User resource with the specified deviceId or the Authorization resource with the specific authorizationId could not be found."
			retValue['response'] = r.json()
		if r.status_code == 406:
			retValue['description'] = "The Accept-Version header is either missing or specifies an API version not supported by the server."
			retValue['response'] = r.json()

	return retValue

    ''' End of Admin Users Authorization '''

    ''' Device Registration control '''

    def getRegistrationState(self, uid):
	""".. function:: getRegistrationState(device_uid)

	Get device registration state by device uid (not UUID)

	:param device_uid: device's uid value (not UUID)
	:type device_uid: string
	:returns: registration state (JSON)::

		'registered' = True|False
		'status' = HTTP Response code from  RCS
		'description' = Error description if request failed
		'response' = JSON response if request succeeded

	:raises: RcsApiFailure

	>>> _rcs.getRegistrationState("/C=IL/O=Jungo Ltd/OU=CTO/CN=Velcom-vCPE-1/serialNumber=20151103")
	{'status': 200, 'registered': True, 'description': '', 'response': {u'device': {u'name': u'Device #1 for Velcom', u'hrefs': [{u'href': u'https://6ff55dddac15b40721a08578ebe4004129c0ae0a.vsaf-velcom.rainbow.jungo.com:10443', u'type': u'wan', u'relay': True}], u'services': [], u'config': None, u'id': u'd-91ce97d3e866b4a7005f9e6dee3b31c97f2b9a', u'uid': u'/C=IL/O=Jungo Ltd/OU=CTO/CN=Velcom-vCPE-1/serialNumber=20151103'}}}

	"""

	url = self.url + "/device"
	hdr = {"Accept-version":"v2", "Authorization":self.token, "Content-type": "application/json", "X-SSL-Client-Subject": uid, "X-SSL-Client-Verify": "SUCCESS"}

	try:
		r = requests.get(url, headers = hdr)
	except:
		raise RcsApiFailure

	retValue = {}
	if r.status_code == 200:
		retValue['registered'] = True
		retValue['status'] = 200
		retValue['description'] = ""
		retValue['response'] = r.json()
	else:
		retValue['registered'] = False
		retValue['status'] = r.status_code
		retValue['description'] = ""
		retValue['response'] = ""
		if r.status_code == 403:
			retValue['description'] = "Either the X-SSL-Client-Verify header is either missing or indicates that the client certificate did not pass verification, or the X-SSL-Client-Subject header is missing."
			retValue['response'] = r.json()
		if r.status_code == 404:
			retValue['description'] = "A device with the Device Unique Identifier (UID) specified in the X-SSL-Client-Subject header could not be found."
		if r.status_code == 406:
			retValue['description'] = "The Accept-Version header is either missing or specifies an API version not supported by the server."
			retValue['response'] = r.json()

	return retValue

    def registerDevice(self, uid, name):
	""".. function:: registerDevice(device_uid, device_name)

	Create registration state on RCS; normally should be done by (v)CPE

	:param device_uid: device's uid value (not UUID)
	:type device_uid: string
	:param device_name: device's name
	:type device_name: string
	:returns: registration creation result (JSON)::

		'added' = True|False
		'status' = HTTP Response code from  RCS
		'description' = Error description if request failed
		'response' = JSON response if request succeeded

	:raises: RcsApiFailure

	>>> _rcs.registerDevice("/C=IL/O=Jungo Ltd/OU=CTO/CN=Velcom-vCPE-1/serialNumber=20151103", "Device #1 for Velcom")
	{'status': 200, 'added': True}

	"""

	url = self.url + "/device"
	hdr = {"Accept-version":"v2", "Authorization":self.token, "Content-type": "application/json", "X-SSL-Client-Subject": uid, "X-SSL-Client-Verify": "SUCCESS"}
	payload = {}
	payload['device'] = {'name': name}
	try:
		r = requests.put(url, json.dumps(payload), headers = hdr)
	except:
		raise RcsApiFailure

	retValue = {}
	if r.status_code == 200:
		retValue['added'] = True
		retValue['status'] = 200
	else:
		retValue['added'] = False
		retValue['status'] = r.status_code
		retValue['description'] = ""
		retValue['response'] = ""
		if r.status_code == 400:
			retValue['description'] = "The Content-Type header is either missing or specifies an unsupported MIME type, the request body does not contain a device object, or the object is empty."
		if r.status_code == 403:
			retValue['description'] = "Either the X-SSL-Client-Verify header is either missing or indicates that the client certificate did not pass verification, or the X-SSL-Client-Subject header is missing."
			retValue['response'] = r.json()
		if r.status_code == 404:
			retValue['description'] = "A device with the Device Unique Identifier (UID) specified in the X-SSL-Client-Subject header could not be found."
		if r.status_code == 406:
			retValue['description'] = "The Accept-Version header is either missing or specifies an API version not supported by the server."
			retValue['response'] = r.json()
		if r.status_code == 422:
			retValue['description'] = "The submitted authorization object did not pass validation."
			retValue['response'] = r.json()
		if r.status_code == 500:
			retValue['description'] = "The request body could not be parsed because of JSON encoding errors."

	return retValue

    ''' End of Device Registration control '''

    def databaseDump(self, format="Text"):
	if format == "Text":
		self.databaseDumpText()
	if format == "Json":
		return self.databaseDumpJson()
	
    def databaseDumpText(self):
	self.databaseDumpTextDevices()
	self.databaseDumpTextServices()
	self.databaseDumpTextUsers()

    def databaseDumpTextDevices(self):
	print "Devices List"
	print "------------"
	devices = self.getAdminDevices()
	cnt = devices['meta']['total_count']
	print "Count " + str(cnt)
	print ""

	for device in devices['devices']:
		print "Device ID: " + device['id']
		print "Device DN: " + device['uid']
		print "Device Name: " + device['name']
		print "Device Services: " 
		for service in device['services']:
			print "\t" + service['id']
		print "Device Authorizations: "
		authorizations = self.getAdminDeviceAuth(device['id'])
		for auth in authorizations['authorizations']:
			user = self.getAdminUser(auth['user_id'])
			print "\t" + user['user']['name']
		print ""
	print "END\n"

    def databaseDumpTextServices(self):
	print "Services List"
	print "-------------"
	services = self.getAdminServices()
	cnt = services['meta']['total_count']
	print "Count " + str(cnt)
	print ""

	for service in services['services']:
		print service['id']
		print ""
	print "END\n"

    def databaseDumpTextUsers(self):
	print "Users List"
	print "----------"
	
	users = self.getAdminUsers()
	cnt = users['meta']['total_count']
	print "Count " + str(cnt)
	print ""

	for user in users['users']:
		print "Name: " + user['name']
		authorizations = self.getAdminUserAuth(user['id'])
		if authorizations['authorizations']:
			print "User Authorizations:"
			for auth in authorizations['authorizations']:
				device_id = auth['device_id']
				device = self.getAdminDevice(device_id)
				print "\t" + device['device']['name']
		print ""
	print "END\n"

    def databaseDumpJson(self):
	retValue = self.getAdminDevices()
	
	return retValue
	
