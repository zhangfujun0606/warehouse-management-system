import tkinter as tk
from tkinter import ttk, messagebox
import datetime

def remove_item_window(window, warehouse1, warehouse2, update_inventory, save_data, history_log, logged_in_user):
    remove_window = tk.Toplevel(window)
    remove_window.title("出貨")

    # 設定視窗可以彈性變動
    remove_window.grid_rowconfigure(5, weight=1)
    remove_window.grid_columnconfigure(0, weight=1)
    remove_window.grid_columnconfigure(1, weight=1)
    
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
        
    def get_date_input(date_str):
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("錯誤", "日期格式錯誤，請使用 YYYY-MM-DD")
            return None

    def clear_input():
        quantity_var.set("")
        note_var.set("")

    # Warehouse selection
    warehouse_var = tk.StringVar(value="倉庫1")
    warehouse_combobox = create_combobox(remove_window, "選擇倉庫:", 0, 0, warehouse_var, ["倉庫1", "倉庫2"])

    # Item name selection
    name_var = tk.StringVar()
    name_combobox = create_combobox(remove_window, "物品名稱:", 1, 0, name_var)

    # Expiry date selection
    expiry_date_var = tk.StringVar()
    expiry_date_combobox = create_combobox(remove_window, "有效日期:", 2, 0, expiry_date_var)
    
    # Quantity input
    quantity_var = tk.StringVar()
    quantity_entry = create_entry(remove_window, "數量:", 3, 0, quantity_var, validate_positive_integer)
    
    # Note input
    note_var = tk.StringVar()
    note_entry = create_entry(remove_window, "備註:", 4, 0, note_var)

    def update_expiry_options(*args):
        warehouse_name = warehouse_var.get()
        item_name = name_var.get()
        warehouse = warehouse1 if warehouse_name == "倉庫1" else warehouse2
        dates = warehouse.get_expiry_dates(item_name)
        
        filtered_dates = [date for date in dates if item_name and any(
           item.name == item_name and item.expiry_date == date and item.quantity > 0
           for item in warehouse1.inventory.values()
        ) or any(
             item.name == item_name and item.expiry_date == date and item.quantity > 0
             for item in warehouse2.inventory.values()
        )] if item_name else dates

        expiry_date_combobox['values'] = [date.strftime("%Y-%m-%d") for date in filtered_dates]
        if filtered_dates:
            expiry_date_var.set(filtered_dates[0].strftime("%Y-%m-%d"))
        else:
            expiry_date_combobox['values'] = []
            expiry_date_var.set("")
    
    def update_remove_item_options(*args):
        warehouse_name = warehouse_var.get()
        warehouse = warehouse1 if warehouse_name == "倉庫1" else warehouse2
        names = warehouse.get_item_names()

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
    warehouse_var.trace("w", update_remove_item_options)
    update_remove_item_options()

    remove_items_list = []

    columns = ('name', 'expiry_date', 'quantity', 'warehouse', 'note')
    item_tree = ttk.Treeview(remove_window, columns=columns, show='headings')
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

    def add_remove_item_to_list():
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
        
      remove_items_list.append((name,expiry_date,quantity, warehouse, note))
      item_tree.insert('', 'end', values=(name, expiry_date.strftime('%Y-%m-%d'), quantity, warehouse, note))
      clear_input()
    
    def edit_remove_item_list():
        selected_item = item_tree.selection()
        if not selected_item:
           messagebox.showerror("錯誤", "請選擇要修改的項目")
           return
        values = item_tree.item(selected_item, 'values')
        name_var.set(values[0])
        expiry_date_var.set(values[1])
        quantity_var.set(values[2])
        note_var.set(values[4])
        warehouse_var.set(values[3])
        
        item_tree.delete(selected_item)
        for item in remove_items_list:
           if item[0] == values[0] and item[1] == get_date_input(values[1]) and item[2] == int(values[2]):
              remove_items_list.remove(item)

    def delete_remove_item_list():
        selected_item = item_tree.selection()
        if not selected_item:
            messagebox.showerror("錯誤", "請選擇要刪除的項目")
            return
        values = item_tree.item(selected_item, 'values')
        for item in remove_items_list:
            if item[0] == values[0] and item[1] == get_date_input(values[1]) and item[2] == int(values[2]):
                remove_items_list.remove(item)
        item_tree.delete(selected_item)

    button_frame = ttk.Frame(remove_window)
    button_frame.grid(row=6, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

    add_to_list_button = ttk.Button(button_frame, text="新增至清單", command=add_remove_item_to_list)
    add_to_list_button.pack(side="right", padx=5)
    
    edit_to_list_button = ttk.Button(button_frame, text="修改清單項目", command=edit_remove_item_list)
    edit_to_list_button.pack(side="right", padx=5)

    delete_to_list_button = ttk.Button(button_frame, text="刪除清單項目", command=delete_remove_item_list)
    delete_to_list_button.pack(side="right", padx=5)

    def remove_item_action():
        if messagebox.askyesno("確認", "確定要出貨嗎？"):
            warehouse_name = warehouse_var.get()
            all_success = True
            total_remove_quantity = {}  # 用來追蹤各個項目的總移除數量
            
            if remove_items_list:
                warehouse = warehouse1 if warehouse_name == "倉庫1" else warehouse2

                # 驗證總移除數量
                for name, expiry_date, quantity, warehouse_item, note_item in remove_items_list:
                  if (name, expiry_date, warehouse_item) not in total_remove_quantity:
                     total_remove_quantity[(name, expiry_date, warehouse_item)] = 0
                  total_remove_quantity[(name, expiry_date, warehouse_item)] += quantity

                for (name, expiry_date, warehouse_item), quantity in total_remove_quantity.items():
                 # 檢查庫存是否足夠
                  warehouse = warehouse1 if warehouse_item == "倉庫1" else warehouse2
                  item_inventory = next((item for item in warehouse.inventory.values() if item.name == name and item.expiry_date == expiry_date), None)
                  if item_inventory and item_inventory.quantity < quantity:
                     all_success = False
                     messagebox.showerror("錯誤", f"商品 {name}，有效日期 {expiry_date.strftime('%Y-%m-%d')} 庫存不足，庫存{item_inventory.quantity}，出貨{quantity}。")
                     break
            
            if all_success:
                for name,expiry_date, quantity, warehouse_item, note_item  in remove_items_list:
                    warehouse = warehouse1 if warehouse_item == "倉庫1" else warehouse2
                    result = warehouse.remove_item(name, expiry_date, quantity)
                    if not result:
                        all_success = False
                        break # 如果移除失敗就停止迴圈
                    else:
                        history_log.append({
                            "type": "出貨",
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
                messagebox.showinfo("成功", "出貨成功")
                remove_window.destroy()
            else:
                messagebox.showerror("錯誤", "出貨失敗，請檢查輸入。")
                
    remove_button = ttk.Button(button_frame, text="確認出貨", command=remove_item_action)
    remove_button.pack(side="right", padx=5)