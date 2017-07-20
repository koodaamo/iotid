import sys
import logging
import http.client
import click
import yaml
from easysnmp import Session


logging.basicConfig()
logger = logging.getLogger("identify")
logger.setLevel(logging.INFO)


METHODS = ("http_root_server_header", "http_onvif_server_header", "snmp_sysobjectid", "snmp_sysdescr")

# SNMP based identification

def snmp_get(oid, ip):
   s = Session(hostname=ip, version=1)
   return s.get(oid).value

def snmp_sysdescr(ip):
   "identify using SNMP sysDescr description"
   return snmp_get(".1.3.6.1.2.1.1.1.0", ip)

def snmp_sysobjectid(ip):
   "identify using the SNMP sysObjectId"
   return snmp_get(".1.3.6.1.2.1.1.2.0", ip).value


# HTTP server header - based identification
def http_server_header(path, ip):
   "identify using http server header at a given path"
   conn = http.client.HTTPConnection(ip, 80)
   conn.request("HEAD", path)
   response = conn.getresponse()
   server = response.getheader("server", default=None)
   return server

def http_root_server_header(ip):
   "identify using http server header"
   return http_server_header("/", ip)

def http_onvif_server_header(ip):
   "identify usig http onvif path server header"
   return http_server_header("/onvif/device_service", ip)


def match(db, matchmethod, matchvalue):
   for value, result in db[matchmethod].items():
      if value in matchvalue:
         return result
   return None


@click.command()
@click.argument("ip")
@click.argument("devicefile", type=click.Path(exists=True))
def identify(ip, devicefile):

   with open(devicefile) as df:
      database = yaml.load(df)

   for method in METHODS:
      check = globals()[method]
      try:
         data = check(ip)
      except:
         continue
      else:
         if not data:
            continue
         logger.info("%s:%s" % (method, data))
         result = match(database, method, data)
         if not result:
            continue
         elif "device" in result:
            click.echo(result)
            return

if __name__=="__main__":
   identify()
