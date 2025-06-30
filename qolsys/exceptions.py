#MIT License
#
#Copyright (c) 2021 Raphaël Beamonte <raphael.beamonte@gmail.com>

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from datetime import datetime, timezone

class QolsysException(Exception):
    STATE = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._at = datetime.now(timezone.utc).isoformat()

        if self.STATE:
            self.STATE.last_exception = self

    @property
    def at(self):
        return self._at


class QolsysGwConfigIncomplete(QolsysException):
    pass


class QolsysGwConfigError(QolsysException):
    pass


class UnableToParseEventException(QolsysException):
    pass


class UnableToParseSensorException(QolsysException):
    pass


class UnknownQolsysControlException(QolsysException):
    pass


class UnknownQolsysEventException(QolsysException):
    pass

class UnknownQolsysSensorException(QolsysException):
    pass


class MissingUserCodeException(QolsysException):
    pass


class InvalidUserCodeException(QolsysException):
    pass
