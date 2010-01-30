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


class MainHandler(webapp.RequestHandler):

  def get(self):
    url = "http://developer.echonest.com/api/alpha_search_tracks?api_key=XRHWHUFCMWU7VLSYI&query=\"romantic\"&heather=true"
    jstr = urlfetch.fetch(url)
    pydict = json.loads(jstr.content)
    for song in pydict['results']:
      self.response.out.write(song['url']+'<br/>')
    # self.response.out.write(str(pydict))

def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
