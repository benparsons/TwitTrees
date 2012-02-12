from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
import urllib2, twitter
import os
from google.appengine.ext.webapp import template
from django.utils import simplejson


class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = {}

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        
class Nain(webapp.RequestHandler):
    def get(self):
        #api = twitter.Api(cache=None)
        #authenticate with your own app data
        api = twitter.Api(consumer_key='', consumer_secret='', access_token_key='', access_token_secret='',cache=None)

        ll = api.GetFriendIDs(user=self.request.get('username'))
        self.response.headers['Content-Type'] = 'text/plain'
        
        #details = api.UsersLookup(user_id=ll['ids'])
        output =  JsonResponse()
        output.friends = ll['ids']
        #self.response.out.write('<hr />')
        #for u in details:
            #self.response.out.write(u.screen_name + ', ')
        #    userobj = TwitterUser(id = u.id, name = u.name, screen_name = u.screen_name)
        #    userobj.put()
            
        self.response.out.write(simplejson.dumps(output.__dict__))

application = webapp.WSGIApplication(
                                     [('/', MainPage), ('/nr', Nain)],
                                     debug=True)

class TwitterUser(db.Model):
    id = db.IntegerProperty()
    name = db.StringProperty()
    screen_name = db.StringProperty()
    location = db.StringProperty()
    description = db.StringProperty()
    profile_image_url = db.StringProperty()
    
class JsonResponse(object):
    userID = 0
    friends = []
    

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
