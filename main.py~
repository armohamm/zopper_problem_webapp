#appcfg.py -A enduring-grid-600 update appengine-try-python
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

# main index
@app.route("/")
def index():
	return render_template("index.html")

@app.route("/IVR", methods=["GET","POST"])
def api_call():
	passed_url = request.args.get('mobile_no')
	
        sum2 = summ.sum2(passed_url)
	return sum2

if __name__ == "__main__":
	app.run(debug=True)
