from flask import Flask, render_template, request
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text

app = Flask(__name__)
engine = create_engine("mysql://root:1234@localhost/boatdb", echo=True)
conn = engine.connect()

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/boats/")
@app.route("/boats/<page>")
def get_boats(page = 1):
	page = int(page)

	query = f"SELECT * FROM boats LIMIT {per_page} OFFSET {(page - 1) * per_page}"

	boats = conn.execute(query).all()

	return render_template("boats.html", boats = boats, page = page)

@app.route("/create", methods=["GET"])
def create_get_request():
	return render_template("boats_create.html")

@app.route("/create", methods=["POST"])
def create_boat():
	try:
		conn.execute(
			text("INSERT INTO boats values (:id, :name, :type, :owner_id, :rental_price)"),
			request.form
		)
		return render_template("boats_create.html", error=None, success="Data inserted successfully!")
	except Exception as e:
		error = e.orig.args[1]
		print(error)
		return render_template("boats_create.html", error=error, success=None)

if __name__ == "__main__":
	app.run(debug=True)
