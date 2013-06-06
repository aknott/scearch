import os
from flask import Flask, request, render_template
from scsearchfast import dosearch

app = Flask(__name__)

@app.route('/', methods=['GET'])
def mainapp():
	if request.method == 'POST':
		result=""
		#result = str(request.form)
		print request.form
		input = request.form['searchstr']
		sorttype = request.form['sort']
		print "searching " + input + " on " + sorttype
		result = dosearch(input,sorttype)
		return render_template('index.html', result=result)
	return render_template('index.html', result="")

@app.route('/search', methods=['POST','GET'])
def search():
	if request.method == 'POST':
		result=""
		#result = str(request.form)
		print request.form
		input = request.form['searchstr']
		sorttype = request.form['sort']
		print "searching " + input + " on " + sorttype
		result = dosearch(input,sorttype)
		return render_template('index.html', result=result)
	return render_template('index.html', result="")
    
if __name__ == '__main__':
	app.run(debug=True)