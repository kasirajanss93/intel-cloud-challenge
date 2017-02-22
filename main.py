"""
Details the various flask endpoints for processing and retrieving
command details as well as a swagger spec endpoint
"""

from multiprocessing import Process, Queue
import sys
from flask import Flask, request, jsonify
from flask_swagger import swagger
import json
from db import session, engine
from base import Base, Command
from command_parser import get_valid_commands, process_command_output

app = Flask(__name__)
#app.config['APPLICATION_ROOT'] = '/Users/kasi-mac/KasiThings/ASU/projects/intel/cloud_code_challenge'


@app.route('/commands', methods=['GET'])
def get_command_output():
    """
    Returns as json the command details that have been processed
    ---
    tags: [commands]
    responses:
      200:
        description: Commands returned OK
      400:
        description: Commands not found
    """
    commands = session.query(Command)
    result=session.execute(commands)
    json_data=[]
    for r in result:
        json_data.append({
            'id' : r[0],
            'command_string' : r[1],
            'length' : r[2],
            'duration' : r[3],
            'output' : r[4].decode()
        })
    json_data = json.dumps(json_data)
    return jsonify(json.loads(json_data))


@app.route('/commands/<int:command_id>', methods=['GET'])
def get_command_id(command_id):
    """
    Returns as json the command details that have been processed
    ---
    tags: [commands]
    responses:
      200:
        description: Commands returned OK
      400:
        description: Commands not found
    """
    commands = session.query(Command)
    commands=(str(commands))
    commands+=" where commands.id={0}".format(command_id)
    result = session.execute(commands)
    json_data = []
    for r in result:
        json_data.append({
            'id': r[0],
            'command_string': r[1],
            'length': r[2],
            'duration': r[3],
            'output': r[4].decode()
        })
    json_data = json.dumps(json_data)
    return jsonify(json.loads(json_data))
    # json_data=json.dumps([dict(r) for r in result])


@app.route('/commands', methods=['POST'])
def process_commands():
    """
    Processes commmands from a command list
    ---
    tags: [commands]
    parameters:
      - name: filename
        in: formData
        description: filename of the commands text file to parse
        required: true
        type: string
    responses:
      200:
        description: Processing OK
    """
    fi = request.args.get('filename')
    print(fi)
    queue = Queue()
    get_valid_commands(queue, fi,session)
    processes = [Process(target=process_command_output, args=(queue,session,))
                 for num in range(2)]
    for process in processes:
        process.start()
    #for process in processes:
    #    process.join()
    return 'Successfully processed commands.'


@app.route('/database', methods=['POST'])
def make_db():
    """
    Creates database schema
    ---
    tags: [db]
    responses:
      200:
        description: DB Creation OK
    """
    Base.metadata.create_all(engine)
    return 'Database creation successful.'


@app.route('/database', methods=['DELETE'])
def drop_db():
    """
    Drops all db tables
    ---
    tags: [db]
    responses:
      200:
        description: DB table drop OK
    """
    Base.metadata.drop_all(engine)
    return 'Database deletion successful.'


if __name__ == '__main__':
    """
    Starts up the flask server
    """
    port = 8080
    use_reloader = True

    # provides some configurable options
    for arg in sys.argv[1:]:
        if '--port' in arg:
            port = int(arg.split('=')[1])
        elif '--use_reloader' in arg:
            use_reloader = arg.split('=')[1] == 'true'

    app.run(port=port, debug=True, use_reloader=use_reloader)


@app.route('/spec')
def swagger_spec():
    """
    Display the swagger formatted JSON API specification.
    ---
    tags: [docs]
    responses:
      200:
        description: OK status
    """
    spec = swagger(app)
    spec['info']['title'] = "Nervana cloud challenge API"
    spec['info']['description'] = ("Nervana's cloud challenge " +
                                   "for interns and full-time hires")
    spec['info']['license'] = {
        "name": "Nervana Proprietary License",
        "url": "http://www.nervanasys.com",
    }
    spec['info']['contact'] = {
        "name": "Nervana Systems",
        "url": "http://www.nervanasys.com",
        "email": "info@nervanasys.com",
    }
    spec['schemes'] = ['http']
    spec['tags'] = [
        {"name": "db", "description": "database actions (create, delete)"},
        {"name": "commands", "description": "process and retrieve commands"}
    ]
    return jsonify(spec)
