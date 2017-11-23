Plugin for CudaText.
Gives intelligence commands for Python lexer.

1) Auto-completion (Ctrl+Space)
   Place caret after incomplete function/class/variable name, and press this hotkey.
2) Go to definition
   Place caret on name of func/class/variable, and call "Go to definition" menuitem from editor context menu.
3) Show function call-tip (Ctrl+Shift+Space)
   Place caret after function name between () brackets, and press this hotkey.
4) Show function doc-string
   Shows doc-string for function/class under caret, in the Output panel. Call it from F1-Commands menu.
5) Show usages
   Menu shows files/line-numbers where identifier is used. Call it from F1-Commands menu.


Based on Jedi:
  Jedi is a static analysis tool for Python that can be used in IDEs/editors.
  https://github.com/davidhalter/jedi

Author: Alexey T.
License: MIT
