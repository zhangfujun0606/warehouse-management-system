import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
from openpyxl import Workbook
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import numpy as np
import warnings

warnings.filterwarnings("ignore", message="findfont: Font family.* not found.")

def display_report_window(window, warehouse1, warehouse2, history_log):
    report_window = tk.Toplevel(window)
    report_window.title("每日庫存報表")

    # 設定視窗可以彈性變動
    report_window.grid_rowconfigure(2, weight=1)
    report_window.grid_columnconfigure(0, weight=1)
    report_window.grid_columnconfigure(1, weight=1)
    report_window.grid_columnconfigure(2, weight=1)
    report_window.grid_columnconfigure(3, weight=1)
    report_window.grid_columnconfigure(4, weight=1)
    report_window.grid_columnconfigure(5, weight=1)  # 新增

    def get_date_input(date_str):
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("錯誤", "日期格式錯誤，請使用 YYYY-MM-DD")
            return None

    def generate_date_options():
        today = datetime.date.today()
        dates = []
        for i in range(365):
            date = today - datetime.timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))
        return dates

    start_date_label = ttk.Label(report_window, text="開始時間:")
    start_date_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
    start_date_var = tk.StringVar()
    start_date_combobox = ttk.Combobox(report_window, textvariable=start_date_var, values=generate_date_options(), width=12)
    start_date_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')
    start_date_var.set(datetime.date.today().strftime("%Y-%m-%d"))

    end_date_label = ttk.Label(report_window, text="結束時間:")
    end_date_label.grid(row=0, column=2, padx=5, pady=5, sticky='e')
    end_date_var = tk.StringVar()
    end_date_combobox = ttk.Combobox(report_window, textvariable=end_date_var, values=generate_date_options(), width=12)
    end_date_combobox.grid(row=0, column=3, padx=5, pady=5, sticky='w')
    end_date_var.set(datetime.date.today().strftime("%Y-%m-%d"))

    warehouse_label = ttk.Label(report_window, text="選擇倉庫:")  # 新增
    warehouse_label.grid(row=0, column=4, padx=5, pady=5, sticky='e')  # 新增
    warehouse_var = tk.StringVar(value="全部")
    warehouse_combobox = ttk.Combobox(report_window, textvariable=warehouse_var, values=["全部", "倉庫1", "倉庫2"])  # 新增
    warehouse_combobox.grid(row=0, column=5, padx=5, pady=5, sticky='w')  # 新增

    # 使用 PanedWindow 分隔視窗
    paned_window = ttk.Panedwindow(report_window, orient=tk.VERTICAL)
    paned_window.grid(row=2, column=0, columnspan=7, sticky='nsew', padx=10, pady=10)  # 修改 columnspan

    # Treeview for displaying report
    columns = ("日期", "產品", "進貨量", "出貨量", "報廢量", "剩餘庫存(未過期)", "剩餘庫存(已過期)")  # 修改
    report_tree = ttk.Treeview(paned_window, columns=columns, show="headings", height=15)
    report_tree.heading("日期", text="日期")
    report_tree.heading("產品", text="產品")  # 修改
    report_tree.heading("進貨量", text="進貨量")
    report_tree.heading("出貨量", text="出貨量")
    report_tree.heading("報廢量", text="報廢量")
    report_tree.heading("剩餘庫存(未過期)", text="剩餘庫存(未過期)")  # 修改
    report_tree.heading("剩餘庫存(已過期)", text="剩餘庫存(已過期)")  # 修改
    report_tree.column("日期", width=100, anchor=tk.CENTER)
    report_tree.column("產品", width=120, anchor=tk.CENTER)  # 修改
    report_tree.column("進貨量", width=80, anchor=tk.CENTER)
    report_tree.column("出貨量", width=80, anchor=tk.CENTER)
    report_tree.column("報廢量", width=80, anchor=tk.CENTER)
    report_tree.column("剩餘庫存(未過期)", width=100, anchor=tk.CENTER)  # 修改
    report_tree.column("剩餘庫存(已過期)", width=100, anchor=tk.CENTER)  # 修改
    report_tree.grid(row=3, column=0, columnspan=7, padx=10, pady=10, sticky='nsew')  # 修改 columnspan
    paned_window.add(report_tree)
    
    def get_visible_data(tree):
        visible_data = []
        for item in tree.get_children():
            visible_data.append(tree.item(item)['values'])
        return visible_data
    
    def generate_report():
        report_tree.delete(*report_tree.get_children())
        start_date_str = start_date_var.get()
        end_date_str = end_date_var.get()
        selected_warehouse = warehouse_var.get()  # 新增

        if not start_date_str or not end_date_str:
            messagebox.showerror("錯誤", "請輸入開始時間與結束時間")
            return

        start_date = get_date_input(start_date_str)
        end_date = get_date_input(end_date_str)

        if not start_date or not end_date:
            return

        if start_date > end_date:
            messagebox.showerror("錯誤", "開始時間不能大於結束時間")
            return

        # 資料篩選與計算
        report_data = {}
        current_date = start_date

        all_items = set()
        if selected_warehouse == "倉庫1":
            for item_data in warehouse1.inventory.values():
                all_items.add(item_data.name)
        elif selected_warehouse == "倉庫2":
            for item_data in warehouse2.inventory.values():
                all_items.add(item_data.name)
        else:
            for item_data in warehouse1.inventory.values():
                all_items.add(item_data.name)
            for item_data in warehouse2.inventory.values():
                all_items.add(item_data.name)

        while current_date <= end_date:
            for item_name in all_items:
                report_data[(current_date, item_name)] = {"進貨": 0, "出貨": 0, "報廢": 0, "剩餘庫存(未過期)": 0, "剩餘庫存(已過期)": 0}
            current_date += datetime.timedelta(days=1)

        # 計算每天的進出貨和報廢
        for record in history_log:
            if isinstance(record, dict):
                record_date = datetime.datetime.strptime(record['time'], "%Y-%m-%d %H:%M:%S").date()
                if start_date <= record_date <= end_date:
                    if selected_warehouse == "全部" or selected_warehouse == record.get("warehouse"):
                        if record["type"] == "進貨":
                            report_data[(record_date, record["name"])]["進貨"] += record["quantity"]
                        elif record["type"] == "出貨":
                            report_data[(record_date, record["name"])]["出貨"] += record["quantity"]
                        elif record["type"] == "報廢":
                            report_data[(record_date, record["name"])]["報廢"] += record["quantity"]

        # 計算剩餘庫存
        for date, item_name in report_data:
            total_inventory = 0
            expired_inventory = 0
            not_expired_inventory = 0
            daily_inventory1 = warehouse1.daily_inventory.get(date, {})
            daily_inventory2 = warehouse2.daily_inventory.get(date, {})

            if selected_warehouse == "倉庫1" or selected_warehouse == "全部":
                for item_data in daily_inventory1.values():
                    if item_data.name == item_name:
                        if item_data.expiry_date < date:
                            expired_inventory += item_data.quantity
                        else:
                            not_expired_inventory += item_data.quantity
            if selected_warehouse == "倉庫2" or selected_warehouse == "全部":
                for item_data in daily_inventory2.values():
                    if item_data.name == item_name:
                        if item_data.expiry_date < date:
                            expired_inventory += item_data.quantity
                        else:
                            not_expired_inventory += item_data.quantity
            report_data[(date, item_name)]["剩餘庫存(未過期)"] = not_expired_inventory
            report_data[(date, item_name)]["剩餘庫存(已過期)"] = expired_inventory
    
        for (date, item_name), data in report_data.items():
            report_tree.insert("", "end", values=(
                date.strftime("%Y-%m-%d"),
                item_name,
                data["進貨"],
                data["出貨"],
                data["報廢"],
                data["剩餘庫存(未過期)"],
                data["剩餘庫存(已過期)"],
            ))

    def export_to_excel():
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            wb = Workbook()
            sheet = wb.active
            sheet.append(columns)

            for item in report_tree.get_children():
                sheet.append(report_tree.item(item)['values'])

            wb.save(file_path)
            messagebox.showinfo("成功", "報表已匯出至 Excel")

    def generate_line_chart():
        visible_data = get_visible_data(report_tree)
        if not visible_data:
            messagebox.showerror("錯誤", "請先產生報表")
            return

        # 提取產品名稱和庫存數據
        dates = sorted(list(set([row[0] for row in visible_data])))
        products = ["橋頭", "橋頭2公升", "漫步"]

        # 設定字型檔案路徑
        font_path = os.path.join(os.getcwd(), "warehouse_management", "utils", "NotoSansTC-Regular.ttf")
        font = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = "Noto Sans TC"  # 使用查詢到的字體名稱
         
        # 創建兩個視窗
        chart_window1 = tk.Toplevel(report_window)
        chart_window1.title("產品進出報廢量圖表")
        chart_window2 = tk.Toplevel(report_window)
        chart_window2.title("產品剩餘庫存圖表")

        # 準備數據
        x = np.arange(len(dates))
        inbound_quantity_data = {}
        outbound_quantity_data = {}
        scrapped_quantity_data = {}
        not_expired_inventory_data = {}
        expired_inventory_data = {}

        for product_name in products:
             not_expired_inventory = []
             expired_inventory = []
             inbound_quantity = []
             outbound_quantity = []
             scrapped_quantity = []
             for date in dates:
                found_data = [row for row in visible_data if row[0] == date and row[1] == product_name]
                if found_data:
                    not_expired_inventory.append(int(found_data[0][5]))
                    expired_inventory.append(int(found_data[0][6]))
                    inbound_quantity.append(int(found_data[0][2]))
                    outbound_quantity.append(int(found_data[0][3]))
                    scrapped_quantity.append(int(found_data[0][4]))
                else:
                    # 如果找不到資料則補 0
                    not_expired_inventory.append(0)
                    expired_inventory.append(0)
                    inbound_quantity.append(0)
                    outbound_quantity.append(0)
                    scrapped_quantity.append(0)
             inbound_quantity_data[product_name] = np.array(inbound_quantity)
             outbound_quantity_data[product_name] = np.array(outbound_quantity)
             scrapped_quantity_data[product_name] = np.array(scrapped_quantity)
             not_expired_inventory_data[product_name] = np.array(not_expired_inventory)
             expired_inventory_data[product_name] = np.array(expired_inventory)

        # 創建子圖 (進貨、出貨、報廢)
        fig1, ax1 = plt.subplots(figsize=(15, 6))
        ax1.set_xticks(x)
        ax1.set_xticklabels(dates, rotation=45, ha="right", fontproperties=font)
        for product_name in products:
            ax1.plot(x, inbound_quantity_data[product_name], label=f"{product_name} 進貨量", marker='^', linestyle=':')
            ax1.plot(x, outbound_quantity_data[product_name], label=f"{product_name} 出貨量", marker='s', linestyle='-.')
            ax1.plot(x, scrapped_quantity_data[product_name], label=f"{product_name} 報廢量", marker='d', linestyle='-')

        ax1.set_xlabel("日期", fontproperties=font)  # 使用 fontproperties 參數
        ax1.set_ylabel("數量", fontproperties=font)  # 使用 fontproperties 參數
        ax1.set_title("產品進出報廢量圖", fontproperties=font)
        ax1.legend(prop=font)
        plt.tight_layout()
        canvas1 = FigureCanvasTkAgg(fig1, master=chart_window1)
        canvas_widget1 = canvas1.get_tk_widget()
        canvas_widget1.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas1.draw()
        
        # 創建子圖 (剩餘庫存)
        fig2, ax2 = plt.subplots(figsize=(15, 6))
        ax2.set_xticks(x)
        ax2.set_xticklabels(dates, rotation=45, ha="right", fontproperties=font)
        for product_name in products:
            ax2.plot(x, not_expired_inventory_data[product_name], label=f"{product_name} 未過期庫存", marker='o', linestyle='-')
            ax2.plot(x, expired_inventory_data[product_name], label=f"{product_name} 已過期庫存", marker='x', linestyle='--')
        ax2.set_xlabel("日期", fontproperties=font)  # 使用 fontproperties 參數
        ax2.set_ylabel("數量", fontproperties=font)  # 使用 fontproperties 參數
        ax2.set_title("產品剩餘庫存圖", fontproperties=font)
        ax2.legend(prop=font)
        plt.tight_layout()
        canvas2 = FigureCanvasTkAgg(fig2, master=chart_window2)
        canvas_widget2 = canvas2.get_tk_widget()
        canvas_widget2.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas2.draw()

    button_frame = ttk.Frame(report_window)
    button_frame.grid(row=4, column=0, columnspan=7, sticky='ew', padx=10, pady=10)  # 修改 columnspan

    export_excel_button = ttk.Button(button_frame, text="匯出 Excel", command=export_to_excel)
    export_excel_button.pack(side="right", padx=5)
    
    display_button = ttk.Button(button_frame, text="顯示報表", command=generate_report)
    display_button.pack(side="right", padx=5)
    
    chart_button = ttk.Button(button_frame, text="顯示圖表", command=generate_line_chart)  # 修改按鈕文字
    chart_button.pack(side="right", padx=5)  # 新增

    # Initialize the display
    generate_report()