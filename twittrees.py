from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
import urllib2, twitter
import os
from google.appengine.ext.webapp import template
from django.utils import simplejson
import datetime
from google.appengine.api import taskqueue
import logging



class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = {}

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        
class Nain(webapp.RequestHandler):
    def get(self):
        #api = twitter.Api(cache=None)
        #authenticate with your own app data
        logging.info("test")
        self.response.headers['Content-Type'] = 'text/plain'
        
        startpoint = TwitterUser(key_name = self.request.get('username'),screen_name = self.request.get('username'))
        firstid = str(self.request.get('username'))
        
        ll = []
        
        query = db.Query(TwitterUser)
        query.filter("screen_name", firstid)
        res = query.get()
        if res is None:
            ll.append(firstid)
            details = api.UsersLookup(screen_name=ll)
            startpoint = TwitterUser(key_name=details[0].screen_name, twitter_id = details[0].id, name = details[0].name, details_updated = datetime.datetime.now(), screen_name = details[0].screen_name)
            startpoint.put()
            logging.info("condition 1")
        
        
        output =  JsonResponse()
        
        ll = api.GetFriendIDs(user=self.request.get('username'))
        details = api.UsersLookup(user_id=ll['ids'][:100])
        output.friends = ll['ids']
        for u in details:
            query = db.Query(TwitterUser)
            query.filter("twitter_id", u.id)
            res = query.get()
            if res is None:
                userobj = TwitterUser(key_name = u.screen_name,twitter_id = u.id, name = u.name, screen_name = u.screen_name, details_updated = datetime.datetime.now())
                userobj.put()
                startpoint.friends.append(userobj.key())
                taskqueue.add(url='/getUser', params={'id': u.id}, method='GET')
                startpoint.friends_updated = datetime.datetime.now()
                startpoint.put()
        
        
            
        self.response.out.write(simplejson.dumps(output.__dict__))
        



class GetUserTask(webapp.RequestHandler):
    def get(self):
        api = twitter.Api(consumer_key='vJfpUnZtusTG8hcNWE0yQ', consumer_secret='oB21rUYaxvY5ltYXsGH80b9rRNkopMJFfBre0k5yXo', access_token_key='8229292-GFJiRDAVqI0skPtrqz1lRJQHdx6tOBTLsYx1f1dwbQ', access_token_secret='95XSs3FsNLtV8FFIDz3iwVxPffKpx6aDp2vskWLqY',cache=None)
        firstid = str(self.request.get('id'))
        ll = []
        ll.append(firstid)
        query = db.Query(TwitterUser)
        query.filter("twitter_id", firstid)
        res = query.get()
        userobj = TwitterUser()
        self.response.out.write(res)
        
        if res is None:
            details = api.UsersLookup(user_id=ll)
            userobj = TwitterUser(key_name = details[0].screen_name,twitter_id = details[0].id, name = details[0].name, screen_name = details[0].screen_name, details_updated = datetime.datetime.now())
            userobj.put()
            
        if res is not None:
            userobj = res
            
        friendslist = api.GetFriendIDs(user=userobj.screen_name)
        followerslist = api.GetFollowerIDs(userid=userobj.twitter_id)
        
        friendsdetails = api.UsersLookup(user_id=friendslist['ids'][:5])
        followersdetails = api.UsersLookup(user_id=followerslist['ids'][:5])

        
                
        for u in friendsdetails:
            query = db.Query(TwitterUser)
            query.filter("screen_name", u.screen_name)
            res = query.get()
            if res is None:
                v = TwitterUser(key_name = u.screen_name,twitter_id = u.id, name = u.name + " line 102", screen_name = u.screen_name, details_updated = datetime.datetime.now())
                v.put()
            else:
                v = res
            userobj.friends.append(v.key())
            #taskqueue.add(url='/getUser', params={'id': v.twitter_id}, method='GET')
        
        for u in followersdetails:
            query.filter("screen_name", u.screen_name)
            res = query.get()
            if res is None:
                v = TwitterUser(key_name = u.screen_name,twitter_id = u.id, name = u.name + " line 113", screen_name = u.screen_name, details_updated = datetime.datetime.now())
                v.put()
            else:
                v = res
            userobj.followers.append(v.key())
            #taskqueue.add(url='/getUser', params={'id': v.twitter_id}, method='GET')
        
        userobj.put()
        
class GetConnections(webapp.RequestHandler):
    def get(self):
        output =  JsonResponse()
        query = db.Query(TwitterUser)
        query.filter("twitter_id", self.request.get('id'))
        res = query.get()
        if res is None:
            self.response.out.write("here")
            return
        
        self.response.out.write(res)
        output.userID = self.request.get('id')
        output.userDetails = res
        self.response.out.write(simplejson.dumps(output.__dict__))
        
class QuickBrowser(webapp.RequestHandler):
    def get(self):
        self.response.out.write("<table>")
        query = db.Query(TwitterUser)
        query.filter("screen_name", self.request.get('username'))
        results = query.run()
        for r in results:
            self.response.out.write("<tr>")
            self.response.out.write("<td>" + r.name + "</td>")
            self.response.out.write("<td>" + r.screen_name + "</td>")
            self.response.out.write("<td>" + str(r.twitter_id) + "</td>")
            self.response.out.write("")
            self.response.out.write("")
            self.response.out.write("")
            self.response.out.write("</tr>")

        
        self.response.out.write("</table>")

        

application = webapp.WSGIApplication(
                                     [('/', MainPage), ('/nr', Nain), ('/getUser', GetUserTask), ('/getConnections', GetConnections)
                                     , ('/browse', QuickBrowser)],
                                     debug=True)                                  

class TwitterUser(db.Model):
    twitter_id = db.IntegerProperty()
    name = db.StringProperty()
    screen_name = db.StringProperty()
    location = db.StringProperty()
    description = db.StringProperty()
    profile_image_url = db.StringProperty()
    friends = db.ListProperty(db.Key)
    followers = db.ListProperty(db.Key)
    details_updated = db.DateTimeProperty()
    friends_updated = db.DateTimeProperty()
    followers_updated = db.DateTimeProperty()
    
class JsonResponse(object):
    userID = 0
    userDetails = TwitterUser()
    friends = []
    followers = []
    

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
