import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import csv
from datetime import datetime

DATA_FILE = "registro_marketplace.json"

class MarketplaceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Llamadas y Pagos - Marketplace")
        self.root.geometry("520x700")
        self.root.resizable(False, False)

        self.dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        self.meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        self.data = self.cargar_datos()

        # Crear Notebook (Pestañas)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_registro = ttk.Frame(self.notebook)
        self.tab_stats = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_registro, text=" Registro y Cobros ")
        self.notebook.add(self.tab_stats, text=" Reporte Mensual ")

        # --- PESTAÑA 1: REGISTRO ---
        self.setup_tab_registro()

        # --- PESTAÑA 2: ESTADÍSTICAS ---
        self.setup_tab_stats()

        # Seleccionar fecha actual automáticamente
        self.seleccionar_fecha_actual()
        self.actualizar_vista()

    def setup_tab_registro(self):
        # Configuración de Fecha y Tarifa
        frame_top = ttk.LabelFrame(self.tab_registro, text=" Configuración y Tarifa ")
        frame_top.pack(fill="x", padx=15, pady=10)

        ttk.Label(frame_top, text="Mes:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_mes = ttk.Combobox(frame_top, values=self.meses, state="readonly", width=11)
        self.combo_mes.grid(row=0, column=1, padx=5, pady=5)
        self.combo_mes.bind("<<ComboboxSelected>>", self.actualizar_vista)

        ttk.Label(frame_top, text="Semana:").grid(row=0, column=2, padx=5, pady=5)
        self.combo_semana = ttk.Combobox(frame_top, values=["Semana 1", "Semana 2", "Semana 3", "Semana 4"], state="readonly", width=9)
        self.combo_semana.grid(row=0, column=3, padx=5, pady=5)
        self.combo_semana.bind("<<ComboboxSelected>>", self.actualizar_vista)

        ttk.Label(frame_top, text="Precio/Llamada ($):").grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="e")
        self.entry_precio = ttk.Entry(frame_top, width=10)
        self.entry_precio.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.entry_precio.insert(0, "1.20")
        self.entry_precio.bind("<KeyRelease>", self.actualizar_calculos_evento)

        # Entradas diarias (Mensajes y Llamadas Válidas)
        frame_dias = ttk.LabelFrame(self.tab_registro, text=" Registro Diario ")
        frame_dias.pack(fill="x", padx=15, pady=5)

        ttk.Label(frame_dias, text="Día", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=10, pady=2, sticky="w")
        ttk.Label(frame_dias, text="Mensajes", font=("Arial", 9, "bold")).grid(row=0, column=1, padx=10, pady=2)
        ttk.Label(frame_dias, text="Llamadas Válidas", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=10, pady=2)

        self.entries_msgs = {}
        self.entries_llamadas = {}

        for idx, dia in enumerate(self.dias, start=1):
            ttk.Label(frame_dias, text=f"{dia}:").grid(row=idx, column=0, sticky="w", padx=10, pady=3)
            
            e_msg = ttk.Entry(frame_dias, width=10)
            e_msg.grid(row=idx, column=1, padx=10, pady=3)
            e_msg.insert(0, "0")
            e_msg.bind("<KeyRelease>", self.actualizar_calculos_evento)
            self.entries_msgs[dia] = e_msg

            e_lla = ttk.Entry(frame_dias, width=10)
            e_lla.grid(row=idx, column=2, padx=10, pady=3)
            e_lla.insert(0, "0")
            e_lla.bind("<KeyRelease>", self.actualizar_calculos_evento)
            self.entries_llamadas[dia] = e_lla

        # Botón Guardar
        btn_guardar = ttk.Button(self.tab_registro, text="Guardar Datos de la Semana", command=self.guardar_semana)
        btn_guardar.pack(pady=10)

        # Resumen Rápido de Cobro
        frame_resumen = ttk.LabelFrame(self.tab_registro, text=" Resumen de Cobro de la Semana ")
        frame_resumen.pack(fill="x", padx=15, pady=5)

        self.lbl_semana_msgs = ttk.Label(frame_resumen, text="Total Mensajes: 0", font=("Arial", 10))
        self.lbl_semana_msgs.pack(anchor="w", padx=10, pady=2)

        self.lbl_semana_llamadas = ttk.Label(frame_resumen, text="Total Llamadas Válidas: 0", font=("Arial", 10))
        self.lbl_semana_llamadas.pack(anchor="w", padx=10, pady=2)

        self.lbl_semana_monto = ttk.Label(frame_resumen, text="Monto a Cobrar esta Semana: $0.00", font=("Arial", 11, "bold"))
        self.lbl_semana_monto.pack(anchor="w", padx=10, pady=4)

    def setup_tab_stats(self):
        frame_mes = ttk.LabelFrame(self.tab_stats, text=" Acumulado Mensual ")
        frame_mes.pack(fill="x", padx=15, pady=10)

        self.lbl_mes_msgs = ttk.Label(frame_mes, text="Mensajes en el Mes: 0", font=("Arial", 10))
        self.lbl_mes_msgs.pack(anchor="w", padx=10, pady=3)

        self.lbl_mes_llamadas = ttk.Label(frame_mes, text="Llamadas Válidas en el Mes: 0", font=("Arial", 10))
        self.lbl_mes_llamadas.pack(anchor="w", padx=10, pady=3)

        self.lbl_mes_promedio = ttk.Label(frame_mes, text="Promedio Diario (Msgs): 0.0", font=("Arial", 10))
        self.lbl_mes_promedio.pack(anchor="w", padx=10, pady=3)

        self.lbl_mes_monto = ttk.Label(frame_mes, text="Total Generado en el Mes: $0.00", font=("Arial", 11, "bold"))
        self.lbl_mes_monto.pack(anchor="w", padx=10, pady=5)

        # Exportación
        frame_export = ttk.LabelFrame(self.tab_stats, text=" Exportar Datos ")
        frame_export.pack(fill="x", padx=15, pady=15)

        btn_excel = ttk.Button(frame_export, text=" Exportar Historial a CSV / Excel", command=self.exportar_csv)
        btn_excel.pack(padx=10, pady=10)

    def seleccionar_fecha_actual(self):
        now = datetime.now()
        mes_idx = now.month - 1
        self.combo_mes.current(mes_idx)

        dia_mes = now.day
        if dia_mes <= 7:
            sem_idx = 0
        elif dia_mes <= 14:
            sem_idx = 1
        elif dia_mes <= 21:
            sem_idx = 2
        else:
            sem_idx = 3
        self.combo_semana.current(sem_idx)

    def cargar_datos(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def guardar_datos(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    def guardar_semana(self):
        mes = self.combo_mes.get()
        semana = self.combo_semana.get()

        if mes not in self.data:
            self.data[mes] = {}

        self.data[mes][semana] = {}
        for dia in self.dias:
            try:
                msgs = int(self.entries_msgs[dia].get())
            except ValueError:
                msgs = 0

            try:
                llamadas = int(self.entries_llamadas[dia].get())
            except ValueError:
                llamadas = 0

            self.data[mes][semana][dia] = {"msgs": msgs, "llamadas": llamadas}

        self.guardar_datos()
        self.calcular_totales()
        messagebox.showinfo("Éxito", f"Datos de {semana} de {mes} guardados correctamente.")

    def actualizar_vista(self, event=None):
        mes = self.combo_mes.get()
        semana = self.combo_semana.get()

        semana_data = self.data.get(mes, {}).get(semana, {})

        for dia in self.dias:
            datos_dia = semana_data.get(dia, {"msgs": 0, "llamadas": 0})
            
            # Compatibilidad con versiones anteriores
            if isinstance(datos_dia, int):
                datos_dia = {"msgs": datos_dia, "llamadas": 0}

            self.entries_msgs[dia].delete(0, tk.END)
            self.entries_msgs[dia].insert(0, str(datos_dia.get("msgs", 0)))

            self.entries_llamadas[dia].delete(0, tk.END)
            self.entries_llamadas[dia].insert(0, str(datos_dia.get("llamadas", 0)))

        self.calcular_totales()

    def actualizar_calculos_evento(self, event=None):
        self.calcular_totales()

    def calcular_totales(self):
        mes = self.combo_mes.get()
        semana = self.combo_semana.get()

        # Obtener Tarifa por llamada
        try:
            tarifa = float(self.entry_precio.get().replace(",", "."))
        except ValueError:
            tarifa = 0.0

        # Totales Semana
        total_msgs_sem = 0
        total_llamadas_sem = 0
        for dia in self.dias:
            try:
                total_msgs_sem += int(self.entries_msgs[dia].get())
            except ValueError:
                pass
            try:
                total_llamadas_sem += int(self.entries_llamadas[dia].get())
            except ValueError:
                pass

        monto_semana = total_llamadas_sem * tarifa

        self.lbl_semana_msgs.config(text=f"Total Mensajes ({semana}): {total_msgs_sem}")
        self.lbl_semana_llamadas.config(text=f"Total Llamadas Válidas ({semana}): {total_llamadas_sem}")
        self.lbl_semana_monto.config(text=f"Monto a Cobrar esta Semana: ${monto_semana:.2f}")

        # Totales Mes
        mes_data = self.data.get(mes, {})
        total_msgs_mes = 0
        total_llamadas_mes = 0
        dias_con_registro = 0

        for sem_nombre, sem_dias in mes_data.items():
            for dia_nombre, valores in sem_dias.items():
                if isinstance(valores, int):
                    m, l = valores, 0
                else:
                    m, l = valores.get("msgs", 0), valores.get("llamadas", 0)

                total_msgs_mes += m
                total_llamadas_mes += l
                if m > 0 or l > 0:
                    dias_con_registro += 1

        promedio_diario = (total_msgs_mes / dias_con_registro) if dias_con_registro > 0 else 0.0
        monto_mes = total_llamadas_mes * tarifa

        self.lbl_mes_msgs.config(text=f"Mensajes en {mes}: {total_msgs_mes}")
        self.lbl_mes_llamadas.config(text=f"Llamadas Válidas en {mes}: {total_llamadas_mes}")
        self.lbl_mes_promedio.config(text=f"Promedio Diario de Msgs ({mes}): {promedio_diario:.1f}")
        self.lbl_mes_monto.config(text=f"Total Generado en {mes}: ${monto_mes:.2f}")

    def exportar_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivo CSV (Excel)", "*.csv")],
            title="Guardar reporte como..."
        )
        if not filepath:
            return

        try:
            tarifa = float(self.entry_precio.get().replace(",", "."))
        except ValueError:
            tarifa = 1.20

        try:
            with open(filepath, mode="w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(["Mes", "Semana", "Día", "Mensajes Recibidos", "Llamadas Válidas", "Monto Generado ($)"])

                for mes, semanas in self.data.items():
                    for semana, dias in semanas.items():
                        for dia, vals in dias.items():
                            if isinstance(vals, int):
                                m, l = vals, 0
                            else:
                                m, l = vals.get("msgs", 0), vals.get("llamadas", 0)
                            writer.writerow([mes, semana, dia, m, l, f"${l * tarifa:.2f}"])

            messagebox.showinfo("Exportación Exitosa", f"Los datos han sido exportados a:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el archivo: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MarketplaceTrackerApp(root)
    root.mainloop()
