import tkinter as tk
from job_app import JobApp
from inmuebles_app import InmueblesApp
from motores_app import MotoresApp
from varios_app import VariosApp

class MainApplication:
    def __init__(self, root):
        self.wind = root
        self.wind.title('Gestor de Anuncios')
        self.current_section = None
        self.current_app = None
        self.buttons = {}
        self.switch_section('Empleos', JobApp)

        # Create buttons for each section
        self.buttons['Empleos'] = tk.Button(self.wind, text='Empleos', command=lambda: self.switch_section('Empleos', JobApp))
        self.buttons['Empleos'].grid(row=0, column=0)

        self.buttons['Inmuebles'] = tk.Button(self.wind, text='Inmuebles', command=lambda: self.switch_section('Inmuebles', InmueblesApp))
        self.buttons['Inmuebles'].grid(row=0, column=1)

        self.buttons['Motores'] = tk.Button(self.wind, text='Motores', command=lambda: self.switch_section('Motores', MotoresApp))
        self.buttons['Motores'].grid(row=0, column=2)

        self.buttons['Varios'] = tk.Button(self.wind, text='Varios', command=lambda: self.switch_section('Varios', VariosApp))
        self.buttons['Varios'].grid(row=0, column=3)

    def switch_section(self, section, app_class):
        if self.current_section == section:
            return
        if self.current_app:
            self.current_app.frame.destroy()
        self.current_app = app_class(self.wind)
        self.current_section = section

        for name, button in self.buttons.items():
            button.config(state=tk.DISABLED if name == section else tk.NORMAL)

if __name__ == '__main__':
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
