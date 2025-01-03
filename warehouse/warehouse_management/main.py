# main.py
import tkinter as tk
import datetime
from warehouse_management.warehouse import Warehouse
# from warehouse_management.login_module import login  # 移除登入模組的 import
from warehouse_management.ui.main_window_ui import setup_main_window
from warehouse_management.utils.data_handler import save_data, load_data
from warehouse_management.item import Item
# from warehouse_management.ui.report_window import display_report_window  # 移除 report_window 的 import

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

# 登入驗證
logged_in_user = "A0510"  # 模擬已登入的使用者

def run_app():
    print("程式開始執行...")
    try:
        global history_log
        global window # 設定 window 為全域變數
        window = tk.Tk()
        window.title("倉儲管理系統")
        history_log = load_data(warehouse1, warehouse2)

        # 直接設定 main_window，跳過登入
        print("準備呼叫 setup_main_window...") # 加入這個print
        setup_main_window(window, warehouse1, warehouse2, lambda: save_data(warehouse1, warehouse2, history_log), history_log, logged_in_user)
        print("已呼叫 setup_main_window")

    except Exception as e:
       print(f"程式發生錯誤: {e}")

    print("準備進入mainloop")  # 在這裡新增print
    window.mainloop()
    print("mainloop執行結束。")

if __name__ == "__main__":
    run_app()