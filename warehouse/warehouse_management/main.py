import tkinter as tk
import datetime
from warehouse_management.warehouse import Warehouse
from warehouse_management.login_module import login
from warehouse_management.ui.main_window_ui import setup_main_window
from warehouse_management.utils.data_handler import save_data, load_data
from warehouse_management.item import Item
from warehouse_management.ui.report_window import display_report_window

# 創建兩個倉庫
warehouse1 = Warehouse("倉庫1")
warehouse2 = Warehouse("倉庫2")

# 預設商品
warehouse1.add_item(Item("橋頭", 0, datetime.date(2024, 12, 31), "預設備註"))
warehouse1.add_item(Item("橋頭2公升", 0, datetime.date(2024, 12, 25),"預設備註"))
warehouse1.add_item(Item("漫步", 0, datetime.date(2024, 12, 25),"預設備註"))
warehouse2.add_item(Item("橋頭", 0, datetime.date(2024, 12, 31),"預設備註"))
warehouse2.add_item(Item("橋頭2公升", 0, datetime.date(2024, 12, 25),"預設備註"))
warehouse2.add_item(Item("漫步", 0, datetime.date(2024, 12, 25),"預設備註"))


# 歷史紀錄
history_log = []

# 創建主視窗
window = tk.Tk()
window.title("倉儲管理系統")

# 登入驗證
logged_in_user = None

def run_app():
    print("程式開始執行...")
    try:
        global history_log
        history_log, daily_inventory1, daily_inventory2 = load_data(warehouse1, warehouse2)    
        warehouse1.daily_inventory = daily_inventory1
        warehouse2.daily_inventory = daily_inventory2
        
        if login(window, lambda: None, lambda logged_in_user: setup_main_window(window, warehouse1, warehouse2, lambda: save_data(warehouse1, warehouse2, history_log, daily_inventory1, daily_inventory2), history_log, logged_in_user)):
            window.mainloop()
        else:
            window.destroy()
    except Exception as e:
       print(f"程式發生錯誤: {e}")
       
    print("程式執行結束。")

if __name__ == "__main__":
    run_app()