import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import clips


class CLIPSManager:
    def __init__(self, rules_file):
        self.env = clips.Environment()
        self.env.load(rules_file)
        #self.env.reset()
        self.run()
        #self.logs = {'alerts': [], 'notices': [], 'infos': []}


    def run(self):
        self.env.reset()
        self.env.run()
        self.categorize_logs()

    def categorize_logs(self):
        self.logs = {'alerts': [], 'notices': [], 'infos': []}

        for fact in self.env.facts():

            if fact.template.name == 'alert':

                self.logs['alerts'].append(
                    f"[ALERT] Товар {fact['product']} близок к окончанию срока годности!"
                )
            elif fact.template.name == 'request' and fact['priority'] == 'high':
                self.logs['notices'].append(
                    f"[NOTICE] Обнаружена заявка высокого приоритета: {fact['id']}"
                )
            elif fact.template.name == 'shipment':
                self.logs['infos'].append(
                    f"[OK] Отгрузка {fact['product']} из {fact['from']} в {fact['to']} запланирована."
                )
            elif fact.template.name == 'candidate_warehouse':
                self.logs['infos'].append(
                    f"[INFO] Найден склад {fact['warehouse_id']} для продукта {fact['product']}"
                )

    def get_requests(self):
        requests = []
        for fact in self.env.facts():
            if fact.template.name == 'request':
                requests.append({
                    'id': fact['id'],
                    'product': fact['product'],
                    'quantity': fact['quantity'],
                    'destination': fact['destination'],
                    'priority': fact['priority']
                })
        return requests

    def get_warehouses(self):
        warehouses = []
        for fact in self.env.facts():
            if fact.template.name == 'warehouse':
                products = ', '.join(fact['products'])
                warehouses.append({
                    'id': fact['id'],
                    'location': fact['location'],
                    'products': products
                })
        return warehouses

    def add_request(self, request_data):
        template = self.env.find_template('request')
        new_fact = template.assert_fact(
            id=clips.Symbol(request_data['id']),
            product=clips.Symbol(request_data['product']),
            quantity=request_data['quantity'],
            destination=clips.Symbol(request_data['destination']),
            priority=clips.Symbol(request_data['priority'])
        )
        self.categorize_logs()
        return new_fact

    def remove_request(self, request_id):
        for fact in self.env.facts():
            if fact.template.name == 'request' and fact['id'] == request_id:
                fact.retract()
                self.categorize_logs()
                return True
        return False

    def add_product_to_warehouse(self, warehouse_id, product_name, shelf_life, storage_conditions):
        for fact in self.env.facts():
            if fact.template.name == 'warehouse' and fact['id'] == warehouse_id:
                # Create new product list
                new_products = list(fact['products'])
                if product_name not in new_products:
                    new_products.append(clips.Symbol(product_name))
                    location = fact['location']
                    # Retract old fact
                    fact.retract()

                    # Create new fact with updated products
                    template = self.env.find_template('warehouse')
                    # print(fact)
                    template.assert_fact(
                        id=clips.Symbol(warehouse_id),
                        location=clips.Symbol(location),
                        products=new_products
                    )

                    # Create new fact with updated products
                    template = self.env.find_template('product')
                    # print(fact)
                    template.assert_fact(
                        name=clips.Symbol(product_name),
                        shelf_life=clips.Symbol(shelf_life),
                        storage_conditions=storage_conditions
                    )
                    self.categorize_logs()
                    return True
        return False


class AddRequestDialog(simpledialog.Dialog):
    def __init__(self, parent, title):
        self.result_data = None
        super().__init__(parent, title)

    def body(self, frame):
        ttk.Label(frame, text="ID:").grid(row=0, sticky=tk.W)
        ttk.Label(frame, text="Товар:").grid(row=1, sticky=tk.W)
        ttk.Label(frame, text="Количество:").grid(row=2, sticky=tk.W)
        ttk.Label(frame, text="Направление:").grid(row=3, sticky=tk.W)
        ttk.Label(frame, text="Приоритет:").grid(row=4, sticky=tk.W)

        self.id_var = tk.StringVar()
        self.product_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.destination_var = tk.StringVar()
        self.priority_var = tk.StringVar()

        ttk.Entry(frame, textvariable=self.id_var).grid(row=0, column=1)
        ttk.Entry(frame, textvariable=self.product_var).grid(row=1, column=1)
        ttk.Entry(frame, textvariable=self.quantity_var).grid(row=2, column=1)
        ttk.Entry(frame, textvariable=self.destination_var).grid(row=3, column=1)

        priorities = ['low', 'medium', 'high']
        ttk.Combobox(frame, textvariable=self.priority_var,
                     values=priorities, state='readonly').grid(row=4, column=1)

        return frame

    def validate(self):
        try:
            # Validate quantity
            int(self.quantity_var.get())

            # Validate required fields
            if (not self.id_var.get() or
                    not self.product_var.get() or
                    not self.destination_var.get() or
                    not self.priority_var.get()):
                raise ValueError("Все поля обязательны для заполнения")

            return True
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return False

    def apply(self):
        self.result_data = {
            'id': self.id_var.get(),
            'product': self.product_var.get(),
            'quantity': int(self.quantity_var.get()),
            'destination': self.destination_var.get(),
            'priority': self.priority_var.get()
        }


class AddProductDialog(simpledialog.Dialog):
    def __init__(self, parent, title):
        self.result_data = None
        super().__init__(parent, title)

    def body(self, frame):
        ttk.Label(frame, text="ID склада:").grid(row=0, sticky=tk.W)
        ttk.Label(frame, text="Товар:").grid(row=1, sticky=tk.W)
        ttk.Label(frame, text="Срок годности:").grid(row=2, sticky=tk.W)
        ttk.Label(frame, text="Условия хранения:").grid(row=3, sticky=tk.W)

        self.warehouse_var = tk.StringVar()
        self.product_var = tk.StringVar()
        self.shelf_life_var = tk.StringVar()
        self.storage_conditions_var = tk.StringVar()

        ttk.Entry(frame, textvariable=self.warehouse_var).grid(row=0, column=1)
        ttk.Entry(frame, textvariable=self.product_var).grid(row=1, column=1)
        ttk.Entry(frame, textvariable=self.shelf_life_var).grid(row=2, column=1)
        ttk.Entry(frame, textvariable=self.storage_conditions_var).grid(row=3, column=1)

        return frame

    def validate(self):
        try:
            if (not self.warehouse_var.get() or not self.product_var.get() or
                    not self.shelf_life_var.get() or not self.storage_conditions_var.get()):
                raise ValueError("Все поля обязательны для заполнения")
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return False

    def apply(self):
        self.result_data = {
            'warehouse_id': self.warehouse_var.get(),
            'product': self.product_var.get(),
            'shelf_life': self.shelf_life_var.get(),
            'storage_conditions': self.storage_conditions_var.get()
        }


class LogisticsApp(tk.Tk):
    def __init__(self, clips_manager):
        super().__init__()
        self.title("Экспертная система логистики")
        self.geometry("1000x700")
        self.clips = clips_manager

        # Create tabs
        self.notebook = ttk.Notebook(self)
        self.main_tab = ttk.Frame(self.notebook)
        self.orders_tab = ttk.Frame(self.notebook)
        self.warehouses_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.main_tab, text="Главная")
        self.notebook.add(self.orders_tab, text="Заказы")
        self.notebook.add(self.warehouses_tab, text="Товары на складах")
        self.notebook.pack(expand=True, fill=tk.BOTH)

        self.setup_main_tab()
        self.setup_orders_tab()
        self.setup_warehouses_tab()

        self.update_all_tabs()

    def setup_main_tab(self):
        # Alerts panel (top-left)
        alerts_frame = ttk.LabelFrame(self.main_tab, text="Предупреждения")
        alerts_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)

        self.alerts_text = tk.Text(alerts_frame, height=15, width=40)
        self.alerts_text.pack(fill=tk.BOTH, expand=True)
        ttk.Scrollbar(alerts_frame,
                      command=self.alerts_text.yview).pack(side=tk.RIGHT, fill=tk.Y)
        self.alerts_text.config(yscrollcommand=lambda *args: None)

        # Notices panel (top-right)
        notices_frame = ttk.LabelFrame(self.main_tab, text="Уведомления")
        notices_frame.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        self.notices_text = tk.Text(notices_frame, height=15, width=40)
        self.notices_text.pack(fill=tk.BOTH, expand=True)
        ttk.Scrollbar(notices_frame,
                      command=self.notices_text.yview).pack(side=tk.RIGHT, fill=tk.Y)
        self.notices_text.config(yscrollcommand=lambda *args: None)

        # Info panel (bottom)
        info_frame = ttk.LabelFrame(self.main_tab, text="Информация")
        info_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)

        self.info_text = tk.Text(info_frame, height=15)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        ttk.Scrollbar(info_frame,
                      command=self.info_text.yview).pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=lambda *args: None)

        # Configure grid weights
        self.main_tab.grid_columnconfigure(0, weight=1)
        self.main_tab.grid_columnconfigure(1, weight=1)
        self.main_tab.grid_rowconfigure(0, weight=1)
        self.main_tab.grid_rowconfigure(1, weight=1)

    def setup_orders_tab(self):
        # Orders treeview
        columns = ("id", "product", "quantity", "destination", "priority")
        self.orders_tree = ttk.Treeview(
            self.orders_tab, columns=columns, show="headings")

        for col in columns:
            self.orders_tree.heading(col, text=col.capitalize())
            self.orders_tree.column(col, width=100)

        self.orders_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons frame
        btn_frame = ttk.Frame(self.orders_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="Добавить заказ",
                   command=self.add_request).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить заказ",
                   command=self.remove_request).pack(side=tk.LEFT, padx=5)

    def setup_warehouses_tab(self):
        # Warehouses treeview
        columns = ("id", "location", "products")
        self.warehouses_tree = ttk.Treeview(
            self.warehouses_tab, columns=columns, show="headings")

        for col in columns:
            self.warehouses_tree.heading(col, text=col.capitalize())
            self.warehouses_tree.column(col, width=100)

        self.warehouses_tree.column("products", width=300)
        self.warehouses_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons frame
        btn_frame = ttk.Frame(self.warehouses_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="Добавить товар",
                   command=self.add_product_to_warehouse).pack(side=tk.LEFT, padx=5)

    def update_all_tabs(self):
        self.update_main_tab()
        self.update_orders_tab()
        self.update_warehouses_tab()

    def update_main_tab(self):
        self.alerts_text.config(state=tk.NORMAL)
        self.alerts_text.delete(1.0, tk.END)
        for alert in self.clips.logs['alerts']:
            self.alerts_text.insert(tk.END, alert + '\n')
        self.alerts_text.config(state=tk.DISABLED)

        self.notices_text.config(state=tk.NORMAL)
        self.notices_text.delete(1.0, tk.END)
        for notice in self.clips.logs['notices']:
            self.notices_text.insert(tk.END, notice + '\n')
        self.notices_text.config(state=tk.DISABLED)

        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        for info in self.clips.logs['infos']:
            self.info_text.insert(tk.END, info + '\n')
        self.info_text.config(state=tk.DISABLED)

    def update_orders_tab(self):
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        for request in self.clips.get_requests():
            self.orders_tree.insert('', tk.END, values=(
                request['id'],
                request['product'],
                request['quantity'],
                request['destination'],
                request['priority']
            ))

    def update_warehouses_tab(self):
        for item in self.warehouses_tree.get_children():
            self.warehouses_tree.delete(item)

        for warehouse in self.clips.get_warehouses():
            self.warehouses_tree.insert('', tk.END, values=(
                warehouse['id'],
                warehouse['location'],
                warehouse['products']
            ))

    def add_request(self):
        dialog = AddRequestDialog(self, "Добавить заказ")
        if dialog.result_data:
            self.clips.add_request(dialog.result_data)
            self.update_all_tabs()

    def remove_request(self):
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ для удаления")
            return

        request_id = self.orders_tree.item(selected[0])['values'][0]
        if self.clips.remove_request(request_id):
            self.update_all_tabs()

    def add_product_to_warehouse(self):
        dialog = AddProductDialog(self, "Добавить товар на склад")
        if dialog.result_data:
            warehouse_id = dialog.result_data['warehouse_id']
            product_name = dialog.result_data['product']
            shelf_life = dialog.result_data['shelf_life']
            storage_conditions = dialog.result_data['storage_conditions']

            if self.clips.add_product_to_warehouse(warehouse_id, product_name, shelf_life, storage_conditions):
                self.update_all_tabs()
            else:
                messagebox.showerror("Ошибка",
                                     "Не удалось добавить товар. Проверьте ID склада и название товара")


if __name__ == "__main__":
    # Инициализация CLIPS с нашими правилами
    manager = CLIPSManager("rules.clp")

    # Запуск приложения
    app = LogisticsApp(manager)
    app.mainloop()
