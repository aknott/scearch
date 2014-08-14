import soundcloud
from time import sleep, time, strptime, mktime,clock
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

import gevent.monkey
gevent.monkey.patch_all()
import gevent.pool
pool = gevent.pool.Pool(40)


cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': 'cache/data',
    'cache.lock_dir': 'cache/lock'
}

#Cache stores search results for 24 hours
cm = CacheManager(**parse_cache_config_options(cache_opts))
cache = cm.get_cache('trackcache', type='dbm', expire=3600*24)


client = soundcloud.Client(client_id='af912f440f0d027065e7351089b08a52')

results = []

def __init__(self):
	print "created searcher"

def generateWidgets(tracks):
	output = ""
	for trackid in tracks:
		widget = "<iframe width=\"100%\" height=\"166\" scrolling=\"no\" frameborder=\"no\" src=\"//w.soundcloud.com/player/?url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F"+str(trackid)+ "\"></iframe>"
		output += "%s</br>" % (widget)
	return output
		
def dosearch(query,type):
	global searchstr
	global sorttype
	searchstr = query
	sorttype = type
	tracks = cache.get(key=searchstr+":::"+sorttype,createfunc=search)
	return generateWidgets(tracks)


def searchg(query):
	start = clock()
	for offset in [i*200 for i in range(40)]:
		pool.spawn(getTracks,query,offset)
	pool.join()
	result = sorted(results, key=lambda x:x[1], reverse=True)[:10]
	print result
	print "Total time: %f" % (clock()-start)

attrerrors = 0

def getTracks(query,offset):
	global attrerrors
	taglist = []
	tracks = client.get('/tracks', q=query, tags=taglist,limit=200,offset=offset,duration={'to':480000})
	for track in tracks:
		try:
			tup = track.id,track.playback_count,track.title
			results.append(tup)
		except AttributeError as ae:
			#Some users choose to not display playback_count or other info, so just skip these tracks
			attrerrors += 1
			continue
		except Exception as exp:
			print 'lastexp'
			print exp
			continue


searchg("twerk")