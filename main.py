from flask import Flask, render_template, request
from sqlalchemy import create_engine, text
import math

app = Flask(__name__)
engine = create_engine("mysql://root:1234@localhost/boatdb")
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

def get_edit_mode(mode):
	mode = str(mode).strip().lower()

	if mode in ( "add", "remove", "edit" ):
		return mode
	else:
		return "invalid"

@app.route("/")
@app.route("/home/")
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

@app.route("/manage/", methods = [ "GET" ])
@app.route("/manage/<page>", methods = [ "GET" ])
def manage():
	return render_template("manage.html")

@app.route("/edit/<mode>", methods = [ "GET" ])
def load_edit(mode = "invalid"):
	return render_template("edit.html", mode = get_edit_mode(mode))

@app.route("/edit/<mode>", methods = [ "POST" ])
def handle_edit(mode = "invalid"):
	mode = get_edit_mode(mode)

	boat_id = request.form.get("boat_id")
	owner_name = request.form.get("owner_name")
	boat_type = request.form.get("boat_type")
	owner_id = request.form.get("owner_id")
	rental_price = request.form.get("rental_price")

	match mode:
		case "add":
			boat_id = run_query("select max(`id`) from `boats`;").first()[0] + 1

			owner_id = run_query(f"select `owner_id` from `boats` where lower(`name`) = '{owner_name.lower()}'").first()

			if owner_id == None:
				owner_id = run_query("select max(`owner_id`) from `boats`;").first()[0] + 1
			else:
				owner_id = owner_id[0]

			run_query(
				"insert into `boats` values (:boat_id, :owner_name, :boat_type, :owner_id, :rental_price)",

				{
					"boat_id": boat_id,
					"owner_name": owner_name,
					"boat_type": boat_type,
					"owner_id": owner_id,
					"rental_price": rental_price
				}
			)

			pass

		case "remove":
			run_query(f"delete from `boats` where `id` = {boat_id}")

			pass

		case "edit":
			owner_id = run_query(f"select `owner_id` from `boats` where lower(`name`) = '{owner_name.lower()}'").first()

			if owner_id == None:
				owner_id = run_query("select max(`owner_id`) from `boats`;").first()[0] + 1
			else:
				owner_id = owner_id[0]

			run_query(f"update `boats` set `name` = '{owner_name}', `type` = '{boat_type}', `owner_id` = {owner_id}, `rental_price` = {rental_price} where `id` = {boat_id}")

			pass

		case "invalid":
			pass

		case _:
			pass

	return render_template("edit.html", mode = mode)

if __name__ == "__main__":
	app.run()
