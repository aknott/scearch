import os
from flask import Flask, request, render_template
#from scsearchfast import dosearch
from scsearchgevent import Searcher

app = Flask(__name__)

@app.route('/', methods=['GET'])
def mainapp():
	result=""
	input = request.args.get('searchstr')
	sorttype = request.args.get('sortselect')
	if((input is not None and sorttype is not None) and input != ""):
		searcher = Searcher(input,sorttype)
		result = searcher.search()
	if input is None:
		input = ""
	return render_template('index.html', input=input,result="".join(result))
    
if __name__ == '__main__':
	app.run(debug=True)