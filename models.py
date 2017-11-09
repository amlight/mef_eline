import datetime
from kytos.core import log

class Path:
    _id = None
    _endpoints = []

    def __init__(self, endpoints):
        self._endpoints = endpoints

    @staticmethod
    def validade(data):
        if not isinstance(data, dict):
            return False
        try:
            endpoints = data['endpoints']
            for endpoint in endpoints:
                if Endpoint.validate(endpoint)is False:
                    return False
        except KeyError:
            return False
        return True

    def to_dict(self):
        path_dict = {'endpoints': []}
        for endpoint in self._endpoints:
            path_dict['endpoints'].append(endpoint.to_dict())

        return path_dict


class Tag:
    _type = None
    _value = None

    def __init__(self, tag_type, value):
        self._type = tag_type
        self._value = value

    @staticmethod
    def validate(data):
        if not isinstance(data, dict):
            return False
        tag_type = data.get('type')
        value = data.get('value')
        log.info('aaa %s %s' % (tag_type, value))
        if tag_type is None or value is None:
            return False
        try:
            int(value)
        except TypeError:
            return False
        return True

    def to_dict(self):
        tag_dict = {}
        tag_dict['type'] = self._type
        tag_dict['value'] = self._value

        return tag_dict


class Endpoint:
    _dpid = None
    _port = None
    _tag = None

    def __init__(self, dpid, port, tag=None):
        self._dpid = dpid
        self._port = port
        self._tag = tag

    @staticmethod
    def validate(data):
        if not isinstance(data, dict):
            return False
        dpid = data.get('dpid')
        port = data.get('port')
        if dpid is None or port is None:
            return False
        tag = data.get('tag')
        if tag is not None:
            if Tag.validate(tag) is False:
                return False
        return True

    def to_dict(self):
        endpoint_dict = {}
        endpoint_dict['dpid'] = self._dpid
        endpoint_dict['port'] = self._port
        if self._tag:
            endpoint_dict['tag'] = self._tag.to_dict()

        return endpoint_dict


class Link:
    _id = None
    _endpoint_a = None
    _endpoint_b = None

    @staticmethod
    def validate(data):
        if not isinstance(data, dict):
            return False
        endpoint_a = data.get('endpoint_a')
        endpoint_b = data.get('endpoint_b')
        if endpoint_a is None or endpoint_b is None:
            return False
        if Endpoint.validate(endpoint_a) is False:
            return False
        if Endpoint.validate(endpoint_b) is False:
            return False
        return True

    def to_dict(self):
        link_dict = {}
        link_dict['endpoint_a'] = self._endpoint_a.to_dict()
        link_dict['endpoint_b'] = self._endpoint_b.to_dict()

        return link_dict


class NewCircuit:
    _name = None
    _start_date = None
    _end_date = None
    _links = None
    _backup_links = None
    _uni_a = None
    _uni_z = None

    @staticmethod
    def validate(data):
        if not isinstance(data, dict):
            return False
        try:
            uni_a = data['uni_a']
            uni_z = data['uni_z']
            name = data['name']
        except KeyError:
            return False
        if Endpoint.validate(uni_a) is False:
            return False
        if Endpoint.validate(uni_z) is False:
            return False
        links = data.get('links')
        if links is not None:
            try:
                for link in links:
                    if Link.validate(link) is False:
                        return False
            except TypeError:
                return False
        backup_links = data.get('backup_links')
        if backup_links is not None:
            try:
                for link in backup_links:
                    if Link.validate(link) is False:
                        return False
            except TypeError:
                return False
        start_date = data.get('start_date')
        if start_date is not None:
            try:
                datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return False
        end_date = data.get('end_date')
        if end_date is not None:
            try:
                datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return False
        bandwidth = data.get('bandwidth')
        if bandwidth is not None:
            try:
                int(bandwidth)
            except TypeError:
                return False
        return True


class Circuit:
    _id = None
    _name = None
    _start_date = None
    _end_date = None
    _path = None
    _backup_path = None

    def __init__(self, id, name, path, start_date=None, end_date=None, backup_path=None):
        self._id = id
        self._name = name
        self._start_date = start_date
        self._end_date = end_date
        self._path = path
        self._backup_path = backup_path

    @staticmethod
    def validate(data):
        if not isinstance(data, dict):
            return False
        try:
            name = data['name']
            path = data['path']
        except KeyError:
            return False
        if Path.validade(path) is False:
            return False
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        backup_path = data.get('backup_path')

        if start_date:
            try:
                datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return False
        if end_date:
            try:
                datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return False
        if backup_path:
            if Path.validade(backup_path) is False:
                return False
        return True

    def to_dict(self):
        circuit_dict = {}
        circuit_dict['id'] = self._id
        circuit_dict['name'] = self._name
        circuit_dict['start_date'] = self._start_date
        circuit_dict['end_date'] = self._end_date
        circuit_dict['path'] = self._path.to_dict()
        if self._backup_path:
            circuit_dict['backup_path'] = self._backup_path.to_dict()

        return circuit_dict
