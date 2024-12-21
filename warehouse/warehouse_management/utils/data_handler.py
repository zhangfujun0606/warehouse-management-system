import json
import os
import datetime
from ..item import Item

def save_data(warehouse1, warehouse2, history_log, daily_inventory1, daily_inventory2):
    data = {
        "warehouse1": {
            "name": warehouse1.name,
            "inventory": {
                str(key): {
                    "name": item.name,
                    "quantity": item.quantity,
                    "expiry_date": item.expiry_date.strftime("%Y-%m-%d"),
                    "note": item.note,
                }
                for key, item in warehouse1.inventory.items()
            },
            "daily_inventory": {
                str(date): {
                    str(key): {
                        "name": item.name,
                        "quantity": item.quantity,
                        "expiry_date": item.expiry_date.strftime("%Y-%m-%d"),
                        "note": item.note,
                    }
                    for key, item in inventory.items()
                }
                for date, inventory in daily_inventory1.items()
            }
        },
        "warehouse2": {
            "name": warehouse2.name,
            "inventory": {
                str(key): {
                    "name": item.name,
                    "quantity": item.quantity,
                    "expiry_date": item.expiry_date.strftime("%Y-%m-%d"),
                     "note": item.note,
                }
                for key, item in warehouse2.inventory.items()
            },
            "daily_inventory": {
                str(date): {
                    str(key): {
                        "name": item.name,
                        "quantity": item.quantity,
                        "expiry_date": item.expiry_date.strftime("%Y-%m-%d"),
                        "note": item.note,
                    }
                    for key, item in inventory.items()
                }
                for date, inventory in daily_inventory2.items()
            }
        },
        "history_log": history_log
    }
    with open("warehouse_data.json", "w") as f:
        json.dump(data, f)

def load_data(warehouse1, warehouse2):
    history_log = []
    daily_inventory1 = {}
    daily_inventory2 = {}
    if os.path.exists("warehouse_data.json"):
        with open("warehouse_data.json", "r") as f:
            data = json.load(f)

            # Load warehouse1 data
            warehouse1.inventory = {}
            for key_str, item_data in data["warehouse1"]["inventory"].items():
                try:
                    key = tuple(eval(key_str))
                    note = item_data.get("note", "")
                    warehouse1.inventory[key] = Item(item_data["name"], int(item_data["quantity"]), datetime.datetime.strptime(item_data["expiry_date"], "%Y-%m-%d").date(), note)
                except Exception as e:
                    print(f"Error loading warehouse1 item: {e}, data: {item_data}, key: {key_str}")
            
            daily_inventory1 = {}
            for date_str, inventory_data in data["warehouse1"].get("daily_inventory", {}).items():
                try:
                    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    daily_inventory1[date] = {}
                    for key_str, item_data in inventory_data.items():
                        key = tuple(eval(key_str))
                        note = item_data.get("note", "")
                        daily_inventory1[date][key] = Item(item_data["name"], int(item_data["quantity"]), datetime.datetime.strptime(item_data["expiry_date"], "%Y-%m-%d").date(), note)
                except Exception as e:
                    print(f"Error loading warehouse1 daily inventory: {e}, data: {inventory_data}, key: {key_str}")

            # Load warehouse2 data
            warehouse2.inventory = {}
            for key_str, item_data in data["warehouse2"]["inventory"].items():
                try:
                    key = tuple(eval(key_str))
                    note = item_data.get("note", "")
                    warehouse2.inventory[key] = Item(item_data["name"], int(item_data["quantity"]), datetime.datetime.strptime(item_data["expiry_date"], "%Y-%m-%d").date(), note)
                except Exception as e:
                    print(f"Error loading warehouse2 item: {e}, data: {item_data}, key: {key_str}")
            
            daily_inventory2 = {}
            for date_str, inventory_data in data["warehouse2"].get("daily_inventory", {}).items():
                try:
                    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    daily_inventory2[date] = {}
                    for key_str, item_data in inventory_data.items():
                        key = tuple(eval(key_str))
                        note = item_data.get("note", "")
                        daily_inventory2[date][key] = Item(item_data["name"], int(item_data["quantity"]), datetime.datetime.strptime(item_data["expiry_date"], "%Y-%m-%d").date(), note)
                except Exception as e:
                    print(f"Error loading warehouse2 daily inventory: {e}, data: {item_data}, key: {key_str}")

            history_log = data.get("history_log", [])
    return history_log, daily_inventory1, daily_inventory2