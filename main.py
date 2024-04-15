from flask import Flask, render_template, request
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text

app = Flask(__name__)
engine = create_engine("mysql://root:1234@localhost/boatdb", echo=True)
conn = engine.connect()

@app.route("/")
def index():
	return render_template("home.html", boat_count = 5)

@app.route("/boats/")
@app.route("/boats/<page>")
def get_boats(page = 1):
	page = int(page)

	query = f"select * from `boats` limit 10 offset {(page - 1) * 10}"
	boats = conn.execute(query).all()

	return render_template("boats.html", boats = boats, page = page)

@app.route("/create", methods = ["GET"])
def create_get_request():
	return render_template("boats_create.html")

@app.route("/create", methods = ["POST"])
def create_boat():
	status = "Boat??"

	try:
		query = "insert into `boats` values (:id, :name, :type, :owner_id, :rental_price)"
		conn.execute(query, request.form)

		status = "Your boat is now"
	except Exception as e:
		print(e.orig.args[1])

		status = "Boat has been DENIED"

	return render_template("boats_create.html", status = status)

if __name__ == "__main__":
	app.run()
