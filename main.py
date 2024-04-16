from flask import Flask, render_template, request
from sqlalchemy import create_engine, text
import math

app = Flask(__name__)
engine = create_engine("mysql://root:1234@localhost/boatdb", echo=True)
conn = engine.connect()

def run_query(query, parameters = None):
	return conn.execute(text(query), parameters)

def get_int(value, min, default):
	try:
		value = int(value)
		assert(value >= min)
	except:
		value = default

	return value

def clamp(x, min, max):
	if x < min: return min
	if x > max: return max

	return x

def get_boats(page = 1, per_page = 10):
	page = get_int(page, 1, 1)
	per_page = get_int(per_page, 10, 10)

	boat_count = run_query("select count(distinct `id`) from `boats`").first()[0]

	min_page = 1
	max_page = math.ceil(boat_count / per_page)

	page = clamp(page, min_page, max_page)

	boats = run_query(f"select * from `boats` limit {per_page} offset {(page - 1) * per_page}").all()

	return boats, page, per_page, min_page, max_page

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
	boat_id = get_int(boat_id, 1, 1)

	boat = run_query(f"select * from `boats` where `id` = {boat_id}").first()

	return render_template("view.html", boat = boat)

@app.route("/boats/")
def view_boats():
	page = request.args.get("page")
	per_page = request.args.get("per_page")

	boats, page, per_page, min_page, max_page = get_boats(page, per_page)

	return render_template(
		"boats.html",
		boats = boats,
		page = page,
		per_page = per_page,
		min_page = min_page,
		max_page = max_page
	)

if __name__ == "__main__":
	app.run()
