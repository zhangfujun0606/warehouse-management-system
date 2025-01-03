import datetime
import sqlite3
DATABASE_FILE = "warehouse.db"

def generate_report_data(history_log, start_date_str, end_date_str, selected_warehouse, warehouse1, warehouse2, filter_vars):
    try:
        def get_date_input(date_str):
            try:
                return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return None

        start_date = get_date_input(start_date_str)
        end_date = get_date_input(end_date_str)
        if not start_date or not end_date:
            return []
        if start_date > end_date:
             return []

        # 建立完整的日期列表
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += datetime.timedelta(days=1)

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

        # 初始化報表資料
        report_data = {}
        for date in date_list:
            for item_name in all_items:
                report_data[(date, item_name)] = {"進貨": 0, "出貨": 0, "報廢": 0, "剩餘庫存(未過期)": 0, "剩餘庫存(已過期)": 0}


        # 從歷史紀錄讀取進出貨和報廢
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
       # 計算每日剩餘庫存
        item_inventory = {}
        for item_name in all_items:
            item_inventory[item_name] = {}
            for date in date_list:
                 item_inventory[item_name][date] = {"not_expired": 0, "expired":0}


        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        for item_name in all_items:
            for date_index, date in enumerate(date_list):
                not_expired_inventory = 0
                expired_inventory = 0

                # 檢查資料庫中是否有當天的數據
                cursor.execute("""
                    SELECT quantity, expiry_date FROM daily_inventory
                    WHERE date = ? AND name = ? 
                    """, (date.strftime("%Y-%m-%d"), item_name))
                daily_data = cursor.fetchall()

                if not daily_data:
                     # 若沒有當天的資料，則向前搜尋歷史資料
                    for i in range(1, 366):
                        past_date = date - datetime.timedelta(days=i)
                        cursor.execute("""
                             SELECT quantity, expiry_date, warehouse FROM daily_inventory
                             WHERE date = ? AND name = ?
                        """, (past_date.strftime("%Y-%m-%d"), item_name))
                        past_data = cursor.fetchall()
                        if past_data:
                           for quantity, expiry_date_str, warehouse in past_data:
                                    expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
                                    if selected_warehouse == "倉庫1" or selected_warehouse == "全部":
                                        if warehouse == "倉庫1":
                                            if expiry_date >= date:
                                              not_expired_inventory += quantity
                                            else:
                                              expired_inventory += quantity
                                    if selected_warehouse == "倉庫2" or selected_warehouse == "全部":
                                         if warehouse == "倉庫2":
                                            if expiry_date >= date:
                                                not_expired_inventory += quantity
                                            else:
                                               expired_inventory += quantity
                           break

                else: # 如果當天有資料
                    if selected_warehouse == "倉庫1" or selected_warehouse == "全部":
                        cursor.execute("""
                            SELECT quantity, expiry_date FROM daily_inventory
                            WHERE date = ? AND name = ? AND warehouse = ?
                        """, (date.strftime("%Y-%m-%d"), item_name, "倉庫1"))
                        for quantity, expiry_date_str in cursor.fetchall():
                            expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
                            if expiry_date >= date:
                                not_expired_inventory += quantity
                            else:
                                expired_inventory += quantity
                    if selected_warehouse == "倉庫2" or selected_warehouse == "全部":
                        cursor.execute("""
                            SELECT quantity, expiry_date FROM daily_inventory
                            WHERE date = ? AND name = ? AND warehouse = ?
                        """, (date.strftime("%Y-%m-%d"), item_name, "倉庫2"))
                        for quantity, expiry_date_str in cursor.fetchall():
                            expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
                            if expiry_date >= date:
                                not_expired_inventory += quantity
                            else:
                                expired_inventory += quantity
                item_inventory[item_name][date]["not_expired"] = not_expired_inventory
                item_inventory[item_name][date]["expired"] = expired_inventory

        conn.close()

        # Apply filters
        filtered_data = []
        columns = ("日期", "產品", "進貨量", "出貨量", "報廢量", "剩餘庫存(未過期)", "剩餘庫存(已過期)")
        for (date, item_name), data in report_data.items():
            not_expired_qty = 0
            expired_qty = 0
            if item_name in item_inventory and date in item_inventory[item_name]:
                not_expired_qty = item_inventory[item_name][date]["not_expired"]
                expired_qty = item_inventory[item_name][date]["expired"]
            item = (
                date.strftime("%Y-%m-%d"),
                item_name,
                data["進貨"],
                data["出貨"],
                data["報廢"],
                not_expired_qty,
                expired_qty
            )

            if all(
                (not filter_vars[col].get() or str(item[i]) == filter_vars[col].get())
                for i, col in enumerate(columns) if filter_vars[col].get()
            ):
                filtered_data.append(item)
        return filtered_data
    except Exception as e:
        print(f"generate_report_data 發生錯誤: {e}")
        return []