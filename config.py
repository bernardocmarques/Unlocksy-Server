import os
import json

from copy import deepcopy

from utils import Singleton


class CONFIG(metaclass=Singleton):
    # FIXME should be absoulute or something else I guess
    PATH = './config.json'

    default_config = {
        'directories': []
    }

    # default_config = {
    #     'directories': {
    #         'path':{
    #             'hash':'',
    #             'fnek_salt':''
    #         }
    #     },
    # }

    def __init__(self):
        # try to load
        try:
            if os.path.isfile(self.PATH):
                with open(self.PATH, 'r') as f:
                    self.config = json.load(f)
            else:
                with open(self.PATH, 'w') as f:
                    json.dump(self.default_config, f)

                # set default
                self.config = deepcopy(self.default_config)
        except Exception:
            print('File corrupted - Loading default config')
            self.config = deepcopy(self.default_config)

    def _save_config(self):
        with open(self.PATH, 'w') as f:
            json.dump(self.config, f)

    def get_config(self):
        return self.config

    def set_config(self, config):
        self.config = config
        self._save_config()
    def reset(self):
        self.config = deepcopy(self.default_config)
        self._save_config()