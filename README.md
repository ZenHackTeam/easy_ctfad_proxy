# Easy python TCP proxy with customable filter rules

Multiconnection simple proxy designed for A/D CTFs. You can apply your own rules on tcp layer.
We also added a tool for automatic cloning and setup of various proxys services, it could be useful at the start of A/D CTF.
Special thanks to [LiveOverflow](https://www.youtube.com/watch?v=iApNzWZG-10&feature=youtu.be).

## Single proxy usage
To create a proxy for a single service running on port LISTEN_PORT you have to move manually this service to another port (aka REAL_PORT). Then call:

```python3 ./proxy_tmp/server.py <LISTEN_PORT> <REAL_PORT> [<SERVICE_NAME>] [<REAL_IP>]```

Default service ip (aka REAL_IP) is 127.0.0.1

This will start a proxy for this service only.

## Create proxys automatically
Edit in your [create_proxys_services.py](https://github.com/ZenHackTeam/easy_ctfad_proxy/blob/master/create_proxys_services.py) file: services array, base_dir and python3_path, then run:
```python3 ./create_proxys_services.py ```
It will create a folder and a completed plisten.service file for each service in the selected base_dir.

Now you have to start all the created services using:
```
systemctl enable /ABSOLUTE/PATH/TO/plisten.service 
systemctl start plisten
```

## Filtering
You can create your own rules adding new functions on [filter.py](https://github.com/ZenHackTeam/easy_ctfad_proxy/blob/master/proxy_tmp/filter.py) and calling them on `input_rule` or `output_rule` function.  
**Restart you proxy to apply the changes**.


