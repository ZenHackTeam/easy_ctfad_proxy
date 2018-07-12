import re

# Application-specific proxy rules:
# If the function returns True, the packet will be sent, else it will be blocked
# If the function returns another object, will be sent in place of the original one
# Filter can save connection-persistent data in client (or server) filter_data dictionary


# An example filter based on the input packet length
def example_buffer_overflow_filter(client, data):
    return len(data) < 256


# A second example of a filter for blocking buffer overflow attempts
def example_sum_buffer_overflow_filter(client, data):

    if 'bof_sum' not in client.filter_data:
        client.filter_data['bof_sum'] = 0

    client.filter_data['bof_sum'] += len(data)

    return client.filter_data['bof_sum'] < 128


# An example filter for basic sql injection
def basic_web_filter(client, data):
    str_packet = str(data, 'UTF-8', errors='ignore')

    exps = []
    exps.append(r"('|\"|%27|%22)(\s|%20|\+)*(OR|AND|UNION|LIMIT)")  # Where concatenations
    exps.append(r"(;|%3B)\s*(SELECT|UPDATE|DELETE|INSERT|CREATE|ALTER|DROP|IF)")  # Stacked queries
    exps.append(r"(\s|%20|\+)+--(\s|%20|\+)+")  # Any sql comment

    for exp in exps:
        if re.search(exp, str_packet, re.IGNORECASE) is not None:
            print("Blocked sqli attempt: ")
            print(str_packet)
            return False

    return True


# Example filter for disabling http compression client-side
def disable_http_compression(client, data):
    compression_regex = r'Accept-Encoding: ([a-zA-Z]|,| )+\r\n'

    str_packet = str(data, 'UTF-8', errors='ignore')

    if re.search(compression_regex, str_packet, re.IGNORECASE) is not None:
        str_packet = re.sub(compression_regex, "Accept-Encoding: identity\r\n", str_packet, 0, re.IGNORECASE)
        return str_packet.encode('utf-8')

    return True


def input_rule(client, data):
    return True


def output_rule(server, data):
    return True