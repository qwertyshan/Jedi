import httplib
from google.appengine.ext import ndb

class Character(ndb.Model):
    """Character -- Character Object"""
    name =          ndb.StringProperty(required=True)
    avatarFile =    ndb.StringProperty()
#    alias =         ndb.StringProperty()

class Message(ndb.Model):
    """Message -- Message in message log"""
    sourceType =    ndb.StringProperty(required=True)
    sourcePhone =   ndb.StringProperty()
    sourceIP =      ndb.StringProperty()
    createDate =    ndb.DateTimeProperty(auto_now_add=True)
    character =     ndb.StringProperty()
    address =       ndb.StringProperty()
    latlng =        ndb.GeoPtProperty()
    rawMessage =    ndb.StringProperty()
    error =         ndb.StringProperty()

class Location():
    """Location -- Location address and latitude-longitude"""
    address =      ndb.StringProperty()
    latlng =       ndb.GeoPtProperty()
    status =       ndb.StringProperty()
