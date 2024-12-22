import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from ..item import Item

def add_item_window(window, warehouse1, warehouse2, update_inventory, save_data, history_log, logged_in_user):
    add_window = tk.Toplevel(window)
    add_window.title("進貨")
    
    # 設定視窗可以彈性變動
    add_window.grid_rowconfigure(5, weight=1)
    add_window.grid_columnconfigure(0, weight=1)
    add_window.grid_columnconfigure(1, weight=1)

    warehouse_label = ttk.Label(add_window, text="選擇倉庫:")
    warehouse_label.grid(row=0, column=0, padx=5, pady=5)
    warehouse_var = tk.StringVar(value="倉庫1")
    warehouse_combobox = ttk.Combobox(add_window, textvariable=warehouse_var, values=["倉庫1", "倉庫2"])
    warehouse_combobox.grid(row=0, column=1, padx=5, pady=5)

    name_label = ttk.Label(add_window, text="物品名稱:")
    name_label.grid(row=1, column=0, padx=5, pady=5)
    name_var = tk.StringVar()
    name_combobox = ttk.Combobox(add_window, textvariable=name_var)
    name_combobox.grid(row=1, column=1, padx=5, pady=5)

    expiry_date_label = ttk.Label(add_window, text="有效日期:")
    expiry_date_label.grid(row=2, column=0, padx=5, pady=5)
    expiry_date_var = tk.StringVar()
    expiry_date_combobox = ttk.Combobox(add_window, textvariable=expiry_date_var)
    expiry_date_combobox.grid(row=2, column=1, padx=5, pady=5)

    def generate_date_options():
        today = datetime.date.today()
        dates = []
        for i in range(365):
            date = today + datetime.timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))
        return dates

    def update_add_item_options(*args):
        warehouse_name = warehouse_var.get()
        if warehouse_name == "倉庫1":
            names = warehouse1.get_item_names(include_zero=True)
        else:
            names = warehouse2.get_item_names(include_zero=True)
        name_combobox['values'] = names
        if names:
            name_var.set(names[0])
        expiry_date_combobox['values'] = generate_date_options()
        expiry_date_var.set(datetime.date.today().strftime("%Y-%m-%d"))

    warehouse_var.trace("w", update_add_item_options)
    update_add_item_options()

    quantity_label = ttk.Label(add_window, text="數量:")
    quantity_label.grid(row=3, column=0, padx=5, pady=5)
    quantity_entry = ttk.Entry(add_window)
    quantity_entry.grid(row=3, column=1, padx=5, pady=5)

    note_label = ttk.Label(add_window, text="備註:")
    note_label.grid(row=4, column=0, padx=5, pady=5)
    note_entry = ttk.Entry(add_window)
    note_entry.grid(row=4, column=1, padx=5, pady=5)
    
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
    
    def add_item_to_list():
        name = name_var.get()
        expiry_date_str = expiry_date_var.get()
        quantity = quantity_entry.get()
        note = note_entry.get()
        warehouse = warehouse_var.get()
        if not expiry_date_str:
           messagebox.showerror("錯誤", "請填寫所有欄位")
           return
        expiry_date = get_date_input(expiry_date_str)
        if not all([name, quantity, expiry_date]):
           messagebox.showerror("錯誤", "請填寫所有欄位")
           return
        try:
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("錯誤", "數量請輸入整數")
            return
        
        add_items_list.append(Item(name,quantity,expiry_date,note, warehouse))
        item_tree.insert('', 'end', values=(name, expiry_date.strftime('%Y-%m-%d'), quantity, warehouse, note))
        
        quantity_entry.delete(0, 'end')
        note_entry.delete(0, 'end')
    
    
    def edit_item_list():
        selected_item = item_tree.selection()
        if not selected_item:
            messagebox.showerror("錯誤", "請選擇要修改的項目")
            return
        values = item_tree.item(selected_item, 'values')
        name_var.set(values[0])
        expiry_date_var.set(values[1])
        quantity_entry.delete(0,'end')
        quantity_entry.insert(0,values[2])
        note_entry.delete(0,'end')
        note_entry.insert(0,values[3])
        
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
    
    add_to_list_button = ttk.Button(button_frame, text="新增", command=add_item_to_list)
    add_to_list_button.pack(side="right", padx=5)
    
    edit_to_list_button = ttk.Button(button_frame, text="修改", command=edit_item_list)
    edit_to_list_button.pack(side="right", padx=5)
    
    delete_to_list_button = ttk.Button(button_frame, text="刪除", command=delete_item_list)
    delete_to_list_button.pack(side="right", padx=5)
    
    def add_item_action():
        if messagebox.askyesno("確認", "確定要進貨嗎？"):
            warehouse_name = warehouse_var.get()
            note = note_entry.get()
            if add_items_list:
                if warehouse_name == "倉庫1":
                    for item in add_items_list:
                        warehouse1.add_item(item)
                        history_log.append({
                            "type": "進貨",
                            "name": item.name,
                            "quantity": item.quantity,
                            "expiry_date": item.expiry_date.strftime("%Y-%m-%d"),
                            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "user": logged_in_user,
                            "note": item.note,
                            "warehouse": warehouse_name
                        })
                else:
                    for item in add_items_list:
                        warehouse2.add_item(item)
                        history_log.append({
                            "type": "進貨",
                            "name": item.name,
                            "quantity": item.quantity,
                            "expiry_date": item.expiry_date.strftime("%Y-%m-%d"),
                            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "user": logged_in_user,
                            "note": item.note,
                            "warehouse": warehouse_name
                        })

            update_inventory()
            save_data()
            messagebox.showinfo("成功", "進貨成功")
            add_window.destroy()

    add_button = ttk.Button(button_frame, text="確認進貨", command=add_item_action)
    add_button.pack(side="right", padx=5)