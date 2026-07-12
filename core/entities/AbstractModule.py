import abc


class Module(abc.ABC):
    config = None
    local_logger = None

    @abc.abstractmethod
    def post_init(self, app_config) -> None:
        """
        Post construct method for initializing config file in module
        :return: None
        """
        pass

    @abc.abstractmethod
    def get_config(self):
        pass
