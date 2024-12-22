import tkinter as tk
from tkinter import ttk, messagebox, Menu, filedialog
import datetime
from .add_item_ui import add_item_window
from .remove_item_ui import remove_item_window
from .history_ui import display_history_window
from .scrap_item_ui import scrap_item_window
# 移除 report 相關的 import
# from .report_window import ReportWindow
# from ..report_generator import generate_report
import openpyxl
from openpyxl.styles import Alignment
import os

def setup_main_window(window, warehouse1, warehouse2, save_data, history_log, logged_in_user):
    inventory_data = []  # Define inventory_data here

    # 使用 PanedWindow 分隔視窗
    paned_window = ttk.Panedwindow(window, orient=tk.VERTICAL)
    paned_window.grid(row=2, column=0, columnspan=4, sticky='nsew', padx=10, pady=10)

    # 設定視窗可以彈性變動
    window.grid_rowconfigure(2, weight=1)
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)
    window.grid_columnconfigure(2, weight=1)
    window.grid_columnconfigure(3, weight=1)

    # Treeview for displaying inventory
    columns = ('name', 'quantity', 'expiry_date', 'warehouse', 'note')
    inventory_tree = ttk.Treeview(paned_window, columns=columns, show='headings', height=15)
    inventory_tree.heading('name', text='品名')
    inventory_tree.heading('quantity', text='數量')
    inventory_tree.heading('expiry_date', text='有效日期')
    inventory_tree.heading('warehouse', text='倉庫')
    inventory_tree.heading('note', text='備註')
    inventory_tree.column('name', anchor=tk.CENTER)
    inventory_tree.column('quantity', anchor=tk.CENTER)
    inventory_tree.column('expiry_date', anchor=tk.CENTER)
    inventory_tree.column('warehouse', anchor=tk.CENTER)
    inventory_tree.column('note', anchor=tk.CENTER)
    inventory_tree.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')
    paned_window.add(inventory_tree)

    filter_vars = {col: tk.StringVar() for col in columns}

    def create_filter_menu(col, event, filtered_data):
        filter_menu = Menu(window, tearoff=0)
        values = sorted(list(set(str(item[i]) for item in filtered_data for i, c in enumerate(columns) if c == col)))
        
        filter_menu.add_command(label="全部", command=lambda c=col: set_filter(c, ""))
        for value in values:
            filter_menu.add_command(label=value, command=lambda c=col, v=value: set_filter(c, v))
        
        filter_menu.tk_popup(event.x_root, event.y_root)

    def set_filter(col, value):
        filter_vars[col].set(value)
        update_inventory(window, warehouse1, warehouse2, filter_vars, inventory_tree)

    inventory_tree.bind("<Button-1>", lambda event: handle_click(event, inventory_tree))
    def handle_click(event, tree):
        col_id = tree.identify_column(event.x)
        if col_id and col_id != "#all":  # 確保點擊的是標題欄
            col_index = int(col_id[1:]) - 1
            col = columns[col_index]
            filtered_data = get_visible_data(inventory_tree)
            create_filter_menu(col, event, filtered_data)

    # 移除倉庫選擇下拉選單
    # warehouse_label = ttk.Label(window, text="選擇倉庫:")
    # warehouse_label.grid(row=0, column=0, padx=5, pady=5)
    # warehouse_combobox = ttk.Combobox(window, textvariable=warehouse_var, values=["全部","倉庫1", "倉庫2"])
    # warehouse_combobox.grid(row=0, column=1, padx=5, pady=5)

    # 創建按鈕
    add_button = ttk.Button(window, text="進貨", command=lambda: add_item_window(window, warehouse1, warehouse2, lambda: update_inventory(window, warehouse1, warehouse2, filter_vars, inventory_tree), save_data, history_log, logged_in_user))
    add_button.grid(row=1, column=0, padx=10, pady=10)

    remove_button = ttk.Button(window, text="出貨", command=lambda: remove_item_window(window, warehouse1, warehouse2, lambda: update_inventory(window, warehouse1, warehouse2, filter_vars, inventory_tree), save_data, history_log, logged_in_user))
    remove_button.grid(row=1, column=1, padx=10, pady=10)

    history_button = ttk.Button(window, text="歷史紀錄", command=lambda: display_history_window(window, history_log))
    history_button.grid(row=1, column=2, padx=10, pady=10)

    scrap_button = ttk.Button(window, text="報廢", command=lambda: scrap_item_window(window, warehouse1, warehouse2, lambda: update_inventory(window, warehouse1, warehouse2, filter_vars, inventory_tree), save_data, history_log, logged_in_user))
    scrap_button.grid(row=1, column=3, padx=10, pady=10)
    
    # 移除 "生成報表" 按鈕
    # report_button = ttk.Button(window, text="生成報表", command=lambda: export_report(window, warehouse1, warehouse2, history_log, logged_in_user))
    # report_button.grid(row=1, column=4, padx=10, pady=10)

    def get_visible_data(tree):
        visible_data = []
        for item in tree.get_children():
            visible_data.append(tree.item(item)['values'])
        return visible_data

    def update_inventory(window, warehouse1, warehouse2, filter_vars, inventory_tree):
        inventory_tree.delete(*inventory_tree.get_children())
        nonlocal inventory_data
        inventory_data = []
        inventory_data.extend(warehouse1.display_inventory())
        inventory_data.extend(warehouse2.display_inventory())

        # Apply filters
        filtered_data = []
        for item in inventory_data:
            if all(
                (not filter_vars[col].get() or str(item[i]) == filter_vars[col].get())
                for i, col in enumerate(columns) if filter_vars[col].get()
            ):
                filtered_data.append(item)

        for col in columns:
            heading_text = inventory_tree.heading(col, "text")
            if filter_vars[col].get() == "" or filter_vars[col].get() is None:
                if heading_text.endswith(" (*)"):
                    inventory_tree.heading(col, text=heading_text[:-4])
            elif "(*)" not in heading_text:
                inventory_tree.heading(col, text=f"{heading_text} (*)")

        for item in filtered_data:
            expiry_date_str = item[2]
            expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            days_left = (expiry_date - datetime.date.today()).days
            if days_left <= 0:
                inventory_tree.insert('', 'end', values=item, tags=('expired',))
            elif days_left <= 3:
                inventory_tree.insert('', 'end', values=item, tags=('warning',))
            else:
                inventory_tree.insert('', 'end', values=item)
        
        inventory_tree.tag_configure('expired', background='red')
        inventory_tree.tag_configure('warning', background='orange')
    
    update_inventory(window, warehouse1, warehouse2, filter_vars, inventory_tree)

    def on_closing():
        if messagebox.askokcancel("關閉", "確定要關閉程式嗎？"):
            save_data()
            window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_closing)