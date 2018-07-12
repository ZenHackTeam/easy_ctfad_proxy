#!/bin/env python3

import os
import shutil

base_dir = '/usr/bin/proxy' # Senza slash finale
dir_tmp = 'plisten'
template_service = 'plisten.service'
python3_path = '/usr/bin/python3'

services = [
    {'port': 80, 'forward_port': 81, 'service_name': 'doodle'},
    {'port': 4242, 'forward_port': 14242, 'service_name': 'toaster'},
    {'port': 8000, 'forward_port': 18000, 'service_name': 'alexa'}
]

if not os.path.exists(base_dir):
    os.makedirs(base_dir)

i = 1

for service in services:
    dir = base_dir + '/' + dir_tmp + str(i)

    print("Creating directory: " + dir)

    if os.path.exists(dir):
        shutil.rmtree(dir)

    shutil.copytree('proxy_tmp', dir)

    with open(template_service) as f:
        service_content = f.read()

    service_content = service_content.replace('{{=PROXY_DIR}}', dir)
    service_content = service_content.replace('{{=PYTHON3_PATH}}', python3_path)
    service_content = service_content.replace('{{=SERVICE_NAME}}', service['service_name'])
    service_content = service_content.replace('{{=LISTEN_PORT}}', str(service['port']))
    service_content = service_content.replace('{{=FORWARD_PORT}}', str(service['forward_port']))

    service_file = open(dir + '/plisten' + str(i) + '.service', "w")
    service_file.write(service_content)
    service_file.close()

    i += 1
