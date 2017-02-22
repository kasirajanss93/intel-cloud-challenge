"""
Handles the work of validating and processing command input.
"""
import time
from datetime import datetime
import bashlex
import subprocess
import pandas as pd
from base import Command

def get_valid_commands(queue, fi,session):
    flag = False
    cmd_lists =[]
    cmd_set=set()
    valid = {}
    with open(fi, 'r') as f:
        for line in f:
            if flag is False and "[COMMAND LIST]" not in line:
                if "[VALID COMMANDS]" not in line and line not in cmd_set:
                    cmd_lists.append(line)
                    cmd_set.add(line)
            else:
                valid[line] = True
            if "[VALID COMMANDS]" in line:
                flag = True
    print(cmd_lists)
    for command in cmd_lists:
        if valid.get(command):
            queue.put(command)


def process_command_output(queue,session):
    while True:
        #print("Inside Process Command")
        if queue.empty():
            break
        command = queue.get()
        #print(command)
        command = command.replace('\n', '')
        execute = list(bashlex.split(command))
        if ';' in command:
            p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            test=datetime.now()
            try:
                start_time = datetime.now()
                outs = p.communicate(timeout=60)
                diff = (datetime.now() - start_time).total_seconds()
                outs = outs[0].decode()
                #print(outs)
                value = Command(command.replace("'", "''"), len(command), round(diff,3), bytes(outs.replace("'", "''"), 'utf8'))
                session.add(value)
            except subprocess.TimeoutExpired:
                p.kill()
                outs=p.communicate()
                diff=(datetime.now()-start_time).total_seconds()
                outs=outs[0].decode()
                #print(outs)
                value = Command(command.replace("'", "''"), len(command), 0,bytes(outs.replace("'","''"),'utf8'))
                session.add(value)
        else:
            start_time=datetime.now()
            output = subprocess.check_output(execute)
            diff=(datetime.now()-start_time).total_seconds()
            output=output.decode()
            #print(output)
            value = Command(command.replace("'", "''"),len(command),round(diff,3), bytes(output.replace("'","''"),'utf8'))
            session.add(value)
        session.commit()
