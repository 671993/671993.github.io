from base_app import BaseApp

class JobApp(BaseApp):
    def __init__(self, window):
        super().__init__(window, 'database.db',
                         "/home/gunnar/Documents/Tienda/tiendaentrerios/todoloquebuscas/empleos/trab.html",
                         "/home/gunnar/Documents/Tienda/tiendaentrerios/todoloquebuscas/empleos/trab.js")
