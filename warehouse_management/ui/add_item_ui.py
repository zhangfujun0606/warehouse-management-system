import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from warehouse_management.item import Item

def add_item_window(window, warehouse1, warehouse2, update_inventory, save_data, history_log, logged_in_user):
    add_window = tk.Toplevel(window)
    add_window.title("進貨")
    
    # 設定視窗可以彈性變動
    add_window.grid_rowconfigure(5, weight=1)
    add_window.grid_columnconfigure(0, weight=1)
    add_window.grid_columnconfigure(1, weight=1)

    # 常數定義
    DATE_RANGE = 365

    def create_combobox(parent, label_text, row, column, var, values=None):
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=column, padx=5, pady=5, sticky="e")
        combobox = ttk.Combobox(parent, textvariable=var, values=values)
        combobox.grid(row=row, column=column + 1, padx=5, pady=5, sticky="w")
        return combobox
    
    def create_entry(parent, label_text, row, column, var=None, validate_func=None):
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=column, padx=5, pady=5, sticky="e")
        entry = ttk.Entry(parent, textvariable=var)
        if validate_func:
            entry.config(validate="key", validatecommand=(entry.register(validate_func), '%P'))
        entry.grid(row=row, column=column + 1, padx=5, pady=5, sticky="w")
        return entry
    
    def validate_integer(new_value):
      if not new_value:
        return True
      try:
        int(new_value)
        return True
      except ValueError:
        return False

    def validate_positive_integer(new_value):
        if not new_value:
           return True
        try:
           value = int(new_value)
           return value > 0
        except ValueError:
           return False

    # Warehouse selection
    warehouse_var = tk.StringVar(value="倉庫1")
    warehouse_combobox = create_combobox(add_window, "選擇倉庫:", 0, 0, warehouse_var, ["倉庫1", "倉庫2"])

    # Item name selection
    name_var = tk.StringVar()
    name_combobox = create_combobox(add_window, "物品名稱:", 1, 0, name_var)

    # Expiry date selection
    expiry_date_var = tk.StringVar()
    expiry_date_combobox = create_combobox(add_window, "有效日期:", 2, 0, expiry_date_var)
    
    # Quantity input
    quantity_var = tk.StringVar()
    quantity_entry = create_entry(add_window, "數量:", 3, 0, quantity_var, validate_positive_integer)
    
    # Note input
    note_var = tk.StringVar()
    note_entry = create_entry(add_window, "備註:", 4, 0, note_var)

    def generate_date_options():
      today = datetime.date.today()
      return [(today + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(DATE_RANGE)]

    def update_add_item_options(*args):
        warehouse_name = warehouse_var.get()
        warehouse = warehouse1 if warehouse_name == "倉庫1" else warehouse2
        names = warehouse.get_item_names(include_zero=True)

        name_combobox['values'] = names
        if names and not name_var.get(): #只有在 name_var 沒有值時，才設定 name_var 的預設值。
            name_var.set(names[0]) # Set default item name
        
        expiry_date_combobox['values'] = generate_date_options()
        expiry_date_var.set(datetime.date.today().strftime("%Y-%m-%d")) # Set default date
    
    warehouse_var.trace("w", update_add_item_options)
    
    #初始呼叫
    update_add_item_options()

    add_items_list = []
    
    #TreeView
    columns = ('name', 'expiry_date', 'quantity', 'warehouse', 'note')
    item_tree = ttk.Treeview(add_window, columns=columns, show='headings')
    item_tree.heading('name', text='物品名稱')
    item_tree.heading('expiry_date', text='有效日期')
    item_tree.heading('quantity', text='數量')
    item_tree.heading('warehouse', text='倉庫')
    item_tree.heading('note', text='備註')
    item_tree.column('name', anchor=tk.CENTER)
    item_tree.column('expiry_date', anchor=tk.CENTER)
    item_tree.column('quantity', anchor=tk.CENTER)
    item_tree.column('warehouse', anchor=tk.CENTER)
    item_tree.column('note', anchor=tk.CENTER)
    item_tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

    def get_date_input(date_str):
      try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
      except ValueError:
        messagebox.showerror("錯誤", "日期格式錯誤，請使用 YYYY-MM-DD")
        return None
    
    def clear_input():
        quantity_var.set("")
        note_var.set("")
        
    def add_item_to_list():
        name = name_var.get()
        expiry_date_str = expiry_date_var.get()
        quantity = quantity_var.get()
        note = note_var.get()
        warehouse = warehouse_var.get()
        
        if not all([name, quantity, expiry_date_str]):
            messagebox.showerror("錯誤", "請填寫所有欄位")
            return
        
        expiry_date = get_date_input(expiry_date_str)
        if not expiry_date:
           return
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                messagebox.showerror("錯誤", "數量必須大於 0")
                return
        except ValueError:
            messagebox.showerror("錯誤", "數量請輸入整數")
            return
        
        new_item = Item(name,quantity,expiry_date,note, warehouse)
        add_items_list.append(new_item)
        item_tree.insert('', 'end', values=(name, expiry_date.strftime('%Y-%m-%d'), quantity, warehouse, note))
        clear_input()
    
    def edit_item_list():
        selected_item = item_tree.selection()
        if not selected_item:
            messagebox.showerror("錯誤", "請選擇要修改的項目")
            return
        values = item_tree.item(selected_item, 'values')
        name_var.set(values[0])
        expiry_date_var.set(values[1])
        quantity_var.set(values[2])
        warehouse_var.set(values[3])
        note_var.set(values[4])

        item_tree.delete(selected_item)
        for item in add_items_list:
          if item.name == values[0] and item.expiry_date == get_date_input(values[1]) and item.quantity == int(values[2]):
            add_items_list.remove(item)
    
    def delete_item_list():
      selected_item = item_tree.selection()
      if not selected_item:
        messagebox.showerror("錯誤", "請選擇要刪除的項目")
        return
      values = item_tree.item(selected_item, 'values')
      for item in add_items_list:
        if item.name == values[0] and item.expiry_date == get_date_input(values[1]) and item.quantity == int(values[2]):
          add_items_list.remove(item)
      item_tree.delete(selected_item)
    
    button_frame = ttk.Frame(add_window)
    button_frame.grid(row=6, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
    
    add_to_list_button = ttk.Button(button_frame, text="新增至清單", command=add_item_to_list)
    add_to_list_button.pack(side="right", padx=5)
    
    edit_to_list_button = ttk.Button(button_frame, text="修改清單項目", command=edit_item_list)
    edit_to_list_button.pack(side="right", padx=5)
    
    delete_to_list_button = ttk.Button(button_frame, text="刪除清單項目", command=delete_item_list)
    delete_to_list_button.pack(side="right", padx=5)
    
    def add_item_action():
      if messagebox.askyesno("確認", "確定要進貨嗎？"):
        warehouse_name = warehouse_var.get()
        warehouse = warehouse1 if warehouse_name == "倉庫1" else warehouse2
        
        if add_items_list:
            for item in add_items_list:
              warehouse_item = warehouse1 if item.warehouse == "倉庫1" else warehouse2
              warehouse_item.add_item(item)

              history_log.append(
                 {
                  "type": "進貨",
                  "name": item.name,
                  "quantity": item.quantity,
                  "expiry_date": item.expiry_date.strftime("%Y-%m-%d"),
                  "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  "user": logged_in_user,
                   "note": item.note,
                   "warehouse": item.warehouse
              })
        update_inventory()
        save_data()
        messagebox.showinfo("成功", "進貨成功")
        add_window.destroy()

    add_button = ttk.Button(button_frame, text="確認進貨", command=add_item_action)
    add_button.pack(side="right", padx=5)