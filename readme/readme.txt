Plugin for CudaText.
Gives intelligence commands for Python lexer.

*  Auto-completion
   To use it: place caret after incomplete function/class/variable/module name,
   and press CudaText hotkey for auto-completion (Ctrl+Space).
*  Go to definition
   To use it: place caret on a name of function/class/variable/module, and call
   "Go to definition" item from editor context menu, or use CudaText mouse shortcut.
*  Show function call-tip
   To use it: place caret after function name between () brackets, and press
   CudaText hotkey for "show function-hint" (Ctrl+Shift+Space).
*  Show function doc-string
   Shows doc-string for function/class under caret, in the Output panel.
   Call it from Command Palette.
*  Show usages
   Shows menu with locations (file name, line number) where identifier under caret
   is used. Jumps to chosen location.
   Call it from Command Palette.
   
Refactoring commands, they change editor text:
   
*  Refactoring - Rename
   Renames all instances of identifier under the caret.
*  Refactoring - Inline
   Inlines a variable under the caret. This is basically the opposite
   of extracting a variable.
*  Refactoring - Extract variable
   Moves an expression to a new statemenet.
*  Refactoring - Extract function
   Moves an expression to a new function.

Plugin handles CudaText projects (internally calling Project Manager plugin).

Based on Jedi library:
  Jedi is a static analysis tool for Python that can be used in IDEs/editors.
  https://github.com/davidhalter/jedi

Authors:
  Alexey Torgashin (CudaText)
  Oleh Lutsak https://github.com/OlehL/
License: MIT
