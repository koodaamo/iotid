# iotid

IOT identification

The provided 'iotid' cli tool identifies IOT devices through various methods.
Currently supported methods check:

 - the 'server' header of the device HTTP server response
 - the 'sysDescr' or 'sysObjectId' SNMP get value

The device database is managed as a separate YAML file.
