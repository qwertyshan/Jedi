#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import urllib2
import json
import datetime
import pprint
import cgi
import codecs
#from twilio import twiml
from models import Character, Message, Location
from google.appengine.ext import ndb

import os
import jinja2
jinja_env = jinja2.Environment(autoescape=True,loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


# mapping aliases to character names
aliases = {
    'chewbacca': 'Chewbacca',
    'wookie': 'Chewbacca',
    'chewy': 'Chewbacca',
    'chewie': 'Chewbacca',
    'r2d2': 'R2-D2',
    'droid': 'R2-D2',
    'r2': 'R2-D2',
    'r2-d2': 'R2-D2',
    'r2-d2': 'R2-D2',
    'yoda': 'Yoda',
    'master-yoda': 'Yoda',
    'leia': 'Princess Leia',
    'princess': 'Princess Leia',
    'princess leia': 'Princess Leia',
    'luke': 'Luke Skywalker',
    'skywalker': 'Luke Skywalker',
    'luke skywalker': 'Luke Skywalker',
    'han': 'Han Solo',
    'solo': 'Han Solo',
    'han solo': 'Han Solo',
    'c3p0': 'C-3PO',
    'c-3p0': 'C-3PO',
    'c3po': 'C-3PO',
    'c-3po': 'C-3PO',
    'obi-wan': 'Obi-Wan Kenobi',
    'kenobi': 'Obi-Wan Kenobi',
    'ben': 'Obi-Wan Kenobi',
    'obi': 'Obi-Wan Kenobi',
    'obi-wan kenobi': 'Obi-Wan Kenobi',
    'emperor': 'Emperor Palpatine',
    'palpatine': 'Emperor Palpatine',
    'sidious': 'Emperor Palpatine',
    'emperor palpatine': 'Emperor Palpatine',
    'vader': 'Darth Vader',
    'darth': 'Darth Vader',
    'darth vader': 'Darth Vader',
    'storm': 'Storm Trooper',
    'trooper': 'Storm Trooper',
    'stormtrooper': 'Storm Trooper',
    'storm trooper': 'Storm Trooper',
    'boba': 'Boba Fett',
    'fett': 'Boba Fett',
    'boba fett': 'Boba Fett'
}

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainHandler(Handler):
    def writeHTML(self, **kw):
        #debug
        for ch in Character.query().order(Character.name).fetch(50):
            print ch
        # Get messages
        messages = Message.query().order(-Message.createDate).fetch(20)
        # Get characters
        characters = Character.query().fetch(20)
        self.render('form.html', messages=messages, characters=characters, **kw)
        #self.response.write(form % {"error": error, "character": character, "address": address})

    # Initial page load
    def get(self):
        '''
        for a, c in aliases.items():
            print a, c
            q = Character.query(Character.name == c)
            r = q.get()
            print "RESULT: "
            print r
            if a not in r.alias:
                r.alias.append(a)
                r.put()
        '''
        character = Character(name="")
        location = Location()
        location.latlng=ndb.GeoPt(37.7749295, -122.4194155)
        # Write
        self.writeHTML(error="", character=character, location=location)

    # User form submission
    def post(self):
        messageid = self.request.get("messageid")
        if messageid == "":
            rawCharacter =  cgi.escape(self.request.get("character"), quote = True)
            rawLocation =   cgi.escape(self.request.get("address"), quote = True)
            # Validate character
            (character, charError) = validateCharacter(rawCharacter)
            # Validate location
            location = validateLocation(rawLocation)
            error, msgError = "", ""

            # Check validation errors and format error message
            if character == None:
                msgChar = rawCharacter
            else:
                msgChar = str(character.name)

            if charError != "":
                error = charError
                msgError = error
            if location.status != "OK":
                error = (error + " " + location.status.encode('utf_8')).decode('utf_8')
                msgError = error
            if (charError == "") and (location.status == "OK"):
                error = ("Move %s to %s. Got it!" % (msgChar, location.address.encode('utf_8'))).decode('utf_8')
                msgError = ""

            print datetime.datetime.utcnow()
            print "error: " + error.encode('utf_8')
            print type(error)
            print "msgError: " + msgError.encode('utf_8')
            print type(msgError)
            # Store in Message store
            if recordMessage("WebForm", None, self.request.remote_addr, msgChar, location, rawCharacter+" "+rawLocation, msgError):
                self.writeHTML(error=error, character=character, location=location)
                #self.redirect("/thanks")
            else:
                error = "App Error: Failed to insert message."
                self.writeHTML(error=error, character=character, location=location)

        else:
            # Validate messageid and get message
            messagekey = ndb.Key(urlsafe=messageid)
            message = Message()
            message = messagekey.get()
            character = Character().query(Character.name==message.character).get()
            location = Location()
            location.address = message.address
            location.latlng = message.latlng
            # Debug
            print message
            print character
            print location

            # If message found
            if not message:
                error = "App Error: Cannot get message."
                self.writeHTML(error=error, character=None, location=None)

            # If message not found
            else:
                # Write
                self.writeHTML(error="", character=character, location=location)


'''
class ThanksHandler(webapp2.RequestHandler):
    def get(self):
        error = self.request.get("error")
        self.response.write(error)
'''

'''
class SMSHandler(webapp2.RequestHandler):
    def post(self):

        messageSid = self.request.get("MessageSid")
        sourcePhone = self.request.get("From")
        rawMessage = self.request.get("Body")

        print ("Debug", messageSid, sourcePhone, rawMessage)

        rawCharacter = rawMesssage.partition(' ')[0]    #first word of message
        rawLocation = rawMesssage.partition(' ')[1]     #rest of the message (except first word)

        error = ""

        # Validate character
        character = validateCharacter(rawCharacter)
        if character == None:
            error = "Invalid character. [Character: %s]" % rawCharacter
            responseMsg = error

        # Validate location
        location = validateLocation(rawLocation)
        if location.error != "OK":
            error += "Invalid location. [Error: %s] [Location: %s]" % (str(location.error), rawLocation)
            responseMsg = error

        # If both character and location are validated
        if error == "":
            responseMsg = "Move %s to %s. Got it!" % (character, location)

        # Store SMS in Message store
        recordMessage("SMS", sourcePhone, None, character,  location, (("messageSid: %s" % messageSid) + rawMessage), error)

        if recordMessage != True:
            print ("Unable to record message.") # for debugging

        response = twilio.twiml.Response()
        response.message(responseMsg)

        return str(response)
'''



def validateCharacter(rawCharacter):
    # debug: print Character table
    for ch in Character.query().fetch(10):
        print ch

    # Validate character
    formattedChar = rawCharacter.lower()
    character = aliases.get(formattedChar)
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

#def processInput(character, address):

def recordMessage(sourceType, sourcePhone, sourceIP, character, location, rawMessage, errorstr):
    message = Message()

    message.sourceType =    sourceType
    message.sourcePhone =   sourcePhone
    message.sourceIP =      sourceIP
    message.character =     character
    message.address =       location.address
    message.latlng =        location.latlng
    message.rawMessage =    rawMessage
    message.error =         errorstr

    message.put()
    return True

def geocode(rawLocation):
    """

    :rtype : Location
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s" % rawLocation.replace(" ","+")

    response = urllib2.urlopen(url)
    #jsongeocode = response.read()
    geocode = json.load(response)
    pprint.pprint(geocode)

    location = Location()
    location.status = geocode["status"].encode('utf_8').decode('utf_8')
    if location.status == "OK":
        location.address = geocode["results"][0]["formatted_address"].encode('utf_8').decode('utf_8')
        location.latlng = ndb.GeoPt(geocode["results"][0]["geometry"]["location"]["lat"], geocode["results"][0]["geometry"]["location"]["lng"])
    else:
        location.address = None
        location.latlng = None

    print "in geocode"
    print location.status.encode('utf_8')
    print type(location.status)
    print location.address.encode('utf_8')
    print type(location.address)
    #print location.address.decode('utf_8')
    #print location.address
    return location

class LoadDB(webapp2.RequestHandler):
    def get(self):
        # Loading character DB
        charlist = [
            ['Boba Fett', 'Boba-Fett-icon.png'],
            ['C-3PO', 'C3PO-icon.png'],
            ['Chewbacca', 'Chewbacca-icon.png'],
            ['Darth Vader', 'Darth-Vader-icon.png'],
            ['Emperor Palpatine', 'Emperor-icon.png'],
            ['Han Solo', 'Han-Solo-icon.png'],
            ['Princess Leia', 'Leia-icon.png'],
            ['Luke Skywalker', 'Luke-Skywalker-icon.png'],
            ['Obi-Wan Kenobi', 'Obi-Wan-icon.png'],
            ['R2-D2', 'R2D2-icon.png'],
            ['Storm Trooper', 'Stormtrooper-icon.png'],
            ['Yoda', 'Yoda-icon.png']
        ]
        char = Character()
        for x in charlist:
            print x[0]
            print x[1]
            char = Character.get_or_insert(str(x[0]), name=str(x[0]), avatarFile=str(x[1]))
            print char
            char.put()

        for ch in Character.query().order(Character.name).fetch(50):
            print ch
        self.response.write('Loaded DB')

app = webapp2.WSGIApplication([
    ('/', MainHandler), ('/submitForm', MainHandler), ('/load', LoadDB)
], debug=True)
