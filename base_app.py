import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import sqlite3
import datetime
import threading
import time

class BaseApp:
    def __init__(self, window, db_name, html_file_path, js_file_path):
        self.db_name = db_name
        self.HTML_FILE_PATH = html_file_path
        self.JS_FILE_PATH = js_file_path

        # Creating a Frame Container
        self.frame = tk.LabelFrame(window, text='Registrar nuevo anuncio')
        self.frame.grid(row=1, column=0, columnspan=3, pady=30)

        # Fecha de publicación Input
        self.fechainicio = self.create_label_entry(self.frame, 'Fecha de Publicación* (YYYY-MM-DD)*: ', 1, 0)
        # Fecha de conclusión Input
        self.fechaconclution = self.create_label_entry(self.frame, 'Fecha de Conclución* (YYYY-MM-DD)*: ', 2, 0)
        # Tipo de anuncio Input
        self.tipo = self.create_combobox(self.frame, 'Tipo de anuncio*: ', [], 3, 0)
        self.tipo.bind("<<ComboboxSelected>>", self.on_type_selected)

        # Cargar tipos de anuncios desde la base de datos
        self.load_ad_types()

        # Título del anuncio Input
        self.titulo = self.create_label_entry(self.frame, 'Título del anuncio: ', 4, 0)
        # Anuncio Input
        self.anuncio = self.create_label_entry(self.frame, 'Descripción*: ', 5, 0)
        # Detalles Input
        self.detalles = self.create_label_entry(self.frame, 'Enlace de Detalles: ', 6, 0)

        # Button Add Product
        ttk.Button(self.frame, text='Guardar Anuncio', command=self.add_product).grid(row=7, columnspan=2, sticky=tk.W + tk.E)

        # Output Messages
        self.message = tk.Label(self.frame, text='', fg='red')
        self.message.grid(row=8, column=0, columnspan=2, sticky=tk.W + tk.E)

        # Table
        self.tree = ttk.Treeview(self.frame, height=10, columns=('col1', 'col2', 'col3'))
        self.tree.grid(row=9, column=0, columnspan=2)
        self.tree.heading('#0', text='Fecha de publicación', anchor=tk.CENTER)
        self.tree.heading('#1', text='Fecha de conclusión', anchor=tk.CENTER)
        self.tree.heading('#2', text='Tipo de anuncio', anchor=tk.CENTER)
        self.tree.heading('#3', text='Título del anuncio', anchor=tk.CENTER)

        # Buttons
        ttk.Button(self.frame, text='Eliminar', command=self.delete_product).grid(row=10, column=0, sticky=tk.W + tk.E)
        ttk.Button(self.frame, text='Actualizar anuncios', command=self.update_html_file).grid(row=10, column=1, sticky=tk.W + tk.E)

        # Filling the Rows
        self.get_products()

        # Start cleanup thread
        cleanup_thread = threading.Thread(target=self.schedule_cleanup)
        cleanup_thread.daemon = True
        cleanup_thread.start()

    def create_label_entry(self, parent, label_text, row, column):
        tk.Label(parent, text=label_text).grid(row=row, column=column)
        entry = tk.Entry(parent)
        entry.grid(row=row, column=column + 1)
        return entry

    def create_combobox(self, parent, label_text, values, row, column):
        tk.Label(parent, text=label_text).grid(row=row, column=column)
        combobox = ttk.Combobox(parent, values=values, state="readonly")
        combobox.grid(row=row, column=column + 1)
        return combobox

    def run_query(self, query, parameters=()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    def load_ad_types(self):
        query = "SELECT DISTINCT tipo FROM product ORDER BY tipo ASC"
        db_rows = self.run_query(query)
        ad_types = [row[0] for row in db_rows]
        ad_types.append("Agregar tipo...")
        self.tipo['values'] = ad_types

    def get_products(self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        query = 'SELECT * FROM product ORDER BY fechainicio DESC'
        db_rows = self.run_query(query)
        for row in db_rows:
            self.tree.insert('', 0, text=row[1], values=(row[2], row[3], row[4]))

    def on_type_selected(self, event):
        if self.tipo.get() == "Agregar tipo...":
            new_type = tk.simpledialog.askstring("Nuevo tipo de anuncio", "Ingrese el nuevo tipo de anuncio:")
            if new_type:
                new_type = new_type.replace(" ", "_")
                self.tipo['values'] = list(self.tipo['values'])[:-1] + [new_type, "Agregar tipo..."]
                self.tipo.set(new_type)

    def validate_date_format(self, date_text):
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def validation(self):
        if not self.validate_date_format(self.fechainicio.get()):
            messagebox.showerror("Error", "La Fecha de Publicación debe estar en el formato YYYY-MM-DD")
            return False
        if not self.validate_date_format(self.fechaconclution.get()):
            messagebox.showerror("Error", "La Fecha de Conclución debe estar en el formato YYYY-MM-DD")
            return False
        if len(self.tipo.get()) == 0 or len(self.anuncio.get()) == 0:
            messagebox.showerror("Error", "Los campos con * son obligatorios")
            return False
        return True

    def add_product(self):
        if self.validation():
            query = 'INSERT INTO product VALUES(NULL, ?, ?, ?, ?, ?, ?)'
            parameters = (self.fechainicio.get(), self.fechaconclution.get(), self.tipo.get(), self.titulo.get(), self.anuncio.get(), self.detalles.get())
            self.run_query(query, parameters)
            self.message['text'] = 'Anuncio {} agregado satisfactoriamente'.format(self.titulo.get())
            self.fechainicio.delete(0, tk.END)
            self.fechaconclution.delete(0, tk.END)
            self.tipo.set("")
            self.titulo.delete(0, tk.END)
            self.anuncio.delete(0, tk.END)
            self.detalles.delete(0, tk.END)
        else:
            self.message['text'] = 'Los items en * son obligatorios'
        self.get_products()

    def delete_product(self):
        self.message['text'] = ''
        try:
            selected_item = self.tree.selection()[0]
            titulo = self.tree.item(selected_item)['values'][2]
        except IndexError as e:
            self.message['text'] = 'Por favor, seleccione un registro'
            return
        query = 'DELETE FROM product WHERE titulo = ?'
        self.run_query(query, (titulo,))
        self.message['text'] = 'Registro {} fue eliminado'.format(titulo)
        self.get_products()

    def clean_expired_ads(self):
        query = "DELETE FROM product WHERE date(fechaconclution) < date('now')"
        self.run_query(query)

    def schedule_cleanup(self):
        while True:
            self.clean_expired_ads()
            time.sleep(3600)  # Espera 1 hora

    def update_html_file(self):
        self.clean_expired_ads()
        query = "SELECT fechainicio, fechainicio, tipo, titulo, anuncio, detalles FROM product WHERE date(fechainicio) <= date('now')"
        db_rows = self.run_query(query)
        ads_content = ""
        job_types = {}
        for row in db_rows:
            ads_content += f"""
            <div class="job {row[2]}">
            <div class="job-header">
            <h4>{row[3]}</h4>
            <span class="job-date">Publicado: {row[0]}</span>
            </div>
            <p>{row[4]}</p>
            <a href="{row[5]}" class="job-details">Ver detalles</a>
            </div>
            """
            job_type = row[2]
            if job_type in job_types:
                job_types[job_type] += 1
            else:
                job_types[job_type] = 1
        with open(self.HTML_FILE_PATH, "r") as file:
            content = file.read()
        start_filters = "<!-- inicio de filtros -->"
        end_filters = "<!-- fin de filtros -->"
        filters_content = ""
        for job_type, count in job_types.items():
            filters_content += f"<li><a href=\"#\" onclick=\"filterJobs('{job_type}')\">{job_type.replace('_', ' ')} <span id=\"{job_type}-count\">({count})</span></a></li>\n"
        start_index = content.find(start_filters) + len(start_filters)
        end_index = content.find(end_filters)
        if start_index != -1 and end_index != -1:
            content = content[:start_index] + filters_content + content[end_index:]
        start_ads = "<!-- inicio de los anuncios -->"
        end_ads = "<!-- fin de los anuncios -->"
        start_index = content.find(start_ads) + len(start_ads)
        end_index = content.find(end_ads)
        if start_index != -1 and end_index != -1:
            content = content[:start_index] + ads_content + content[end_index:]
        with open(self.HTML_FILE_PATH, "w") as file:
            file.write(content)
        with open(self.JS_FILE_PATH, "r") as file:
            js_content = file.read()
        for job_type, count in job_types.items():
            job_type_with_underscores = job_type.replace(" ", "_")
            js_content = js_content.replace(f"var {job_type_with_underscores}_count = 0;", f"var {job_type_with_underscores}_count = {count};")
        with open(self.JS_FILE_PATH, "w") as file:
            file.write(js_content)
        self.message['text'] = "Archivo HTML actualizado"
