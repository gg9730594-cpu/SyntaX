import tkinter as tk
from tkinter import filedialog, messagebox
from pygments import lex
from pygments.lexers import get_lexer_by_name, guess_lexer, PythonLexer
from pygments.token import Token


class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("SyntaX")
        self.root.geometry("900x600")

        self.current_file = None

        self.bg_color = "#1e1e1e"
        self.fg_color = "#d4d4d4"
        self.line_bg = "#252526"
        self.line_fg = "#858585"

        self.styles = {
            Token.Keyword: "#569cd6",
            Token.String: "#ce9178",
            Token.Comment: "#6a9955",
            Token.Name.Function: "#dcdcaa",
            Token.Name.Class: "#4ec9b0",
            Token.Number: "#b5cea8",
            Token.Operator: "#d4d4d4",
        }

        self._create_menu()
        self._create_ui()
        self._setup_tags()

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())

    def _create_ui(self):
        self.line_numbers = tk.Text(
            self.root, width=4, padx=5, takefocus=0, border=0,
            background=self.line_bg, foreground=self.line_fg,
            state="disabled", font=("Consolas", 12)
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.text_area = tk.Text(
            self.root, wrap=tk.NONE, font=("Consolas", 12),
            bg=self.bg_color, fg=self.fg_color, insertbackground="white",
            undo=True, border=0
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.root, command=self.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_area.config(yscrollcommand=scrollbar.set)
        self.line_numbers.config(yscrollcommand=scrollbar.set)

        self.text_area.bind("<KeyRelease>", self.on_content_changed)
        self.text_area.bind("<MouseWheel>", self.update_line_numbers)

    def yview(self, *args):
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)

    def _setup_tags(self):
        """Creating styles using Pygments."""
        for token, color in self.styles.items():
            tag_name = str(token)
            self.text_area.tag_configure(tag_name, foreground=color)

    def update_line_numbers(self, event=None):
        lines = self.text_area.get("1.0", tk.END).split("\n")
        line_count = len(lines) - 1
        line_string = "\n".join(str(i) for i in range(1, line_count + 1))

        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_string)
        self.line_numbers.config(state="disabled")

    def highlight_syntax(self):
        content = self.text_area.get("1.0", tk.END)

        for token in self.styles.keys():
            self.text_area.tag_remove(str(token), "1.0", tk.END)

        try:
            lexer = PythonLexer()
        except Exception:
            return

        for token, text in lex(content, lexer):
            for t, color in self.styles.items():
                if token in t:
                    start_idx = "1.0"
                    while True:
                        pos = self.text_area.search(text, start_idx, stopindex=tk.END, exact=True)
                        if not pos:
                            break
                        end_idx = f"{pos}+{len(text)}c"
                        self.text_area.tag_add(str(t), pos, end_idx)
                        start_idx = end_idx

    def on_content_changed(self, event=None):
        self.update_line_numbers()
        self.highlight_syntax()

    def open_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if filepath:
            self.current_file = filepath
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
            self.root.title(f"Python Code Editor - {filepath}")
            self.on_content_changed()

    def save_file(self):
        if not self.current_file:
            self.current_file = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
            )
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.text_area.get("1.0", tk.END))
            self.root.title(f"SyntaX - {self.current_file}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditor(root)
    root.mainloop()