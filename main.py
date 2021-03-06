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
import logging
#from twilio import twiml

from google.appengine.api import memcache
from google.appengine.ext import ndb

import map
import aliases
from models import Character, Message, Location

import os
import jinja2
jinja_env = jinja2.Environment(
                    autoescape=True,
                    loader=jinja2.FileSystemLoader(
                            os.path.join(os.path.dirname(__file__), 'templates')
                            )
                    )

def cache(key, update = False):
    msgs = memcache.get(key)
    if msgs is None or update:
        print "DB CACHE QUERY %s" % key
        if key is 'top_msgs':
            msgs = Message.query().order(-Message.createDate).fetch(20)
        elif key is 'get_chars':
            msgs = Character.all()
        msgs = list(msgs)
        memcache.set(key, msgs)
    return msgs

def top_msgs(update = False):
    key = 'top_msgs'
    msgs = cache(key, update)
    print msgs
    return msgs

def get_chars(update = False):
    key = 'get_chars'
    msgs = cache(key, update)
    print msgs
    return msgs

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
        # Get messages
        messages = top_msgs()
        # Get characters
        characters = get_chars()
        self.render('form.html', messages=messages, characters=characters, **kw)

    # Initial page load
    def get(self):
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
            (character, charError) = map.validateCharacter(rawCharacter)
            # Validate location
            location = map.validateLocation(rawLocation)
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
                print "IN APP:"
                top_msgs(True)
                self.writeHTML(error=error, character=character, location=location)
            else:
                error = "App Error: Failed to insert message."
                self.writeHTML(error=error, character=character, location=location)

        else:
            # Validate messageid and get message
            messagekey = ndb.Key(urlsafe=messageid)
            message = Message()
            message = messagekey.get()
            character = Character.query(Character.name == message.character).get()
            location = Location()
            location.address = message.address
            location.latlng = message.latlng

            # If message found
            if not message:
                error = "App Error: Cannot get message."
                self.writeHTML(error=error, character=None, location=None)

            # If message not found
            else:
                # Write
                self.writeHTML(error="", character=character, location=location)


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

    if message.put():
        return True
    else:
        return False

class LoadDB(webapp2.RequestHandler):
    def get(self):
        # Loading character DB
        char = Character()
        for x in aliases.charlist:
            print x[0]
            print x[1]
            char = Character.get_or_insert(str(x[0]), name=str(x[0]), avatarFile=str(x[1]))
            print char
            char.put()

        for ch in Character.query().order(Character.name).fetch():
            print ch

        get_chars(True)
        self.response.write('Loaded DB')

app = webapp2.WSGIApplication([
    ('/', MainHandler), ('/submitForm', MainHandler), ('/load', LoadDB)
], debug=True)
