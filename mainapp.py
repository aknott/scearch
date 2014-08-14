import os
from flask import Flask, request, render_template
#from scsearchfast import dosearch
from search import Searcher, SearchResult

app = Flask(__name__)

@app.route('/', methods=['GET'])
def mainapp():
	result=""
	input = request.args.get('searchstr')
	sorttype = request.args.get('sortselect')
	if((input is not None and sorttype is not None) and input != ""):
		searcher = Searcher(input,sorttype)
		results = searcher.search()
	if input is None:
		input = ""
	widgets = [r.widget for r in results]
	#return render_template('index.html', input=input,result="".join(widgets))
	return render_template('index2.html', input=input,results=results)
    
if __name__ == '__main__':
	app.run(debug=True)