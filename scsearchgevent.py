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

sortCriterias = {u"plays":3,u"favorites":4,u"hype":6,u"playsper":7}

def getPlaysPer(track):
	created_time = strptime(track.created_at[:-6],"%Y/%m/%d %H:%M:%S")
	plays_per = track.playback_count / ((time() - mktime(created_time)) / (3600*24))
	return plays_per

def getHype(track):
	if(track.playback_count > 500):
		hyperatio = float(track.favoritings_count) / float(track.playback_count)
		playsper = getPlaysPer(track)
		hype = (track.playback_count*playsper)**(hyperatio)
		#hype = plays_per**(hyperatio)
		return hype
	return 0

class Searcher:
	def __init__(self,querystr,sorttype):
		self.querystr = querystr
		self.type = sorttype
		self.results = []

	def generateWidgets(self,tracks):
		widgets = []
		for track in tracks:
			widget = "<iframe width=\"100%\" height=\"166\" scrolling=\"no\" frameborder=\"no\" src=\"//w.soundcloud.com/player/?url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F"+str(track[0])+ "\"></iframe>"
			widgets += ["%s</br>" % (widget)]
		return widgets
			
	def search(self):
		start = clock()
		tracks = cache.get(key=self.querystr+":::"+self.type,createfunc=self.dosearch)
		print "Total time: %f" % (clock()-start)
		return self.generateWidgets(tracks)


	def dosearch(self):
		for offset in [i*200 for i in range(40)]:
			pool.spawn(self.getTracks,self.querystr,offset)
		pool.join()
		sortcolumn = sortCriterias[self.type]
		result = sorted(self.results, key=lambda x:x[sortcolumn], reverse=True)[:10]
		for t in result:
			print "(%s) %s - %s"%(t[sortcolumn],t[1].encode('ascii', 'ignore'),t[2].encode('ascii', 'ignore'))
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
				tup = track.id,track.user["username"],track.title,track.playback_count,track.favoritings_count,track.created_at,hype,getPlaysPer(track)
				self.results.append(tup)
			except AttributeError as ae:
				continue
			except Exception as exp:
				print exp
				continue


# searcher = Searcher("twerk",'hype')
# searcher.dosearch()