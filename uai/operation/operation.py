
class Operation(object):

    def __init__(self, parser):
        self.parser = parser
        self._add_args(self.parser)
        pass

    def _add_args(self, parser):
        pass
        #add other params in subclasses#

    def _parse_args(self):
        pass
        # add other params in subclasses#

    def cmd_run(self, params):
        self.params = params
        self._parse_args()
        pass
        # add other params in subclasses#