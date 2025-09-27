# market_editor_v2.5.py
"""
MarketPrice Editor (English)
- Live diff: the right text pane highlights changed lines (green).
- Improved readability: monospace font, bigger font size and contrast.
- English UI text and status messages.
- Requires: Pillow (pip install pillow)
"""

import json
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import xml.etree.ElementTree as ET

APP_TITLE = "MarketPrice Editor by Vo7d ©2025"

class MarketConfigEditor:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        try:
            self.root.state("zoomed")
        except:
            pass

        # Theme / colors
        self.bg = "#1e1e1f"
        self.panel_bg = "#252525"
        self.fg = "#e8eef1"
        self.muted = "#9aa4ab"

        # Readability font (monospace)
        if "Consolas" in tkfont.families():
            self.code_font = ("Consolas", 12)
            self.ln_font = ("Consolas", 10)
        else:
            self.code_font = ("Courier New", 12)
            self.ln_font = ("Courier New", 10)

        self.insert_color = "white"

        self.file_data = None
        self.file_path = None
        self.current_type = None   # 'market' or 'types'

        # Logo (optional)
        try:
            img = Image.open("Logo Vo7d.jpg")
            img = img.resize((140, 140), Image.LANCZOS)
            self.logo = ImageTk.PhotoImage(img)
            logo_label = tk.Label(root, image=self.logo, bg=self.bg)
            logo_label.pack(pady=6)
        except Exception as e:
            print("Logo could not be loaded:", e)

        # Menu
        self.menubar = tk.Menu(root)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Open", accelerator="Ctrl+O", command=self.open_shortcut)
        filemenu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_shortcut)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", accelerator="Ctrl+Q", command=root.quit)
        self.menubar.add_cascade(label="File", menu=filemenu)
        root.config(menu=self.menubar)

        # Notebook (tabs)
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass
        style.configure("TNotebook", background=self.bg, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 11, "bold"), padding=[12, 8], background=self.panel_bg, foreground=self.fg)
        style.map("TNotebook.Tab", background=[("selected", "#2f8f4e")], foreground=[("selected", "white")])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=6)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Market tab
        market_tab = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(market_tab, text="Market Editor")
        self.build_market_editor(market_tab)

        # Types tab
        types_tab = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(types_tab, text="Types.xml Editor")
        self.build_types_editor(types_tab)

        # About tab
        about_tab = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(about_tab, text="About")
        tk.Label(about_tab, text="All rights reserved.\nby Vo7d copyright 2025.\nNot for distribution.",
                 fg=self.fg, bg=self.bg, font=("Segoe UI", 14, "bold")).pack(expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="No file opened")
        status = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor="w", bg="#101010", fg=self.muted)
        status.pack(side="bottom", fill="x")

        # Shortcuts
        root.bind("<Control-o>", lambda e: self.open_shortcut())
        root.bind("<Control-s>", lambda e: self.save_shortcut())
        root.bind("<Control-r>", lambda e: self.reset_shortcut())
        root.bind("<Control-v>", lambda e: self.validate_shortcut())
        root.bind("<Control-q>", lambda e: self.root.quit())

        # Initial UI state
        self.update_ui_state()

    # ------------------------
    # UI helpers
    # ------------------------
    def set_status(self, text):
        self.status_var.set(text)

    def update_ui_state(self):
        tab_index = self.notebook.index(self.notebook.select())
        if tab_index == 0:
            enabled = (self.current_type == "market")
            for w in getattr(self, "_market_toggle_widgets", []):
                w.config(state=("normal" if enabled else "disabled"))
        else:
            enabled = (self.current_type == "types")
            for w in getattr(self, "_types_toggle_widgets", []):
                w.config(state=("normal" if enabled else "disabled"))

    def on_tab_change(self, event=None):
        self.update_ui_state()
        if self.file_path:
            self.set_status(f"Open file: {os.path.basename(self.file_path)} • type: {self.current_type}")
        else:
            self.set_status("No file opened")

    # ------------------------
    # Market editor
    # ------------------------
    def build_market_editor(self, parent):
        file_panel = tk.LabelFrame(parent, text="File", fg=self.fg, bg=self.panel_bg, font=("Segoe UI", 11, "bold"))
        file_panel.pack(pady=6, fill="x")
        b_open = tk.Button(file_panel, text="Open", command=self.load_market)
        b_open.pack(side="left", padx=6, pady=6)
        b_save = tk.Button(file_panel, text="Save", command=self.save_market)
        b_save.pack(side="left", padx=6)
        b_reset = tk.Button(file_panel, text="Reset", command=self.reset_market)
        b_reset.pack(side="left", padx=6)
        b_validate = tk.Button(file_panel, text="Validate JSON", command=self.validate_market)
        b_validate.pack(side="left", padx=6)
        b_close = tk.Button(file_panel, text="Close", command=self.root.quit)
        b_close.pack(side="left", padx=6)

        self._market_toggle_widgets = [b_save, b_reset, b_validate]

        adjust_panel = tk.LabelFrame(parent, text="Adjustments", fg=self.fg, bg=self.panel_bg, font=("Segoe UI", 11, "bold"))
        adjust_panel.pack(pady=6, fill="x")
        self.percent_entry = tk.Entry(adjust_panel, width=6)
        self.percent_entry.insert(0, "20")
        self.percent_entry.pack(side="left", padx=6)
        self.market_mode = tk.StringVar(value="Lower %")
        tk.OptionMenu(adjust_panel, self.market_mode, "Lower %", "Raise %", "Set Custom").pack(side="left", padx=6)
        self.price_mode = tk.StringVar(value="Both")
        tk.OptionMenu(adjust_panel, self.price_mode, "Min", "Max", "Both").pack(side="left", padx=6)
        b_apply = tk.Button(adjust_panel, text="Apply", command=self.apply_market_changes)
        b_apply.pack(side="left", padx=6)
        self.sell_entry = tk.Entry(adjust_panel, width=6)
        self.sell_entry.insert(0, "45")
        self.sell_entry.pack(side="left", padx=6)
        b_apply_sell = tk.Button(adjust_panel, text="Apply Sell %", command=self.apply_sell)
        b_apply_sell.pack(side="left", padx=6)

        text_frame = tk.Frame(parent, bg=self.bg)
        text_frame.pack(fill="both", expand=True, padx=8, pady=8)

        left = tk.Frame(text_frame, bg=self.bg)
        left.pack(side="left", fill="both", expand=True, padx=6)
        tk.Label(left, text="Original Market", fg=self.fg, bg=self.bg).pack(anchor="w")
        self.market_original = self.create_text_with_line_numbers(left, filetype="json")
        self.search_setup(left, self.market_original)

        right = tk.Frame(text_frame, bg=self.bg)
        right.pack(side="right", fill="both", expand=True, padx=6)
        tk.Label(right, text="Modified Market", fg=self.fg, bg=self.bg).pack(anchor="w")
        self.market_modified = self.create_text_with_line_numbers(right, filetype="json", enable_change_highlight=True)
        self.search_setup(right, self.market_modified)

    def load_market(self, path=None):
        if not path:
            path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read JSON: {e}")
            return
        pretty = json.dumps(data, indent=2, ensure_ascii=False)
        self.market_original.delete("1.0", tk.END)
        self.market_original.insert(tk.END, pretty)
        self.market_original._update_line_numbers()
        self.market_modified.delete("1.0", tk.END)
        self.market_modified.insert(tk.END, pretty)
        self.market_modified._update_line_numbers()
        self.file_path = path
        self.current_type = "market"
        self.file_data = data
        self.set_status(f"Open file: {os.path.basename(path)} • market")
        self.highlight_diffs(self.market_original, self.market_modified)

    def save_market(self):
        content = self.market_modified.get("1.0", tk.END).strip()
        try:
            parsed = json.loads(content)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid JSON: {e}")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Saved", f"File saved: {path}")

    def reset_market(self):
        if not self.file_data:
            return
        pretty = json.dumps(self.file_data, indent=2, ensure_ascii=False)
        self.market_modified.delete("1.0", tk.END)
        self.market_modified.insert(tk.END, pretty)
        self.market_modified._update_line_numbers()
        self.highlight_diffs(self.market_original, self.market_modified)

    def validate_market(self):
        content = self.market_modified.get("1.0", tk.END).strip()
        try:
            json.loads(content)
            messagebox.showinfo("Validation", "JSON is valid")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid JSON: {e}")

    def apply_market_changes(self):
        try:
            val = float(self.percent_entry.get())
        except:
            messagebox.showerror("Error", "Percent must be numeric")
            return
        try:
            data = json.loads(self.market_modified.get("1.0", tk.END))
        except Exception:
            messagebox.showerror("Error", "Invalid JSON in Modified Market")
            return
        for item in data.get("Items", []):
            if self.market_mode.get() == "Set Custom":
                if self.price_mode.get() in ("Min", "Both") and "MinPriceThreshold" in item:
                    item["MinPriceThreshold"] = int(val)
                if self.price_mode.get() in ("Max", "Both") and "MaxPriceThreshold" in item:
                    item["MaxPriceThreshold"] = int(val)
            else:
                factor = 1 + (val / 100.0) if self.market_mode.get() == "Raise %" else 1 - (val / 100.0)
                if self.price_mode.get() in ("Min", "Both") and "MinPriceThreshold" in item:
                    item["MinPriceThreshold"] = max(1, int(item["MinPriceThreshold"] * factor))
                if self.price_mode.get() in ("Max", "Both") and "MaxPriceThreshold" in item:
                    item["MaxPriceThreshold"] = max(1, int(item["MaxPriceThreshold"] * factor))
        self.market_modified.delete("1.0", tk.END)
        self.market_modified.insert(tk.END, json.dumps(data, indent=2, ensure_ascii=False))
        self.market_modified._update_line_numbers()
        self.highlight_diffs(self.market_original, self.market_modified)

    def apply_sell(self):
        try:
            new_val = int(self.sell_entry.get())
        except:
            messagebox.showerror("Error", "Sell % must be integer")
            return
        try:
            data = json.loads(self.market_modified.get("1.0", tk.END))
        except:
            messagebox.showerror("Error", "Invalid JSON in Modified Market")
            return
        for item in data.get("Items", []):
            if "SellPricePercent" in item:
                item["SellPricePercent"] = new_val
        self.market_modified.delete("1.0", tk.END)
        self.market_modified.insert(tk.END, json.dumps(data, indent=2, ensure_ascii=False))
        self.market_modified._update_line_numbers()
        self.highlight_diffs(self.market_original, self.market_modified)

    # ------------------------
    # Types.xml editor
    # ------------------------
    def build_types_editor(self, parent):
        file_panel = tk.LabelFrame(parent, text="File", fg=self.fg, bg=self.panel_bg, font=("Segoe UI", 11, "bold"))
        file_panel.pack(pady=6, fill="x")
        b_open = tk.Button(file_panel, text="Open", command=self.load_types)
        b_open.pack(side="left", padx=6, pady=6)
        b_save = tk.Button(file_panel, text="Save", command=self.save_types)
        b_save.pack(side="left", padx=6)
        b_validate = tk.Button(file_panel, text="Validate XML", command=self.validate_types)
        b_validate.pack(side="left", padx=6)

        self._types_toggle_widgets = [b_save, b_validate]

        adjust_panel = tk.LabelFrame(parent, text="Adjustments", fg=self.fg, bg=self.panel_bg, font=("Segoe UI", 11, "bold"))
        adjust_panel.pack(pady=6, fill="x")
        self.type_value = tk.Entry(adjust_panel, width=6)
        self.type_value.insert(0, "20")
        self.type_value.pack(side="left", padx=6)
        self.type_mode = tk.StringVar(value="Lower %")
        tk.OptionMenu(adjust_panel, self.type_mode, "Lower %", "Raise %", "Set Custom").pack(side="left", padx=6)

        self.nominal_var = tk.BooleanVar(value=True)
        self.lifetime_var = tk.BooleanVar(value=False)
        self.restock_var = tk.BooleanVar(value=False)
        self.cost_var = tk.BooleanVar(value=False)
        tk.Checkbutton(adjust_panel, text="Nominal", variable=self.nominal_var, bg=self.panel_bg, fg=self.fg, selectcolor=self.panel_bg).pack(side="left", padx=6)
        tk.Checkbutton(adjust_panel, text="Lifetime", variable=self.lifetime_var, bg=self.panel_bg, fg=self.fg, selectcolor=self.panel_bg).pack(side="left", padx=6)
        tk.Checkbutton(adjust_panel, text="Restock", variable=self.restock_var, bg=self.panel_bg, fg=self.fg, selectcolor=self.panel_bg).pack(side="left", padx=6)
        tk.Checkbutton(adjust_panel, text="Cost", variable=self.cost_var, bg=self.panel_bg, fg=self.fg, selectcolor=self.panel_bg).pack(side="left", padx=6)
        tk.Button(adjust_panel, text="Apply", command=self.apply_types_changes).pack(side="left", padx=6)

        text_frame = tk.Frame(parent, bg=self.bg)
        text_frame.pack(fill="both", expand=True, padx=8, pady=8)

        left = tk.Frame(text_frame, bg=self.bg)
        left.pack(side="left", fill="both", expand=True, padx=6)
        tk.Label(left, text="Original Types.xml", fg=self.fg, bg=self.bg).pack(anchor="w")
        self.types_original = self.create_text_with_line_numbers(left, filetype="xml")
        self.search_setup(left, self.types_original)

        right = tk.Frame(text_frame, bg=self.bg)
        right.pack(side="right", fill="both", expand=True, padx=6)
        tk.Label(right, text="Modified Types.xml", fg=self.fg, bg=self.bg).pack(anchor="w")
        self.types_modified = self.create_text_with_line_numbers(right, filetype="xml", enable_change_highlight=True)
        self.search_setup(right, self.types_modified)

    def load_types(self, path=None):
        if not path:
            path = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml"), ("All files", "*.*")])
        if not path:
            return
        try:
            tree = ET.parse(path)
            root = tree.getroot()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read XML: {e}")
            return
        pretty = self.prettify_xml(root)
        self.types_original.delete("1.0", tk.END)
        self.types_original.insert(tk.END, pretty)
        self.types_original._update_line_numbers()
        self.types_modified.delete("1.0", tk.END)
        self.types_modified.insert(tk.END, pretty)
        self.types_modified._update_line_numbers()
        self.file_path = path
        self.current_type = "types"
        self.set_status(f"Open file: {os.path.basename(path)} • types")
        self.highlight_diffs(self.types_original, self.types_modified)

    def save_types(self):
        content = self.types_modified.get("1.0", tk.END).strip()
        path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML Files", "*.xml")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("Saved", f"File saved: {path}")

    def validate_types(self):
        content = self.types_modified.get("1.0", tk.END).strip()
        try:
            ET.fromstring(content)
            messagebox.showinfo("Validation", "XML is valid")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid XML: {e}")

    def apply_types_changes(self):
        content = self.types_modified.get("1.0", tk.END).strip()
        try:
            root = ET.fromstring(content)
        except Exception:
            messagebox.showerror("Error", "Invalid XML in Modified Types")
            return
        try:
            val = float(self.type_value.get())
        except:
            messagebox.showerror("Error", "Value must be numeric")
            return
        targets = []
        if self.nominal_var.get():
            targets.append("nominal")
        if self.lifetime_var.get():
            targets.append("lifetime")
        if self.restock_var.get():
            targets.append("restock")
        if self.cost_var.get():
            targets.append("cost")
        for type_elem in root.findall("type"):
            for child in type_elem:
                if child.tag in targets:
                    try:
                        old = int(child.text)
                    except:
                        continue
                    if self.type_mode.get() == "Set Custom":
                        child.text = str(int(val))
                    else:
                        factor = 1 + (val/100.0) if self.type_mode.get() == "Raise %" else 1 - (val/100.0)
                        child.text = str(max(1, int(old * factor)))
        self.types_modified.delete("1.0", tk.END)
        self.types_modified.insert(tk.END, self.prettify_xml(root))
        self.types_modified._update_line_numbers()
        self.highlight_diffs(self.types_original, self.types_modified)

    def remove_tier(self):
        content = self.types_modified.get("1.0", tk.END).strip()
        try:
            root = ET.fromstring(content)
        except:
            messagebox.showerror("Error", "Invalid XML in Modified Types")
            return
        tier = self.tier_entry.get().strip()
        for type_elem in root.findall("type"):
            to_remove = []
            for child in list(type_elem):
                if child.tag.lower() == "usage" and child.text and child.text.strip().lower() == tier.lower():
                    to_remove.append(child)
            for elem in to_remove:
                type_elem.remove(elem)
        self.types_modified.delete("1.0", tk.END)
        self.types_modified.insert(tk.END, self.prettify_xml(root))
        self.types_modified._update_line_numbers()
        self.highlight_diffs(self.types_original, self.types_modified)

    def prettify_xml(self, elem, level=0):
        indent = "  "
        txt = ""
        space = "\n" + indent * level
        txt += f"<{elem.tag}"
        for k, v in elem.attrib.items():
            txt += f' {k}="{v}"'
        children = list(elem)
        if not children and not (elem.text and elem.text.strip()):
            txt += " />"
            return txt
        txt += ">"
        if elem.text and elem.text.strip():
            txt += elem.text.strip()
        for child in children:
            txt += space + self.prettify_xml(child, level+1)
        if children:
            txt += space
        txt += f"</{elem.tag}>"
        return txt

    # ------------------------
    # Text widget helper
    # ------------------------
    def create_text_with_line_numbers(self, parent, filetype="text", enable_change_highlight=False):
        container = tk.Frame(parent, bg=self.bg)
        container.pack(fill="both", expand=True)

        ln = tk.Text(container, width=5, padx=4, takefocus=0, border=0,
                     background="#2a2a2a", foreground=self.muted, font=self.ln_font, state="disabled")
        ln.pack(side="left", fill="y")

        text = tk.Text(container, wrap="none", undo=True, font=self.code_font,
                       background="#101214", foreground=self.fg, insertbackground=self.insert_color,
                       selectbackground="#3d6d3d", spacing3=4)
        text.pack(side="left", fill="both", expand=True)

        ysb = tk.Scrollbar(container, orient="vertical", command=lambda *args: (text.yview(*args), ln.yview(*args)))
        ysb.pack(side="right", fill="y")
        xsb = tk.Scrollbar(container, orient="horizontal", command=text.xview)
        xsb.pack(side="bottom", fill="x")
        text.config(yscrollcommand=ysb.set, xscrollcommand=xsb.set)

        text.tag_configure("changed_line", background="#1b4f1b")
        text.tag_configure("search", background="#ffeaa7")

        def update_line_numbers(event=None):
            ln.config(state="normal")
            ln.delete("1.0", tk.END)
            last = text.index("end-1c").split(".")[0]
            lines = "\n".join(str(i) for i in range(1, int(last) + 1))
            ln.insert("1.0", lines)
            ln.config(state="disabled")
            try:
                ln.yview_moveto(text.yview()[0])
            except:
                pass

        text.bind("<KeyRelease>", update_line_numbers)
        text.bind("<MouseWheel>", update_line_numbers)
        text.bind("<Button-1>", update_line_numbers)
        text.bind("<Configure>", update_line_numbers)
        text.bind("<FocusIn>", update_line_numbers)

        text._update_line_numbers = update_line_numbers
        text._line_numbers_widget = ln
        text._enable_change_highlight = enable_change_highlight

        if enable_change_highlight:
            def on_change_event(event=None):
                update_line_numbers()
            text.bind("<<Paste>>", on_change_event)
            text.bind("<KeyRelease>", on_change_event, add='+')

        return text

    # ------------------------
    # Search bar
    # ------------------------
    def search_setup(self, parent, text_widget):
        frame = tk.Frame(parent, bg=self.bg)
        frame.pack(fill="x", pady=(4, 8))
        tk.Label(frame, text="Search:", fg=self.fg, bg=self.bg).pack(side="left", padx=(2,4))
        search_entry = tk.Entry(frame)
        search_entry.pack(side="left", padx=4)
        case_var = tk.BooleanVar(value=False)
        whole_var = tk.BooleanVar(value=False)
        regex_var = tk.BooleanVar(value=False)
        tk.Checkbutton(frame, text="Case", variable=case_var, bg=self.bg, fg=self.fg, selectcolor=self.bg).pack(side="left", padx=4)
        tk.Checkbutton(frame, text="Whole word", variable=whole_var, bg=self.bg, fg=self.fg, selectcolor=self.bg).pack(side="left", padx=4)
        tk.Checkbutton(frame, text="Regex", variable=regex_var, bg=self.bg, fg=self.fg, selectcolor=self.bg).pack(side="left", padx=4)

        def find_next():
            needle = search_entry.get()
            if not needle:
                return
            text_widget.tag_remove("search", "1.0", tk.END)
            content = text_widget.get("1.0", tk.END)
            try:
                if regex_var.get():
                    pattern = needle if case_var.get() else "(?i)" + needle
                    m = re.search(pattern, content)
                    if not m:
                        messagebox.showinfo("Search", "No match")
                        return
                    start = "1.0 + %dc" % m.start()
                    end = "1.0 + %dc" % m.end()
                else:
                    if whole_var.get():
                        pat = r"\b" + re.escape(needle) + r"\b"
                        if case_var.get():
                            m = re.search(pat, content)
                        else:
                            m = re.search(pat, content, flags=re.IGNORECASE)
                        if not m:
                            messagebox.showinfo("Search", "No match")
                            return
                        start = "1.0 + %dc" % m.start()
                        end = "1.0 + %dc" % m.end()
                    else:
                        if case_var.get():
                            idx = text_widget.search(needle, tk.INSERT, tk.END)
                        else:
                            idx = text_widget.search(needle, "1.0", tk.END, nocase=True)
                        if not idx:
                            messagebox.showinfo("Search", "No match")
                            return
                        start = idx
                        end = f"{idx}+{len(needle)}c"
                text_widget.tag_add("search", start, end)
                text_widget.tag_config("search", background="#ffeaa7")
                text_widget.mark_set(tk.INSERT, end)
                text_widget.see(start)
            except Exception as e:
                messagebox.showerror("Search error", str(e))

        def find_prev():
            needle = search_entry.get()
            if not needle:
                return
            content = text_widget.get("1.0", tk.END)
            insert_pos = text_widget.index(tk.INSERT)
            try:
                matches = []
                if regex_var.get():
                    pattern = needle if case_var.get() else "(?i)" + needle
                    for m in re.finditer(pattern, content):
                        matches.append((m.start(), m.end()))
                else:
                    if whole_var.get():
                        pat = r"\b" + re.escape(needle) + r"\b"
                        flags = 0 if case_var.get() else re.IGNORECASE
                        for m in re.finditer(pat, content, flags=flags):
                            matches.append((m.start(), m.end()))
                    else:
                        if case_var.get():
                            idx = content.find(needle, 0)
                            while idx != -1:
                                matches.append((idx, idx+len(needle)))
                                idx = content.find(needle, idx+1)
                        else:
                            lcontent = content.lower()
                            ln = needle.lower()
                            idx = lcontent.find(ln, 0)
                            while idx != -1:
                                matches.append((idx, idx+len(needle)))
                                idx = lcontent.find(ln, idx+1)
                if not matches:
                    messagebox.showinfo("Search", "No match")
                    return
                chosen = matches[-1]
                s,e = chosen
                start = "1.0 + %dc" % s
                end = "1.0 + %dc" % e
                text_widget.tag_remove("search", "1.0", tk.END)
                text_widget.tag_add("search", start, end)
                text_widget.tag_config("search", background="#ffeaa7")
                text_widget.mark_set(tk.INSERT, end)
                text_widget.see(start)
            except Exception as e:
                messagebox.showerror("Search error", str(e))

        tk.Button(frame, text="Prev", command=find_prev).pack(side="left", padx=4)
        tk.Button(frame, text="Next", command=find_next).pack(side="left", padx=4)

    # ------------------------
    # Diff highlighting
    # ------------------------
    def highlight_diffs(self, original_widget, modified_widget):
        orig_text = original_widget.get("1.0", tk.END).splitlines()
        mod_text = modified_widget.get("1.0", tk.END).splitlines()

        modified_widget.tag_remove("changed_line", "1.0", tk.END)

        max_lines = max(len(orig_text), len(mod_text))
        for i in range(max_lines):
            o = orig_text[i] if i < len(orig_text) else None
            m = mod_text[i] if i < len(mod_text) else None
            if o is None and m is not None:
                start = f"{i+1}.0"
                end = f"{i+1}.end"
                modified_widget.tag_add("changed_line", start, end)
            elif m is None:
                continue
            else:
                if self.normalize_line(o) != self.normalize_line(m):
                    start = f"{i+1}.0"
                    end = f"{i+1}.end"
                    modified_widget.tag_add("changed_line", start, end)
        modified_widget.update_idletasks()

    def normalize_line(self, s):
        if s is None:
            return ""
        return re.sub(r"\s+", " ", s.strip())

    # ------------------------
    # Shortcuts
    # ------------------------
    def open_shortcut(self):
        idx = self.notebook.index(self.notebook.select())
        if idx == 0:
            self.load_market()
        else:
            self.load_types()

    def save_shortcut(self):
        idx = self.notebook.index(self.notebook.select())
        if idx == 0:
            self.save_market()
        else:
            self.save_types()

    def reset_shortcut(self):
        idx = self.notebook.index(self.notebook.select())
        if idx == 0:
            self.reset_market()
        else:
            content = self.types_original.get("1.0", tk.END)
            if content.strip():
                self.types_modified.delete("1.0", tk.END)
                self.types_modified.insert(tk.END, content)
                self.types_modified._update_line_numbers()
                self.highlight_diffs(self.types_original, self.types_modified)

    def validate_shortcut(self):
        idx = self.notebook.index(self.notebook.select())
        if idx == 0:
            self.validate_market()
        else:
            self.validate_types()

# Main
if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#111111")
    app = MarketConfigEditor(root)
    root.mainloop()
