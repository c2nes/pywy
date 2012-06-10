
import urlparse

class FieldSet(object):
    def __init__(self, encoded=None):
        if encoded:
            self.parameters = urlparse.parse_qs(encoded)
        else:
            self.parameters = dict()

    def get(self, key, default=""):
        values = self.parameters.get(key, False)

        if values:
            return values[0]

        return default

    def get_all(self, key):
        return self.parameters.get(key, [])

    def __getitem__(self, key):
        return self.get(key, "")
