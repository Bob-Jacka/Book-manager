from multiprocessing import Process


class LW_process:
    """
    Process lightweight abstraction
    """
    __process_name: str
    __pid: int
    __process: Process

    def __init__(self, name: str, target):
        self.__process_name = name
        self.__process = Process(target=target)
        self.__pid = self.__process.pid

    def get_pid(self):
        return self.__pid

    def get_process_name(self):
        return self.__process_name

    def still_alive(self):
        return self.__process.is_alive()

    def close_process(self):
        """
        End process
        :return: None
        """
        print(f'Process with name {self.__process_name} is finished')
        self.__process.close()

    def start_proc(self):
        print(f'{self.__process_name} started')
        self.__process.start()

    def swap_proc(self, process):
        """
        Replace process with another
        :param process: process to replace with
        :return: None
        """
        self.__process = process
