""""
Entry point to utility and modules, contains global data from modules
"""

from core.entities.browser.Web_module import Web_interface
from core.modules.Book_analytic import Book_analytic
from core.modules.Kindle_history import Kindle_history
from data.Constants import (
    APP_NAME
)
from data.Wrappers import log


class BootLoader:

    def __init__(self, app_config, logger):
        self.app_config = app_config
        self.local_logger = logger

        self.history_module: Kindle_history = Kindle_history()
        self.analytic_module: Book_analytic = Book_analytic()

    def __init_app_entities(self):
        """
        Init modules with config entity
        :return: None
        """
        self.history_module.post_init(self.app_config)
        self.analytic_module.post_init(self.app_config)
        self.local_logger.log('All entities are inited')

    @log
    def run_app_browser(self):
        """
        Run physical devices in browser
        :return: None`
        """
        self.__init_app_entities()
        try:
            webinterface = Web_interface(logger=self.local_logger,
                                         stat_module=self.analytic_module,
                                         history_module=self.history_module,
                                         transfer_module=self.transfer_module)
            webinterface.run_interface()
        except Exception as e:
            self.local_logger.log(f'Run browser app failed - {e}')
            raise Exception(e)

    @log
    def help_distribution_manager(self):
        print(f'{APP_NAME} utility')
        print('Description:')
        print('You can manage your saved books with help of this utility.')
        print('')
        print('')
        print('')
        print('')

#################################################################################
