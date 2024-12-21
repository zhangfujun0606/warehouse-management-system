import datetime

class Item:
    def __init__(self, name, quantity, expiry_date, note="", warehouse=None):
        self.name = name
        self.quantity = quantity
        self.expiry_date = expiry_date
        self.note = note
        self.warehouse = warehouse # Add warehouse attribute

    def __str__(self):
        return f"品名: {self.name:<10} 數量: {self.quantity:<6} 有效日期: {self.expiry_date.strftime('%Y-%m-%d')} 備註: {self.note}"