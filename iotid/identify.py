import sys
import logging
import http.client
import click
from easysnmp import Session


logging.basicConfig()
logger = logging.getLogger("identify")
logger.setLevel(logging.INFO)


MATCHING = {
   "http_server_header": {
      "MoxaHttp": {"manufacturer": "Moxa"},
      "WISE-4000/LAN": {"manufacturer": "Advantech", "device": "WISE-4000/LAN"},
   },
   "snmp_sysdescr": {
      "NP5210": {"manufacturer": "Moxa", "device": "NPort 5210"}
   },
}

METHODS = ("http_server_header", "snmp_sysdescr")


def snmp_sysdescr(ip):
   "identify using SNMP sysDescr description"

   s = Session(hostname=ip, version=1)
   return s.get(".1.3.6.1.2.1.1.1.0").value


def http_server_header(ip):
   "identify using http server header"

   conn = http.client.HTTPConnection(ip, 80)
   conn.request("HEAD","/")
   response = conn.getresponse()
   server = response.getheader("server", default=None)
   return server


def match(matchmethod, matchvalue):
   for value, result in MATCHING[matchmethod].items():
      if value in matchvalue:
         return result
   return None


@click.command()
@click.argument("ip")
def identify(ip):
   for method in METHODS:
      check = globals()[method]
      try:
         data = check(ip)
      except:
         continue
      else:
         logger.info("%s:%s" % (method, data))
         result = match(method, data)
         if not result:
            continue
         elif "device" in result:
            click.echo(result)


if __name__=="__main__":
   identify()
