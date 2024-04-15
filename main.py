from flask import Flask, render_template
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:1234@localhost/boatdb"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


# render a file
@app.route('/')
def index():
    return render_template('index.html')


# remember how to take user inputs?
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


# get all boats
@app.route('/boats/')
@app.route('/boats/<page>')
def get_boats(page=1):
    # boats = BoatsModel.query.paginate(page=int(page), per_page=10)  # returns all boats
    page = int(page)
    per_page = 10
    boats = conn.execute(text(f"SELECT * FROM boats LIMIT {per_page} OFFSET {(page - 1) * per_page}")).all()
    print(boats)
    return render_template('boats.html', boats=boats, page=page, per_page=per_page)


if __name__ == '__main__':
    app.run(debug=True)
