import datetime


class Path:
    _id = None
    _endpoints = []


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
            if Tag.validade(tag) is False:
                return False
        return True


class Tag:
    _type = None
    _value = None

    @staticmethod
    def validate(data):
        if not isinstance(data, dict):
            return False
        type = data.get('type')
        value = data.get('value')
        if type is None or value is None:
            return False
        try:
            int(value)
        except TypeError:
            return False
        return True


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
        uni_a = data.get('uni_a')
        uni_z = data.get('uni_z')
        name = data.get('name')
        if uni_a is None or uni_z is None or name is None:
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
