import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def generate_report_window(window, warehouse1, warehouse2, history_log):
    report_window = tk.Toplevel(window)
    report_window.title("生成報表")

    report_type_label = ttk.Label(report_window, text="選擇報表類型:")
    report_type_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
    report_type_var = tk.StringVar(value="庫存報表")
    report_type_combobox = ttk.Combobox(report_window, textvariable=report_type_var, values=["庫存報表", "歷史紀錄報表"])
    report_type_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    def generate_date_options():
        today = datetime.date.today()
        dates = []
        for i in range(365):
            date = today - datetime.timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))
        return dates

    start_date_label = ttk.Label(report_window, text="開始時間:")
    start_date_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
    start_date_var = tk.StringVar()
    start_date_combobox = ttk.Combobox(report_window, textvariable=start_date_var, values=generate_date_options(), width=12)
    start_date_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='w')
    start_date_var.set(datetime.date.today().strftime("%Y-%m-%d"))

    end_date_label = ttk.Label(report_window, text="結束時間:")
    end_date_label.grid(row=1, column=2, padx=5, pady=5, sticky='e')
    end_date_var = tk.StringVar()
    end_date_combobox = ttk.Combobox(report_window, textvariable=end_date_var, values=generate_date_options(), width=12)
    end_date_combobox.grid(row=1, column=3, padx=5, pady=5, sticky='w')
    end_date_var.set(datetime.date.today().strftime("%Y-%m-%d"))

    warehouse_label = ttk.Label(report_window, text="選擇倉庫:")
    warehouse_label.grid(row=2, column=0, padx=5, pady=5, sticky='e')
    warehouse_var = tk.StringVar(value="全部")
    warehouse_combobox = ttk.Combobox(report_window, textvariable=warehouse_var, values=["全部", "倉庫1", "倉庫2"])
    warehouse_combobox.grid(row=2, column=1, padx=5, pady=5, sticky='w')

    def generate_report():
        report_type = report_type_var.get()
        start_date_str = start_date_var.get()
        end_date_str = end_date_var.get()
        warehouse_name = warehouse_var.get()
        
        start_date = get_date_input(start_date_str)
        end_date = get_date_input(end_date_str)
        
        if report_type == "庫存報表":
            export_inventory_report(warehouse1, warehouse2, warehouse_name, start_date, end_date)
        elif report_type == "歷史紀錄報表":
            export_history_report(history_log, start_date, end_date)
        report_window.destroy()
    
    def get_date_input(date_str):
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("錯誤", "日期格式錯誤，請使用 YYYY-MM-DD")
            return None

    def export_inventory_report(warehouse1, warehouse2, warehouse_name, start_date, end_date):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            wb = Workbook()
            sheet = wb.active
            sheet.append(["日期", "品名", "未過期數量", "過期數量", "倉庫"])
            
            all_inventory = {}
            if warehouse_name == "全部":
                for date, inventory in warehouse1.daily_inventory.items():
                    if start_date <= date <= end_date:
                        if date not in all_inventory:
                            all_inventory[date] = {}
                        for key, item in inventory.items():
                            item_name = item.name
                            if (item_name, item.warehouse) not in all_inventory[date]:
                                all_inventory[date][(item_name, item.warehouse)] = {"未過期": 0, "過期": 0, "warehouse": item.warehouse}
                            if item.expiry_date < datetime.date.today():
                                all_inventory[date][(item_name, item.warehouse)]["過期"] += item.quantity
                            else:
                                all_inventory[date][(item_name, item.warehouse)]["未過期"] += item.quantity
                for date, inventory in warehouse2.daily_inventory.items():
                    if start_date <= date <= end_date:
                        if date not in all_inventory:
                            all_inventory[date] = {}
                        for key, item in inventory.items():
                            item_name = item.name
                            if (item_name, item.warehouse) not in all_inventory[date]:
                                all_inventory[date][(item_name, item.warehouse)] = {"未過期": 0, "過期": 0, "warehouse": item.warehouse}
                            if item.expiry_date < datetime.date.today():
                                all_inventory[date][(item_name, item.warehouse)]["過期"] += item.quantity
                            else:
                                all_inventory[date][(item_name, item.warehouse)]["未過期"] += item.quantity
            elif warehouse_name == "倉庫1":
                all_inventory = warehouse1.daily_inventory
            elif warehouse_name == "倉庫2":
                all_inventory = warehouse2.daily_inventory
            
            for date, inventory in all_inventory.items():
                if start_date <= date <= end_date:
                    for (item_name, warehouse), quantities in inventory.items():
                        sheet.append([date.strftime("%Y-%m-%d"), item_name, quantities["未過期"], quantities["過期"], quantities["warehouse"]])
            
            wb.save(file_path)
            messagebox.showinfo("成功", "庫存報表已匯出至 Excel")

    def export_history_report(history_log, start_date, end_date):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            c = canvas.Canvas(file_path, pagesize=letter)
            c.setFont("Helvetica", 10)
            y = 750
            
            # 註冊字體
            font_path = os.path.join(os.path.dirname(__file__), "..", "utils", "NotoSansCJKtc-Regular.ttf")
            if not os.path.exists(font_path):
                messagebox.showerror("錯誤", f"字體檔案不存在:{font_path}，請檢查檔案路徑。")
                return
            pdfmetrics.registerFont(TTFont('NotoSansCJKtc-Regular', font_path))
            c.setFont('NotoSansCJKtc-Regular', 10)
            c.setFillColor(colors.black)
            header = ["類型", "品名", "數量", "有效日期", "時間", "帳號", "倉庫", "備註"]
            x_pos = 50
            for col in header:
                c.drawString(x_pos, y, col)
                x_pos += 100
            y -= 20
            
            for record in history_log:
                record_date = datetime.datetime.strptime(record['time'], "%Y-%m-%d %H:%M:%S").date()
                if start_date <= record_date <= end_date:
                    x_pos = 50
                    for i, item in enumerate([record['type'], record['name'], record['quantity'], record['expiry_date'], record['time'], record.get('user', 'N/A'), record.get('warehouse', 'N/A'), record['note']]):
                        c.drawString(x_pos, y, str(item))
                        x_pos += 100
                    y -= 15
                    if y < 50:
                        c.showPage()
                        y = 750

            c.save()
            messagebox.showinfo("成功", "歷史記錄已匯出至 PDF")

    generate_button = ttk.Button(report_window, text="生成報表", command=generate_report)
    generate_button.grid(row=3, column=1, padx=5, pady=10, sticky='w')