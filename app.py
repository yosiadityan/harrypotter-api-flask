# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

# Configure Flask app. For client encoding, check this : https://www.postgresql.org/docs/9.3/multibyte.html
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
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

# A welcome message to test our server
@app.route('/')
def index():
	return {'message' : 'OK', 'tables' : list(meta.tables.keys())}

# Get Harry Potter 1 data
@app.route('/hp1/', methods=['GET'])
def get_hp1_data():
	return get_hp_data('Harry Potter 1')

# Get Harry Potter 2 data
@app.route('/hp2/', methods=['GET'])
def get_hp2_data():
	return get_hp_data('Harry Potter 2')

# Get Harry Potter 3 data
@app.route('/hp3/', methods=['GET'])
def get_hp3_data():
	return get_hp_data('Harry Potter 3')

# Get Potions data
@app.route('/spells/', methods=['GET'])
def get_spells_data():
	return get_hp_data('Spells')

@app.route('/potions/', methods=['GET'])
def get_potions_data():
	return get_hp_data('Potions')


if __name__ == '__main__':
	# Threaded option to enable multiple instances for multiple user access support
	app.run(debug=True, threaded=True, port=5000)