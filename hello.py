import os
from flask import Flask, request, render_template
from scsearchfast import dosearch

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
	error=None	
	return render_template('index.html', error=error)

@app.route('/search', methods=['POST','GET'])
def search():
	if request.method == 'POST':
		#result = str(request.form)
		result = dosearch(request.form['searchstr'])
		return render_template('index.html', result=result)
	return render_template('index.html', result="")
    
if __name__ == '__main__':
	app.run(debug=True)