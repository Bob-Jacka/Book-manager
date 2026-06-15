from core.exceptions.WebException import WebException


class Web_interface:
    """
    Class responsible for web interface of the utility
    """

    def __init__(self, logger, stat_module, history_module):
        self.logger = logger
        self.stat = stat_module
        self.history_book = history_module

    def run_interface(self):
        """
        Entry point to web interface.
        Open browser and create all components in it
        :return: None
        """
        from core.entities.browser.WebInterface import Flask_interface
        try:
            self.logger.log('Server starting work')
            Flask_interface.Dp.history_mod = self.history_book
            Flask_interface.Dp.stat_mod = self.stat
            Flask_interface.Dp.local_logger = self.logger
            Flask_interface.Dp.config = self.history_book.get_config()
            Flask_interface.run_web_app()
            self.logger.log('Server ending work')
        except Exception as e:
            raise WebException(f'Exception occurred while running web interface {e}')
