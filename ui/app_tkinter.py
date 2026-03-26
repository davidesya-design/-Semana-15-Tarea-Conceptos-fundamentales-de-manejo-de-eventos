"""Interfaz gráfica Tkinter para la lista de tareas."""
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import font as tkfont
from pathlib import Path
from servicios.tarea_servicio import TareaServicio


class ListaTareasApp:
    def __init__(self, servicio: TareaServicio) -> None:
        self._servicio = servicio
        self._root = tk.Tk()
        self._root.title("Lista de Tareas - Semana 15")
        self._root.geometry("620x460")
        self._root.resizable(False, False)
        self._configurar_icono()
        self._status_var = tk.StringVar(value="Listo")
        self._resumen_var = tk.StringVar(value="0 pendientes | 0 hechas")
        self._placeholder = "Describe tu tarea y presiona Enter..."
        self._font_normal: tkfont.Font | None = None
        self._font_tachado: tkfont.Font | None = None
        self._entrada_descripcion: tk.Entry
        self._tree: ttk.Treeview

    def iniciar(self) -> None:
        self._configurar_ui()
        self._root.mainloop()

    def _configurar_icono(self) -> None:
        """Define el ícono de la ventana; intenta primero icons151.ico (nueva versión)."""
        base_dir = self._resource_base()
        ico_candidates = [base_dir / "icons151.ico", base_dir / "S15.ico"]
        for ico_path in ico_candidates:
            if ico_path.exists():
                try:
                    self._root.iconbitmap(default=str(ico_path))
                    break
                except Exception:
                    # iconbitmap falla en algunas plataformas; si ocurre, probamos el siguiente o seguimos.
                    continue

    @staticmethod
    def _resource_base() -> Path:
        """
        Devuelve la ruta base para recursos en modo desarrollo y empaquetado.
        - En PyInstaller onefile, los recursos se extraen en sys._MEIPASS.
        - En desarrollo, se usa la carpeta del proyecto.
        """
        if getattr(sys, "_MEIPASS", None):
            return Path(sys._MEIPASS)
        return Path(__file__).resolve().parent.parent

    def _configurar_ui(self) -> None:
        self._configurar_estilos()
        frm = ttk.Frame(self._root, padding=12, style="Card.TFrame")
        frm.pack(fill="both", expand=True)

        header = ttk.Label(frm, text="Lista de Tareas", style="Title.TLabel")
        header.grid(row=0, column=0, columnspan=3, sticky="w")
        sub = ttk.Label(frm, text="Añade rápido con Enter o completa con doble clic", style="Sub.TLabel")
        sub.grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 10))

        # Entrada + botón añadir en la misma fila para alinear mejor el texto
        entrada_lbl = ttk.Label(frm, text="Nueva tarea", style="Field.TLabel")
        entrada_lbl.grid(row=2, column=0, sticky="w", padx=(0, 6), pady=(0, 4))
        self._entrada_descripcion = ttk.Entry(frm, width=44, style="Input.TEntry")
        self._entrada_descripcion.grid(row=2, column=1, sticky="we", pady=(0, 4))
        self._entrada_descripcion.bind("<Return>", self._evento_enter_agregar)
        self._entrada_descripcion.bind("<FocusIn>", self._remover_placeholder)
        self._entrada_descripcion.bind("<FocusOut>", self._poner_placeholder)
        self._poner_placeholder()  # inicial

        btn_agregar = ttk.Button(frm, text="Añadir Tarea", command=self._accion_agregar, style="Flat.TButton")
        btn_agregar.grid(row=2, column=2, padx=(8, 0))

        # Treeview para mostrar tareas
        self._tree = ttk.Treeview(
            frm,
            columns=("descripcion", "estado"),
            show="headings",
            height=12,
            selectmode="browse",
            style="List.Treeview",
        )
        self._tree.heading("descripcion", text="Descripción")
        self._tree.heading("estado", text="Estado")
        self._tree.column("descripcion", width=330, anchor="w")
        self._tree.column("estado", width=110, anchor="center")
        self._tree.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=(0, 6))
        self._tree.tag_configure("completada", foreground="#6b7280", font=self._font_tachado)
        self._tree.tag_configure("pendiente", foreground="#0f172a", font=self._font_normal)
        self._tree.tag_configure("fila_par", background="#f8fafc")
        self._tree.tag_configure("fila_impar", background="#ffffff")

        # Doble clic marca completada (manejador de ratón)
        self._tree.bind("<Double-1>", self._evento_doble_click)

        scroll = ttk.Scrollbar(frm, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=4, column=3, sticky="ns")

        # Botones de acción inferiores
        btn_completar = ttk.Button(frm, text="Marcar Completada", command=self._accion_completar, style="Flat.TButton")
        btn_eliminar = ttk.Button(frm, text="Eliminar", command=self._accion_eliminar, style="Flat.Danger.TButton")
        btn_completar.grid(row=5, column=0, pady=6, sticky="w")
        btn_eliminar.grid(row=5, column=1, pady=6, sticky="w", padx=(8, 0))

        resumen_lbl = ttk.Label(frm, textvariable=self._resumen_var, style="Info.TLabel")
        resumen_lbl.grid(row=6, column=0, columnspan=2, sticky="w", pady=(6, 2))
        status_lbl = ttk.Label(frm, textvariable=self._status_var, style="Status.TLabel")
        status_lbl.grid(row=7, column=0, columnspan=3, sticky="w")

        frm.columnconfigure(0, weight=1)
        frm.columnconfigure(1, weight=0)
        frm.columnconfigure(2, weight=0)
        frm.rowconfigure(4, weight=1)

        self._refrescar_lista()

    def _configurar_estilos(self) -> None:
        style = ttk.Style(self._root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        self._root.configure(background="#f1f5f9")
        self._font_normal = tkfont.nametofont("TkDefaultFont").copy()
        self._font_tachado = self._font_normal.copy()
        self._font_tachado.configure(overstrike=1)

        style.configure("Card.TFrame", background="#f1f5f9")
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#0f172a", background="#f1f5f9")
        style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground="#475569", background="#f1f5f9")
        style.configure("Field.TLabel", font=("Segoe UI", 10), foreground="#0f172a", background="#f1f5f9")
        style.configure(
            "Input.TEntry",
            padding=6,
            relief="flat",
            borderwidth=0,
            foreground="#0f172a",
            fieldbackground="#f8fafc",
            background="#f8fafc",
        )
        style.map("Input.TEntry", bordercolor=[("focus", "#2563eb")], fieldbackground=[("focus", "#e0ecff")])

        style.configure("Flat.TButton", padding=(12, 8), relief="flat", borderwidth=0, background="#2563eb",
                        foreground="#ffffff")
        style.map("Flat.TButton", background=[("active", "#1d4ed8"), ("pressed", "#1e3a8a")])
        style.configure("Flat.Danger.TButton", padding=(12, 8), relief="flat", borderwidth=0, background="#f43f5e",
                        foreground="#ffffff")
        style.map("Flat.Danger.TButton", background=[("active", "#e11d48"), ("pressed", "#9f1239")])
        style.configure(
            "List.Treeview",
            rowheight=24,
            borderwidth=0,
            relief="flat",
            background="#ffffff",
            fieldbackground="#ffffff",
        )
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), borderwidth=0, relief="flat", background="#ffffff")
        # Selección azul con texto claro para evitar que quede en blanco
        style.map(
            "Treeview",
            background=[("selected", "#2563eb")],
            foreground=[("selected", "#ffffff")],
            bordercolor=[("selected", "#1d4ed8")],
        )
        style.configure("Info.TLabel", foreground="#2563eb", background="#f1f5f9")
        style.configure("Status.TLabel", foreground="#94a3b8", background="#f1f5f9")

    def _accion_agregar(self) -> None:
        descripcion = self._entrada_descripcion.get()
        if descripcion == self._placeholder:
            descripcion = ""
        try:
            tarea = self._servicio.agregar(descripcion)
        except ValueError as exc:
            messagebox.showwarning("Campo vacío", str(exc))
            return
        self._entrada_descripcion.delete(0, tk.END)
        self._status_var.set(f"Tarea creada: #{tarea.id}")
        self._refrescar_lista()
        self._poner_placeholder()

    def _accion_completar(self) -> None:
        tarea_id = self._obtener_tarea_seleccionada()
        if tarea_id is None:
            messagebox.showinfo("Sin selección", "Selecciona una tarea para marcarla como completada.")
            return
        try:
            self._servicio.marcar_completada(tarea_id)
            self._status_var.set(f"Tarea #{tarea_id} marcada como completada")
        except KeyError as exc:
            messagebox.showerror("Error", str(exc))
        self._refrescar_lista()

    def _accion_eliminar(self) -> None:
        tarea_id = self._obtener_tarea_seleccionada()
        if tarea_id is None:
            messagebox.showinfo("Sin selección", "Selecciona una tarea para eliminarla.")
            return
        try:
            self._servicio.eliminar(tarea_id)
            self._status_var.set(f"Tarea #{tarea_id} eliminada")
        except KeyError as exc:
            messagebox.showerror("Error", str(exc))
        self._refrescar_lista()

    def _evento_enter_agregar(self, event: tk.Event) -> None:
        """Permite añadir presionando Enter en la entrada."""
        self._accion_agregar()

    def _evento_doble_click(self, event: tk.Event) -> None:
        """Marca como completada al hacer doble clic en una fila."""
        tarea_id = self._obtener_tarea_seleccionada()
        if tarea_id is None:
            return
        try:
            self._servicio.marcar_completada(tarea_id)
            self._status_var.set(f"Tarea #{tarea_id} completada (doble clic)")
            self._refrescar_lista()
        except KeyError:
            pass

    def _obtener_tarea_seleccionada(self) -> int | None:
        seleccion = self._tree.selection()
        if not seleccion:
            return None
        return int(seleccion[0])

    def _refrescar_lista(self) -> None:
        for item in self._tree.get_children():
            self._tree.delete(item)
        total = 0
        hechas = 0
        for idx, tarea in enumerate(self._servicio.listar()):
            estado_txt = "Hecha" if tarea.completada else "Pendiente"
            base_tag = "completada" if tarea.completada else "pendiente"
            paridad_tag = "fila_par" if idx % 2 == 0 else "fila_impar"
            tags = (base_tag, paridad_tag)
            # iid = id para poder recuperar fácilmente
            self._tree.insert("", "end", iid=str(tarea.id), values=(tarea.descripcion, estado_txt), tags=tags)
            total += 1
            if tarea.completada:
                hechas += 1
        pendientes = total - hechas
        self._resumen_var.set(f"{pendientes} pendientes | {hechas} hechas | {total} total")

    def _poner_placeholder(self, event: tk.Event | None = None) -> None:
        if not self._entrada_descripcion.get():
            self._entrada_descripcion.insert(0, self._placeholder)
            self._entrada_descripcion.configure(foreground="#9ca3af")

    def _remover_placeholder(self, event: tk.Event | None = None) -> None:
        if self._entrada_descripcion.get() == self._placeholder:
            self._entrada_descripcion.delete(0, tk.END)
            self._entrada_descripcion.configure(foreground="#111827")
