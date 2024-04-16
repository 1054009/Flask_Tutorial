from flask import Flask, render_template, request
from sqlalchemy import create_engine, text
import math

app = Flask(__name__)
engine = create_engine("mysql://root:1234@localhost/boatdb", echo=True)
conn = engine.connect()

def run_query(query, parameters = None):
	return conn.execute(text(query), parameters)

@app.route("/")
@app.route("/home")
def index():
	boat_count = run_query("select count(distinct `id`) from `boats`").first()[0]
	owner_count = run_query("select count(distinct `owner_id`) from `boats`").first()[0]
	type_count = run_query("select count(distinct `type`) from `boats`").first()[0]

	return render_template(
		"home.html",
		boat_count = boat_count,
		owner_count = owner_count,
		type_count = type_count
	)

@app.route("/boats/view/<boat_id>")
def view_boat(boat_id = 1):
	try:
		boat_id = int(boat_id)
		assert(boat_id > 0)
	except:
		boat_id = 1

	boat = run_query(f"select * from `boats`where `id` = {boat_id}").first()

	return render_template("view.html", boat = boat)

@app.route("/boats/")
@app.route("/boats/<page>")
def get_boats(page = 1):
	try:
		page = int(page)
		assert(page > 0)
	except:
		page = 1

	boat_count = run_query("select count(distinct `id`) from `boats`").first()[0]
	boats = run_query(f"select * from `boats` limit 10 offset {(page - 1) * 10}").all()

	return render_template(
		"boats.html",
		boats = boats,
		page = page,
		min_page = 1,
		max_page = math.ceil(boat_count / 10)
	)

if __name__ == "__main__":
	app.run()
