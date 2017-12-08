class CmdOutput(object):

    def __init__(self, text):
        self._text = text

    def __repr__(self):
        if self._text:
            return self._text
        return ''