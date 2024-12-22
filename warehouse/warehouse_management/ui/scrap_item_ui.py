import tkinter as tk
from tkinter import ttk, messagebox
import datetime

def scrap_item_window(window, warehouse1, warehouse2, update_inventory, save_data, history_log, logged_in_user):
    scrap_window = tk.Toplevel(window)
    scrap_window.title("報廢")

    # 設定視窗可以彈性變動
    scrap_window.grid_rowconfigure(5, weight=1)
    scrap_window.grid_columnconfigure(0, weight=1)
    scrap_window.grid_columnconfigure(1, weight=1)

    warehouse_label = ttk.Label(scrap_window, text="選擇倉庫:")
    warehouse_label.grid(row=0, column=0, padx=5, pady=5)
    warehouse_var = tk.StringVar(value="倉庫1")
    warehouse_combobox = ttk.Combobox(scrap_window, textvariable=warehouse_var, values=["倉庫1", "倉庫2"])
    warehouse_combobox.grid(row=0, column=1, padx=5, pady=5)

    name_label = ttk.Label(scrap_window, text="物品名稱:")
    name_label.grid(row=1, column=0, padx=5, pady=5)
    name_var = tk.StringVar()
    name_combobox = ttk.Combobox(scrap_window, textvariable=name_var)
    name_combobox.grid(row=1, column=1, padx=5, pady=5)

    expiry_date_label = ttk.Label(scrap_window, text="有效日期:")
    expiry_date_label.grid(row=2, column=0, padx=5, pady=5)
    expiry_date_var = tk.StringVar()
    expiry_date_combobox = ttk.Combobox(scrap_window, textvariable=expiry_date_var)
    expiry_date_combobox.grid(row=2, column=1, padx=5, pady=5)

    def update_expiry_options(*args):
        warehouse_name = warehouse_var.get()
        item_name = name_var.get()
        if warehouse_name == "倉庫1":
            dates = warehouse1.get_expiry_dates(item_name)
        else:
            dates = warehouse2.get_expiry_dates(item_name)

        filtered_dates = []
        for date in dates:
            if item_name:
                for item in warehouse1.inventory.values():
                    if item.name == item_name and item.expiry_date == date and item.quantity > 0:
                        filtered_dates.append(date)
                        break
                for item in warehouse2.inventory.values():
                    if item.name == item_name and item.expiry_date == date and item.quantity > 0:
                        filtered_dates.append(date)
                        break
            else:
                filtered_dates = dates
        expiry_date_combobox['values'] = [date.strftime("%Y-%m-%d") for date in filtered_dates]
        if filtered_dates:
            expiry_date_var.set(filtered_dates[0].strftime("%Y-%m-%d"))
        else:
            expiry_date_combobox['values'] = []
            expiry_date_var.set("")

    def update_scrap_item_options(*args):
        warehouse_name = warehouse_var.get()
        if warehouse_name == "倉庫1":
            names = warehouse1.get_item_names()
        else:
            names = warehouse2.get_item_names()
        name_combobox['values'] = names
        if names:
          name_var.set(names[0])
          update_expiry_options()
        else:
          name_combobox['values'] = []
          name_var.set("")
          expiry_date_combobox['values'] = []
          expiry_date_var.set("")

    name_var.trace('w', update_expiry_options)
    warehouse_var.trace("w", update_scrap_item_options)
    update_scrap_item_options()

    quantity_label = ttk.Label(scrap_window, text="數量:")
    quantity_label.grid(row=3, column=0, padx=5, pady=5)
    quantity_entry = ttk.Entry(scrap_window)
    quantity_entry.grid(row=3, column=1, padx=5, pady=5)

    note_label = ttk.Label(scrap_window, text="備註:")
    note_label.grid(row=4, column=0, padx=5, pady=5)
    note_entry = ttk.Entry(scrap_window)
    note_entry.grid(row=4, column=1, padx=5, pady=5)
    
    scrap_items_list = []

    columns = ('name', 'expiry_date', 'quantity', 'warehouse', 'note') # Add warehouse column
    item_tree = ttk.Treeview(scrap_window, columns=columns, show='headings')
    item_tree.heading('name', text='物品名稱')
    item_tree.heading('expiry_date', text='有效日期')
    item_tree.heading('quantity', text='數量')
    item_tree.heading('warehouse', text='倉庫') # Add warehouse heading
    item_tree.heading('note', text='備註')
    item_tree.column('name', anchor=tk.CENTER)
    item_tree.column('expiry_date', anchor=tk.CENTER)
    item_tree.column('quantity', anchor=tk.CENTER)
    item_tree.column('warehouse', anchor=tk.CENTER) # Add warehouse column
    item_tree.column('note', anchor=tk.CENTER)
    item_tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
    
    def get_date_input(date_str):
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
           messagebox.showerror("錯誤", "日期格式錯誤，請使用 YYYY-MM-DD")
           return None

    def add_scrap_item_to_list():
        name = name_var.get()
        expiry_date_str = expiry_date_var.get()
        if not expiry_date_str:
           messagebox.showerror("錯誤", "請填寫所有欄位")
           return
        
        expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
        quantity = quantity_entry.get()
        note = note_entry.get()
        warehouse = warehouse_var.get()
        
        if not all([name, quantity, expiry_date]):
           messagebox.showerror("錯誤", "請填寫所有欄位")
           return
                
        try:
          quantity = int(quantity)
        except ValueError:
            messagebox.showerror("錯誤", "數量請輸入整數")
            return

        scrap_items_list.append((name,expiry_date,quantity, warehouse, note))
        item_tree.insert('', 'end', values=(name, expiry_date.strftime('%Y-%m-%d'), quantity, warehouse, note))
        quantity_entry.delete(0, 'end')
        note_entry.delete(0,'end')
    
    def edit_scrap_item_list():
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
        note_entry.insert(0,values[4])
        
        item_tree.delete(selected_item)
        for item in scrap_items_list:
           if item[0] == values[0] and item[1] == get_date_input(values[1]) and item[2] == int(values[2]):
              scrap_items_list.remove(item)
    
    def delete_scrap_item_list():
        selected_item = item_tree.selection()
        if not selected_item:
            messagebox.showerror("錯誤", "請選擇要刪除的項目")
            return
        values = item_tree.item(selected_item, 'values')
        for item in scrap_items_list:
            if item[0] == values[0] and item[1] == get_date_input(values[1]) and item[2] == int(values[2]):
                scrap_items_list.remove(item)
        item_tree.delete(selected_item)
    
    button_frame = ttk.Frame(scrap_window)
    button_frame.grid(row=6, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
    
    add_to_list_button = ttk.Button(button_frame, text="新增", command=add_scrap_item_to_list)
    add_to_list_button.pack(side="right", padx=5)

    edit_to_list_button = ttk.Button(button_frame, text="修改", command=edit_scrap_item_list)
    edit_to_list_button.pack(side="right", padx=5)

    delete_to_list_button = ttk.Button(button_frame, text="刪除", command=delete_scrap_item_list)
    delete_to_list_button.pack(side="right", padx=5)

    def scrap_item_action():
        if messagebox.askyesno("確認", "確定要報廢嗎？"):
            warehouse_name = warehouse_var.get()
            note = note_entry.get()
            all_success = True
            if scrap_items_list:
                if warehouse_name == "倉庫1":
                    for name,expiry_date, quantity, warehouse_item, note_item in scrap_items_list:
                        result = warehouse1.remove_item(name, expiry_date, quantity)
                        if not result:
                            all_success = False
                        else:
                            history_log.append({
                                "type": "報廢",
                                "name": name,
                                "quantity": quantity,
                                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "user": logged_in_user,
                                "note": note_item,
                                "warehouse": warehouse_item
                            })
                else:
                    for name, expiry_date, quantity, warehouse_item, note_item in scrap_items_list:
                        result = warehouse2.remove_item(name, expiry_date, quantity)
                        if not result:
                            all_success = False
                        else:
                            history_log.append({
                                "type": "報廢",
                                "name": name,
                                "quantity": quantity,
                                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "user": logged_in_user,
                                "note": note_item,
                                "warehouse": warehouse_item
                            })

            if all_success:
                update_inventory()
                save_data()
                messagebox.showinfo("成功", "報廢成功")
                scrap_window.destroy()

    scrap_button = ttk.Button(button_frame, text="確認報廢", command=scrap_item_action)
    scrap_button.pack(side="right", padx=5)