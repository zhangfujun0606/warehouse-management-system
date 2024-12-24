import sqlite3
import os
import datetime
from warehouse_management.item import Item
import shutil

DATABASE_FILE = "warehouse.db"
BACKUP_FOLDER = "warehouse_backup"

def initialize_database():
    """初始化資料庫連線，建立資料庫表格(如果不存在)。"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # 檢查 `products` 表格是否存在，如果不存在則創建
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            name TEXT,
            quantity INTEGER,
            expiry_date TEXT,
            note TEXT,
            warehouse TEXT,
            PRIMARY KEY (name, expiry_date, warehouse)
        )
    """)

    # 檢查 `history` 表格是否存在，如果不存在則創建
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            name TEXT,
            quantity INTEGER,
            time TEXT,
            user TEXT,
            note TEXT,
            warehouse TEXT
        )
    """)    

    # 判斷products是否有資料
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
      # 加入預設商品
      default_items = [
          ("橋頭", 0, datetime.date(2024, 12, 31).strftime("%Y-%m-%d"), "預設備註", "倉庫1"),
          ("橋頭2公升", 0, datetime.date(2024, 12, 25).strftime("%Y-%m-%d"), "預設備註", "倉庫1"),
          ("漫步", 0, datetime.date(2024, 12, 25).strftime("%Y-%m-%d"), "預設備註", "倉庫1"),
          ("橋頭", 0, datetime.date(2024, 12, 31).strftime("%Y-%m-%d"), "預設備註", "倉庫2"),
          ("橋頭2公升", 0, datetime.date(2024, 12, 25).strftime("%Y-%m-%d"), "預設備註", "倉庫2"),
          ("漫步", 0, datetime.date(2024, 12, 25).strftime("%Y-%m-%d"), "預設備註", "倉庫2"),
      ]
      cursor.executemany("INSERT INTO products (name, quantity, expiry_date, note, warehouse) VALUES (?, ?, ?, ?, ?)", default_items)

      conn.commit()
    #初始化列表
    warehouse1_items = []
    warehouse2_items = []

    #讀取產品資料
    cursor.execute("SELECT name, quantity, expiry_date, note, warehouse FROM products")
    for row in cursor.fetchall():
        name, quantity, expiry_date_str, note, warehouse = row
    conn.close()

def backup_database():
    """將資料庫檔案備份。"""
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)

    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_FOLDER, f"warehouse_{now}.db")    
    
    try:
       shutil.copy2(DATABASE_FILE, backup_file)
    except Exception as e:
      print(f"Error backing up database: {e}")

    # 刪除三個月前的備份
    threshold_date = datetime.datetime.now() - datetime.timedelta(days=90)

    for filename in os.listdir(BACKUP_FOLDER):
        if filename.startswith("warehouse_") and filename.endswith(".db"):
            try:
                file_time = datetime.datetime.strptime(filename[10:-3], "%Y%m%d_%H%M%S")
                if file_time < threshold_date:
                  os.remove(os.path.join(BACKUP_FOLDER, filename))
            except:
                continue


def save_data_to_database(warehouse1, warehouse2, history_log):
    """將資料儲存到資料庫。"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    #刪除所有產品
    cursor.execute("DELETE FROM products")

    #儲存產品
    for item in warehouse1.inventory.values():
       cursor.execute("INSERT INTO products (name, quantity, expiry_date, note, warehouse) VALUES (?, ?, ?, ?, ?)",
                      (item.name, item.quantity, item.expiry_date.strftime("%Y-%m-%d"), item.note, warehouse1.name))
    for item in warehouse2.inventory.values():
      cursor.execute("INSERT INTO products (name, quantity, expiry_date, note, warehouse) VALUES (?, ?, ?, ?, ?)",
                     (item.name, item.quantity, item.expiry_date.strftime("%Y-%m-%d"), item.note, warehouse2.name))

    #刪除所有歷史紀錄
    cursor.execute("DELETE FROM history")
        
    #儲存歷史紀錄
    for record in history_log:
       cursor.execute("INSERT INTO history (type, name, quantity, time, user, note, warehouse) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (record["type"], record["name"], record["quantity"], record["time"], record["user"], record["note"], record["warehouse"]))

    conn.commit()
    conn.close()

def load_data_from_database(warehouse1, warehouse2):
    """從資料庫讀取資料。"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    #初始化列表
    history_log = []
    warehouse1.inventory = {}
    warehouse2.inventory = {}
    
    #讀取產品資料
    cursor.execute("SELECT name, quantity, expiry_date, note, warehouse FROM products")
    for row in cursor.fetchall():
        name, quantity, expiry_date_str, note, warehouse = row
        expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
        if warehouse == "倉庫1":
            warehouse1.add_item(Item(name, quantity, expiry_date, note, warehouse))
        elif warehouse == "倉庫2":
            warehouse2.add_item(Item(name, quantity, expiry_date, note, warehouse))
    conn.close()
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    #讀取歷史紀錄
    cursor.execute("SELECT type, name, quantity, time, user, note, warehouse FROM history")
    for row in cursor.fetchall():
        type, name, quantity, time, user, note, warehouse = row
        history_log.append({
            "type": type,
            "name": name,            
            "quantity": quantity,
            "time": time,
            "user": user,
            "note": note,
            "warehouse": warehouse
            })
    conn.close()
    
    #初始化 daily_inventory
    daily_inventory1 = {}
    daily_inventory2 = {}
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, quantity, expiry_date, note, warehouse FROM products")
    for row in cursor.fetchall():
      name, quantity, expiry_date_str, note, warehouse = row
      expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
      if warehouse == "倉庫1":
          daily_inventory1[datetime.date.today()] =  { (name, expiry_date) :  Item(name, quantity, expiry_date, note, warehouse) }
      elif warehouse == "倉庫2":
          daily_inventory2[datetime.date.today()] =  { (name, expiry_date) :  Item(name, quantity, expiry_date, note, warehouse) }
    return history_log, daily_inventory1, daily_inventory2
  
def load_data(warehouse1, warehouse2):
  initialize_database()
  history_log, daily_inventory1, daily_inventory2 = load_data_from_database(warehouse1, warehouse2)
  return history_log, daily_inventory1, daily_inventory2

#其他程式碼使用
def save_data(warehouse1, warehouse2, history_log, daily_inventory1, daily_inventory2):
    #backup_database()  先不備份，避免產生多個無用備份
    save_data_to_database(warehouse1, warehouse2, history_log)