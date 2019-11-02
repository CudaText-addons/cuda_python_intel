import os
import sys
from cudatext import *
import cudatext_cmd as cmds
from .intel_work import *

INI_FILE = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_python_intel.ini')
INI_PY = 'python'
INI_ENV = 'environment'

IS_NT = os.name == 'nt'
IS_LINUX = sys.platform == 'linux'
IS_MAC = sys.platform == 'darwin'
LINE_GOTO_OFFSET = 5


def is_wordchar(s):
    return (s=='_') or s.isalnum()


class Command:

    def __init__(self):
        self.env = None
        self.sys_path = None
        self.env_path = ini_read(INI_FILE, INI_PY, INI_ENV, '')
        if self.env_path:
            self.env = create_env(self.env_path)
            self.sys_path = env_sys_path(self.env)
        if IS_NT and not self.env:
            print("Error: Python interpreter not selected. You cannot use Python IntelliSense.")

    def on_complete(self, ed_self):
        params = self.get_params()
        if not params: return True

        text, fn, y0, x0, *args = params
        line = ed.get_text_line(y0)

        #calc len left
        x = x0
        while x>0 and is_wordchar(line[x-1]): x -= 1
        len1 = x0-x

        after_dot = x>1 and line[x-1]=='.'

        #calc len right
        x = x0
        while x<len(line) and is_wordchar(line[x]): x += 1
        len2 = x-x0

        #print('len1', len1)
        #print('len2', len2)
        if len1<=0 and not after_dot:
            return True

        text = handle_autocomplete(*params)
        if not text: return True

        ed.complete(text, len1, len2)
        return True

    def on_goto_def(self, ed_self):
        params = self.get_params()
        if not params: return True

        res = handle_goto_def(*params)
        if res is None: return True

        #res has (filename, y, x)
        self.goto_file(*res)
        return True

    def on_func_hint(self, ed_self):
        params = self.get_params()
        if not params: return

        item = handle_func_hint(*params)
        if item is None:
            return
        else:
            return ' '+item

    def show_docstring(self):
        params = self.get_params()
        if not params: return

        text = handle_docstring(*params)
        if text:
            app_log(LOG_CLEAR, '', panel=LOG_PANEL_OUTPUT)
            for s in text.splitlines():
                app_log(LOG_ADD, s, panel=LOG_PANEL_OUTPUT)

            ed.cmd(cmds.cmd_ShowPanelOutput)
            ed.focus()
        else:
            msg_status('Cannot find doc-string')

    def show_usages(self):
        params = self.get_params()
        if not params:
            return

        items = handle_usages(*params)
        if not items:
            msg_status('Cannot find usages')
            return

        items_show = [
            os.path.basename(item[0]) +
            ', Line %s, Col %d' % (item[1] + 1, item[2] + 1) +
            '\t' + item[0]
            for item in items
            ]
        res = dlg_menu(MENU_LIST_ALT, '\n'.join(items_show))
        if res is None:
            return

        item = items[res]
        self.goto_file(item[0], item[1], item[2])

    def goto_file(self, filename, num_line, num_col):
        if not os.path.isfile(filename):
            return

        file_open(filename)
        
        ed.action(EDACTION_SHOW_POS, (num_col, num_line), (0, LINE_GOTO_OFFSET))
        ed.set_caret(num_col, num_line, options=CARET_OPTION_UNFOLD)

        msg_status('Go to file: '+filename)
        print('Goto "%s", Line %d'%(filename, num_line+1))


    def get_params(self):
        if IS_NT and not self.env:
            return
        fn = ed.get_filename()
        carets = ed.get_carets()
        if len(carets)!=1:
            return
        x0, y0, x1, y1 = carets[0]

        if not 0 <= y0 < ed.get_line_count():
            return
        line = ed.get_text_line(y0)
        if not 0 <= x0 <= len(line):
            return

        if ed.get_token(TOKEN_GET_KIND, x0, y0) in ('c', 's'):
            return

        text = ed.get_text_all()
        if not text:
            return

        return (text, fn, y0, x0, self.sys_path, self.env)

    def select_py_interpreter(self):

        if IS_LINUX:
            items = [
                '/usr/bin/python',
                '/usr/bin/python3',
                ]
            r = dlg_menu(MENU_LIST, items, caption='Select Python interpreter')
            if r is None: return
            fn = items[r]
        elif IS_MAC:
            items = ['/Library/Frameworks/Python.framework/Versions/3.%d/bin/python3'%i for i in [3,4,5,6,7,8,9,10]]
            items = [i for i in items if os.path.exists(i)]
            items2 = [os.path.dirname(os.path.dirname(i)) for i in items]
            r = dlg_menu(MENU_LIST, items2, caption='Select Python interpreter')
            if r is None: return
            fn = items[r]
        else:
            filters = 'Executables|*.exe' if IS_NT else ''
            fn = dlg_file(True, '!', '', filters)
            if not fn: return

        env_ = create_env(fn)
        if env_:
            ini_write(INI_FILE, INI_PY, INI_ENV, fn)
            self.env = env_
            self.sys_path = env_sys_path(env_)
            return env_
        else:
            fn = self.env_path if self.env_path else sys.executable
            print('Current Python interpreter: '+fn)
