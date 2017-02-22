import command_parser as Parser
from multiprocessing import Process, Queue
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base, Command
import time
import os

engine = create_engine('sqlite:///commands_test.db')
session = sessionmaker(bind=engine)()

"""
Function to create db
"""
def make_db():
    Base.metadata.create_all(engine)
    return 'Database creation successful.'


"""
Function to drop db
"""
def drop_db():
    Base.metadata.drop_all(engine)
    return 'Database deletion successful.'

"""
Function to process command
"""
def process_commands(filename):
    try:
        queue = Queue()
        Parser.get_valid_commands(queue, filename)
        processes = [Process(target=Parser.process_command_output, args=(queue,session,))
                     for num in range(2)]
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        print("Process Completed")
    except Exception as detail:
        print('Exception raised' + detail)

"""
Function to run tests against the given full setup
"""
def test_full_setup_sync():
    process_commands("commands.txt")
    time.sleep(1)
    result=session.execute("select count(*) from commands")
    count=result.fetchone()[0]
    if count==6:
        session.execute("delete from commands")
        session.commit()
        return True
    session.execute("delete from commands")
    session.commit()

"""
Function to run tests against the commands that takes more than 60 to run
"""
def test_long_running_command(filename):
    with open(filename,'w') as f:
        f.write('[COMMAND LIST]\n')
        f.write('while true; do echo \'Ctrl c to kill\'; sleep 1; done\n')
        f.write('[VALID COMMANDS]\n')
        f.write('while true; do echo \'Ctrl c to kill\'; sleep 1; done\n')
    process_commands(filename)
    result = session.execute("select count(*) from commands")
    count=result.fetchone()[0]
    if count==1:
        rows=session.execute("select * from commands")
        for row in rows:
            if row[3] == 0:
                os.remove(filename)
                session.execute("delete from commands")
                session.commit()
                return True
    os.remove(filename)
    session.execute("delete from commands")
    session.commit()

"""
Function to run tests against the commands that are not given in the testcase
"""
def test_extra_command(filename):
    with open(filename,'w') as f:
        f.write('[COMMAND LIST]\n')
        f.write('ls -a\n')
        f.write('[VALID COMMANDS]\n')
        f.write('ls\n')
        f.write('ls -a\n')
        f.write('ls -ltr\n')
    process_commands(filename)
    result = session.execute("select count(*) from commands")
    count=result.fetchone()[0]
    #print(count)
    if count==1:
        rows=session.execute("select * from commands")
        for row in rows:
            if "ls -a" in row[1]:
                os.remove(filename)
                session.execute("delete from commands")
                session.commit()
                return True
    os.remove(filename)
    session.execute("delete from commands")
    session.commit()


"""
Function to run tests against the commands that takes more than 60sec to run (cat -) commands without ;
"""
def test_long_command_line(filename):
    with open(filename,'w') as f:
        f.write('[COMMAND LIST]\n')
        f.write('cat -\n')
        f.write('test command\n')
        f.write('[VALID COMMANDS]\n')
        f.write('count=0; while [ $count -le 5 ]; do echo $count; count=$(( $count + 1 )); sleep 1; done\n')
        f.write('cat -\n')
        f.write('ls -a\n')
        f.write('ls -ltr\n')
    process_commands(filename)
    result = session.execute("select count(*) from commands")
    count = result.fetchone()[0]
    if count == 1:
        rows = session.execute("select * from commands")
        for row in rows:
            if row[3] == 0:
                os.remove(filename)
                session.execute("delete from commands")
                session.commit()
                return True
    os.remove(filename)
    session.execute("delete from commands")
    session.commit()


"""
Function to run tests against the commands that takes more than 5sec and less than 60sec to run
"""
def test_not_long_command(filename):
    with open(filename,'w') as f:
        f.write('[COMMAND LIST]\n')
        f.write('count=0; while [ $count -le 5 ]; do echo $count; count=$(( $count + 1 )); sleep 1; done\n')
        f.write('test command\n')
        f.write('[VALID COMMANDS]\n')
        f.write('count=0; while [ $count -le 5 ]; do echo $count; count=$(( $count + 1 )); sleep 1; done\n')
        f.write('ls -a\n')
        f.write('ls -ltr\n')
    process_commands(filename)
    result = session.execute("select count(*) from commands")
    count=result.fetchone()[0]
    #print(count)
    if count==1:
        rows=session.execute("select * from commands")
        for row in rows:
            if row[3]>=5 and row[3] <= 60:
                os.remove(filename)
                session.execute("delete from commands")
                session.commit()
                return True
    os.remove(filename)
    session.execute("delete from commands")
    session.commit()

"""
Main method
"""
if __name__ == '__main__':
    print(make_db())
    try:
        assert test_extra_command('extra_commands.txt'), "Failed Test Case"
        print("Extra Command test case Ran Successfully!!")
    except AssertionError:
        print("Extra Command test case Ran Failed!!")
    try:
        assert test_not_long_command('not_long_commands.txt'), "Failed Test Case"
        print("Not Long Command test case Ran Successfully!!")
    except AssertionError:
        print("Not Long Command test case Ran Failed!!")
    try:
        assert test_long_running_command('long_commands.txt'), "Failed Test Case"
        print("Long Running test case Ran Successfully!!")
    except AssertionError:
        print("Long Running test case Ran Failed!!")
    try:
        assert test_long_command_line('long_commands_line.txt'), "Failed Test Case"
        print("Long Running single line test case Ran Successfully!!")
    except AssertionError:
        print("Long Running single line test case Ran Failed!!")
    try:
        assert test_full_setup_sync(), "Failed Test Case"
        print("Full Setup test case Ran Successfully!!")
    except AssertionError:
        print("Full Setup test case Ran Failed!!")
    print(drop_db())
    os.remove('commands_test.db')
