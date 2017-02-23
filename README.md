# Nervana Cloud Coding Challenge Submission#

#Steps to Run

1. clone the repository from git

2. inside the cloned folder, execute the command make run

3. This will start the server

#Operations that can be performed

1. The database can be created and dropped using the database resource

	- Resource - /database
	- Operation - POST
	- Action - Creates the database
	- Operation - DELETE
	- Action - Delete the databse

2. Command resource is used to process commands and view the results of the executed command

	- Resource - /commands
	- Operation - GET
	- Action - Outputs the list of commands that has been executed to the user
	- Operation - POST
	- Action - post the data with the filename to the server and the server executes the command and stores the result in the database

	- Resource - /commands/<id> -> added by me
	- Operation - GET
	- Action - Outputs the details of the individual command


#Outline of the Implemnetaion

	- On POST request the name of the file is obtained from the user, the command_parser.py has method get_valid_commands to get unique list of commands and add it to the queue.
	- The process_command_output method gets the values that are stored in the queue and process the result one by one. The execution of the command is run in a thread thus processing commands in a concurrent manner
	- Once the POST method is hit, the execution happends in the thread that is running in the background hence it process the request asynchronously

#Test Cases
	- The test cases are found in the test.py file
	- The following testcase are written
		- Testcase to check if commands other than the one's given in the file are executed
		- Testcase to check if the commands that takes longer time but less than a minute is executed correctly
		- Testcase to check if the commands that are beyond a minute are executed successfully
		- Testcase to check if the commands that are beyond a minute and are executed with ; in between are executed successfully
		- Testcase to check if all the commands in the given commands.txt is executed successfully

#Bonus Implementation

	- File that are bigger than memory - Since I read the file line by line, the number of bytes stoed in the memory will be very low and this problem won't occur
	- Asynchronous command execution - In the Flask's POST method, I am not waiting for all the child threads to complete before returning the output message. In which case the thread will run in the backgroud and complete the task. Therefore, doing a GET request will return the commands that has been process at the point in time
	- Use file_data or filename - Provision has been done in the code to accept file data, the contents of which be in stored to a file and that is processed. The sample input for file data is below:

	[COMMAND LIST]\nls\npwd\necho "hello there"\n[VALID COMMANDS]\nls\necho "hello there"\npwd
	- Added a GET request 127.0.0.1:8080/commands/<id> to view metadata of the individual command 

#Sample Output

	- Used postman to execute the following endpoints
	
	- GET 127.0.0.1:8080/commands
		- [
  			{
    			"command_string": "ls",
    			"duration": 0.013,
    			"id": 1,
    			"length": 2,
    			"output": "Makefile\nREADME.md\n__pycache__\nbase.py\ncommand_parser.py\ncommands.db\ncommands.txt\ncommands_data.txt\ndb.py\nmain.py\nrequirements.txt\ntest.py\n"
  			},
  			{
    			"command_string": "pwd",
    			"duration": 0.009,
    			"id": 2,
    			"length": 3,
    			"output": "/Users/kasi-mac/KasiThings/ASU/projects/intel/cloud_code_challenge\n"
  			}
  		  ]

  	- GET 127.0.0.1:8080/commands/2
  		- 	[
  			{
    			"command_string": "pwd",
    			"duration": 0.009,
    			"id": 2,
    			"length": 3,
    			"output": "/Users/kasi-mac/KasiThings/ASU/projects/intel/cloud_code_challenge\n"
  			}
  		  ]  

  	- POST 127.0.0.1:8080/commands?filename=commands.txt
  		- Successfully processed commands.

  	- POST 127.0.0.1:8080/commands?file_data=[COMMAND LIST]\nls\npwd\necho "hello there"\n[VALID COMMANDS]\nls\necho "hello there"\npwd
  		-Successfully processed commands.

