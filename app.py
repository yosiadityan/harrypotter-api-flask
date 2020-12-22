# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Configure Flask app. For client encoding, check this : https://www.postgresql.org/docs/9.3/multibyte.html
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://atvtqynasseqsx:f41f3db470641fc322a99a4114aa31b3e4ab6db53d8c0e0db1abf2d822c45555@ec2-54-146-118-15.compute-1.amazonaws.com:5432/d9qbka0q4dqs9k?client_encoding=WIN1252"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# Configure database connection using SQLAlchemy
db = SQLAlchemy(app)
engine = db.engine
meta = db.MetaData()
meta.reflect(engine)


def get_hp_data(table_name):
	hp_data = db.Table(table_name, meta, autoload=True, autoload_with=engine)

	if request.method == 'GET':
		params = request.args
		col_name = hp_data.c.keys()
		col_name.pop(col_name.index('index'))

		params_dict = dict()
		for param, val in params.items():
			if param.title() in col_name:
				params_dict[param.title()] = val

		cond = db.and_(*(hp_data.c[col].ilike(f"%{params_dict.get(col, '')}%") for col in col_name))
		query = db.select([*[hp_data.c[col] for col in col_name]]).where(cond)

		with engine.connect() as conn:
			resultproxy = conn.execute(query).fetchall()
		query_result = {idx: dict(row) for idx, row in enumerate(resultproxy)}

		return ({'parameter' : {k:params_dict.get(k, 'None').title() for k in col_name},
				 'data' : query_result})

@app.route('/getmsg/', methods=['GET'])
def respond():
	# Retrieve the name from url parameter
	name = request.args.get("name", None)

	# For debugging
	print(f"got name {name}")

	response = {}

	# Check if user sent a name at all
	if not name:
		response["ERROR"] = "no name found, please send a name."
	# Check if the user entered a number not a name
	elif str(name).isdigit():
		response["ERROR"] = "name can't be numeric."
	# Now the user entered a valid name
	else:
		response["MESSAGE"] = f"Welcome {name} to our awesome platform!!"

	# Return the response in json format
	return jsonify(response)

@app.route('/post/', methods=['POST'])
def post_something():
	param = request.form.get('name')
	print(param)
	# You can add the test cases you made in the previous function, but in our case here you are just testing the POST functionality
	if param:
		return jsonify({
			"Message": f"Welcome {name} to our awesome platform!!",
			# Add this option to distinct the POST request
			"METHOD" : "POST"
		})
	else:
		return jsonify({
			"ERROR": "no name found, please send a name."
		})

# A welcome message to test our server
@app.route('/')
def index():
	return {'message' : 'OK', 'tables' : list(meta.tables.keys())}

# Get Harry Potter 1 data
@app.route('/hp1/', methods=['GET', 'POST'])
def get_hp1_data():
	return get_hp_data('Harry Potter 1')

# Get Harry Potter 2 data
@app.route('/hp2/', methods=['GET', 'POST'])
def get_hp2_data():
	return get_hp_data('Harry Potter 2')

# Get Harry Potter 3 data
@app.route('/hp3/', methods=['GET', 'POST'])
def get_hp3_data():
	return get_hp_data('Harry Potter 3')

# Get Potions data
@app.route('/spells/', methods=['GET', 'POST'])
def get_spells_data():
	return get_hp_data('Spells')

@app.route('/potions/', methods=['GET', 'POST'])
def get_potions_data():
	return get_hp_data('Potions')

# -----------------------------------------------WHATS NEXT: PARAMETER IS CASE INSENSITIVE---------------------------------------------------

if __name__ == '__main__':
	# Threaded option to enable multiple instances for multiple user access support
	app.run(debug=True, threaded=True, port=5000)

	# queries = db.session.execute("SELECT * FROM employee")
	# result = [dict(row.items()) for row in queries]

	# meta = db.MetaData()
	# hp1 = db.Table('Harry Potter 1', meta, autoload=True, autoload_with=db.engine)
	# print(db.session.query(hp1).first())

	# meta.reflect(db.engine)
	# print(meta.tables.keys())

	# return jsonify({idx:val for idx, val in enumerate(result)})