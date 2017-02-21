"""
Handles the work of validating and processing command input.
"""
import time
import bashlex
import subprocess
from db import session, engine
from threading import Timer

def get_valid_commands(queue, fi):
    # TODO: efficiently evaluate commands
    flag = False
    cmd_lists = []
    valid = {}
    with open(fi, 'r') as f:
        for line in f:
            if flag is False and "[COMMAND LIST]" not in line:
                if "[VALID COMMANDS]" not in line:
                    cmd_lists.append(line)
            else:
                valid[line] = True
            if "[VALID COMMANDS]" in line:
                flag = True
    for command in cmd_lists:
        if valid.get(command):
            queue.put(command)


def process_command_output(queue):
    while True:
        print("Inside Process Command")
        if queue.empty():
            break
        command = queue.get()
        print(command)
        command = command.replace('\n', '')
        execute = list(bashlex.split(command))
        if ';' in command:
            p = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE)
            try:
                outs=p.communicate(timeout=5)
                outs=outs[0].decode()
                print(outs)
                session.execute(
                    "insert into {0} (command_string,length,duration,output) VALUES ('{1}',{2},{3},'{4}')".format(
                        "commands", command.replace("'", "''"),
                        len(command), 0, (outs.replace("'", "''"))))
            except subprocess.TimeoutExpired:
                #print("Time: " + str((time.clock() - start)))
                p.kill()
                outs=p.communicate()
                outs=outs[0].decode()
                print(outs)
                session.execute(
                    "insert into {0} (command_string,length,duration,output) VALUES ('{1}',{2},{3},'{4}')".format(
                        "commands", command.replace("'","''"),
                        len(command), 0,outs.replace("'","''")))
        else:
            output = subprocess.check_output(execute)
            output=output.decode()
            print(output)
            session.execute(
                "insert into {0} (command_string,length,duration,output) VALUES ('{1}',{2},{3},'{4}')".format(
                    "commands", command.replace("'","''"),
                    len(command), 0, (output.replace("'","''"))))
        session.commit()
