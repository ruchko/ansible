#!/usr/bin/python3
import json

"""
    Tasks:
        1. Get the 'tenant_id and 'tenant_type' from 'data', store each in a variable and print
        2. Add an extra value to 'tenant_type' in 'data' using code
        3. Get the unique values from 'sites', store in a var and print
"""
 
data = [
    {
        "prefix": "192.168.1.1/32",
        "role": {"name": "Counter Party"},
        "site": "NY",
        "tenant": {
            "custom_field_data": '{"tenant_id": "1000", "tenant_type": ["Counter Party"]}'
        },
        "name": "client1",
    }
]
 
sites = ["NY", "NY", "NY", "CH", "CH", "MAH", "LON", "CA", "CA"]





a=data[0]
b=a["tenant"]["custom_field_data"]
c=json.loads(b)
#print(c["tenant_id"])
#print(c["tenant_type"][0])
c["tenant_type"].append("extra value")
a["tenant"]["custom_field_data"]=c
#print(a)
data[0]=a
print(data)


#print(a["tenant"]["custom_field_data"]["tenant_type"])

u_list=[]
for item in sites:
#  print(item)
  if item not in u_list:
    u_list.append(item)

print("-"*20)

for i2 in u_list:
  print(i2)

print("v2:")
u_sites2=set(sites)
print(u_sites2)
