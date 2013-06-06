import soundcloud
import operator
import ThreadPool
from time import sleep, time
from threading import Thread
from Queue import Queue

ResultsLeft = 8000
q = Queue()
favdict = {}

results = ""

client = soundcloud.Client(client_id='af912f440f0d027065e7351089b08a52')

def dosearch(searchstr,sorttype):
    global ResultsLeft
    ResultsLeft = 8000
    output = ""
    favdict.clear()
    offsetval = 0
    
    t = Thread(target=worker)
    t.daemon = True
    t.start()

    tp = ThreadPool.ThreadPool(15,20)

    while(offsetval < 8000):
        tp.add_job(GetTracks,[searchstr,offsetval,sorttype])
        offsetval += 200
    starttime = time()
    #kill if shit takes longer than a minute
    while ((ResultsLeft>0) and (time()-starttime < 20.0)):
        print "%s" % (ResultsLeft)
        sleep(0.50)
    print time()-starttime    
    print "facdict is " + str(len(favdict.keys())) + " long"
    

    sorted_x = sorted(favdict.iteritems(), key=operator.itemgetter(1))
    sorted_x.reverse()

    if(len(sorted_x) > 0):
        for i in range(0,10):
            trackid = sorted_x[i][0]
            widget = "<iframe width=\"100%\" height=\"166\" scrolling=\"no\" frameborder=\"no\" src=\"http://w.soundcloud.com/player/?url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F"+str(trackid)+ "\"></iframe>"
            try:
                output += "%s</br>" % (widget)
            except Exception as e:
                print "got some funky characters here\n" + str(e)
                continue
    return output
    
def worker():
    while True:
        item = q.get()
        favdict[item[0]] = item[1]
        q.task_done()


def GetTracks(searchstr,offsetnum,sorttype):
    global ResultsLeft
    usePlayCount = True
    taglist = []
    retries = 0
    while(retries < 3):
        try:
            #print "get %i" % offsetnum
            tracks = client.get('/tracks', q=searchstr, tags=taglist,limit=200,offset=offsetnum,duration={'to':480000})
            #print "got result"
            if(len(tracks) < 1): 
                return
            for track in tracks:
                    try:
                        if(sorttype == u'plays'):
                            q.put((track.id,track.playback_count))
                            #favdict[track.permalink_url] = track.playback_count
                        elif(sorttype == u'favorites'):
                            q.put((track.id,track.favoritings_count))
                        elif(sorttype == u'hype'):
                            if(track.playback_count > 500):
                                q.put((track.id,float(track.favoritings_count) / float(track.playback_count)))
                        else:
                            q.put((track.id,track.playback_count))
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
