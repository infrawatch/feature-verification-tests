#!/usr/bin/python

import sys
import getopt

from pysensu.api import SensuAPI

DEFAULT_SENSU_ADDR = "127.0.0.1"
DEFAULT_SENSU_PORT = "4567"

def display_help(name):
      print """Usage: %s [options] [<client> [<check0> .. <checkN>]]
  -a <address>    Sensu API hostname or IP address
  -p <port>       Sensu API TCP port
  -U <username>   Sensu API username
  -P <password>   Sensu API password
  -v              Print verbose output
  -h              Display this help message""" % name

def main():
  sensu_addr = DEFAULT_SENSU_ADDR
  sensu_port = DEFAULT_SENSU_PORT
  sensu_user = None
  sensu_passwd = None
  verbose = False

  try:
   opts, args = getopt.getopt(sys.argv[1:], "a:p:U:P:hv")
  except getopt.GetoptError as err:
   sys.stderr.write("%s\n", err)
   display_help(sys.argv[0])
   sys.exit(3)

  for o, a in opts:
    if o == "-a":
      sensu_addr = a
    elif o == "-p":
      sensu_port = a
    elif o == "-U":
      sensu_user = a
    elif o == "-P":
      sensu_passwd = a
    elif o == "-v":
      verbose = True
    else:
      display_help(sys.argv[0])
      if o == "-h":
        sys.exit(0)
      sys.exit(3)

  if len(args) < 1:
    client = None
    checks = []
  else:
    client = args[0]
    checks = args[1:]

  try:
    sensu_url = "http://%s:%s" % (sensu_addr, sensu_port)
    if verbose:
      sys.stdout.write("Connecting to %s\n" % sensu_url)
    api = SensuAPI(sensu_url, username=sensu_user, password=sensu_passwd)
    if not api:
      raise Exception, "login failed"
  except Exception, e:
    sys.stderr.write("Unable to connect to sensu API: %s\n" % str(e))
    sys.exit(3)

  status = 0
  if len(checks) > 0:
    for check in checks:
      try:
        result = api.get_result(client, check)
        status = result["check"]["status"]
        if verbose:
          sys.stdout.write("%s\n" % result["check"])
        sys.stdout.write("Status for client \"%s\" check \"%s\": %d\n" % (
            client, check, status))
        status = max(status, result["check"]["status"])
      except Exception, e:
        sys.stderr.write(
            "Unable to get results for client \"%s\" check \"%s\": %s\n" % (
                client, check, str(e)))
        status = 3
  else:
    try:
      if client:
        results = api.get_results(client)
      else:
        results = api.get_all_client_results()

      for result in results:
        client = result["client"]
        check = result["check"]["name"]
        status = result["check"]["status"]
        if verbose:
          sys.stdout.write("%s\n" % result["check"])
        sys.stdout.write("Status for client \"%s\" check \"%s\": %d\n" % (
            client, check, status))
        status = max(status, result["check"]["status"])
    except Exception, e:
      if client:
        sys.stderr.write("Unable to get results for client \"%s\": %s\n" % (
            (client, str(e))))
      else:
        sys.stderr.write("Unable to get results all clients: %s\n" % str(e))
      status = 3

  sys.exit(status)

if __name__ == "__main__":
  main()
