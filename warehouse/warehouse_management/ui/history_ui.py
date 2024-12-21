import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import tkinter.font as tkFont
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def display_history_window(window, history_log):
    history_window = tk.Toplevel(window)
    history_window.title("歷史紀錄")

    # 設定視窗可以彈性變動
    history_window.grid_rowconfigure(2, weight=1)
    history_window.grid_columnconfigure(0, weight=1)
    history_window.grid_columnconfigure(1, weight=1)
    history_window.grid_columnconfigure(2, weight=1)
    history_window.grid_columnconfigure(3, weight=1)
    
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

    start_date_label = ttk.Label(history_window, text="開始時間:")
    start_date_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
    start_date_var = tk.StringVar()
    start_date_combobox = ttk.Combobox(history_window, textvariable=start_date_var, values=generate_date_options(), width=12)
    start_date_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')
    start_date_var.set(datetime.date.today().strftime("%Y-%m-%d"))

    end_date_label = ttk.Label(history_window, text="結束時間:")
    end_date_label.grid(row=0, column=2, padx=5, pady=5, sticky='e')
    end_date_var = tk.StringVar()
    end_date_combobox = ttk.Combobox(history_window, textvariable=end_date_var, values=generate_date_options(), width=12)
    end_date_combobox.grid(row=0, column=3, padx=5, pady=5, sticky='w')
    end_date_var.set(datetime.date.today().strftime("%Y-%m-%d"))
    
    # 使用 PanedWindow 分隔視窗
    paned_window = ttk.Panedwindow(history_window, orient=tk.VERTICAL)
    paned_window.grid(row=2, column=0, columnspan=4, sticky='nsew', padx=10, pady=10)

    # Create filter Comboboxes
    columns = ("type", "name", "quantity", "expiry_date", "time", "user", "warehouse", "note")
    
    history_tree = ttk.Treeview(paned_window, columns=columns, show="headings", height=15)
    history_tree.heading("type", text="類型")
    history_tree.heading("name", text="品名")
    history_tree.heading("quantity", text="數量")
    history_tree.heading("expiry_date", text="有效日期")
    history_tree.heading("time", text="時間")
    history_tree.heading("user", text="帳號")
    history_tree.heading("warehouse", text="倉庫")
    history_tree.heading("note", text="備註")
    history_tree.column("type", anchor=tk.CENTER, width=80)
    history_tree.column("name", width=120, anchor=tk.CENTER)
    history_tree.column("quantity", width=80, anchor=tk.CENTER)
    history_tree.column("expiry_date", width=100, anchor=tk.CENTER)
    history_tree.column("time", width=140, anchor=tk.CENTER)
    history_tree.column("user", width=80, anchor=tk.CENTER)
    history_tree.column("warehouse", width=80, anchor=tk.CENTER)
    history_tree.column("note", width=150, anchor=tk.CENTER)
    history_tree.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')
    paned_window.add(history_tree)
    
    def get_visible_data(tree):
        visible_data = []
        for item in tree.get_children():
             visible_data.append(tree.item(item)['values'])
        return visible_data

    def display_history():
        history_tree.delete(*history_tree.get_children())
        start_date_str = start_date_var.get()
        end_date_str = end_date_var.get()
        
        if not start_date_str or not end_date_str:
            messagebox.showerror("錯誤", "請輸入開始時間與結束時間")
            return
        
        start_date = get_date_input(start_date_str)
        end_date = get_date_input(end_date_str)

        if not start_date or not end_date:
            return
        
        for record in history_log:
            if isinstance(record, dict):
                record_date = datetime.datetime.strptime(record['time'], "%Y-%m-%d %H:%M:%S").date()
                if start_date <= record_date <= end_date:
                    user_str = record.get('user') if 'user' in record else None
                    user_str = 'N/A' if user_str is None else user_str
                    history_tree.insert('', 'end', values=(
                        record['type'],
                        record['name'],
                        record['quantity'],
                        record['expiry_date'],
                        record['time'],
                        user_str,
                        record.get('warehouse', 'N/A'),
                        record['note']
                    ))
    
    def export_to_excel():
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            wb = Workbook()
            sheet = wb.active
            sheet.append(columns)
            
            # Get visible data
            filtered_data = get_visible_data(history_tree)
            
            for record in filtered_data:
                sheet.append(record)
            
            wb.save(file_path)
            messagebox.showinfo("成功", "歷史記錄已匯出至 Excel")

    def export_to_pdf():
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            c = canvas.Canvas(file_path, pagesize=letter)
            c.setFont("Helvetica", 10)
            y = 750
            
            # Get visible data
            filtered_data = get_visible_data(history_tree)
            
            # 註冊字體
            font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils", "NotoSansCJKtc-Regular.ttf"))
            
            if not os.path.exists(font_path):
                messagebox.showerror("錯誤", f"字體檔案不存在:{font_path}，請檢查檔案路徑。")
                return
            pdfmetrics.registerFont(TTFont('NotoSansCJKtc-Regular', font_path))
            c.setFont('NotoSansCJKtc-Regular', 10)
            c.setFillColor(colors.black)
            header = columns
            x_pos = 50
            for col in header:
                c.drawString(x_pos, y, col)
                x_pos += 100
            y -= 20

            for record in filtered_data:
                x_pos = 50
                for i, item in enumerate(record):
                    c.drawString(x_pos, y, str(item))
                    x_pos += 100
                y -= 15
                if y < 50:
                    c.showPage()
                    y = 750

            c.save()
            messagebox.showinfo("成功", "歷史記錄已匯出至 PDF")
    
    button_frame = ttk.Frame(history_window)
    button_frame.grid(row=4, column=0, columnspan=4, sticky='ew', padx=10, pady=10)

    export_excel_button = ttk.Button(button_frame, text="匯出 Excel", command=export_to_excel)
    export_excel_button.pack(side="right", padx=5)

    export_pdf_button = ttk.Button(button_frame, text="匯出 PDF", command=export_to_pdf)
    export_pdf_button.pack(side="right", padx=5)
    
    display_button = ttk.Button(button_frame, text="顯示紀錄", command=display_history)
    display_button.pack(side="right", padx=5)

    # Initialize the display
    display_history()