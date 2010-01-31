#!/usr/bin/env python
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

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from django.utils import simplejson as json

from google.appengine.api import users, memcache, mail
from google.appengine.ext import db
from google.appengine.ext.webapp import template


import os
import re
import logging
import random
from google.appengine.ext import db

DURATION = 2

class Spiff(db.Model):
  body = db.TextProperty()
  create_date = db.DateTimeProperty(auto_now_add=True)
  

class HandlerBase(webapp.RequestHandler):
  """Base request handler extends webapp.Request handler

     It defines the render method, which renders a Django template
     in response to a web request
  """
  def render_and_store(self, template_name, template_values={}):
    """Renders an HTML template along with values
       passed to that template

       Args:
         template_name: A string that represents the name of the HTML template
         template_values: A dictionary that associates objects with a string
           assigned to that object to call in the HTML template.  The defualt
           is an empty dictionary.
    """
    # Construct the path to the template
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 'templates', template_name)

    # Respond to the request by rendering the template
    page = template.render(path, template_values, debug=False)
    spiff = Spiff(body=page)
    spiff.put()
    return spiff
  
  def render(self, template_name, template_values={}):
    """Renders an HTML template along with values
       passed to that template

       Args:
         template_name: A string that represents the name of the HTML template
         template_values: A dictionary that associates objects with a string
           assigned to that object to call in the HTML template.  The defualt
           is an empty dictionary.
    """
    # We check if there is a current user and generate a login or logout URL
    user = users.get_current_user()

    if user:
      log_in_out_url = users.create_logout_url('/')
    else:
      log_in_out_url = users.create_login_url(self.request.path) 
    
    # Some default template values
    default_values = {
      'current_path':self.request.path, # gives /a/282
      'current_url':self.request.url, # gives http://localhost:8080/a/282
      'host_url':self.request.host_url, # gives http://localhost:8080
      'user_email':(user.email() if user else None),
      'log_in_out_url':log_in_out_url
    }
    template_values.update(default_values)
    if users.is_current_user_admin():
      template_values.update({
        'user_is_admin':True
      })
    
    # Construct the path to the template
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 'templates', template_name)

    # Respond to the request by rendering the template
    page = template.render(path, template_values, debug=False)
    self.response.out.write(page)

class MainHandler(HandlerBase):

  def get(self):
    self.render('home.html', {})
    
class SupaMixHandler(HandlerBase):
  
  def post(self):
    song_urls = []
    lady_data = self.request.body
    logging.info(self.request.body)
    chunks = json.loads(lady_data)
    for chunk in chunks:
      # parse chunk to get parameters
      q = chunk['query']
      a = chunk['artist']
      t = chunk['title']
      d = int(chunk['duration'])
      
      # possible cases: query and duration, artist, title, artist and title, artist and duration
    
      # put parameters in url unless they are blank strings
      url = "http://developer.echonest.com/api/alpha_search_tracks?api_key=XRHWHUFCMWU7VLSYI&query='%s'&artist='%s'&title='%s'&heather=true" % (q, a, t)
      # fetch the url to get back json string of results
      jstr = urlfetch.fetch(url)
      # turn json string into python dictionary of song urls => dict_job
      dict_job = json.loads(jstr.content)['results']
      # logging.info(str(dict_job))
      # do a randomization of which songs to pick and how many based on the duration parameter
      if d:
        # the smallest d can be is DURATION
        num_songs = d / DURATION
      for i in range(1):
        index = random.randint(0,len(dict_job)-1)
        song_urls.append(dict_job[index]['url'])
      
    # outside the for loop create spiff file from song_urls array
    spiff = self.render_and_store('spiff.xml', {'urls':song_urls})
    spiff_url = 'http://' + self.request.host + '/spiff/' + str(spiff.key().id()) + '.xspf'
    son = urlfetch.fetch('http://developer.echonest.com/api/alpha_capsule?api_key=XRHWHUFCMWU7VLSYI&xspf_url=' + spiff_url)
    logging.info('http://developer.echonest.com/api/alpha_capsule?api_key=XRHWHUFCMWU7VLSYI&xspf_url=' + spiff_url)
    self.response.out.write(son.content)
    
class SpiffHandler(webapp.RequestHandler):
  def get(self, spiff_id):
    self.response.out.write(Spiff.get_by_id(int(spiff_id)).body)
    
class StatusCodeHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write(json.dumps({'status':urlfetch.fetch(self.request.get('url')).status_code}))

def main():
  application = webapp.WSGIApplication([
    ('/', MainHandler),
    ('/supa_mix', SupaMixHandler),
    ('/spiff/([0-9]+)\.xspf', SpiffHandler),
    ('/check_status_code', StatusCodeHandler)
  ],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
