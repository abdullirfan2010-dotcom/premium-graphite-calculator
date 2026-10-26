import customtkinter as ctk
import ast
import operator

# -------------------- THEME --------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG = "#111416"
PANEL = "#191E21"
DISPLAY_BG = "#0D1012"
KEY = "#242B2F"
KEY_HOVER = "#303A3F"
KEY_SPECIAL = "#293438"
KEY_SPECIAL_HOVER = "#36464A"
ACCENT = "#2DD4BF"
ACCENT_HOVER = "#5EEAD4"
TEXT = "#F1F5F5"
MUTED = "#91A0A5"
DANGER = "#D97777"
DANGER_HOVER = "#E58B8B"
BORDER = "#2B3438"

# -------------------- WINDOW --------------------
app = ctk.CTk()
app.title("Graphite Calculator")
app.geometry("390x590")
app.resizable(False, False)
app.configure(fg_color=BG)

# -------------------- SAFE CALCULATION --------------------
# Only allows numbers and basic arithmetic operators.
_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

def safe_calculate(expression):
    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
            left = evaluate(node.left)
            right = evaluate(node.right)
            # Prevent unreasonable exponent calculations.
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("Exponent too large")
            result = _BIN_OPS[type(node.op)](left, right)
            if isinstance(result, complex):
                raise ValueError("Invalid result")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
            return _UNARY_OPS[type(node.op)](evaluate(node.operand))
        raise ValueError("Invalid expression")

    return evaluate(tree)

# -------------------- HEADER --------------------
header = ctk.CTkFrame(app, fg_color="transparent")
header.pack(fill="x", padx=24, pady=(22, 12))

brand = ctk.CTkLabel(
    header,
    text="GRAPHITE",
    font=("Arial", 13, "bold"),
    text_color=ACCENT
)
brand.pack(anchor="w")

subtitle = ctk.CTkLabel(
    header,
    text="CALCULATOR  /  STANDARD",
    font=("Arial", 10, "bold"),
    text_color=MUTED
)
subtitle.pack(anchor="w", pady=(4, 0))

# -------------------- DISPLAY PANEL --------------------
display_panel = ctk.CTkFrame(
    app,
    fg_color=DISPLAY_BG,
    corner_radius=18,
    border_width=1,
    border_color=BORDER
)
display_panel.pack(fill="x", padx=20, pady=(8, 18))

display = ctk.CTkEntry(
    display_panel,
    height=82,
    font=("Arial", 32),
    text_color=TEXT,
    fg_color="transparent",
    border_width=0,
    corner_radius=0,
    justify="right",
    placeholder_text="0"
)
display.pack(fill="x", padx=14, pady=8)

status = ctk.CTkLabel(
    display_panel,
    text="READY",
    font=("Arial", 9, "bold"),
    text_color=MUTED
)
status.pack(anchor="e", padx=18, pady=(0, 10))

# -------------------- BUTTONS --------------------
keys_frame = ctk.CTkFrame(app, fg_color="transparent")
keys_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

for col in range(4):
    keys_frame.grid_columnconfigure(col, weight=1, uniform="key")
for row in range(5):
    keys_frame.grid_rowconfigure(row, weight=1, uniform="key")

buttons = [
    ["C", "⌫", "%", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "−"],
    ["1", "2", "3", "+"],
    ["±", "0", ".", "="],
]

def format_result(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)

def button_click(value):
    current = display.get()

    if value == "C":
        display.delete(0, "end")
        status.configure(text="CLEARED", text_color=MUTED)
        return

    if value == "⌫":
        display.delete(0, "end")
        display.insert(0, current[:-1])
        status.configure(text="EDITING", text_color=MUTED)
        return

    if value == "±":
        if current:
            try:
                if current.startswith("-"):
                    updated = current[1:]
                else:
                    updated = "-" + current
                display.delete(0, "end")
                display.insert(0, updated)
                status.configure(text="SIGN CHANGED", text_color=MUTED)
            except Exception:
                status.configure(text="INVALID INPUT", text_color=DANGER)
        return

    if value == "=":
        if not current.strip():
            return
        expression = (
            current.replace("×", "*")
            .replace("÷", "/")
            .replace("−", "-")
            .replace("%", "/100")
        )
        try:
            result = safe_calculate(expression)
            display.delete(0, "end")
            display.insert(0, format_result(result))
            status.configure(text="COMPLETE", text_color=ACCENT)
        except ZeroDivisionError:
            display.delete(0, "end")
            display.insert(0, "Cannot divide by zero")
            status.configure(text="MATH ERROR", text_color=DANGER)
        except Exception:
            display.delete(0, "end")
            display.insert(0, "Invalid input")
            status.configure(text="INPUT ERROR", text_color=DANGER)
        return

    if current in ("Cannot divide by zero", "Invalid input"):
        display.delete(0, "end")
        current = ""

    if value == ".":
        # Prevent multiple decimal points in the current number.
        last_number = current.replace("+", " ").replace("−", " ").replace("-", " ")
        last_number = last_number.replace("×", " ").replace("÷", " ").split(" ")[-1]
        if "." in last_number:
            return

    display.insert("end", value)
    status.configure(text="EDITING", text_color=MUTED)

for row_index, row in enumerate(buttons):
    for col_index, label in enumerate(row):
        fg = KEY
        hover = KEY_HOVER
        txt = TEXT

        if label in ("C", "⌫", "%", "±"):
            fg = KEY_SPECIAL
            hover = KEY_SPECIAL_HOVER
            txt = ACCENT if label == "%" else TEXT
        elif label in ("÷", "×", "−", "+"):
            fg = KEY_SPECIAL
            hover = KEY_SPECIAL_HOVER
            txt = ACCENT
        elif label == "=":
            fg = ACCENT
            hover = ACCENT_HOVER
            txt = "#09201D"

        button = ctk.CTkButton(
            keys_frame,
            text=label,
            height=56,
            font=("Arial", 17, "bold"),
            text_color=txt,
            fg_color=fg,
            hover_color=hover,
            corner_radius=14,
            border_width=1 if label != "=" else 0,
            border_color=BORDER,
            command=lambda value=label: button_click(value)
        )
        button.grid(
            row=row_index,
            column=col_index,
            padx=5,
            pady=5,
            sticky="nsew"
        )

# Keyboard support
def on_key(event):
    char = event.char
    key = event.keysym

    if key in ("Return", "KP_Enter"):
        button_click("=")
    elif key == "BackSpace":
        button_click("⌫")
    elif key == "Escape":
        button_click("C")
    elif key in ("plus", "equal") and char == "+":
        button_click("+")
    elif char in "0123456789.":
        button_click(char)
    elif char == "+":
        button_click("+")
    elif char == "-":
        button_click("−")
    elif char == "*":
        button_click("×")
    elif char == "/":
        button_click("÷")
    elif char == "%":
        button_click("%")

app.bind("<Key>", on_key)

# Start the app
app.mainloop()
