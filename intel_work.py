import sys
import os
sys.path.append(os.path.dirname(__file__))
import jedi


def handle_autocomplete(text, fn, row, col):
    row += 1 #Jedi has 1-based
    script = jedi.Script(text, row, col, fn)
    completions = script.completions()
    if not completions: return

    text = ''
    for c in completions:
        pars = '()' if c.type=='function' else ''
        if hasattr(c, 'params'):
            pars = '(' + ', '.join([p.name for p in c.params]) + ')'
        text += c.type + '|' + c.name + '|' + pars + '\n'
    return text


def handle_goto_def(text, fn, row, col):
    row += 1 #Jedi has 1-based
    script = jedi.Script(text, row, col, fn)
    items = script.goto_assignments()
    if not items: return

    d = items[0]
    modfile = d.module_path
    if modfile is None: return

    if not os.path.isfile(modfile):
        # second way to get symbol definitions
        items = script.goto_definitions()
        if not items: return

        d = items[0]
        modfile = d.module_path # module_path is all i need?
        if modfile is None: return
        if not os.path.isfile(modfile): return

    return (modfile, d.line-1, d.column)


def handle_func_hint(text, fn, row, col):
    row += 1 #Jedi
    script = jedi.Script(text, row, col, fn)
    items = script.call_signatures()
    if items:
        par = items[0].params
        desc = ', '.join([n.name for n in par])
        return desc


def handle_docstring(text, fn, row, col):
    row += 1 #Jedi
    script = jedi.Script(text, row, col, fn)
    items = script.goto_definitions()
    if items:
        return items[0].docstring()


def handle_usages(text, fn, row, col):
    row += 1 #Jedi
    script = jedi.Script(text, row, col, fn)
    items = script.usages()
    if items:
        res = []
        for d in items:
            modfile = d.module_path
            if modfile and os.path.isfile(modfile):
                res += [(modfile, d.line-1, d.column)]
        return res
