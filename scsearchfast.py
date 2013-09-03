import soundcloud
import operator
import ThreadPool
from time import sleep, time, strptime, mktime
from threading import Thread, Lock
from Queue import Queue
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
q = Queue()

tp = ThreadPool.ThreadPool(20,20)
lockobj = Lock()

favdict = {}
ResultsLeft = 8000

searchstr = "foo"
sorttype = ""

def __init__(self):
	print "created searcher"

def generateWidgets(tracks):
	output = ""
	for trackid in tracks:
		widget = "<iframe width=\"100%\" height=\"166\" scrolling=\"no\" frameborder=\"no\" src=\"http://w.soundcloud.com/player/?url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F"+str(trackid)+ "\"></iframe>"
		output += "%s</br>" % (widget)
	return output
		
def dosearch(query,type):
	global searchstr
	global sorttype
	searchstr = query
	sorttype = type
	tracks = cache.get(key=searchstr+":::"+sorttype,createfunc=search)
	return generateWidgets(tracks)

	
def search():
	global ResultsLeft
	offsetval = 0
	ResultsLeft = 8000
	
	favdict.clear()
	
	t = Thread(target=worker)
	t.daemon = True
	t.start()
	
	while(offsetval < 8000):
		tp.add_job(GetTracks,[searchstr,offsetval,sorttype])
		offsetval += 200
	
	starttime = time()
	#kill if shit takes longer than 20 seconds
	while ((ResultsLeft>0) and (time()-starttime < 20.0)):
		print "%s" % (ResultsLeft)
		sleep(1)
	print time()-starttime 
	print "facdict is " + str(len(favdict.keys())) + " long"

	sorted_x = sorted(favdict.iteritems(), key=operator.itemgetter(1))
	sorted_x.reverse()

	toptracks = [x[0] for x in sorted_x[0:21]]
	
	return toptracks

def worker():
	while True:
		try:
			item = q.get()
			favdict[item[0]] = item[1]
			q.task_done()
		except Exception as exp:
			print exp
			continue


def GetTracks(searchstr,offsetnum,sorttype):
	global ResultsLeft
	exactString = False
	taglist = []
	retries = 0
	if(searchstr.startswith(r'"') and searchstr.endswith(r'"')):
		#strip quotes
		searchstr = searchstr[1:-1]
		exactString = True
	while(retries < 3):
		try:
			tracks = client.get('/tracks', q=searchstr, tags=taglist,limit=200,offset=offsetnum,duration={'to':480000})
			if(len(tracks) < 1): 
				lockobj.acquire()
				ResultsLeft -= 200
				lockobj.release()
				return
			for track in tracks:
				try:
					trackid = track.id
					sort_criteria = 0
					if(exactString):
						info = "%s %s %s" % (track.user["username"],track.title,track.description)
						if(searchstr.lower() not in info.lower()):
							continue
					if(sorttype == u'plays'):
						sort_criteria = track.playback_count
					elif(sorttype == u'favorites'):
						sort_criteria = track.favoritings_count
					elif(sorttype == u'hype'):
						#only calculate hype on tracks with more than 500 plays 
						#due to ratio values going too high with low playback
						if(track.playback_count > 500):
							created_time = strptime(track.created_at[:-6],"%Y/%m/%d %H:%M:%S")
							plays_per = track.playback_count / ((time() - mktime(created_time)) / (3600*24))
							hyperatio = float(track.favoritings_count) / float(track.playback_count)
							#hype = track.playback_count**(hyperatio)
							hype = plays_per**(hyperatio)
							sort_criteria = hype
							q.put((trackid,sort_criteria))
							continue
					elif(sorttype == u'playsper'):
						created_time = strptime(track.created_at[:-6],"%Y/%m/%d %H:%M:%S")
						sort_criteria = track.playback_count / ((time() - mktime(created_time)) / 3600)
					else:
						sort_criteria = track.playback_count
					q.put((trackid,sort_criteria))
				except AttributeError as ae:
					#Some users choose to not display playback_count or other info, so just skip these tracks
					continue
				except Exception as exp:
					print exp
					continue
			lockobj.acquire()
			ResultsLeft -= 200
			lockobj.release()
			return
		except Exception, excep:
			retries += 1
			print "error getting tracks %i! %s, retry count=%i" % (offsetnum,str(excep),retries)
	lockobj.acquire()
	ResultsLeft -= 200
	lockobj.release()

class SearchResult:
	def __init__(self,trackid=0,tracktitle="",value=0):
		trackid = trackid
		title = tracktitle
		value = value
