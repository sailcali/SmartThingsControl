
import json
import urllib.request
import urllib.parse


def get_info(ip):
    """Get the INFO, SENSORS and RUNTIMES data from VENSTAR
    Returns the info in a dict and sensors in a list"""

    # Formulate URL's for INFO and SENSORS
    url1 = 'http://' + ip + '/query/info'
    url2 = 'http://' + ip + '/query/sensors'
    url3 = 'http://' + ip + '/query/runtimes'

    # uinfo and usensors are file-like objects
    uinfo = urllib.request.urlopen(url1)
    usensors = urllib.request.urlopen(url2)
    uruntimes = urllib.request.urlopen(url3)
    jsonStr1 = uinfo.read()
    jsonStr2 = usensors.read()
    jsonStr3 = uruntimes.read()

    # parse json strings to dictionary/list
    info = json.loads(jsonStr1)
    sensors = json.loads(jsonStr2)
    runtimes = json.loads(jsonStr3)
    sensor_list = list(sensors.values())[0]
    runtimes = list(runtimes.values())[0]

    return info, sensor_list, runtimes


def change_state(ip, mode, fan, heat, cool):
    """Changes the status of the VENSTAR thermostat at IP address.
    mode: 1 is heat, 2 is cool, 3 is auto, 0 is off
    fan: 0 is auto 1 is on
    heattemp: deg F
    cooltemp: deg F"""

    url = 'http://' + ip + '/control'

    params = urllib.parse.urlencode({
        'mode': mode,
        'fan': fan,
        'heattemp': heat,
        'cooltemp': cool
    }).encode("utf-8")
    result = urllib.request.urlopen(url, params).read()
    result = json.loads(result)

    if list(result.keys())[0] != 'success':
        print('Error. Could not connect!')

