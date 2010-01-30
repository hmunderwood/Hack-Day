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

class HandlerBase(webapp.RequestHandler):
  """Base request handler extends webapp.Request handler

     It defines the render method, which renders a Django template
     in response to a web request
  """
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
    # cookies = cookies_helper.Cookies(self)
    # try:
    #   visited = cookies['visited']
    #   if visited != 'veteran':
    #     template_values['visitor_is_new'] = True
    #     if visited == 'once':
    #       cookies['visited'] = 'twice'
    #     if visited == 'twice':
    #       cookies['visited'] = 'veteran'
    # except:
    #   template_values['visitor_is_new'] = True
    #   cookies['visited'] = 'once'
    
    # Construct the path to the template
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 'templates', template_name)

    # Respond to the request by rendering the template
    page = template.render(path, template_values, debug=False)
    self.response.out.write(page)

class MainHandler(HandlerBase):

  def get(self):
    urls = []
    url = "http://developer.echonest.com/api/alpha_search_tracks?api_key=XRHWHUFCMWU7VLSYI&query=\"funk\"&results=3&heather=true"
    jstr = urlfetch.fetch(url)
    pydict = json.loads(jstr.content)
    for song in pydict['results']:
      urls.append(song['url'])
    self.render('spiff.xml', {'urls':urls})
    # self.response.out.write(str(pydict))

def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
