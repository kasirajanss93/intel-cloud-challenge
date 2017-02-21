import command_parser as Parser
from multiprocessing import Process, Queue
from main import get_command_output

def process_command():
    try:
        queue = Queue()
        Parser.get_valid_commands(queue, "commands.txt")
        processes = [Process(target=Parser.process_command_output, args=(queue,))
                     for num in range(2)]
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        print("Process Completed")
    except Exception as detail:
        print('Exception raised' + detail)



if __name__ == '__main__':
    process_command()
    #get_command_output()
