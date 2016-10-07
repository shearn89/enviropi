import rrdtool
import json

from flask import Flask, render_template

app = Flask(__name__)

dataFile = "environment.rrd"
FACTOR = 1.3

def get_data():
    jsonData = rrdtool.xport("--start",
        "now-4h",
        "--end",
        "now",
        "--step",
        "300",
        "DEF:a="+dataFile+":cpuTemp:AVERAGE",
        "DEF:b="+dataFile+":boardTemp:AVERAGE",
        "DEF:c="+dataFile+":calibTemp:AVERAGE",
        "DEF:d="+dataFile+":atm:AVERAGE",
        "DEF:e="+dataFile+":light:AVERAGE",
        'XPORT:a:"CPU Temp"',
        'XPORT:b:"Board Temp"',
        'XPORT:c:"Estimated Temp"',
        'XPORT:d:"Atmospheric Pressure"',
        'XPORT:e:"Light"')
    return jsonData

def get_series(data):
    rows = map(list, zip(*data['data']))
    return zip(data['meta']['legend'], rows)

@app.route('/')
@app.route('/index')
def index():
    jsonData = get_data()
    data = get_series(jsonData)
    startTime = jsonData['meta']['start']
    endTime = jsonData['meta']['end']
    step = jsonData['meta']['step']
    ticks = ((endTime - startTime)/step)

    timestamps = [ x*1000 for x in range(startTime, endTime, step)]

    chart = {'renderTo': 'temperatures', 'type': 'line', 'zoomType': 'x'}
    title = {'text': 'EnviroPi'}

    series = []
    for (name, d) in data:
        tdata = zip(timestamps, d)
        if 'Temp' in name:
            series.append({'name': name, 'data': tdata, 'yAxis': 0})
        elif 'Pres' in name:
            continue
            # series.append({'name': name, 'data': tdata, 'yAxis': 1})
        elif 'Light' in name:
            continue
            # series.append({'name': name, 'data': tdata, 'yAxis': 2})
        else:
            series.append({'name': name, 'data': tdata})

    xAxis = {'type': 'datetime',
            'dateTimeLabelFormats':{
                'second': '%H:%M:%S',
                'minute': '%H:%M',
                'hour': '%H:%M',
                'day': '%e. %b',
                'week': '%e. %b',
                'month': '%b \'%y',
                'year': '%Y' },
            'tickInterval': 1000 * step}

    yAxis = [{'title': {'text': 'Temperature'}}]
            # {'title': {'text': 'Pressure'}, 'opposite': 'true'},
            # {'title': {'text': 'Light'}, 'opposite': 'true'}]

    return render_template('index.html',
        chartID='temperatures',
        chart=chart,
        series=json.dumps(series),
        title=title,
        xAxis=xAxis,
        yAxis=yAxis)

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=8080, passthrough_errors=True)
