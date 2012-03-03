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
        
        startpoint = TwitterUser.get_or_insert(key_name = self.request.get('username'),screen_name = self.request.get('username'))
        ll = []
        if not startpoint.name:
            ll.append(str(startpoint.screen_name))
            logging.info(ll)
            details = api.UsersLookup(screen_name=ll)
            startpoint.twitter_id = details[0].id
            startpoint.name = details[0].name
            startpoint.details_updated = datetime.datetime.now()
            startpoint.put()
            logging.info("condition 1")
        
        
        output =  JsonResponse()
        
        ll = api.GetFriendIDs(user=self.request.get('username'))
        details = api.UsersLookup(user_id=ll['ids'][:100])
        output.twitter_id = startpoint.twitter_id
        output.friends = ll['ids']
        for u in details:
            userobj = TwitterUser.get_or_insert(key_name = u.screen_name,twitter_id = u.id, name = u.name, screen_name = u.screen_name, details_updated = datetime.datetime.now())
            userobj.put()
            startpoint.friends.append(userobj.key())
            #taskqueue.add(url='/getUser', params={'username': u.screen_name}, method='GET')
            startpoint.friends_updated = datetime.datetime.now()
        
        startpoint.put()
        
        
            
        self.response.out.write(simplejson.dumps(output.__dict__))
        



class GetUserTask(webapp.RequestHandler):
    def get(self):
        firstid = str(self.request.get('username'))
        ll = []
        ll.append(firstid)
        userobj = TwitterUser.get_or_insert(key_name = self.request.get('username'))
        
        details = api.UsersLookup(screen_name=ll)
        userobj.twitter_id = details[0].id
        userobj.name = details[0].name
        userobj.screen_name = self.request.get('username')
        userobj.details_updated = datetime.datetime.now()
        userobj.put()
            
        friendslist = api.GetFriendIDs(user=userobj.screen_name)
        followerslist = api.GetFollowerIDs(userid=userobj.twitter_id)
        
        friendsdetails = api.UsersLookup(user_id=friendslist['ids'][:5])
        followersdetails = api.UsersLookup(user_id=followerslist['ids'][:5])

        
                
        for u in friendsdetails:
            v = TwitterUser.get_or_insert(u.screen_name)
            v.twitter_id = u.id
            v.name = u.name
            v.screen_name = u.screen_name
            v.details_updated = datetime.datetime.now()
            v.put()
            userobj.friends.append(v.key())
            #taskqueue.add(url='/getUser', params={'username': v.screen_name}, method='GET')
        
        for u in followersdetails:
            v = TwitterUser.get_or_insert(u.screen_name)
            v.twitter_id = u.id
            v.name = u.name
            v.screen_name = u.screen_name
            v.details_updated = datetime.datetime.now()
            v.put()
            userobj.followers.append(v.key())
            #taskqueue.add(url='/getUser', params={'id': v.screen_name}, method='GET')
        
        userobj.put()
        
class GetConnections(webapp.RequestHandler):
    def get(self):
        output =  JsonResponse()
        query = db.Query(TwitterUser)
        query.filter("twitter_id", long(self.request.get('id')))
        res = query.get()
        if res is None:
            output.response = "1"
        else:
            output.response = "0"
            output.userID = self.request.get('id')
            output.screen_name = res.screen_name
            friends = []
            for user in res.friends:
                friendsquery = db.Query(TwitterUser)
                friendsquery.filter("__key__", user)
                friendres = friendsquery.get()
                friends.append(friendres.twitter_id)
            output.friends = friends
            
            followers = []
            for user in res.followers:
                followersquery = db.Query(TwitterUser)
                followersquery.filter("__key__", user)
                friendres = followersquery.get()
                followers.append(friendres.twitter_id)
            output.followers = followers
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
