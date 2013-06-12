import soundcloud
import operator
import ThreadPool
from time import sleep, time
from threading import Thread, Lock
from Queue import Queue


class Searcher:
	client = soundcloud.Client(client_id='af912f440f0d027065e7351089b08a52')
	q = Queue()
	tp = ThreadPool.ThreadPool(15,20)
	lockobj = Lock()
	ResultsLeft = 8000
	favdict = {}
	
	def __init__(self):
		print "created searcher"

		

	def dosearch(self,searchstr,sorttype):
		output = ""
		self.favdict.clear()
		offsetval = 0
		
		t = Thread(target=self.worker)
		t.daemon = True
		t.start()

		while(offsetval < 8000):
			self.tp.add_job(self.GetTracks,[searchstr,offsetval,sorttype])
			offsetval += 200
		starttime = time()
		#kill if shit takes longer than 20 seconds
		while ((self.ResultsLeft>0) and (time()-starttime < 20.0)):
			print "%s" % (self.ResultsLeft)
			sleep(0.50)
		print time()-starttime    
		print "facdict is " + str(len(self.favdict.keys())) + " long"
		

		sorted_x = sorted(self.favdict.iteritems(), key=operator.itemgetter(1))
		sorted_x.reverse()

		if(len(sorted_x) > 0):
			if(len(sorted_x) < 20):
				numresults = len(sorted_x)
			else:
				numresults = 20
			for i in range(0,numresults):
				trackid = sorted_x[i][0]
				widget = "<iframe width=\"100%\" height=\"166\" scrolling=\"no\" frameborder=\"no\" src=\"http://w.soundcloud.com/player/?url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F"+str(trackid)+ "\"></iframe>"
				try:
					output += "%s</br>" % (widget)
				except Exception as e:
					print "got some funky characters here\n" + str(e)
					continue
		return output
		
	def worker(self):
		while True:
			item = self.q.get()
			self.favdict[item[0]] = item[1]
			self.q.task_done()


	def GetTracks(self,searchstr,offsetnum,sorttype):
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
				tracks = self.client.get('/tracks', q=searchstr, tags=taglist,limit=200,offset=offsetnum,duration={'to':480000})
				if(len(tracks) < 1): 
					self.lockobj.acquire()
					self.ResultsLeft -= 200
					self.lockobj.release()
					return
				for track in tracks:
						try:
							if(exactString):
								info = "%s %s" % (track.title,track.description)
								if(searchstr.lower() not in info.lower()):
									continue
							if(sorttype == u'plays'):
								self.q.put((track.id,track.playback_count))
							elif(sorttype == u'favorites'):
								self.q.put((track.id,track.favoritings_count))
							elif(sorttype == u'hype'):
								if(track.playback_count > 500):
									self.q.put((track.id,track.playback_count**(float(track.favoritings_count) / float(track.playback_count))))
							else:
								self.q.put((track.id,track.playback_count))
						except AttributeError:
							continue
				self.lockobj.acquire()
				self.ResultsLeft -= 200
				self.lockobj.release()
				return
			except Exception, excep:
				retries += 1
				print "error getting tracks %i! %s, retry count=%i" % (offsetnum,str(excep),retries)
		self.lockobj.acquire()
		self.ResultsLeft -= 200
		self.lockobj.release()

