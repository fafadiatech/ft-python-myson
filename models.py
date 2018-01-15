# mongodb models file create models to be used in application
from pymongo import MongoClient
from functools import wraps
from bson.objectid import ObjectId


# mongodb connection handler
try:
    mongo = MongoClient("localhost", 27017)
    print("MongoDB Connected successfully!!!")
except pymongo.errors.ConnectionFailure as e:
    raise Exception("Could not connect to MongoDB: %s" % e)


# Initialize myson mongodb database
db = mongo.myson


class MissingFields(Exception):
    """
    missing model field exception
    """
    pass


class UnknownField(Exception):
    """
    unknown model field exception
    """
    pass


def validate(func):
    """
    validate fields and raise unknown field exception if fields do not match
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        for key, value in kwargs.items():
            if key not in self.fields:
                raise UnknownField("unknown field {0}".format(key))
        return func(self, *args, **kwargs)
    return wrapper


class Model(object):
    """
    base model class for mongo collections
    """

    @validate
    def create(self, *args, **kwargs):
        if not all(map(lambda each: each in kwargs.keys(), self.required_fields)):
            raise MissingFields(
                "required fields are missing uid & phone number")

        result = self.collection.insert(kwargs)
        kwargs['_id'] = result
        return kwargs

    @validate
    def get(self, *args, **kwargs):
        """
        get mongodb document for given kwargs
        """
        return self.collection.find_one(kwargs)

    @validate
    def filter(self, *args, **kwargs):
        """
        filter mongodb collection for given kwargs
        """
        result = self.collection.find(kwargs)
        return list(result)

    @validate
    def count(self, *args, **kwargs):
        """
        get mongodb document count for given kwargs
        """
        return self.collection.count(kwargs)

    @validate
    def update(self, *args, **kwargs):
        """
        update mongodb collection for given kwargs
        """
        return self.collection.find_one_and_update({"_id": ObjectId(args[0])}, {"$set": kwargs})


class User(Model):
    """
    user collection to store user details
    """

    def __init__(self):
        """
        initialize mongodb user collection with fields and required fileds
        """
        self.collection = db.user
        self.fields = ["_id", "uid", "phone_num", "first_name",
                       "last_name", "username", "photo", "is_admin"]
        self.required_fields = ["uid", "phone_num"]

    @property
    def admins(self):
        """
        method to get list of admins in user models
        """
        users = self.filter(is_admin=True)
        return [i['uid'] for i in users]


class Group(Model):
    """
    group collection to store telegram group details
    """

    def __init__(self):
        self.collection = db.tele_group
        self.fields = ["_id", "gid", "group_name", "members", "photo"]
        self.required_fields = ["gid", "group_name"]


class ServerInfo(Model):
    """
    server info collection to store server credentials and access user
    """

    def __init__(self):
        self.collection = db.serverinfo
        self.fields = ["_id", "server_ip", "server_name",
                       "server_username", "server_password", "users"]
        self.required_fields = ["server_ip", "server_name",
                                "server_username", "server_password", "users"]
