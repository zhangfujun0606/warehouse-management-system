import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
import datetime
from warehouse_management.ui.report_data_handler import generate_report_data
from warehouse_management.ui.report_chart_generator import generate_line_chart, generate_bar_chart, generate_pie_chart
from openpyxl import Workbook

DATABASE_FILE = "warehouse.db"
BACKUP_FOLDER = "warehouse_backup"

def display_report_window(window, warehouse1, warehouse2, history_log):
    print("display_report_window: 開始執行")
    report_window = tk.Toplevel(window)
    report_window.title("每日庫存報表")
    print("display_report_window: 建立 Toplevel 視窗")

    # 設定視窗可以彈性變動
    report_window.grid_rowconfigure(2, weight=1)
    report_window.grid_columnconfigure(0, weight=1)
    report_window.grid_columnconfigure(1, weight=1)
    report_window.grid_columnconfigure(2, weight=1)
    report_window.grid_columnconfigure(3, weight=1)
    report_window.grid_columnconfigure(4, weight=1)
    report_window.grid_columnconfigure(5, weight=1)  # 新增
    print("display_report_window: 設定視窗彈性")

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
    print("display_report_window: 開始時間選擇完成")

    end_date_label = ttk.Label(report_window, text="結束時間:")
    end_date_label.grid(row=0, column=2, padx=5, pady=5, sticky='e')
    end_date_var = tk.StringVar()
    end_date_combobox = ttk.Combobox(report_window, textvariable=end_date_var, values=generate_date_options(), width=12)
    end_date_combobox.grid(row=0, column=3, padx=5, pady=5, sticky='w')
    end_date_var.set(datetime.date.today().strftime("%Y-%m-%d"))
    print("display_report_window: 結束時間選擇完成")

    warehouse_label = ttk.Label(report_window, text="選擇倉庫:")  # 新增
    warehouse_label.grid(row=0, column=4, padx=5, pady=5, sticky='e')  # 新增
    warehouse_var = tk.StringVar(value="全部")
    warehouse_combobox = ttk.Combobox(report_window, textvariable=warehouse_var, values=["全部", "倉庫1", "倉庫2"])  #  新增
    warehouse_combobox.grid(row=0, column=5, padx=5, pady=5, sticky='w')  # 新增
    print("display_report_window: 倉庫選擇完成")

    # 新增圖表類型選擇
    chart_type_label = ttk.Label(report_window, text="圖表類型:")
    chart_type_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
    chart_type_var = tk.StringVar(value="折線圖")
    chart_type_combobox = ttk.Combobox(report_window, textvariable=chart_type_var, values=["折線圖", "柱狀圖", "圓餅圖"], width=12)
    chart_type_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='w')
    print("display_report_window: 圖表類型選擇完成")

    # 新增顯示內容選擇
    display_content_label = ttk.Label(report_window, text="顯示內容:")
    display_content_label.grid(row=1, column=2, padx=5, pady=5, sticky='e')
    display_content_var = tk.StringVar(value="未過期庫存")
    display_content_combobox = ttk.Combobox(report_window, textvariable=display_content_var, values=["未過期庫存", "已過期庫存", "所有庫存", "進貨量", "出貨量", "報廢量"], width=12)
    display_content_combobox.grid(row=1, column=3, padx=5, pady=5, sticky='w')
    print("display_report_window: 顯示內容選擇完成")

    # 新增選擇商品名稱
    product_label = ttk.Label(report_window, text="選擇產品:")
    product_label.grid(row=1, column=4, padx=5, pady=5, sticky='e')
    product_var = tk.StringVar(value="全部")
    product_combobox = ttk.Combobox(report_window, textvariable=product_var, values=["全部", "橋頭", "橋頭2公升", "漫步"], width=12)
    product_combobox.grid(row=1, column=5, padx=5, pady=5, sticky='w')
    print("display_report_window: 產品選擇完成")

    # 使用 PanedWindow 分隔視窗
    paned_window = ttk.Panedwindow(report_window, orient=tk.VERTICAL)
    paned_window.grid(row=2, column=0, columnspan=7, sticky='nsew', padx=10, pady=10)  # 修改 columnspan
    print("display_report_window: 建立 PanedWindow")

    # Treeview for displaying report
    columns = ("日期", "產品", "進貨量", "出貨量", "報廢量", "剩餘庫存(未過期)", "剩餘庫存(已過期)")  # 修改
    
    # 創建一個框架來放置 Treeview 和滾動條
    tree_frame = ttk.Frame(paned_window)
    tree_frame.grid(row=3, column=0, columnspan=7, sticky='nsew', padx=10, pady=10)
    paned_window.add(tree_frame)

    # 創建垂直滾動條
    tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
    tree_scrollbar.pack(side="right", fill="y")

    # 直接建立 Treeview
    report_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10, yscrollcommand=tree_scrollbar.set)
    report_tree.pack(side="left", fill="both", expand=True)

    # 綁定滾動條和 Treeview
    tree_scrollbar.config(command=report_tree.yview)

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

    print("display_report_window: 建立 Treeview 和 Scrollbar")
    # 圖表容器
    chart_frame = ttk.Frame(paned_window)
    chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    paned_window.add(chart_frame)
    print("display_report_window: 建立 chart_frame")
    
    # 按鈕框架
    button_frame = ttk.Frame(report_window)  # 將按鈕框架建立在 report_window
    button_frame.grid(row=5, column=0, columnspan=7, sticky='ew', padx=10, pady=10)
    print("display_report_window: 建立 button_frame")


    filter_vars = {}
    for col in columns:
        filter_vars[col] = tk.StringVar()

    def create_filter_menu(col, event, filtered_data):
        filter_menu = Menu(report_window, tearoff=0)
        values = sorted(list(set(str(item[i]) for item in filtered_data for i, c in enumerate(columns) if c == col)))

        filter_menu.add_command(label="全部", command=lambda c=col: set_filter(c, ""))
        for value in values:
            filter_menu.add_command(label=value, command=lambda c=col, v=value: set_filter(c, v))

        filter_menu.tk_popup(event.x_root, event.y_root)

    def set_filter(col, value):
        filter_vars[col].set(value)
        generate_report(report_tree)

    def handle_click(event, tree):
        region = tree.identify_region(event.x, event.y)  # 修改點：使用 identify_region 判斷點擊區域
        if region == "heading":  # 修改點：判斷點擊區域是否是 heading
            col_id = tree.identify_column(event.x)
            if col_id and col_id != "#all":  # 確保點擊的是標題欄
                col_index = int(col_id[1:]) - 1
                col = columns[col_index]
                filtered_data = get_visible_data(report_tree)
                create_filter_menu(col, event, filtered_data)
    print("display_report_window: 定義 handle_click")
    # 修改點：綁定標題欄的點擊事件
    report_tree.bind("<Button-1>", lambda event: handle_click(event, report_tree))
    print("display_report_window: 綁定 handle_click")
 
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
    print("display_report_window: 定義 export_to_excel")

    def _generate_chart(chart_frame):
        for widget in chart_frame.winfo_children():
             widget.destroy()
        chart_type = chart_type_var.get()
        display_content = display_content_var.get()
        product = product_var.get()
        visible_data = get_visible_data(report_tree)

        if chart_type == "折線圖":
            generate_line_chart(chart_frame, visible_data, display_content, product)
        elif chart_type == "柱狀圖":
             generate_bar_chart(chart_frame, visible_data, display_content, product)
        elif chart_type == "圓餅圖":
            generate_pie_chart(chart_frame, visible_data, display_content, product)
    print("display_report_window: 定義 _generate_chart")
    
    def get_visible_data(tree):
       visible_data = []
       for item in tree.get_children():
            visible_data.append(tree.item(item)['values'])
       return visible_data

    def generate_report(report_tree):
        print("generate_report: 開始執行")
        report_tree.delete(*report_tree.get_children())
        report_data = generate_report_data(
            history_log,
            start_date_var.get(),
            end_date_var.get(),
            warehouse_var.get(),
            warehouse1,
            warehouse2,
            filter_vars
        )
        for item in report_data:
           report_tree.insert("", "end", values=item)
        print("generate_report: 資料顯示完成")


    export_excel_button = ttk.Button(button_frame, text="匯出 Excel", command=export_to_excel)
    export_excel_button.pack(side="right", padx=5)
    print("display_report_window: 建立 export_excel_button")

    display_button = ttk.Button(button_frame, text="顯示報表", command=lambda: generate_report(report_tree))
    display_button.pack(side="right", padx=5)
    print("display_report_window: 建立 display_button")

    chart_button = ttk.Button(button_frame, text="顯示圖表", command=lambda: _generate_chart(chart_frame))
    chart_button.pack(side="right", padx=5)
    print("display_report_window: 建立 chart_button")

    # Initialize the display
    generate_report(report_tree)
    print("display_report_window: 執行 generate_report")