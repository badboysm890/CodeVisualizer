
import cgi
import json
import pg_logger
import sys


# set to true if you want to log queries in DB_FILE 
LOG_QUERIES = False

if LOG_QUERIES:
  import os, datetime, create_log_db, sqlite3


def cgi_finalizer(input_code, output_trace):
  """Write JSON output for js/pytutor.js as a CGI result."""
  ret = dict(code=input_code, trace=output_trace)
  json_output = json.dumps(ret, indent=None) # use indent=None for most compact repr

  if LOG_QUERIES:
    try:
      con = sqlite3.connect(create_log_db.DB_FILE)
      cur = con.cursor()

      cur.execute("INSERT INTO query_log VALUES (NULL, ?, ?, ?, ?, ?, ?)",
                  (datetime.datetime.now(),
                   os.environ.get("REMOTE_ADDR", "N/A"),
                   os.environ.get("HTTP_USER_AGENT", "N/A"),
                   os.environ.get("HTTP_REFERER", "N/A"),
                   user_script,
                   int(cumulative_mode)))
      con.commit()
      cur.close()
    except Exception as err:
      print(err)

  print("Content-type: text/plain; charset=iso-8859-1\n")
  print(json_output)

raw_input_json = None
options_json = None

if len(sys.argv) > 1:
  user_script = open(sys.argv[1]).read()

else:
  form = cgi.FieldStorage()
  user_script = form['user_script'].value
  if 'raw_input_json' in form:
    raw_input_json = form['raw_input_json'].value
  if 'options_json' in form:
    options_json = form['options_json'].value

pg_logger.exec_script_str(user_script, raw_input_json, options_json, cgi_finalizer)
