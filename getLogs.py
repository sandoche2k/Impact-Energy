import json
import time
import math
import shutil
import subprocess
import clickhouse_connect
import numpy 
from datetime import datetime

#global variables
timestamp = str(math.floor(time.time()))
logFile = '/var/log/dnsdist/dnsdist.log'
oldLogFile = '/var/log/dnsdist/dnsdist.log.'+ timestamp
tempFile = '/var/log/dnsdist/temp.txt'
cleanedlogFile = '/var/log/dnsdist/dnsdist.log.cleaned'+ timestamp
client = clickhouse_connect.get_client(host='localhost', username='default', password='victorberhault')

#read file
def readFile(filename):
    with open(filename, 'r') as f:
        content = f.read()
    return content

#write to file
def writeFile(filename, content):
    with open(filename, 'w') as f:
        f.write(content)

#json to file
def jsonToFile(filename, content):
    with open(filename, 'w') as f:
        json.dump(content, f)
    
#extract logs from file
def extractLogs(filename):
    logs = []
    content = readFile(filename)
    lines = content.replace('[','').replace(']','').split('\n')
    for line in lines:
        if(line == ''): continue
        lineSplit = line.split(' ')
        timesplit = lineSplit[0].split('.')
        time = datetime.fromtimestamp(int(timesplit[0]))
        logs.append([time, lineSplit[5], lineSplit[6]])
    return logs

def getPid():
    return (subprocess.check_output(['pidof', 'dnsdist']).decode('utf-8').split('\n')[0], subprocess.check_output(['pidof', 'unbound']).decode('utf-8').split('\n')[0])

def getUpTime():
    timesplit = subprocess.check_output(['cat', '/proc/uptime']).decode('utf-8').split(' ')[0].split('.')
    return (int(timesplit[0]))


def getStat(pids):
    res = []
    systime = getUpTime()
    tickrate = getClockTick()
    stats = subprocess.check_output(['cat', '/proc/'+pids[0]+'/stat']).decode('utf-8').split(' ')
    res.append([datetime.now(),int((int(stats[12].split('.')[0])/tickrate)), int((int(stats[13].split('.')[0])/tickrate)), int((int(stats[21].split('.')[0])/tickrate)),systime, 'dnsdist'])
    stats = subprocess.check_output(['cat', '/proc/'+pids[1]+'/stat']).decode('utf-8').split(' ')
    res.append([datetime.now(),int((int(stats[12].split('.')[0])/tickrate)), int((int(stats[13].split('.')[0])/tickrate)), int((int(stats[21].split('.')[0])/tickrate)),systime, 'unbound'])
    return res

def getClockTick():
    return int(subprocess.check_output(['getconf', 'CLK_TCK']).decode('utf-8').split('\n')[0])

#main function
shutil.copyfile(logFile, oldLogFile)
writeFile(logFile, '')
logs = extractLogs(oldLogFile)
stats = getStat(getPid())
#jsonToFile(cleanedlogFile, json.dumps((logs,stats)))

#insert into clickhouse
#print(logs, stats)
client.insert('dnsstats.requests',logs, column_names=['timestamp', 'website', 'RRtype'])
client.insert('dnsstats.cpustats',stats, column_names=['timestamp', 'utime', 'stime', 'starttime','systemuptime', 'process'])

#/proc/pid/stat => 14 + 15 (en clock tick => diviser par getconf CLK_TCK pour avoir en secondes)
#a comparer avec /proc/upime temps en secondes depuis le boot - stat 22 start time du process


