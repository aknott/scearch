import soundcloud
import operator
import ThreadPool
from time import sleep, time
from threading import Thread
from Queue import Queue

ResultsLeft = 8000
q = Queue()
favdict = {}

client = soundcloud.Client(client_id='af912f440f0d027065e7351089b08a52')

def dosearch(searchstr):
	output = ""
	
	offsetval = 0
	
	t = Thread(target=worker)
	t.daemon = True
	t.start()

	tp = ThreadPool.ThreadPool(10,20)

	while(offsetval < 8000):
		tp.add_job(GetTracks,[searchstr,offsetval])
		offsetval += 200
	starttime = time()
	#kill if shit takes longer than a minute
	while ResultsLeft>0 or (time()-starttime > 60):
		print "%s\r" % (ResultsLeft),
		sleep(0.25)
	print "facdict is " + str(len(favdict.keys())) + " long"
	

	sorted_x = sorted(favdict.iteritems(), key=operator.itemgetter(1))
	sorted_x.reverse()

	if(len(sorted_x) > 0):
		for i in range(0,10):
			urlstr = sorted_x[i][0]
			print urlstr
			try:
				embed_info = client.get('/oembed', url=urlstr)
			except:
				print "skippin " + urlstr
			try:
				output += "%s</br>" % (embed_info.html)
			except Exception as e:
				print "got some funky characters here\n" + str(e)
				continue
	return output
	
def worker():
    global results
    while True:
        item = q.get()
        favdict[item[0]] = item[1]
        q.task_done()


def GetTracks(searchstr,offsetnum):
	global ResultsLeft
	usePlayCount = True
	taglist = []
	retries = 0
	while(retries < 3):
		try:
			tracks = client.get('/tracks', q=searchstr, tags=taglist,limit=200,offset=offsetnum,duration={'to':480000})
			if(len(tracks) < 1): 
				return
			for track in tracks:
					try:
						if(usePlayCount):
							q.put((track.permalink_url,track.playback_count))
							#favdict[track.permalink_url] = track.playback_count
						else:
							#favdict[track.permalink_url] = track.favoritings_count
							if(track.playback_count > 100):
								q.put((track.permalink_url,float(track.favoritings_count) / float(track.playback_count)))
								#favdict[track.permalink_url] = float(track.favoritings_count) / float(track.playback_count)
					except AttributeError:
						continue
			ResultsLeft -= 200
			return
		except Exception, excep:
			#results += 200
			retries += 1
			print "error getting tracks %i! %s, retry count=%i" % (offsetnum,str(excep),retries)
	ResultsLeft -= 200
	
#GetTracks(client,"bam bam",0)
#dosearch('bam bam')
