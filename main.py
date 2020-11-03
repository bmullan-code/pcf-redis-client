import json
import csv
import os
import redis
from flask import request, Response
from flask import Flask
import logging
import sys
import json

# if an instance of redis is bound as a pcf service the VCAP_SERVICES environment variable will be populated.
# we parse that for the host, port and passowrd. Otherwise we assume a localhost instance (useful for testing in 
#dev environment and running redis from a docker image. eg.
# docker run -it -p 6379:6379 redis
#)
vcap = os.environ.get("VCAP_SERVICES")
if (vcap!=None):
	vcapjson = json.loads(vcap)
	creds = vcapjson["p-redis"][0]["credentials"]
	redisHost     = creds["host"]
	redisPort     = creds["port"]
	redisPassword = creds["password"]
else:
	redisHost = 'localhost'
	redisPort = 6379

# r = redis.StrictRedis(host='192.168.8.27', port=36921, db=0,password="526c9413-52e2-46da-a73c-c19a18951058")
if (redisPassword!=None):
	r = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
else:
	r = redis.StrictRedis(host=redisHost, port=redisPort, password=redisPassword,db=0)

def load_csv():
	with open('drugsComTest_raw.csv') as csv_file:
	    csv_reader = csv.reader(csv_file, delimiter=',')
	    line_count = 0
	    for row in csv_reader:
	        if line_count == 0:
	            print(f'Column names are {", ".join(row)}')
	            line_count += 1
	        else:
	            # uniqueID,drugName,condition,review,rating,date,usefulCount
	            # print(f'\t{row[0]} {row[1]} {row[2]} {row[4]} {row[5]} {row[6]}')
	            line_count += 1
	            if (line_count % 250 == 0):
	            	print(line_count)
	            r.set(str(row[0]),json.dumps(row))
	            # print(f'Processed {line_count} lines.')


@app.route('/entry/<id>')
def foo(id):
	print(id)
	return r.get(str(id) )

@app.route('/size')
def size():
	return str(r.dbsize())

// return first 10 values
@app.route('/first')
def first():
	rows = []
	s = ""
	app.logger.debug("first()")
	for key in r.scan_iter():
		rows.append(r.get(key))
		app.logger.debug(len(rows))
		if(len(rows)>10):
			break
	return str(rows)


app = Flask(__name__)
cf_port = int(os.getenv('PORT', '3000'))
app.debug=True

if __name__ == '__main__':
	gunicorn_logger = logging.getLogger('gunicorn.error')
	app.logger.handlers = gunicorn_logger.handlers
	app.logger.setLevel(gunicorn_logger.level)
	app.run(port=cf_port,host='0.0.0.0')

load_csv()
