import os
from flask import Flask, request, render_template
from scsearchfast import Searcher

app = Flask(__name__)

@app.route('/', methods=['GET'])
def mainapp():
	result=""
	input = request.args.get('searchstr')
	sorttype = request.args.get('sort')
	if((input is not None and sorttype is not None) and input != ""):
		print "searching " + input + " on " + sorttype
		searcher = Searcher()
		result = searcher.dosearch(input,sorttype)
	if input is None:
		input = ""
	return render_template('index.html', input=input,result=result)


@app.route('/search', methods=['POST','GET'])
def search():
	if request.method == 'POST':
		result=""
		#result = str(request.form)
		print request.form
		input = request.form['searchstr']
		sorttype = request.form['sort']
		print "searching " + input + " on " + sorttype
		searcher = Searcher()
		result = searcher.dosearch(input,sorttype)
		return render_template('index.html', result=result)
	return render_template('index.html', result="")
    
if __name__ == '__main__':
	app.run(debug=True)