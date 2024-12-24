import datetime
from tkinter import messagebox
import copy

class Warehouse:
    def __init__(self, name):
        self.name = name
        self.inventory = {}
        self.daily_inventory = {}  # 新增 daily_inventory 屬性

    def add_item(self, item):
        item.warehouse = self.name
        key = (item.name, item.expiry_date)
        if key in self.inventory:
            self.inventory[key].quantity += item.quantity
        else:
            self.inventory[key] = item
        self._record_daily_inventory()

    def remove_item(self, item_name, expiry_date, quantity):
        key = (item_name, expiry_date)
        if key in self.inventory:
            if self.inventory[key].quantity >= quantity:
                self.inventory[key].quantity -= quantity
                if self.inventory[key].quantity == 0:
                    del self.inventory[key]
                self._record_daily_inventory()
                return True
            else:
                messagebox.showerror("錯誤", "庫存不足")
                return False
        else:
            messagebox.showerror("錯誤", "此物品不在倉庫中")
            return False

    def display_inventory(self):
        inventory_list = []
        # 自訂排序函數
        def sort_key(item):
            return (item.name, item.expiry_date)

        sorted_items = sorted(self.inventory.values(), key=sort_key)
        for item in sorted_items:
            if item.quantity > 0:
                expiry_str = item.expiry_date.strftime('%Y-%m-%d')
                inventory_list.append((item.name, item.quantity, expiry_str, self.name, item.note))
        return inventory_list

    def get_item_names(self, include_zero=False):
        if include_zero:
            return sorted(list(set(item.name for item in self.inventory.values())))
        else:
            return sorted(list(set(item.name for item in self.inventory.values() if item.quantity > 0)))

    def get_expiry_dates(self, item_name=None):
        if item_name:
            filtered_dates = []
            for item in self.inventory.values():
                if item.name == item_name and item.quantity > 0:
                    filtered_dates.append(item.expiry_date)
            return sorted(list(set(filtered_dates)))
        else:
            filtered_dates = []
            for item in self.inventory.values():
                if item.quantity > 0:
                    filtered_dates.append(item.expiry_date)
            return sorted(list(set(filtered_dates)))
    
    def _record_daily_inventory(self):
        today = datetime.date.today()
        self.daily_inventory[today] = copy.deepcopy(self.inventory)
        for key, item in self.daily_inventory[today].items():
            item.warehouse = self.name