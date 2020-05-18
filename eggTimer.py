"""
Define a class that tracks process times from start to finish with sub-marks

Built during 100DaysofCode.

Coded by: Preocts
    Discord: Preocts#8196
    GitHub: https://github.com/Preocts
"""
import time


class eggTimer_Exception(Exception):
    """ Custom Raise Class """
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'eggTimer_Exception, {self.message}'
        else:
            return 'eggTimer_Exception, an error has been raised'


class eggTimer():
    """
    Raises:
        eggTimer_Exception
    """
    def __init__(self, desc=None):
        """
        Init a timer.

        Args:
            desc(str)(optional): Immediately starts a timer
        """
        self.desc = None
        self.tic = None
        self.toc = None
        self.marks = {}
        if desc is not None:
            self.start(desc)
        return

    def __bool__(self):
        """ Check if self is running or not """
        if self.desc is None:
            return False
        return True

    def __int__(self):
        """ Return current perf_counter() if running """
        if self.desc is None:
            return 0
        return time.perf_counter()

    def __str__(self):
        """ Return current description """
        return self.desc

    def start(self, desc):
        """
        Start a timer labeled by a given  name

        Args:
            desc(str): Description of timer (used in formatted output)

        Raises:
            eggTimer_Exception
        """
        if self.desc is not None:
            raise eggTimer_Exception('eggTimer can only be started once')
        self.desc = desc
        self.tic = time.perf_counter()
        return

    def stop(self):
        """
        Stops and finalizes timer

        Raises:
            eggTimer_Exception
        """
        if self.tic is None:
            raise eggTimer_Exception('Use .start() before stopping a timer')
        self.toc = time.perf_counter()
        return

    def mark(self, desc):
        """
        Create a mark with description while continuing to run timer

        Args:
            desc(str): Description of the mark (used in formatted output)

        Raises:
            eggTimer_Exception
        """
        if self.tic is None:
            raise eggTimer_Exception('Use .start() before adding a mark')
        # Auto incriment postfix if desc has been used
        if desc in self.marks.keys():
            n = 0
            while desc + str(n) in self.marks.keys():
                n += 1
            desc = desc + str(n)
        self.marks[desc] = time.perf_counter()
        return
