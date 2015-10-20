import aliases
from models import Character, Message, Location
import urllib2
import json
import datetime
import pprint
import cgi
import codecs
from google.appengine.ext import ndb

def validateCharacter(rawCharacter):
    # debug: print Character table
    for ch in Character.query().fetch(10):
        print ch

    # Validate character
    formattedChar = rawCharacter.lower()
    character = aliases.aliases.get(formattedChar)
    print rawCharacter
    print formattedChar
    print "Character: %s" % character
    character = Character.query(Character.name == character).get()
    print character
    if character != None:
        error = ""
        print ('character found')
        print character
    else:
        error = "Invalid character [%s]" % rawCharacter

    print "error0: "+error
    return (character, error)

def validateLocation(rawLocation):
    # Validate location
    location = geocode(rawLocation)
    if location.status != "OK":
        location.status = "Invalid location [%s] [Error: %s]" % (rawLocation, str(location.status))
    return location

def geocode(rawLocation):
    """

    :rtype : Location
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s" % rawLocation.replace(" ","+")

    response = urllib2.urlopen(url)
    geocode = json.load(response)
    #debug
    pprint.pprint(geocode)

    location = Location()
    location.status = geocode["status"].encode('utf_8').decode('utf_8')
    if location.status == "OK":
        location.address = geocode["results"][0]["formatted_address"].encode('utf_8').decode('utf_8')
        location.latlng = ndb.GeoPt(geocode["results"][0]["geometry"]["location"]["lat"], geocode["results"][0]["geometry"]["location"]["lng"])
    else:
        location.address = None
        location.latlng = None

    # Debugs
    print "in geocode"
    print (location.status.encode('utf_8') if location.status else None)
    print type(location.status)
    print (location.address.encode('utf_8') if location.address else None)
    print type(location.address)

    return location
