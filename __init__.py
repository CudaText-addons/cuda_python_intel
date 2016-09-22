import os
from cudatext import *
import cudatext_cmd as cmds
from .intel_work import *

offset_lines=5

def is_wordchar(s):
    return (s=='_') or s.isalnum()
    

class Command:
    def on_complete(self, ed_self):
        fn = ed.get_filename()
        carets = ed.get_carets()
        if len(carets)!=1: return True
        x0, y0, x1, y1 = carets[0]

        if not 0 <= y0 < ed.get_line_count(): 
            return True
        line = ed.get_text_line(y0)
        if not 0 < x0 <= len(line): 
            return True        
        
        #calc len left
        x = x0
        while x>0 and is_wordchar(line[x-1]): x -= 1
        len1 = x0-x

        #calc len right
        x = x0
        while x<len(line) and is_wordchar(line[x]): x += 1
        len2 = x-x0

        #print('len1', len1)
        #print('len2', len2)
        if len1<=0: return True
        
        text = ed.get_text_all()
        if not text: return True
        
        text = handle_autocomplete(text, fn, y0, x0)
        if not text: return True
        ed.complete(text, len1, len2)
        return True
        
        
    def on_goto_def(self, ed_self):
        fn = ed.get_filename()
        carets = ed.get_carets()
        if len(carets)!=1: return True
        x0, y0, x1, y1 = carets[0]

        if not 0 <= y0 < ed.get_line_count(): 
            return
        line = ed.get_text_line(y0)
        if not 0 <= x0 <= len(line): 
            return
            
        text = ed.get_text_all()
        if not text: return True
        
        res = handle_goto_def(text, fn, y0, x0)
        if res is None: return True
        
        fn, y, x = res
        file_open(fn)
        ed.set_prop(PROP_LINE_TOP, str(y-offset_lines)) #must be
        ed.set_caret(x, y)

        print('Goto "%s", line %d' % (fn, y+1))
        return True


    def on_func_hint(self, ed_self):
        fn = ed.get_filename()
        carets = ed.get_carets()
        if len(carets)!=1: return
        x0, y0, x1, y1 = carets[0]

        if not 0 <= y0 < ed.get_line_count(): 
            return
        line = ed.get_text_line(y0)
        if not 0 <= x0 <= len(line): 
            return
            
        text = ed.get_text_all()
        if not text: return
        
        res = handle_func_hint(text, fn, y0, x0)
        if res:
            return ' *** '.join(res)
            

    def show_docstring(self):
        fn = ed.get_filename()
        carets = ed.get_carets()
        if len(carets)!=1: return
        x0, y0, x1, y1 = carets[0]

        if not 0 <= y0 < ed.get_line_count(): 
            return
        line = ed.get_text_line(y0)
        if not 0 <= x0 <= len(line): 
            return
            
        text = ed.get_text_all()
        if not text: return
        
        text = handle_docstring(text, fn, y0, x0)
        if text:
            app_log(LOG_SET_PANEL, LOG_PANEL_OUTPUT)
            app_log(LOG_CLEAR, '')
            for s in text.splitlines():
                app_log(LOG_ADD, s)
            #
            ed.cmd(cmds.cmd_ShowPanelOutput)
            ed.focus()
        else:
            msg_status('Cannot find doc-string')
