import os
import sys
import cudatext as ct
import cudatext_cmd as cmds
from difflib import SequenceMatcher
sys.path.append(os.path.dirname(__file__))
import jedi
import cuda_project_man as prj_man


INI_FILE = os.path.join(ct.app_path(ct.APP_DIR_SETTINGS), 'cuda_python_intel.ini')
INI_PY = 'python'
INI_ENV = 'environment'

IS_NT = os.name == 'nt'
# IS_LINUX = sys.platform == 'linux'
# IS_MAC = sys.platform == 'darwin'
LINE_GOTO_OFFSET = 5


def input_name(caption, name):
    while True:
        s = ct.dlg_input(caption, name)
        if not s:
            return
        if (s != name) and s.isidentifier():
            return s

def is_wordchar(s):
    return (s == '_') or s.isalnum()


def msg(*args):
    print('Python IntelliSense: ', *args)
    ct.msg_status(', '.join([str(arg) for arg in args]))


def create_env(env_path):
    try:
        env = jedi.create_environment(env_path)
        msg(repr(env).replace('Environment:', 'Python'))
        return env
    except jedi.InvalidPythonEnvironment:
        msg('Error! Python interpreter not activate')
        return


def select_env():
    items = list(jedi.find_system_environments())
    names = [repr(i).replace('Environment:', 'Python') for i in items]
    names.append('Other...')
    i = ct.dlg_menu(ct.MENU_LIST, names, caption='Select Python interpreter')
    if i is None:
        return
    elif i == len(names) - 1:
        filters = 'Executables|*.exe' if IS_NT else ''
        fn = ct.dlg_file(True, '!', '', filters)
        if not fn:
            return
    else:
        fn = items[i].executable
    env = create_env(fn)
    if env:
        ct.ini_write(INI_FILE, INI_PY, INI_ENV, fn)
        return env


def goto_file(filename, num_line, num_col):
    if not os.path.isfile(filename):
        return

    ct.file_open(filename, options="/nohistory")

    # needed because edaction_show_pos don't scroll w/o it
    ct.app_idle(False)
    ct.ed.action(ct.EDACTION_SHOW_POS, (num_col, num_line), (0, LINE_GOTO_OFFSET))
    ct.ed.set_caret(num_col, num_line, options=ct.CARET_OPTION_UNFOLD)

    ct.msg_status('Go to file: '+filename)
    print('Goto "%s", Line %d' % (filename, num_line + 1))


def diff_patch_code(changed_file):
    old_s = ct.ed.get_text_all()
    new_s = changed_file.get_new_code()
    old_code = old_s.splitlines()
    new_code = new_s.splitlines()

    matcher = SequenceMatcher(None, old_code, new_code)
    for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
        if tag == 'delete':
            ct.ed.replace_lines(i1, i2-1, [])
        elif tag == 'insert':
            ct.ed.insert(0, i1, '\n' + '\n'.join(new_code[j1:j2]))
        elif tag == 'replace':
            ct.ed.replace_lines(i1, i2-1, new_code[j1:j2])


class Cursor:
    def __init__(self, x, y, x1=None, y1=None):
        self.x = x
        self.y = y
        self.row = y + 1
        self.x1 = None if x1 == -1 else x1
        self.y1 = None if y1 == -1 else y1
        self.row1 = self.y1 + 1 if self.y1 else None


class App:
    def __init__(self):
        self.environment = None
        self.project = None

    @property
    def code(self):
        return ct.ed.get_text_all()

    @property
    def cursor(self):
        carets = ct.ed.get_carets()
        if len(carets) != 1:
            return
        x, y, selx, sely = carets[0]
        if not 0 <= y < ct.ed.get_line_count():
            return
        line = ct.ed.get_text_line(y)
        if not 0 <= x <= len(line):
            return
        # if ct.ed.get_token(ct.TOKEN_GET_KIND, x, y) in ('c', 's'):
        #     print("doesn't work correct")
        #     return
        return Cursor(x, y, selx, sely)

    @property
    def cursor_sorted(self):
        carets = ct.ed.get_carets()
        if len(carets) != 1:
            return
        x, y, x1, y1 = carets[0]
        if not 0 <= y < ct.ed.get_line_count():
            return
        line = ct.ed.get_text_line(y)
        if not 0 <= x <= len(line):
            return
        if (y, x) > (y1, x1):
            x, y, x1, y1 = x1, y1, x, y
        return Cursor(x, y, x1, y1)

    @property
    def path(self):
        return ct.ed.get_filename()

    @property
    def script(self):
        return jedi.Script(
            code=self.code,
            path=self.path,
            environment=self.environment,
            project=self.project)


class Command:

    def __init__(self):
        self.app = App()
        self.fn = None
        self.nodes = []

        self.env_path = ct.ini_read(INI_FILE, INI_PY, INI_ENV, '')
        if self.env_path:
            self.app.environment = create_env(self.env_path)
        if not self.app.environment:
            # show menu
            self.app.environment = select_env()

        if IS_NT and not self.app.environment:
            msg("ERROR: Python interpreter not selected. You can't use Python IntelliSense.")

    def on_open(self, ed_self):
        self.load_prj()

    def on_tab_change(self, ed_self):
        self.load_prj()

    def load_prj(self):
        nodes = prj_man.global_project_info.get('nodes')
        fn = ct.ed.get_filename()

        if fn == self.fn and [x for x in nodes if x in self.nodes]:
            return
        else:
            self.nodes = nodes
            self.fn = fn

        for n in nodes:
            if n in fn:
                _fn = prj_man.global_project_info['filename']
                if os.path.exists(_fn):
                    fn = _fn
                break
        if not os.path.isfile(fn):
            self.app.project = None
            return
        fpath = os.path.dirname(fn)

        prj_sys_path = []
        prj_sys_path.extend(sys.path)
        for n in nodes:
            if os.path.isdir(n):
                prj_sys_path.append(n)
            elif os.path.isfile(n):
                prj_sys_path.append(os.path.dirname(n))

        self.app.project = jedi.Project(
            path=fpath,
            added_sys_path=prj_sys_path)

    def on_complete(self, ed_self):
        """Completes objects under the cursor."""
        if IS_NT and not self.app.environment:
            return True

        cursor = self.app.cursor
        if not cursor:
            return True

        line = ct.ed.get_text_line(cursor.y)

        # calc len left
        x = cursor.x
        while x > 0 and is_wordchar(line[x-1]):
            x -= 1
        len1 = cursor.x - x

        after_dot = x > 1 and line[x-1] == '.'

        # calc len right
        x = cursor.x
        while x < len(line) and is_wordchar(line[x]):
            x += 1
        len2 = x - cursor.x

        if len1 <= 0 and not after_dot:
            return True

        completions = self.app.script.complete(
            cursor.row,
            cursor.x)
        if not completions:
            return True

        text = ''
        for c in completions:
            pars = ''
            if c.type == 'function':
                pars = '(' + ', '.join([p.name for p in c.params]) + ')'
            text += c.type + '|' + c.name + '|' + pars + '\n'

        ct.ed.complete(text, len1, len2)
        return True

    def refactoring_rename(self):
        """Renames all references of the variable under the cursor."""
        if IS_NT and not self.app.environment:
            return

        cursor = self.app.cursor
        if not cursor:
            return

        script = self.app.script

        refs = script.get_references(
            line=cursor.row,
            column=cursor.x,
            include_builtins=False)
        if not refs:
            return
        name = refs[0].name
        
        new_name = input_name('Rename to:', name)
        if not new_name:
            return

        item = script.rename(
            line=cursor.row,
            column=cursor.x,
            new_name=new_name)

        changed_files = item.get_changed_files()
        if len(changed_files) > 1:
            item.apply()
        else:
            k, v = changed_files.popitem()
            diff_patch_code(v)

    def refactoring_inline(self):
        """
        Inlines a variable under the cursor.
        This is basically the opposite of extracting a variable
        """
        if IS_NT and not self.app.environment:
            return

        cursor = self.app.cursor
        if not cursor:
            return

        try:
            item = self.app.script.inline(
                line=cursor.row,
                column=cursor.x)
        except jedi.api.exceptions.RefactoringError as er:
            msg(er)
            return

        changed_files = item.get_changed_files()
        if len(changed_files) > 1:
            item.apply()
        else:
            k, v = changed_files.popitem()
            diff_patch_code(v)

    def refactoring_extract_variable(self):
        """Moves an expression to a new statemenet."""
        if IS_NT and not self.app.environment:
            return

        cursor = self.app.cursor_sorted
        if not cursor:
            return

        new_name = input_name('Extract variable:', '')
        if not new_name:
            return

        try:
            item = self.app.script.extract_variable(
                line=cursor.row,
                column=cursor.x,
                until_line=cursor.row1,
                until_column=cursor.x1,
                new_name=new_name)
        except ValueError:
            msg("Can't do that. :(")
            return

        changed_files = item.get_changed_files()
        if len(changed_files) > 1:
            item.apply()
        else:
            k, v = changed_files.popitem()
            diff_patch_code(v)
            
        ct.ed.set_caret(cursor.x, cursor.row)

    def refactoring_extract_function(self):
        """Moves an expression to a new function."""
        if IS_NT and not self.app.environment:
            return

        cursor = self.app.cursor_sorted
        if not cursor:
            return

        new_name = input_name('Extract function:', '')
        if not new_name:
            return

        try:
            item = self.app.script.extract_function(
                line=cursor.row,
                column=cursor.x,
                until_line=cursor.row1,
                until_column=cursor.x1,
                new_name=new_name)
        except ValueError:
            msg("Can't do that. :(")
            return

        changed_files = item.get_changed_files()
        if len(changed_files) > 1:
            item.apply()
        else:
            k, v = changed_files.popitem()
            diff_patch_code(v)

        ct.ed.set_caret(cursor.x, cursor.row)

    def on_goto_def(self, ed_self):
        """Goes to the name that defined the object under the cursor."""
        if IS_NT and not self.app.environment:
            return True

        cursor = self.app.cursor
        if not cursor:
            return True

        items = self.app.script.goto(
            line=cursor.row,
            column=cursor.x)

        if not items:
            return True

        d = items[0]
        modfile = d.module_path
        if modfile is None:
            return True

        res = (modfile, d.line-1, d.column)
        if res is None:
            return True

        goto_file(*res)
        return True

    def on_func_hint(self, ed_self):
        """Return the function object of the call under the cursor."""
        if not self.app.environment:
            return

        cursor = self.app.cursor
        if not cursor:
            return

        items = self.app.script.get_signatures(
            line=cursor.row,
            column=cursor.x)

        if items:
            par = items[0].params
            desc = ', '.join([n.name for n in par])
            return ' ' + desc if desc else None

    def show_docstring(self):
        if not self.app.environment:
            return

        cursor = self.app.cursor
        if not cursor:
            return

        items = self.app.script.goto(
            line=cursor.row,
            column=cursor.x)

        if items:
            text = items[0].docstring()
        else:
            return

        if text:
            ct.app_log(ct.LOG_CLEAR, '', panel=ct.LOG_PANEL_OUTPUT)
            for s in text.splitlines():
                ct.app_log(ct.LOG_ADD, s, panel=ct.LOG_PANEL_OUTPUT)

            ct.ed.cmd(cmds.cmd_ShowPanelOutput)
            ct.ed.focus()
        else:
            ct.msg_status('Cannot find doc-string')

    def show_usages(self):
        if not self.app.environment:
            return

        cursor = self.app.cursor
        if not cursor:
            return

        items = self.app.script.get_references(
            line=cursor.row,
            column=cursor.x)

        if items:
            usages = []
            for d in items:
                modfile = d.module_path
                if modfile and os.path.isfile(modfile):
                    usages += [(modfile, d.line-1, d.column)]
        else:
            return

        if not usages:
            ct.msg_status('Cannot find usages')
            return

        items_show = [
            ''.join([os.path.basename(item[0]),
                     ', Line %s, Col %d' % (item[1] + 1, item[2] + 1),
                     '\t',
                     item[0]])
            for item in usages]
        res = ct.dlg_menu(ct.MENU_LIST_ALT, '\n'.join(items_show))
        if res is None:
            return

        item = usages[res]
        goto_file(item[0], item[1], item[2])

    def select_py_interpreter(self):
        select_env()
