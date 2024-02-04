#!/usr/bin/python3

import pynetbox
import json
import sys
import os
import re
from napalm import get_network_driver

NETBOX_TOKEN="47266655105a25cf2727ec53409e92fabd18f6ee"
NETBOX_URL="http://127.0.0.1:8001"
SSH_USERNAME="test"
SSH_PASSWORD="test"

nb = pynetbox.api(url=NETBOX_URL, token=NETBOX_TOKEN)

if len(sys.argv) == 1:
    print("Usage: "+sys.argv[0]+" CISCO_DEVICE_TO_DISCOVER")
    sys.exit()

print("Device name has been supplied...")  

devices = nb.dcim.devices.all()
existingdevices = [device.name for device in devices]

driver = get_network_driver('ios')
device = driver(sys.argv[1], SSH_USERNAME, SSH_PASSWORD)
device.open()
device_information=device.get_facts()
device_lldp=device.get_lldp_neighbors_detail()
device_vrf=device.get_network_instances()
response_interface_ip=device.get_interfaces_ip()
print(json.dumps(device_information, indent=4))
# print(json.dumps(device_lldp, indent=4))


if device_information['hostname'] not in existingdevices:
    response_device=nb.dcim.devices.create(
        name=device_information['hostname'],
        serial=device_information['serial_number'],
        device_role=8,
        device_type=990,
        site=2
    )
    for interface in device_information["interface_list"]:
        response_interface=nb.dcim.interfaces.create(
            device=response_device["id"],
            type="100base-tx",
            name=interface,
        )
    print("add to netbox result: "+str(response_device))
else:
    print("this device is already in Netbox.")
    print("-"*79)
print(device_lldp)

for interface_a in device_lldp:
    for interface_a_data in device_lldp[interface_a]:
        interface_b=""
        if re.match("^Et[0-9]",interface_a_data["remote_port"]):
            interface_b=interface_a_data["remote_port"].replace("Et","Ethernet")
        try:
            response_device_b=nb.dcim.devices.get(name=interface_a_data["remote_system_name"].split(".")[0])
        except pynetbox.core.query.RequestError as e:
            print(e)
            print("LLDP link: "+sys.argv[1]+" "+interface_a+" <> "+interface_b+" "+interface_a_data["remote_system_name"].split(".")[0])
            print(" - Device "+interface_a_data["remote_system_name"].split(".")[0]+" not found in Netbox")
        else:
            print("LLDP link: "+sys.argv[1]+" "+interface_a+" <> "+interface_b+" "+interface_a_data["remote_system_name"].split(".")[0])
            if response_device_b is not None:
                print(interface_a_data["remote_system_name"].split(".")[0]+" "+"("+str(response_device_b["id"])+")")
        
        try:
            response_interface_b=nb.dcim.interfaces.get(name=interface_b,device=interface_a_data["remote_system_name"].split(".")[0])
        except pynetbox.core.query.RequestError as e:
            print(e)
        else:
            if response_interface_b is not None:
                print(interface_b+" ("+str(response_interface_b["id"])+")")
                print (nb.dcim.interfaces.get(name=interface_a,device=sys.argv[1])["id"])
                try:
                    response_connection=nb.dcim.cables.create(
                        a_terminations=[
                            {
                                "object_type": "dcim.interface",
                                "object_id": nb.dcim.interfaces.get(name=interface_a,device=sys.argv[1])["id"]
                            }
                        ],
                        b_terminations=[
                            {
                            "object_type": "dcim.interface",
                            "object_id": response_interface_b["id"]
                            }
                        ]
                    )
                except pynetbox.core.query.RequestError as e:
                    print(e)
                else:
                    print ("connection added")

response_interface_ip=device.get_interfaces_ip()
# data=json.loads(response_interface_ip)
for interface in response_interface_ip:
    print(interface)
    print(response_interface_ip[interface]["ipv4"])
    for ipv4 in response_interface_ip[interface]["ipv4"]:
        print(ipv4)
        prefix_length=response_interface_ip[interface]["ipv4"][ipv4]["prefix_length"]
        print(prefix_length)
        interface_id=nb.dcim.interfaces.get(name=interface,device=sys.argv[1])["id"]
        print("interface_id: "+str(interface_id))
        if nb.ipam.ip_addresses.get(address=ipv4)==None:
            try:
                response_ipaddress_netbox=nb.ipam.ip_addresses.create(
                    address=ipv4+"/"+str(prefix_length),
                    assigned_object_id=interface_id,
                    assigned_object_type="dcim.interface"
                    
                )
            except pynetbox.core.query.RequestError as e:
                print(e)
        else:
            print("IP address "+ipv4+" is already in Netbox")

for vrf in device_vrf:
    if vrf=="default":
        continue
    print("VRF: "+vrf)
    try:
        vrf_id=nb.ipam.vrfs.get(name=vrf)
    except pynetbox.core.query.RequestError as e:
                print(e)
    
    if vrf_id!=None:
        print(" Existing VRF ID: "+str(vrf_id["id"]))
    else:
        vrf_id=nb.ipam.vrfs.create(name=vrf)
        print(" New VRF ID: "+str(vrf_id["id"])+" has been created")

device.close()

