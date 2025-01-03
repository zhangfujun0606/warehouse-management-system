import tkinter as tk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import numpy as np

def generate_line_chart(parent, visible_data, display_content, product):
    if not visible_data:
        tk.messagebox.showerror("錯誤", "請先產生報表")
        return

    # 提取產品名稱和庫存數據
    dates = sorted(list(set([row[0] for row in visible_data])))
    products = ["橋頭", "橋頭2公升", "漫步"]

    # 設定字型檔案路徑
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "utils", "NotoSansTC-Regular.ttf")
    font = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font.get_name()

    # 準備數據
    x = np.arange(len(dates))
    inventory_data = {}
    for product_name in products:
        if product == "全部" or product == product_name:
            inventory = []
            for date in dates:
               found_data = [row for row in visible_data if row[0] == date and row[1] == product_name]
               if found_data:
                  if display_content == "未過期庫存":
                       inventory.append(int(found_data[0][5]))
                  elif display_content == "已過期庫存":
                       inventory.append(int(found_data[0][6]))
                  elif display_content == "所有庫存":
                        inventory.append(int(found_data[0][5]) + int(found_data[0][6]))
                  elif display_content == "進貨量":
                        inventory.append(int(found_data[0][2]))
                  elif display_content == "出貨量":
                        inventory.append(int(found_data[0][3]))
                  elif display_content == "報廢量":
                        inventory.append(int(found_data[0][4]))
               else:
                  # 如果找不到資料則補 0
                   inventory.append(0)
            inventory_data[product_name] = np.array(inventory)

    # 創建子圖 (剩餘庫存)
    for widget in parent.winfo_children():
        widget.destroy()  # 清除現有 widget
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xticks(x)
    ax.set_xticklabels(dates, rotation=45, ha="right", fontproperties=font)
    for product_name in products:
        if product == "全部" or product == product_name:
            ax.plot(x, inventory_data[product_name], label=f"{product_name}", marker='o', linestyle='-')
    ax.set_xlabel("日期", fontproperties=font)
    ax.set_ylabel("數量", fontproperties=font)
    ax.set_title(f"{product} 產品剩餘庫存圖 ({display_content})", fontproperties=font)
    ax.legend(prop=font)
    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    canvas.draw()
    plt.close(fig)

def generate_bar_chart(parent, visible_data, display_content, product):
        if not visible_data:
            tk.messagebox.showerror("錯誤", "請先產生報表")
            return

        # 提取產品名稱和庫存數據
        dates = sorted(list(set([row[0] for row in visible_data])))
        products = ["橋頭", "橋頭2公升", "漫步"]

        # 設定字型檔案路徑
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "utils", "NotoSansTC-Regular.ttf")
        font = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font.get_name()
        # 準備數據
        x = np.arange(len(dates))
        quantity_data = {}
        for product_name in products:
            if product == "全部" or product == product_name:
                quantity = []
                for date in dates:
                    found_data = [row for row in visible_data if row[0] == date and row[1] == product_name]
                    if found_data:
                      if display_content == "進貨量":
                          quantity.append(int(found_data[0][2]))
                      elif display_content == "出貨量":
                          quantity.append(int(found_data[0][3]))
                      elif display_content == "報廢量":
                         quantity.append(int(found_data[0][4]))
                      elif display_content == "未過期庫存":
                        quantity.append(int(found_data[0][5]))
                      elif display_content == "已過期庫存":
                           quantity.append(int(found_data[0][6]))
                      elif display_content == "所有庫存":
                            quantity.append(int(found_data[0][5]) + int(found_data[0][6]))
                    else:
                    # 如果找不到資料則補 0
                        quantity.append(0)
                quantity_data[product_name] = np.array(quantity)

        # 創建子圖
        for widget in parent.winfo_children():
            widget.destroy()  # 清除現有 widget
        fig, ax = plt.subplots(figsize=(15, 6))
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, ha="right", fontproperties=font)
        bar_width = 0.2
        offset = -bar_width

        for product_name in products:
            if product == "全部" or product == product_name:
                ax.bar(x + offset, quantity_data[product_name], label=f"{product_name} {display_content}", width=bar_width, align='center')
                offset += bar_width

        ax.set_xlabel("日期", fontproperties=font)
        ax.set_ylabel("數量", fontproperties=font)
        ax.set_title(f"{product} 產品進出報廢量圖", fontproperties=font)
        ax.legend(prop=font)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas.draw()
        plt.close(fig)

def generate_pie_chart(parent, visible_data, display_content, product):
    if not visible_data:
      tk.messagebox.showerror("錯誤", "請先產生報表")
      return
    # 提取產品名稱和庫存數據
    dates = sorted(list(set([row[0] for row in visible_data])))
    if not dates:
        tk.messagebox.showerror("錯誤", "請選擇有效的日期範圍")
        return
    products = ["橋頭", "橋頭2公升", "漫步"]
    # 設定字型檔案路徑
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "utils", "NotoSansTC-Regular.ttf")
    font = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font.get_name()
    # 準備數據
    inventory_data = {}
    for product_name in products:
         if product == "全部" or product == product_name:
            found_data = [row for row in visible_data if row[0] == dates[-1] and row[1] == product_name]
            if found_data:
                 if display_content == "未過期庫存":
                    inventory_data[product_name] = int(found_data[0][5])
                 elif display_content == "已過期庫存":
                    inventory_data[product_name] = int(found_data[0][6])
                 else:
                    inventory_data[product_name] = int(found_data[0][5]) + int(found_data[0][6])
            else:
                 inventory_data[product_name] = 0


    labels = list(inventory_data.keys())
    sizes = list(inventory_data.values())
    if all(size == 0 for size in sizes):
         tk.messagebox.showerror("錯誤", "沒有任何資料可以顯示")
         return
    # 創建子圖
    for widget in parent.winfo_children():
      widget.destroy()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'fontproperties': font})
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title(f"{product} 產品庫存佔比圖 ({display_content})", fontproperties=font)

    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    canvas.draw()
    plt.close(fig)