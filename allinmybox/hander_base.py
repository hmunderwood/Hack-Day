from google.appengine.api import users, memcache, mail
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from django.utils import simplejson as json
from helpers import cookies_helper
import os
import models
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
    if PAGE_CACHE_TIME: # and not user #only cache it if there is no user logged in (to avoid caching the log out and stuff)
      memcache.add(key=self.request.path+self.request.query_string+('__admin' if users.is_current_user_admin() else ''), value=page, time=PAGE_CACHE_TIME) 