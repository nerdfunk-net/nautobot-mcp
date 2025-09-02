# To Onboard a device to nautobot use the following properties:

- use POST as method
- use the URL "{{ nautobot_hostname }}/api/extras/jobs/Sync%20Devices%20From%20Network/run/"
- the header must contain

* Content-Type: application/json
* Authorization: "Token nautobot_api_token"

- add "body_format: json" to the request
- ask the user to enter the following data:
  1. ip_address
  2. location
  3. secret_groups
  4. role
  5. namespace
  6. status
  7. platform
- the body must contain a dict called 'data' that contains the following properties:

  "location": location,
  'ip_addresses': ip_address,
  "secrets_group": secret_groups,
  "device_role": role,
  "namespace": namespace,
  "device_status": status,
  "interface_status": status,
  "ip_address_status": status,
  "platform": platform,
  "port": 22,
  "timeout": 30,
  "update_devices_without_primary_ip": false

# To sync the device with the network data use the following properties:

- use POST as method
- use the URL "{{ nautobot_hostname }}/api/extras/jobs/Sync%20Network%20Data%20From%20Network/run/"
- the header must contain

* Content-Type: application/json
* Authorization: "Token nautobot_api_token"

- add "body_format: json" to the request
- ask the user to enter the following data:
  1. prefix status (selection)
  2. interface status (selection)
  3. IP address status (selection)
  4. namespace (selection)
  5. Sync Cables (parameter is named sync_cables) as checkbox
  6. Sync Software (parameter is sync_software_version) as checkbox
  7. Sync VLANs (parameter is named sync_vlans) as checkbox
  8. Sync VRFs (parameter is named sync_vrfs) as checkbox
- the body must contain a dict called 'data' that contains the following properties:

       "devices": [ device_id ], # list
       "default_prefix_status": status_id, # string
       "interface_status": status_id, # string
       "ip_address_status": status_id, # string
       "namespace": namespace_id, # string
       "sync_cables": sync_cables, #bool
       "sync_software_version": sync_software_version, # bool
       "sync_vlans": sync_vlans, # bool
       "sync_vrfs": sync_vrfs # bool
