Plugin for CudaText.
Gives intelligence commands for Python lexer.

1) Auto-completion
   To use it: place caret after incomplete function/class/variable/module name,
   and press CudaText hotkey for auto-completion (Ctrl+Space).
2) Go to definition
   To use it: place caret on a name of function/class/variable/module, and call
   "Go to definition" item from editor context menu, or use CudaText mouse shortcut.
3) Show function call-tip
   To use it: place caret after function name between () brackets, and press
   CudaText hotkey for "show function-hint" (Ctrl+Shift+Space).
4) Show function doc-string
   Shows doc-string for function/class under caret, in the Output panel.
   Call it from Command Palette.
5) Show usages
   Shows menu with locations (file name, line number) where identifier under caret
   is used. Jumps to chosen location.
   Call it from Command Palette.
6) Refactoring - Rename
   Renames all instances of identifier under the caret.
7) Refactoring - Inline
   Inlines a variable under the caret. This is basically the opposite
   of extracting a variable.
8) Refactoring - Extract variable
   Moves an expression to a new statemenet.
9) Refactoring - Extract function
   Moves an expression to a new function.

Based on Jedi library:
  Jedi is a static analysis tool for Python that can be used in IDEs/editors.
  https://github.com/davidhalter/jedi

Authors:
  Alexey Torgashin (CudaText)
  Oleh Lutsak https://github.com/OlehL/
License: MIT
