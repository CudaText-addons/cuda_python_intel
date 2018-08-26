import os
import sys
from cudatext import *
import cudatext_cmd as cmds
from .intel_work import *

LINE_GOTO_OFFSET = 5
INI = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_python_intel.ini')
PY = 'Python'
ENV = 'Environment'

env = None
sys_path = None
env_path = ini_read(INI, PY, ENV, '')
if env_path:
    env = create_env(env_path)
    sys_path = env_sys_path(env)
if os.name == 'nt' and not env:
    print("   ! Python interpreter not selected.\n   ! You can't use Python Intel")


def is_wordchar(s):
    return (s=='_') or s.isalnum()


class Command:
    def on_complete(self, ed_self):
        params = self.get_params()
        if not params: return

        text, fn, y0, x0, *args = params
        line = ed.get_text_line(y0)
        if not 0 < x0 <= len(line):
            return True

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
        ed.set_prop(PROP_LINE_TOP, str(max(0, num_line-LINE_GOTO_OFFSET)))
        ed.set_caret(num_col, num_line)

        msg_status('Go to file: '+filename)
        print('Goto "%s", Line %d'%(filename, num_line+1))


    def get_params(self):
        if os.name == 'nt' and not env:
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

        text = ed.get_text_all()
        if not text:
            return

        return (text, fn, y0, x0, sys_path, env)

    def select_py_interpreter(self):
        global env
        global sys_path
        selected_env_path = dlg_file(True, '!', '', '')
        env_ = create_env(selected_env_path)
        if env_:
            ini_write(INI, PY, ENV, selected_env_path)
            env = env_
            sys_path = env_sys_path(env_)
            return env_
        else:
            if env_path:
                print('Current Python interpreter: {}'.format(env_path))
            else:
                print('Current Python interpreter: {}'.format(sys.executable))
