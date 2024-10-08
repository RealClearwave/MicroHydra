"""
MicroHydra SHELL & Terminal
Version: 1.0

A simple Terminal that can run console-based Apps.
Have fun!

TODO:
KFC V me 50
"""

from lib.display import Display
from lib.userinput import UserInput
from lib.hydra.config import Config
import machine, time, os

machine.freq(240_000_000)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CONSTANTS: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
_MH_DISPLAY_HEIGHT = const(240)
_MH_DISPLAY_WIDTH = const(320)
_DISPLAY_WIDTH_HALF = const(_MH_DISPLAY_WIDTH // 2)

_CHAR_WIDTH = const(8)
_CHAR_WIDTH_HALF = const(_CHAR_WIDTH // 2)
_MAX_CHARS = const(_MH_DISPLAY_WIDTH // _CHAR_WIDTH)

_LINE_HEIGHT = const(10)
_LINE_COUNT = const(_MH_DISPLAY_HEIGHT // _LINE_HEIGHT)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GLOBAL OBJECTS: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# init object for accessing display
tft = Display()

# object for accessing microhydra config (Delete if unneeded)
config = Config()

# object for reading keypresses
kb = UserInput()

#screen buffer
scr_buf = [""]*_LINE_COUNT

RTC = machine.RTC()

#--------------------------------------------------------------------------------------------------
#-------------------------------------- FUNCTION DEFINITIONS: -------------------------------------
#--------------------------------------------------------------------------------------------------

def scr_feed(string):
    for i in range(1, _LINE_COUNT):
        scr_buf[i-1] = scr_buf[i]
    scr_buf[-1] = string
    
def scr_show():
    # clear framebuffer 
    tft.fill(config['bg_color'])
    # write current text to framebuffer
    for i in range(_LINE_COUNT):
        tft.text(text=scr_buf[i], x=0, y=_LINE_HEIGHT*i,color=config['ui_color'])
    # write framebuffer to display
    tft.show()

def scr_clear():
    for i in range(_LINE_COUNT):
        scr_buf[i] = ""
    scr_show()

# Custom print function that writes to the buffer
def custom_print(*args, **kwargs):
    str_out = (' '.join(map(str, args)) + kwargs.get('end', '')).split('\n')
    for i in str_out:
        while len(i)>_MAX_CHARS:
            scr_feed(i[:_MAX_CHARS])
            scr_show()
            i = i[_MAX_CHARS:]
        
        scr_feed(i)
        scr_show()


# Replace the built-in print function with the custom one
print = custom_print

def custom_input(prmpt):
    print(f"{prmpt} _")
    
    current_text = []
    while True:
        keys = kb.get_new_keys()
        # if there are keys, convert them to a string, and store for display
        if keys:
            if 'SPC' in keys:
                current_text.append(' ')
            elif 'BSPC' in keys:
                current_text = current_text[:-1]
            else:
                current_text += [i for i in keys if i != 'ENT']
            
            scr_buf[-1] = f"{prmpt} " + ''.join(current_text) + "_"
            scr_show()
            
            if 'ENT' in keys or 'GO' in keys:
                scr_buf[-1] = scr_buf[-1][:-1]
                scr_show()
                line = ''.join(current_text)
                return line

input = custom_input
#--------------------------------------------------------------------------------------------------
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main Loop: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main_loop():
    """
    The main loop of the program. Runs forever (until program is closed).
    """
    
    app_path = RTC.memory().decode()
    if len(app_path) > 0 and app_path[0] == '$':
        #print(app_path[1:])
        exec(open(app_path[1:]).read(), {'__name__': '__main__'},globals())
    else:
        print(f"MicroHydra v{os.uname().release}) on {os.uname().sysname}, Terminal Ver 1.0.")
        print("Press GO Button to Exit.")
    
    print(f"root@MH:{os.getcwd()}# _")
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ INITIALIZATION: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # If you need to do any initial work before starting the loop, this is a decent place to do that.
    
    # create variable to remember text between loops
    current_text = []
    
    
    while True: # Fill this loop with your program logic! (delete old code you dont need)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ INPUT: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        # put user input logic here
        
        # get list of newly pressed keys
        keys = kb.get_new_keys()
        
        # if there are keys, convert them to a string, and store for display
        if keys:
            if 'GO' in keys:
                machine.reset()
            if 'SPC' in keys:
                current_text.append(' ')
            elif 'BSPC' in keys:
                current_text = current_text[:-1]
            else:
                current_text += [i for i in keys if len(i) == 1]
            
            scr_buf[-1] = f"root@MH:{os.getcwd()}# " + ''.join(current_text) + "_"
            scr_show()
            
            if 'ENT' in keys:
                scr_buf[-1] = scr_buf[-1][:-1]
                try:
                    args = (''.join(current_text)).split()
                    if args:
                        if args[0] == 'ls':
                            print('  '.join(os.listdir() if len(args) == 1 else os.listdir(args[1])))
                                
                        elif args[0] == 'cat':
                            with open(args[1], 'r') as f:
                                print(f.read())
                        elif args[0] == 'cd' or args[0] == 'chdir':
                            os.chdir(args[1])
                        elif args[0] == 'rm':
                            for i in args[1:]:
                                os.remove(i)
                        elif args[0] == 'touch':
                            for i in args[1:]:
                                with open(i, 'w') as f:
                                    f.write(i)
                        elif args[0] == 'mv':
                            os.rename(args[1],args[2])
                        elif args[0] == 'cwd':
                            print(os.getcwd())
                        elif args[0] == 'mkdir':
                            for i in args[1:]:
                                os.mkdir(i)
                        elif args[0] == 'rmdir':
                            for i in args[1:]:
                                os.rmdir(i)
                        elif args[0] == 'uname':
                            print(os.uname().machine)
                        elif args[0] == 'clear':
                            scr_clear()
                        elif args[0] == 'reboot' or args[0] == 'exit':
                            machine.reset()
                        else:
                            try:
                                if not '.py' in args[0]:
                                    args[0] = args[0] + '.py'
                                if args[0] in os.listdir():
                                    exec(open(args[0]).read(), {'__name__': '__main__', 'argv':args},globals())
                                elif args[0] in os.listdir('/apps'):
                                    exec(open('/apps/' + args[0]).read(), {'__name__': '__main__', 'argv':args},globals())
                                else:
                                    print("Bad Command.")
                            except Exception as e:
                                print(e)
                                print("Trying Hard Launch...")
                                cwd = os.getcwd()
                                if cwd != '/':
                                    cwd += '/'
                                
                                RTC.memory(cwd + args[0])
                                # reset clock speed to default.
                                machine.freq(160_000_000)
                                time.sleep_ms(10)
                                machine.reset()
                        
                except Exception as e:
                    print(f"{e}")
                       
                print(f"root@MH:{os.getcwd()}# _")
                current_text = []
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HOUSEKEEPING: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        # anything that needs to be done to prepare for next loop
        
        # do nothing for 10 milliseconds
        time.sleep_ms(10)


# start the main loop
try:
    main_loop()
except Exception as e:
    import sys
    with open('/log.txt', 'a') as f:
        f.write('[TERMINAL]')
        sys.print_exception(e, f)
    
    tft.text(text=f"{e}",x=0, y=0, color=config['ui_color'])
    tft.show()


