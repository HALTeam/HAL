from __future__ import print_function
import codecs
from getpass import getuser
from glob import glob
import logging
import sys, os
import io

from HAL import HAL, set_agent

# Windows doesn't have readline, but it's useful on linux,
# as the console doesn't do editing like windows
try:
    import readline
except ImportError:
    pass

logger = logging.getLogger('HAL')


def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    # Using the correct encoding when printing
    sys.stdout = codecs.getwriter('mbcs' if os.name == 'nt' and sys.stdout.isatty() else 'utf-8')(sys.stdout, 'replace')
    set_agent('(PrivateChatSession; http://dev.ivybits.tk/projects/hal/)')

    try:
        sys.argv.remove('-d')
    except ValueError:
        pass
    else:
        from xail import main
        main.DEBUG_MODE = True
        logger.warning('Using debug mode!')

    try:
        dir = sys.argv[1]
    except IndexError:
        dir = '.'
    
    hal = HAL()

    def loadengine(pattern, name):
        engine = getattr(hal.xail, name)
        for file in glob(os.path.join(dir, pattern)):
            logger.info('%s Engine: Loading %s', name, file)
            engine.load(io.open(file, encoding='utf-8'))
    loadengine('*.gen', 'substr')
    loadengine('*.mtx', 'matrix')
    loadengine('*.rgx', 'regex')

    for file in glob(os.path.join(dir, '*.xail')):
        logger.info('Loading %s', file)
        hal.feed(io.open(file, encoding='utf-8'))

    user = getuser()
    prompt = '-%s:' % user
    halpro = '-HAL:'
    length = max(len(prompt), len(halpro))
    prompt.ljust(length)
    halpro.ljust(length)
    prompt += ' '
    context = {'USERNAME': user}
    print(halpro, 'Hello %s. I am HAL %s.'%(user, hal.version))
    print()
    try:
        while True:
            line = raw_input(prompt)
            try:
                print(halpro, hal.answer(line, context))
            except IOError as e:
                if e.errno != 0:
                    raise
                print() # It gets error 0 when some characters can't be displayed
            print()
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        print(halpro, 'Goodbye.')

if __name__ == '__main__':
    main()
