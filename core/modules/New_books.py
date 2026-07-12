from core.entities.AbstractModule import Module


class New_books(Module):
    """
    Module for finding new books on publisher sites.
    Example: You have O'Reilly site with books and want to see new books
    """

    def __init__(self):
        pass

    def post_init(self, app_config) -> None:
        self.config = app_config

    def get_config(self):
        return self.config
