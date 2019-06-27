import argparse
import argparse
import json
import requests
import socket
import time
import yaml

PROMETHEUS_SERVER_TIMEOUT = 3
PROMETHEUS_SERVER_RETRY = 3
PROMETHEUS_SERVER_DELAY = 5

def is_open (hostname, port):

    try:
        s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout (PROMETHEUS_SERVER_TIMEOUT)
    except socket.error as err:
        print ("Failed with error %s" % (err))

    try:
        s.connect ((hostname, int (port)))
        s.shutdown (socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close ()

def reachability_test (hostname, port):
    up = False
    for i in range (PROMETHEUS_SERVER_RETRY):
        if (is_open (hostname, port)):
            up = True
            break
        else:
            time.sleep (PROMETHEUS_SERVER_DELAY)
    return up

def target_get (hostname, port):
    if (port == -1):
        target = hostname
    else:
        target = hostname + ":" + str (port)

    return target

def time_range_query (hostname, port, query_string, start_time, end_time, step, timeout):
        target = target_get (hostname, port)
        url = "http://" + target + "/api/v1/query_range?query=" + query_string + \
            "&start=" + str (start_time) + "&end=" + str(end_time) + "&step=" + str (step)
        headers = {"Content-Type" : "application/x-www-form-urlencoded"}

        r = requests.post (url, headers = headers, verify = False, timeout = timeout)

        result = json.loads (r.content)

        return result
       
def time_range_values (hostname, port, query_string, start_time, end_time, step, timeout = 60, top = True):

    result = time_range_query (hostname, port, query_string, start_time, end_time, step, timeout)
    
    if result ["status"] == "success":
        data = result ["data"]
        if top == True:
            top_value = 0
        
        # handle matrix data return
        if (data ["resultType"] == "matrix"):
            metric_values_list = data ["result"]
            for metric_values in metric_values_list:
                values = metric_values ["values"]

                if top == True:
                    for value in values:
                        value_to_compare = float (value [1])
                        if (value_to_compare > top_value):
                            top_value = value_to_compare
                    return top_value
                else:
                    return values
        else:
            return None
    else:
        return None

            
def main ():
    parser = argparse.ArgumentParser (description="Prometheus Server class functional test")
    parser.add_argument ('--hostname', help = "Prometheus hostname")
    parser.add_argument ('--port', help = "Prometheus port")
    args = parser.parse_args ()

    result = time_series_query ("up", "2019-05-01T20:10:51.781Z", "2019-05-02T20:10:51.781Z", "1h", 120)
    print (result)

# Test function
if __name__ == "__main__":
     main ()
