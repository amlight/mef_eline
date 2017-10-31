class Path:
    _id = None
    _endpoints = []


class Endpoint:
    _dpid = None
    _port = None
    _tag = None




class Tag:
    _type = None
    _value = None


class Link:
    _id = None
    _endpoint_a = None
    _endpoint_b = None


class Circuit:
    _id = None
    _name = None
    _start_date = None
    _end_date = None
    _path = None
    _backup_path = None

    def __init__(self):
        pass