"""
Define a class that tracks process times from start to finish with sub-marks

Built during 100DaysofCode.

Coded by: Preocts
    Discord: Preocts#8196
    GitHub: https://github.com/Preocts

Usage Example:

    # Creates a timer
    timer = eggTimer()
    # Some setup code here
    timer.start("Main Process")  # Starts timer (tic)
    for i in iterableList:
        # Do some things


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
        self.tac = None
        self.marks = []
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
        self.tic = time.perf_counter()
        self.desc = desc
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

    def recmark(self, desc):
        """
        Create a mark with description while continuing to run timer

        These are stored in the class instance, so don't use these on heavily
        looped processes unless you are aware they are retained in state. Marks
        are exported to file with .dumpTimes()

        Args:
            desc(str): Description of the mark (used in formatted output)

        Returns:
            (int) diff between 'now' and last mark/start

        Raises:
            eggTimer_Exception
        """
        if self.tic is None:
            raise eggTimer_Exception('Use .start() before adding a mark')
        self.tac = time.perf_counter()
        self.marks.append((desc, self.tac))

        if len(self.marks) == 1:
            return self.marks[-1][1] - self.tic
        return self.marks[-1][1] - self.marks[-2][1]

    def mark(self):
        """
        Returns the diff between 'now' and the prior mark

        Does not store this value in state. Safe for heavy loops or long runs

        Raises:
            eggTimer_Exception
        """
        if self.tic is None:
            raise eggTimer_Exception('Use .start() before asking for a tac')
        nowtac = time.perf_counter()
        oldtac = self.tac
        self.tac = nowtac
        if oldtac is None:
            return self.tac - self.tic
        return nowtac - oldtac

    def dumpTimes(self, filename, mode='w'):
        """
        Dump all stored times and descriptions to a text file

        Args:
            filename(str): path and filename to create text file
            mode(str)(optional): Python's file mode. Default: w

        Raises:
            eggTimer_Exception
        """
        if self.tic is None:
            raise eggTimer_Exception('Use .start() before dumping times')

        try:
            with open(filename, mode) as file:
                file.write(f'Main eggTimer: {self.desc}\n')
                file.write(f'Start: {self.tic}\n')
                if self.toc is not None:
                    file.write(f'Stop : {self.toc}\n')
                    file.write(f'Total: {self.toc - self.tic}\n')
                if len(self.marks):
                    file.write('\n=-=-=-=-=-= Marks =-=-=-=-=\n\n')
                    for desc, tic in self.marks:
                        file.write(f'Mark desc: {desc}\n')
                        file.write(f'     tic: {tic}\n')
        except OSError as err:
            raise eggTimer_Exception(f'eggTimer.dumpTimes(): {err}')
