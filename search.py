import gevent.monkey
gevent.monkey.patch_all()
import gevent.pool
pool = gevent.pool.Pool(40)

import soundcloud
from time import time, strptime, mktime,clock
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': 'cache/data',
    'cache.lock_dir': 'cache/lock'
}

#Cache stores search results for 24 hours
cm = CacheManager(**parse_cache_config_options(cache_opts))
cache = cm.get_cache('trackcache', type='dbm', expire=3600*24)


client = soundcloud.Client(client_id='af912f440f0d027065e7351089b08a52')

def getPlaysPer(track):
	created_time = strptime(track.created_at[:-6],"%Y/%m/%d %H:%M:%S")
	plays_per = track.playback_count / ((time() - mktime(created_time)) / (3600*24))
	return plays_per

def getHype(track):
	if(track.playback_count > 500):
		hyperatio = float(track.favoritings_count) / float(track.playback_count)
		playsper = getPlaysPer(track)
		hype = (track.playback_count*playsper)**(hyperatio)
		return hype
	return 0

def makeWidget(trackid):
	return "<iframe width=\"100%\" height=\"166\" scrolling=\"no\" frameborder=\"no\" src=\"//w.soundcloud.com/player/?url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F"+str(trackid)+"\"></iframe>"

class Searcher:
	def __init__(self,querystr,sorttype):
		self.querystr = querystr
		self.type = sorttype
		self.results = []

	def generateWidgets(self,tracks):
		widgets = []
		for track in tracks:
			widget = "<iframe width=\"100%\" height=\"166\" scrolling=\"no\" frameborder=\"no\" src=\"//w.soundcloud.com/player/?url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F"+str(track.id)+ "\"></iframe>"
			widgets += ["%s</br>" % (widget)]
		return widgets
			
	def search(self):
		start = clock()
		tracks = cache.get(key=self.querystr+":::"+self.type,createfunc=self.dosearch)
		print "Total time: %f" % (clock()-start)
		return tracks


	def dosearch(self):
		for offset in [i*200 for i in range(40)]:
			pool.spawn(self.getTracks,self.querystr,offset)
		pool.join()
		result = sorted(self.results, key=lambda x:x.tosort, reverse=True)[:20]
		for t in result:
			t.widget = makeWidget(t.id)
			print "(%s) %s - %s"%(t.tosort,t.username.encode('ascii', 'ignore'),t.title.encode('ascii', 'ignore'))
		return result

	def getTracks(self,query,offset):
		exactString = False
		if(query.startswith(r'"') and query.endswith(r'"')):
			#strip quotes
			query = query[1:-1]
			exactString = True
		taglist = []
		tracks = client.get('/tracks', q=query, tags=taglist,limit=200,offset=offset,duration={'to':480000})
		for track in tracks:
			try:
				if(exactString):
					info = "%s %s %s" % (track.user["username"],track.title,track.description)
					if(query.lower() not in info.lower()):
						continue
				hype = getHype(track)
				result = SearchResult(track,hype,getPlaysPer(track),self.type)
				self.results.append(result)
			except AttributeError as ae:
				continue
			except Exception as exp:
				print exp
				continue


# searcher = Searcher("twerk",'hype')
# searcher.dosearch()
class SearchResult():
	def __init__(self,track,hype,playsper,sorttype):
		self.id = track.id
		self.username = track.user["username"]
		self.title = track.title
		self.plays = track.playback_count
		self.favorites = track.favoritings_count
		self.date = track.created_at
		self.hype = hype
		self.playsper = playsper
		self.widget = ""
		if(sorttype == "plays"):
			self.tosort = track.playback_count
		if(sorttype == "favorites"):
			self.tosort = track.favoritings_count
		if(sorttype == "hype"):
			self.tosort = hype
		if(sorttype == "playsper"):
			self.tostor = playsper
