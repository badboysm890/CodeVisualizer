import asyncio
from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
import requests
from urllib.parse import quote
try:
    import StringIO # NB: don't use cStringIO since it doesn't support unicode!!!
except:
    import io as StringIO # py3
import json
import pg_logger

app = Flask(__name__)
CORS(app)

@app.route('/web_exec.py')
def dummy_ok(name=None):
    print(request.args.get('user_script'))
    url = "http://23.239.12.25/"+request.args.get('type')+"?user_script="+quote(request.args.get('user_script'))+"&options_json=%7B%22cumulative_mode%22%3Atrue%2C%22heap_primitives%22%3Atrue%2C%22show_only_outputs%22%3Afalse%2C%22origin%22%3A%22opt-frontend.js%22%7D&raw_input_json=&_=1610536900515"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text


@app.route('/web_exec_py2.py')
@app.route('/web_exec_py3.py')
@app.route('/LIVE_exec_py2.py')
@app.route('/LIVE_exec_py3.py')
def get_py_exec():
  out_s = StringIO.StringIO()
  def json_finalizer(input_code, output_trace):
    ret = dict(code=input_code, trace=output_trace)
    json_output = json.dumps(ret, indent=None)
    out_s.write(json_output)
  options = json.loads(request.args.get('options_json'))
  pg_logger.exec_script_str_local(request.args.get('user_script'),
                                  request.args.get('raw_input_json'),
                                  options['cumulative_mode'],
                                  options['heap_primitives'],
                                  json_finalizer)

  return out_s.getvalue()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003)