# Easy python TCP proxy with customable filter rules

Usage: python3 server.py <LISTEN_PORT> <REAL_PORT> [<SERVICE_NAME>] [<REAL_IP>]

REAL_IP default is 127.0.0.1

Install your application-specific filter in filter.py

create_proxys_services.py is a tool for automatic cloning and setup of various proxy services