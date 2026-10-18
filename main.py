import os
import json
import inspect
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
import flet as ft


# =====================================================================
# 0. TEMA VISUAL (ESTÉTICA PANEL WEB SHINOBI GAIDEN) Y COMPATIBILIDAD
# =====================================================================
COLOR_BG = "#0f0b18"           # Fondo principal oscuro
COLOR_SURFACE = "#181226"      # Fondo de paneles/tarjetas
COLOR_INPUT = "#120d1d"        # Fondo de inputs como en las capturas
COLOR_BORDER = "#2d2246"       # Borde sutil violeta oscuro
COLOR_PRIMARY = "#8b5cf6"      # Violeta principal (botones Guardar/Crear/Cargar)
COLOR_ACCENT = "#f97316"       # Barra vertical naranja/ámbar de los títulos
COLOR_TEXT = "#f3f0ff"         # Texto principal
COLOR_MUTED = "#9ca3af"        # Etiquetas secundarias
COLOR_OK = "#10b981"           # Verde validación
COLOR_WARN = "#f59e0b"         # Ámbar advertencia
COLOR_ERR = "#ef4444"          # Rojo error/eliminar


# =====================================================================
# 1. BASE DE DATOS DE MODERACIÓN ('Doc Moderacion')
# =====================================================================
TABLA_MODERACION = {
    "Base Simple":      {"formula": "--",        "slot": -2, "usa_stat": False, "tipo": "Base",   "chakra": -10, "nivel": -1},
    "Base Media":       {"formula": "--",        "slot": 2,  "usa_stat": False, "tipo": "Base",   "chakra": 10,  "nivel": 0},
    "Base Compleja":    {"formula": "--",        "slot": 4,  "usa_stat": False, "tipo": "Base",   "chakra": 20,  "nivel": 1},
    "50% Daño":         {"formula": "[STAT/2]",  "slot": 3,  "usa_stat": True,  "tipo": "Daño",   "chakra": 15,  "nivel": 1},
    "100% Daño":        {"formula": "[STATx1]",  "slot": 5,  "usa_stat": True,  "tipo": "Daño",   "chakra": 25,  "nivel": 2},
    "Daño+Modx1":       {"formula": "[MSTATx1]", "slot": 2,  "usa_stat": True,  "tipo": "Daño",   "chakra": 10,  "nivel": 0},
    "Daño+Modx2":       {"formula": "[MSTATx2]", "slot": 3,  "usa_stat": True,  "tipo": "Daño",   "chakra": 15,  "nivel": 1},
    "Daño+Modx3":       {"formula": "[MSTATx3]", "slot": 4,  "usa_stat": True,  "tipo": "Daño",   "chakra": 20,  "nivel": 1},
    "Daño+Modx4":       {"formula": "[MSTATx4]", "slot": 5,  "usa_stat": True,  "tipo": "Daño",   "chakra": 25,  "nivel": 2},
    "Daño+Modx5":       {"formula": "[MSTATx5]", "slot": 6,  "usa_stat": True,  "tipo": "Daño",   "chakra": 30,  "nivel": 2},
    "Daño+Modx6":       {"formula": "[MSTATx6]", "slot": 7,  "usa_stat": True,  "tipo": "Daño",   "chakra": 35,  "nivel": 2},
    "Daño+Modx7":       {"formula": "[MSTATx7]", "slot": 8,  "usa_stat": True,  "tipo": "Daño",   "chakra": 40,  "nivel": 3},
    "Daño+Modx8":       {"formula": "[MSTATx8]", "slot": 9,  "usa_stat": True,  "tipo": "Daño",   "chakra": 45,  "nivel": 3},
    "Daño+Modx9":       {"formula": "[MSTATx9]", "slot": 11, "usa_stat": True,  "tipo": "Daño",   "chakra": 55,  "nivel": 4},
    "Daño+Modx10":      {"formula": "[MSTATx10]","slot": 13, "usa_stat": True,  "tipo": "Daño",   "chakra": 65,  "nivel": 5},
    "Más Nivel":        {"formula": "[+1]",      "slot": 3,  "usa_stat": False, "tipo": "Nivel",  "chakra": 15,  "nivel": 1},
    "Efecto x1":        {"formula": "[MSTATx1]", "slot": 3,  "usa_stat": True,  "tipo": "Efecto", "chakra": 15,  "nivel": 1},
    "Efecto x2":        {"formula": "[MSTATx2]", "slot": 5,  "usa_stat": True,  "tipo": "Efecto", "chakra": 25,  "nivel": 2},
    "Efecto x3":        {"formula": "[MSTATx3]", "slot": 8,  "usa_stat": True,  "tipo": "Efecto", "chakra": 40,  "nivel": 3},
    "Rango Medio":      {"formula": "[MSTATx5]", "slot": 2,  "usa_stat": True,  "tipo": "Rango",  "chakra": 10,  "nivel": 0},
    "Rango Largo":      {"formula": "[MSTATx10]","slot": 4,  "usa_stat": True,  "tipo": "Rango",  "chakra": 20,  "nivel": 1},
    "Rango + 1x":       {"formula": "[MSTATx1]", "slot": 2,  "usa_stat": True,  "tipo": "Rango",  "chakra": 10,  "nivel": 0},
    "Rango + 2x":       {"formula": "[MSTATx2]", "slot": 4,  "usa_stat": True,  "tipo": "Rango",  "chakra": 20,  "nivel": 1},
    "Rango + 3x":       {"formula": "[MSTATx3]", "slot": 6,  "usa_stat": True,  "tipo": "Rango",  "chakra": 30,  "nivel": 2},
    "Buff Personajex1": {"formula": "[MSTATx1]", "slot": 3,  "usa_stat": True,  "tipo": "Buff",   "chakra": 15,  "nivel": 1},
    "Buff Personajex2": {"formula": "[MSTATx2]", "slot": 5,  "usa_stat": True,  "tipo": "Buff",   "chakra": 25,  "nivel": 2},
    "Buff Personajex3": {"formula": "[MSTATx3]", "slot": 7,  "usa_stat": True,  "tipo": "Buff",   "chakra": 35,  "nivel": 2},
    "stat x1":          {"formula": "[MSTATx1]", "slot": 1,  "usa_stat": True,  "tipo": "Stat",   "chakra": 5,   "nivel": 0},
    "stat x2":          {"formula": "[MSTATx2]", "slot": 3,  "usa_stat": True,  "tipo": "Stat",   "chakra": 15,  "nivel": 1},
    "stat x3":          {"formula": "[MSTATx3]", "slot": 5,  "usa_stat": True,  "tipo": "Stat",   "chakra": 25,  "nivel": 2},
    "stat x4":          {"formula": "[MSTATx4]", "slot": 7,  "usa_stat": True,  "tipo": "Stat",   "chakra": 35,  "nivel": 2},
    "stat x5":          {"formula": "[MSTATx5]", "slot": 9,  "usa_stat": True,  "tipo": "Stat",   "chakra": 45,  "nivel": 3},
    "Chico (armas)":    {"formula": "1",         "slot": -2, "usa_stat": False, "tipo": "Tamaño", "chakra": -10, "nivel": -1},
    "Mediano (armas)":  {"formula": "2",         "slot": 2,  "usa_stat": False, "tipo": "Tamaño", "chakra": 10,  "nivel": 0},
    "Grande (armas)":   {"formula": "3",         "slot": 4,  "usa_stat": False, "tipo": "Tamaño", "chakra": 20,  "nivel": 1},
}

TAMANOS_VALIDOS = ["Chico (armas)", "Mediano (armas)", "Grande (armas)"]
EFECTOS_VALIDOS = [k for k, v in TABLA_MODERACION.items() if v["tipo"] != "Tamaño"]
STATS_ARMAS = ["", "CCK", "DES", "FUE", "INT", "SAL", "VEL", "TEN", "SIG"]
STATS_CLAN = [
    "",
    "MCCK", "MDES", "MFUE", "MINT", "MSAL", "MVEL", "MTEN", "MSIG",
    "CCK", "DES", "FUE", "INT", "SAL", "VEL", "TEN", "SIG",
]
FX_VALIDOS = ["", "x", "/", "+", "-"]
CATEGORIAS_CLAN = [
    "Yang", "Yin", "Yin-Yang", "Ninjutsu", "Ninjutsu a distancia",
    "Taijutsu", "Genjutsu", "Fūinjutsu", "Iryō Ninjutsu", "Bukijutsu",
    "Katon", "Suiton", "Doton", "Raiton", "Fūton",
    "Mejora", "Especialidad", "Otra (Escribir)"
]


# =====================================================================
# 2. VALIDADOR DE REGLAS DE MODERACIÓN (ANTI-ERRORES)
# =====================================================================
class ValidadorModeracion:
    @staticmethod
    def validar_arma(arma) -> List[str]:
        errores = []
        if not arma.nombre.strip():
            errores.append("El nombre del objeto/arma no puede estar vacío.")
        if not arma.codigo.strip():
            errores.append("El Objeto ID (código) no puede estar vacío.")
        if arma.tamano not in TAMANOS_VALIDOS:
            errores.append(f"Objeto '{arma.nombre}': Tamaño '{arma.tamano}' inválido.")
        if len(arma.efectos) > 3:
            errores.append(f"Objeto '{arma.nombre}': Excede el límite de 3 efectos.")

        for i, ef in enumerate(arma.efectos, 1):
            if not ef.tipo_efecto:
                continue
            if ef.tipo_efecto not in TABLA_MODERACION:
                errores.append(f"Objeto '{arma.nombre}' (Efecto {i}): '{ef.tipo_efecto}' no existe.")
                continue
            regla = TABLA_MODERACION[ef.tipo_efecto]
            if regla["tipo"] == "Tamaño":
                errores.append(f"Objeto '{arma.nombre}' (Efecto {i}): '{ef.tipo_efecto}' es un Tamaño, no un Efecto.")
            if regla["usa_stat"] and not ef.stat.strip():
                errores.append(
                    f"Objeto '{arma.nombre}' (Efecto {i}: {ef.tipo_efecto}): "
                    f"Requiere seleccionar un STAT obligatoriamente."
                )
            if not ef.texto_efecto.strip():
                errores.append(f"Objeto '{arma.nombre}' (Efecto {i}): Falta escribir qué produce el efecto (ej. Daño, Radio).")

        if arma.slots <= 0:
            errores.append(
                f"Objeto '{arma.nombre}': Suma {arma.slots} Slots ({arma.ryos} Ryos). "
                f"El total de Slots debe ser mayor a 0."
            )
        return errores

    @staticmethod
    def validar_nodo_clan(nodo) -> List[str]:
        errores = []
        campos_formula = [bool(nodo.stat.strip()), bool(nodo.fx.strip()), nodo.n is not None]
        if any(campos_formula) and not all(campos_formula):
            errores.append(f"Técnica [{nodo.id_unico}]: Si usas fórmula de escalado, debes completar Stat, F(x) y N.")
        if all(campos_formula) and not nodo.texto_efecto.strip():
            errores.append(f"Técnica [{nodo.id_unico}]: Tienes fórmula [{nodo.stat}{nodo.fx}{nodo.n}] pero falta el texto del Efecto.")
        if nodo.mantenido.lower() == "si" and nodo.chakra is None:
            errores.append(f"Técnica [{nodo.id_unico}]: Marcada como Mantenida ('Si'), pero no tiene coste de Chakra.")
        return errores

    @staticmethod
    def validar_bingo(bingo) -> List[str]:
        errores = []
        for p in bingo.participantes.values():
            for victima in p.bajas:
                if victima not in bingo.participantes:
                    errores.append(f"Bingo ({p.nombre}): La víctima '{victima}' no está registrada en la tabla.")
                elif not bingo.participantes[victima].muerto:
                    errores.append(f"Bingo ({p.nombre}): Reclama baja de '{victima}', pero '{victima}' no figura como Muerto.")
        return errores

    @classmethod
    def validar_todo(cls, clanes: Dict[str, "ArbolClan"], armas: List["Arma"], bingo: "GestorBingo") -> List[str]:
        avisos = []
        for clan in clanes.values():
            for n in clan.nodos.values():
                avisos.extend(cls.validar_nodo_clan(n))
        for a in armas:
            avisos.extend(cls.validar_arma(a))
        avisos.extend(cls.validar_bingo(bingo))
        return avisos


# =====================================================================
# 3. MODELOS DE DATOS (ALINEADOS CON EL PANEL WEB DE LAS CAPTURAS)
# =====================================================================
@dataclass
class EfectoArma:
    tipo_efecto: str = ""
    stat: str = ""
    texto_efecto: str = ""

    def formatear_efecto(self) -> str:
        if not self.tipo_efecto or self.tipo_efecto not in TABLA_MODERACION:
            return self.texto_efecto
        formula = TABLA_MODERACION[self.tipo_efecto]["formula"]
        if self.stat and "MSTAT" in formula:
            st = self.stat if self.stat.startswith("M") else f"M{self.stat}"
            return f"{formula.replace('MSTAT', st)} de {self.texto_efecto}"
        elif self.stat and "STAT" in formula:
            st = self.stat if self.stat.startswith("M") else f"M{self.stat}"
            return f"{formula.replace('STAT', st)} de {self.texto_efecto}"
        elif formula == "[+1]":
            return f"[1] de {self.texto_efecto}"
        return self.texto_efecto


@dataclass
class Arma:
    nombre: str
    codigo: str
    tipo: str
    tamano: str
    municion: int
    efectos: List[EfectoArma] = field(default_factory=list)
    descripcion: str = ""

    @property
    def slots(self) -> int:
        total = TABLA_MODERACION.get(self.tamano, {}).get("slot", 0)
        for ef in self.efectos:
            total += TABLA_MODERACION.get(ef.tipo_efecto, {}).get("slot", 0)
        return total

    @property
    def ryos(self) -> int:
        return self.slots * 245

    def texto_efecto_n(self, indice: int) -> str:
        if 0 <= indice < len(self.efectos):
            return self.efectos[indice].formatear_efecto()
        return ""

    def generar_txt(self) -> str:
        ef1 = self.texto_efecto_n(0) or "--"
        ef2 = self.texto_efecto_n(1) or "--"
        ef3 = self.texto_efecto_n(2) or "--"
        lineas = [
            "--------------------------------------------------------------------------------",
            f"OBJETO ID   : {self.codigo}",
            f"NOMBRE      : {self.nombre}",
            f"TIPO        : {self.tipo}",
            f"MUNICIÓN    : {self.municion}",
            f"TAMAÑO      : {self.tamano} ({self.slots} Slots)",
            f"COSTE (RYOS): {self.ryos}",
            f"EFECTO 1    : {ef1}",
            f"EFECTO 2    : {ef2}",
            f"EFECTO 3    : {ef3}",
            f"DESCRIPCIÓN : {self.descripcion or '--'}",
            "--------------------------------------------------------------------------------",
        ]
        return "\n".join(lineas)


@dataclass
class NodoJutsu:
    codigo_corto: str
    tipo_nodo: str
    numero: int
    arbol: str
    rama: str
    nombre_jutsu: str = ""
    categoria: str = ""
    sellos: int = 0
    chakra: Optional[int] = None
    mantenido: str = "No"
    stat: str = ""
    fx: str = ""
    n: Optional[int] = None
    texto_efecto: str = ""
    descripcion: str = ""

    @property
    def id_unico(self) -> str:
        prefijo = self.arbol.strip()[:4].upper()
        return f"{prefijo}{self.codigo_corto}"

    @property
    def esta_activo(self) -> bool:
        tiene_nombre_real = bool(self.nombre_jutsu.strip()) and not self.nombre_jutsu.strip().startswith("[]")
        return bool(
            tiene_nombre_real
            or self.descripcion.strip()
            or self.chakra is not None
            or self.texto_efecto.strip()
            or self.sellos > 0
        )

    @property
    def coste_formateado(self) -> str:
        if self.chakra is None:
            return "--"
        if self.mantenido.lower() == "si":
            return f"{self.chakra + 10} de Chakra, {self.chakra} de Chakra por Turno"
        return f"{self.chakra} de Chakra"

    @property
    def efecto_formateado(self) -> str:
        if self.stat and self.fx and self.n is not None and self.texto_efecto:
            return f"[{self.stat}{self.fx}{self.n}] de {self.texto_efecto}"
        if self.texto_efecto.strip():
            return self.texto_efecto.strip()
        return "--"

    def generar_txt(self) -> str:
        nombre = self.nombre_jutsu if self.nombre_jutsu else "(Vacío)"
        lineas = [
            "--------------------------------------------------------------------------------",
            f"NOMBRE DE TÉCNICA : {nombre}",
            f"TÉCNICA ID        : {self.id_unico}",
            f"ÁRBOL             : {self.arbol.lower()}",
            f"RAMA              : {self.rama}",
            f"CATEGORÍA         : {self.categoria or '--'}",
            f"NIVEL             : {self.sellos}",
            f"COSTE             : {self.coste_formateado}",
            f"EFECTO            : {self.efecto_formateado}",
            f"DESCRIPCIÓN       : {self.descripcion or '--'}",
            "--------------------------------------------------------------------------------",
        ]
        return "\n".join(lineas)


class ArbolClan:
    def __init__(self, nombre_clan: str):
        self.nombre_clan = nombre_clan.strip().upper()
        self.nodos: Dict[str, NodoJutsu] = {}
        self._generar_plantilla_31_nodos()

    def _generar_plantilla_31_nodos(self):
        self.nodos["101B"] = NodoJutsu("101B", "B", 101, self.nombre_clan, "BASE")
        for r in range(1, 4):
            cod_r = f"00{r}R"
            nombre_rama = f"Rama {r}"
            self.nodos[cod_r] = NodoJutsu(cod_r, "R", r, self.nombre_clan, nombre_rama)
            for m in range(1, 7):
                num_m = r * 100 + m
                self.nodos[f"{num_m}M"] = NodoJutsu(
                    f"{num_m}M", "M", num_m, self.nombre_clan, nombre_rama,
                    nombre_jutsu="[]  []", categoria="Mejora"
                )
            for e in range(1, 4):
                num_e = r * 100 + e
                self.nodos[f"{num_e}E"] = NodoJutsu(
                    f"{num_e}E", "E", num_e, self.nombre_clan, nombre_rama,
                    categoria="Especialidad"
                )

    def renombrar(self, nuevo_nombre: str):
        self.nombre_clan = nuevo_nombre.strip().upper()
        for n in self.nodos.values():
            n.arbol = self.nombre_clan

    def actualizar_nodo(self, codigo_corto: str, **kwargs) -> List[str]:
        if codigo_corto not in self.nodos:
            return [f"El nodo '{codigo_corto}' no existe."]
        nodo = self.nodos[codigo_corto]
        for k, v in kwargs.items():
            if hasattr(nodo, k):
                setattr(nodo, k, v)
        if nodo.tipo_nodo == "R" and "nombre_jutsu" in kwargs and kwargs["nombre_jutsu"]:
            r = nodo.numero
            for m in range(1, 7):
                cod_m = f"{r*100 + m}M"
                if self.nodos[cod_m].nombre_jutsu.startswith("[]"):
                    self.nodos[cod_m].nombre_jutsu = f"[]  [{nodo.nombre_jutsu}]"
        return ValidadorModeracion.validar_nodo_clan(nodo)

    def limpiar_nodo(self, codigo_corto: str):
        if codigo_corto not in self.nodos:
            return
        n = self.nodos[codigo_corto]
        n.nombre_jutsu = "[]  []" if n.tipo_nodo == "M" else ""
        n.categoria = "Mejora" if n.tipo_nodo == "M" else ("Especialidad" if n.tipo_nodo == "E" else "")
        n.sellos = 0
        n.chakra = None
        n.mantenido = "No"
        n.stat = ""
        n.fx = ""
        n.n = None
        n.texto_efecto = ""
        n.descripcion = ""

    def generar_txt(self, ocultar_vacios: bool = True) -> str:
        lineas = [
            "=" * 80,
            f"ÁRBOL DE CLAN: {self.nombre_clan}",
            "=" * 80,
        ]
        incluidos = 0
        for n in self.nodos.values():
            if ocultar_vacios and not n.esta_activo:
                continue
            incluidos += 1
            lineas.append(n.generar_txt())
        if incluidos == 0:
            lineas.append("(Sin técnicas registradas o activas en este árbol)")
        return "\n".join(lineas)


@dataclass
class ParticipanteBingo:
    nombre: str
    modo_seguro: bool
    bingo_inicial: float
    bingo_mision: float
    muerto: bool
    reconocimiento: float = 50.0
    bajas: List[str] = field(default_factory=list)

    bingo_pre_calculo: float = 0.0
    recompensa_bajas: float = 0.0
    bingo_final: float = 0.0
    madaras: float = 0.0
    ryos: float = 0.0
    tobis: float = 0.0
    exp: int = 0
    ascenso: str = "No"


class GestorBingo:
    def __init__(self):
        self.participantes: Dict[str, ParticipanteBingo] = {}

    def agregar_participante(self, p: ParticipanteBingo):
        self.participantes[p.nombre] = p

    def eliminar_participante(self, nombre: str):
        if nombre in self.participantes:
            del self.participantes[nombre]
        for p in self.participantes.values():
            if nombre in p.bajas:
                p.bajas = [b for b in p.bajas if b != nombre]

    def calcular_resultados(self):
        botin_por_caido: Dict[str, float] = {}
        conteo_ejecutores: Dict[str, int] = {}

        for nombre, p in self.participantes.items():
            suma_base = p.bingo_inicial + p.bingo_mision + p.reconocimiento
            if p.muerto:
                p.bingo_pre_calculo = suma_base / 2.0
                if not p.modo_seguro:
                    p.madaras = p.bingo_pre_calculo
                    botin_por_caido[nombre] = p.bingo_pre_calculo
                else:
                    p.madaras = 0.0
            else:
                p.bingo_pre_calculo = suma_base
                p.madaras = 0.0

        for p in self.participantes.values():
            for victima in p.bajas:
                conteo_ejecutores[victima] = conteo_ejecutores.get(victima, 0) + 1

        for p in self.participantes.values():
            p.recompensa_bajas = 0.0
            bono_ryos_seguro = 0.0
            bono_tobis_seguro = 0.0

            for victima in p.bajas:
                if victima in self.participantes:
                    v_obj = self.participantes[victima]
                    n_killers = conteo_ejecutores.get(victima, 1)
                    if not v_obj.modo_seguro and v_obj.muerto:
                        p.recompensa_bajas += botin_por_caido.get(victima, 0.0) / n_killers
                    elif v_obj.modo_seguro and v_obj.muerto:
                        bono_ryos_seguro += (v_obj.bingo_pre_calculo * 0.4) / n_killers
                        bono_tobis_seguro += (v_obj.bingo_pre_calculo * 0.1) / n_killers

            p.bingo_final = 0.0 if (p.muerto and not p.modo_seguro) else (p.bingo_pre_calculo + p.recompensa_bajas)
            base_ryos = 1500.0 if p.modo_seguro else 3000.0
            base_tobis = 15.0 if p.modo_seguro else 30.0
            p.exp = 65 if p.modo_seguro else 130
            p.ryos = base_ryos + (p.recompensa_bajas * 0.4) + bono_ryos_seguro
            p.tobis = base_tobis + (p.recompensa_bajas * 0.1) + bono_tobis_seguro
            p.ascenso = "Si" if (not p.modo_seguro and not p.muerto) else "No"

    def generar_txt(self) -> str:
        self.calcular_resultados()
        fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        lineas = [
            "=" * 95,
            f"LIQUIDACIÓN DE COMBATE Y LIBRO BINGO - GENERADO: {fecha_str}",
            "=" * 95,
            f"{'Personaje':<12} | {'Seguro':<6} | {'Muerto':<6} | {'Pre-Calc':>8} | {'Botín Bajas':>11} | "
            f"{'Bingo Final':>11} | {'Madaras':>7} | {'Ryos':>8} | {'Tobis':>7} | {'Exp':>4} | {'Ascenso':<7}",
            "-" * 95
        ]
        for p in self.participantes.values():
            lineas.append(
                f"{p.nombre:<12} | {str(p.modo_seguro):<6} | {str(p.muerto):<6} | "
                f"{p.bingo_pre_calculo:>8.2f} | {p.recompensa_bajas:>11.2f} | "
                f"{p.bingo_final:>11.2f} | {p.madaras:>7.0f} | "
                f"{p.ryos:>8.1f} | {p.tobis:>7.3f} | {p.exp:>4} | {p.ascenso:<7}"
            )
        lineas.append("-" * 95)
        lineas.append("\nDETALLE DE BAJAS RECLAMADAS:")
        for p in self.participantes.values():
            if p.bajas:
                lineas.append(f"  • {p.nombre}: {', '.join(p.bajas)}")
        return "\n".join(lineas)


# =====================================================================
# 4. GESTOR DE ALMACENAMIENTO (3 ARCHIVOS .TXT + AUTOGUARDADO JSON)
# =====================================================================
def construir_datos_ejemplo() -> Tuple[Dict[str, ArbolClan], List[Arma], GestorBingo]:
    armas = [
        Arma(
            nombre="Mascara Uzumaki", codigo="uzumaki", tipo="Otros", tamano="Chico (armas)", municion=1,
            efectos=[
                EfectoArma("Base Simple", "", "[MCCKx2] de Limite de Estadísticas con 1 Especialidad"),
                EfectoArma("Base Media", "", "[MCCKx3] de Limite de Estadísticas con 2 Especialidades"),
                EfectoArma("Base Compleja", "", "[MCCKx4] de Limite de Estadísticas con 3 Especialidades"),
            ],
            descripcion="La Máscara Uzumaki es un medio de unión entre el plano astral y el plano terrenal..."
        ),
        Arma(
            nombre="Granadas de Calabaza", codigo="calabaza", tipo="Arrojadiza", tamano="Chico (armas)", municion=3,
            efectos=[
                EfectoArma("Rango + 1x", "CCK", "Radio"),
                EfectoArma("Efecto x2", "CCK", "Lesión"),
                EfectoArma("100% Daño", "CCK", "Daño"),
            ],
            descripcion="Unas siniestras granadas con forma de calabaza que explotan al contacto..."
        ),
        Arma(
            nombre="El Infalible", codigo="infalible", tipo="Empuñada", tamano="Mediano (armas)", municion=1,
            efectos=[
                EfectoArma("Rango Medio", "DES", "Rango"),
                EfectoArma("Más Nivel", "DES", "Infección"),
                EfectoArma("Base Compleja", "", "Puede atacar a Distancia con Munición"),
            ],
            descripcion="Un arco de apariencia siniestra elaborado con huesos retorcidos, madera oscura y placas metálicas..."
        )
    ]

    uzumaki = ArbolClan("UZUMAKI")
    uzumaki.actualizar_nodo("101B", nombre_jutsu="Vitalidad Uzumaki", categoria="Yang", descripcion="Reserva de Chakra extraordinaria...")
    uzumaki.actualizar_nodo(
        "001R", nombre_jutsu="Fūin no Men", categoria="Yang", sellos=1,
        chakra=25, mantenido="Si", stat="MCCK", fx="x", n=1,
        texto_efecto="Límite de Absorción de Estadisticas por turno, Control Fisico",
        descripcion="El usuario recibirá una máscara poseída por un Shinigami..."
    )
    uzumaki.actualizar_nodo("101E", nombre_jutsu="Meifu no Te", categoria="Especialidad")
    uzumaki.actualizar_nodo("102E", nombre_jutsu="Kamigoroshi no Jutsu", categoria="Especialidad")
    uzumaki.actualizar_nodo("103E", nombre_jutsu="Shiki Fūjin", categoria="Especialidad")
    uzumaki.actualizar_nodo("002R", nombre_jutsu="Kagura Shingan", categoria="Yang", descripcion="Sensor")
    uzumaki.actualizar_nodo("003R", nombre_jutsu="Kongō Fūsa", categoria="Yang", descripcion="Cadenas")

    clanes = {"UZUMAKI": uzumaki}

    bingo = GestorBingo()
    for p in [
        ParticipanteBingo("Kyoshiro",   False, 0,   200, True,  50, []),
        ParticipanteBingo("Kishue",     False, 0,   200, True,  50, []),
        ParticipanteBingo("Rin to Rei", False, 0,   200, True,  50, []),
        ParticipanteBingo("Kinzo",      True,  50,  0,   True,  50, []),
        ParticipanteBingo("Hachibi",    False, 0,   200, False, 50, []),
        ParticipanteBingo("Akira",      True,  100, 0,   False, 50, ["Rin to Rei", "Kishue"]),
        ParticipanteBingo("Mayura",     False, 0,   200, False, 50, ["Rin to Rei"]),
        ParticipanteBingo("Asuna",      True,  0,   0,   False, 50, ["Kyoshiro", "Rin to Rei"]),
        ParticipanteBingo("Keisuke",    True,  0,   0,   False, 50, ["Kishue"]),
        ParticipanteBingo("Kuroto",     False, 0,   200, False, 50, ["Kyoshiro", "Rin to Rei"]),
        ParticipanteBingo("Daeru",      True,  0,   0,   False, 50, []),
        ParticipanteBingo("Chota",      True,  0,   0,   False, 50, []),
        ParticipanteBingo("Ibuki",      False, 100, 200, False, 50, ["Kinzo"]),
    ]:
        bingo.agregar_participante(p)

    return clanes, armas, bingo


class GestorBiblioteca:
    def __init__(self, nombre_carpeta: str = "Biblioteca_Shinobi_Gaiden"):
        self.es_android = "ANDROID_ARGUMENT" in os.environ or "ANDROID_STORAGE" in os.environ
        if self.es_android:
            base = Path("/storage/emulated/0/Documents")
            if not base.exists():
                base = Path.home()
        else:
            base = Path(__file__).parent

        self.ruta_biblioteca = base / nombre_carpeta
        self._configurar_rutas()
        self.inicializar_carpetas()

    def _configurar_rutas(self):
        self.ruta_txt_clanes = self.ruta_biblioteca / "Clanes.txt"
        self.ruta_txt_armas = self.ruta_biblioteca / "Armas.txt"
        self.ruta_txt_bingo = self.ruta_biblioteca / "Bingo.txt"
        self.ruta_db_json = self.ruta_biblioteca / "datos_guardados.json"

    def inicializar_carpetas(self):
        try:
            self.ruta_biblioteca.mkdir(parents=True, exist_ok=True)
        except Exception:
            self.ruta_biblioteca = Path.home() / "Biblioteca_Shinobi_Gaiden"
            self.ruta_biblioteca.mkdir(parents=True, exist_ok=True)
            self._configurar_rutas()

    def generar_textos(
        self,
        clanes: Dict[str, ArbolClan],
        armas: List[Arma],
        bingo: GestorBingo,
        ocultar_vacios: bool = True
    ) -> Tuple[str, str, str, List[str]]:
        fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        advertencias = ValidadorModeracion.validar_todo(clanes, armas, bingo)

        # 1. Clanes.txt
        bloques_clanes = [
            "================================================================================",
            f"   COMPENDIO DE CLANES Y TÉCNICAS - GENERADO: {fecha_str}",
            "================================================================================",
        ]
        for clan in clanes.values():
            bloques_clanes.append("\n" + clan.generar_txt(ocultar_vacios=ocultar_vacios))
        txt_clanes = "\n".join(bloques_clanes) + "\n"

        # 2. Armas.txt
        bloques_armas = [
            "================================================================================",
            f"   CATÁLOGO DE OBJETOS Y ARMAS - GENERADO: {fecha_str}",
            "================================================================================",
        ]
        if armas:
            for a in armas:
                bloques_armas.append("\n" + a.generar_txt())
        else:
            bloques_armas.append("\n(Sin objetos registrados)")
        txt_armas = "\n".join(bloques_armas) + "\n"

        # 3. Bingo.txt
        txt_bingo = bingo.generar_txt() + "\n"

        return txt_clanes, txt_armas, txt_bingo, advertencias

    def guardar_todo(
        self,
        clanes: Dict[str, ArbolClan],
        armas: List[Arma],
        bingo: GestorBingo,
        ocultar_vacios: bool = True
    ) -> Tuple[str, str, str, List[str]]:
        self.inicializar_carpetas()
        txt_clanes, txt_armas, txt_bingo, advertencias = self.generar_textos(
            clanes, armas, bingo, ocultar_vacios=ocultar_vacios
        )

        self.ruta_txt_clanes.write_text(txt_clanes, encoding="utf-8")
        self.ruta_txt_armas.write_text(txt_armas, encoding="utf-8")
        self.ruta_txt_bingo.write_text(txt_bingo, encoding="utf-8")

        estado = {
            "clanes": {
                nombre: {k: asdict(v) for k, v in clan.nodos.items()}
                for nombre, clan in clanes.items()
            },
            "armas": [asdict(a) for a in armas],
            "bingo": {k: asdict(v) for k, v in bingo.participantes.items()},
        }
        self.ruta_db_json.write_text(json.dumps(estado, ensure_ascii=False, indent=4), encoding="utf-8")
        return txt_clanes, txt_armas, txt_bingo, advertencias

    def cargar_datos(self) -> Tuple[Dict[str, ArbolClan], List[Arma], GestorBingo]:
        if not self.ruta_db_json.exists():
            clanes, armas, bingo = construir_datos_ejemplo()
            self.guardar_todo(clanes, armas, bingo)
            return clanes, armas, bingo

        try:
            raw = json.loads(self.ruta_db_json.read_text(encoding="utf-8"))
            clanes: Dict[str, ArbolClan] = {}

            # Soporte tanto para formato multi-clan ("clanes") como legado ("clan_nombre" + "nodos")
            if "clanes" in raw and isinstance(raw["clanes"], dict):
                for nom_clan, dic_nodos in raw["clanes"].items():
                    arbol = ArbolClan(nom_clan)
                    for cod, nd in dic_nodos.items():
                        if cod in arbol.nodos:
                            arbol.nodos[cod] = NodoJutsu(**nd)
                    clanes[arbol.nombre_clan] = arbol
            elif "nodos" in raw:
                nom_clan = raw.get("clan_nombre", "UZUMAKI")
                arbol = ArbolClan(nom_clan)
                for cod, nd in raw["nodos"].items():
                    if cod in arbol.nodos:
                        arbol.nodos[cod] = NodoJutsu(**nd)
                clanes[arbol.nombre_clan] = arbol

            if not clanes:
                clanes, _, _ = construir_datos_ejemplo()

            armas: List[Arma] = []
            for ad in raw.get("armas", []):
                efs = [EfectoArma(**ef) for ef in ad.get("efectos", [])]
                armas.append(
                    Arma(
                        nombre=ad.get("nombre", ""),
                        codigo=ad.get("codigo", ""),
                        tipo=ad.get("tipo", "Otros"),
                        tamano=ad.get("tamano", "Mediano (armas)"),
                        municion=int(ad.get("municion", 1)),
                        efectos=efs,
                        descripcion=ad.get("descripcion", ""),
                    )
                )

            bingo = GestorBingo()
            for nom, pd in raw.get("bingo", {}).items():
                bingo.agregar_participante(
                    ParticipanteBingo(
                        nombre=pd.get("nombre", nom),
                        modo_seguro=bool(pd.get("modo_seguro", False)),
                        bingo_inicial=float(pd.get("bingo_inicial", 0.0)),
                        bingo_mision=float(pd.get("bingo_mision", 0.0)),
                        muerto=bool(pd.get("muerto", False)),
                        reconocimiento=float(pd.get("reconocimiento", 50.0)),
                        bajas=list(pd.get("bajas", [])),
                    )
                )
            bingo.calcular_resultados()
            return clanes, armas, bingo
        except Exception:
            clanes, armas, bingo = construir_datos_ejemplo()
            self.guardar_todo(clanes, armas, bingo)
            return clanes, armas, bingo


# =====================================================================
# 5. HELPERS DE UI COMPATIBLES CON FLET 0.2x Y FLET 1.0+ (PC & ANDROID)
# =====================================================================
_DROPDOWN_USA_ON_SELECT = "on_select" in inspect.signature(ft.Dropdown.__init__).parameters
_BTN_CLASS = getattr(ft, "ElevatedButton", getattr(ft, "Button", None))


def borde_all(width: float, color: str):
    if hasattr(ft, "Border") and hasattr(ft.Border, "all"):
        return ft.Border.all(width, color)
    return ft.border.all(width, color)


def padding_only(left: int = 0, top: int = 0, right: int = 0, bottom: int = 0):
    if hasattr(ft, "Padding") and hasattr(ft.Padding, "only"):
        return ft.Padding.only(left=left, top=top, right=right, bottom=bottom)
    return ft.padding.only(left=left, top=top, right=right, bottom=bottom)


def crear_titulo_seccion(texto: str, subtitulo: str = "") -> ft.Control:
    bloque_texto = [ft.Text(texto.upper(), size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT)]
    if subtitulo:
        bloque_texto.append(ft.Text(subtitulo, size=12, color=COLOR_MUTED))
    return ft.Container(
        content=ft.Row(
            [
                ft.Container(width=4, height=26, bgcolor=COLOR_ACCENT, border_radius=2),
                ft.Column(bloque_texto, spacing=2),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=padding_only(bottom=4, top=4),
    )


def crear_input(
    label: str,
    value: str = "",
    width: Optional[int] = None,
    expand: Optional[bool] = None,
    multiline: bool = False,
    min_lines: int = 1,
    max_lines: int = 1,
    es_numero: bool = False,
    read_only: bool = False,
    hint_text: str = "",
    on_change=None,
) -> ft.TextField:
    kwargs = dict(
        label=label,
        value=value,
        width=width,
        multiline=multiline,
        min_lines=min_lines,
        max_lines=max_lines,
        read_only=read_only,
        hint_text=hint_text,
        bgcolor=COLOR_INPUT,
        color=COLOR_TEXT,
        text_size=13,
    )
    if expand is not None:
        kwargs["expand"] = expand
    if es_numero:
        kwargs["keyboard_type"] = ft.KeyboardType.NUMBER
    if on_change is not None:
        kwargs["on_change"] = on_change
    return ft.TextField(**kwargs)


def crear_dropdown(
    label: str,
    opciones: List[Tuple[str, str]],
    value: str = "",
    width: Optional[int] = None,
    expand: Optional[bool] = None,
    on_change=None,
) -> ft.Dropdown:
    opts = [ft.dropdown.Option(key=k, text=t) for k, t in opciones]
    kwargs = dict(
        label=label,
        options=opts,
        value=value,
        width=width,
        bgcolor=COLOR_INPUT,
        color=COLOR_TEXT,
        text_size=13,
    )
    if expand is not None:
        kwargs["expand"] = expand
    if on_change is not None:
        if _DROPDOWN_USA_ON_SELECT:
            kwargs["on_select"] = on_change
        else:
            kwargs["on_change"] = on_change
    return ft.Dropdown(**kwargs)


def crear_boton(
    texto: str,
    on_click,
    bgcolor: str = COLOR_PRIMARY,
    color: str = "white",
    width: Optional[int] = None,
) -> ft.Control:
    sig = inspect.signature(_BTN_CLASS.__init__).parameters
    kwargs = dict(on_click=on_click, bgcolor=bgcolor, color=color, width=width)
    if "text" in sig:
        kwargs["text"] = texto
    else:
        kwargs["content"] = ft.Text(texto, color=color, weight=ft.FontWeight.W_600, size=13)
    return _BTN_CLASS(**kwargs)


# =====================================================================
# 6. INTERFAZ GRÁFICA TÁCTIL CON FLET (ANDROID & PC)
# =====================================================================
def main(page: ft.Page):
    page.title = "Shinobi Gaiden - Moderación y Herramientas"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COLOR_BG
    page.padding = 12
    page.scroll = ft.ScrollMode.ADAPTIVE

    # Servicio de Portapapeles compatible con Flet 1.0+ y Flet 0.2x
    servicio_clipboard = None
    if hasattr(ft, "Clipboard"):
        try:
            servicio_clipboard = ft.Clipboard()
            if hasattr(page, "services"):
                page.services.append(servicio_clipboard)
        except Exception:
            servicio_clipboard = None

    biblioteca = GestorBiblioteca()
    clanes, armas, bingo = biblioteca.cargar_datos()
    estado_ui = {
        "clan_actual": next(iter(clanes.keys())),
        "ocultar_vacios_clan": True,
        "archivo_txt_activo": "Clanes.txt",
        "arma_editando_idx": None,
    }

    def mostrar_mensaje(texto: str, es_error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(texto, color="white", size=13),
            bgcolor=COLOR_ERR if es_error else COLOR_OK,
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def copiar_texto(texto: str, etiqueta: str = "Texto"):
        valor = (texto or "").strip()
        if not valor or valor == "--":
            mostrar_mensaje(f"El campo '{etiqueta}' está vacío.", es_error=True)
            return
        try:
            if hasattr(page, "set_clipboard"):
                page.set_clipboard(valor)
            elif servicio_clipboard is not None:
                if inspect.iscoroutinefunction(servicio_clipboard.set):
                    page.run_task(servicio_clipboard.set, valor)
                else:
                    servicio_clipboard.set(valor)
            mostrar_mensaje(f"Copiado al portapapeles: {etiqueta}")
        except Exception as ex:
            mostrar_mensaje(f"No se pudo copiar: {ex}", es_error=True)

    def boton_copiar_campo(etiqueta: str, obtener_valor) -> ft.Control:
        return crear_boton(
            f"Copiar {etiqueta}",
            on_click=lambda e: copiar_texto(obtener_valor(), etiqueta),
            bgcolor="#2d2246",
            color="#d8b4fe",
        )

    def autoguardar_todo():
        txt_c, txt_a, txt_b, _ = biblioteca.guardar_todo(
            clanes, armas, bingo, ocultar_vacios=estado_ui["ocultar_vacios_clan"]
        )
        actualizar_vista_biblioteca_textos(txt_c, txt_a, txt_b)

    # =================================================================
    # PESTAÑA 1: CREAR TÉCNICA (MÚLTIPLES CLANES - 31 NODOS)
    # =================================================================
    def obtener_clan_actual() -> ArbolClan:
        nom = estado_ui["clan_actual"]
        if nom not in clanes:
            estado_ui["clan_actual"] = next(iter(clanes.keys()))
        return clanes[estado_ui["clan_actual"]]

    dd_clan_selector = crear_dropdown(
        "ÁRBOL / CLAN ACTIVO",
        [(k, k) for k in clanes.keys()],
        value=estado_ui["clan_actual"],
        width=200,
    )
    tf_nuevo_clan = crear_input("Nuevo / Renombrar Árbol (ej. UCHIHA)", width=230)

    dd_nodo = crear_dropdown(
        "NODO DE LA PLANTILLA (31 NODOS)",
        [],
        value="001R",
        width=280,
    )
    tf_tec_id = crear_input("TÉCNICA ID *", width=150, read_only=True)
    tf_tec_nombre = crear_input("NOMBRE DE TÉCNICA *", width=280, hint_text="Amaterasu")
    tf_tec_arbol = crear_input("ÁRBOL *", width=150, read_only=True)
    tf_tec_rama = crear_input("RAMA *", width=150, read_only=True)

    dd_tec_cat = crear_dropdown(
        "CATEGORÍA",
        [(c, c) for c in CATEGORIAS_CLAN],
        value="Yang",
        width=220,
    )
    tf_tec_cat_custom = crear_input("Categoría personalizada", width=200)
    tf_tec_cat_custom.visible = False

    tf_tec_nivel = crear_input("NIVEL (Sellos)", value="0", width=130, es_numero=True)
    tf_tec_chakra = crear_input("CHAKRA BASE", value="", width=140, es_numero=True)
    sw_tec_mantenido = ft.Switch(label="Mantenido (Por turno)", value=False, active_color=COLOR_PRIMARY)
    tf_tec_coste_preview = crear_input("COSTE (Generado para el panel)", width=320, read_only=True)

    dd_tec_stat = crear_dropdown(
        "STAT",
        [(s, s if s else "(Sin Stat)") for s in STATS_CLAN],
        value="",
        width=140,
    )
    dd_tec_fx = crear_dropdown(
        "F(x)",
        [(f, f if f else "(Sin F(x))") for f in FX_VALIDOS],
        value="",
        width=120,
    )
    tf_tec_n = crear_input("MULTIPLICADOR N", value="", width=140, es_numero=True)
    tf_tec_txt_ef = crear_input("TEXTO DEL EFECTO", width=280, hint_text="80 Vida por turno / Daño")
    tf_tec_efecto_preview = crear_input("EFECTO (Generado para el panel)", width=320, read_only=True)

    # Asistente / Referencia visual de TABLA_MODERACION (usa 'chakra' y 'nivel' como guía)
    dd_ref_moderacion = crear_dropdown(
        "Referencia Doc Moderación (Consulta de Chakra y Nivel)",
        [("", "(Seleccionar baremo para consultar)")] + [
            (
                k,
                f"{k} -> Chakra: {v['chakra']} | Nivel: {v['nivel']} | Fórmula: {v['formula']}"
            )
            for k, v in TABLA_MODERACION.items()
            if v["tipo"] != "Tamaño"
        ],
        value="",
        width=450,
    )
    lbl_ref_comparacion = ft.Text(
        "Selecciona un baremo de la Tabla de Moderación para comparar Chakra, Nivel y Fórmula con tu técnica.",
        size=12,
        color=COLOR_MUTED,
    )

    tf_tec_desc = crear_input(
        "DESCRIPCIÓN *",
        multiline=True,
        min_lines=4,
        max_lines=7,
        hint_text="El usuario cierra uno de sus ojos para concentrar chakra durante un turno completo...",
    )

    sw_solo_nodos_activos = ft.Switch(
        label="Mostrar solo nodos con contenido en el listado",
        value=True,
        active_color=COLOR_PRIMARY,
    )
    lv_nodos_resumen = ft.Column(spacing=8)

    def obtener_categoria_formulario() -> str:
        if dd_tec_cat.value == "Otra (Escribir)":
            return tf_tec_cat_custom.value.strip()
        return (dd_tec_cat.value or "").strip()

    def construir_nodo_temporal() -> NodoJutsu:
        clan_obj = obtener_clan_actual()
        cod = dd_nodo.value or "001R"
        base = clan_obj.nodos.get(cod, clan_obj.nodos["001R"])
        chakra_str = tf_tec_chakra.value.strip()
        n_str = tf_tec_n.value.strip()
        nivel_str = tf_tec_nivel.value.strip()

        chakra_val = int(chakra_str) if chakra_str.lstrip("-").isdigit() else None
        n_val = int(n_str) if n_str.lstrip("-").isdigit() else None
        sellos_val = int(nivel_str) if nivel_str.lstrip("-").isdigit() else 0

        return NodoJutsu(
            codigo_corto=base.codigo_corto,
            tipo_nodo=base.tipo_nodo,
            numero=base.numero,
            arbol=clan_obj.nombre_clan,
            rama=base.rama,
            nombre_jutsu=tf_tec_nombre.value.strip(),
            categoria=obtener_categoria_formulario(),
            sellos=sellos_val,
            chakra=chakra_val,
            mantenido="Si" if sw_tec_mantenido.value else "No",
            stat=dd_tec_stat.value or "",
            fx=dd_tec_fx.value or "",
            n=n_val,
            texto_efecto=tf_tec_txt_ef.value.strip(),
            descripcion=tf_tec_desc.value.strip(),
        )

    def actualizar_preview_tecnica(e=None):
        tf_tec_cat_custom.visible = (dd_tec_cat.value == "Otra (Escribir)")
        temp = construir_nodo_temporal()
        tf_tec_id.value = temp.id_unico
        tf_tec_arbol.value = temp.arbol.lower()
        tf_tec_rama.value = temp.rama
        tf_tec_coste_preview.value = temp.coste_formateado
        tf_tec_efecto_preview.value = temp.efecto_formateado

        ref_key = dd_ref_moderacion.value
        if ref_key and ref_key in TABLA_MODERACION:
            regla = TABLA_MODERACION[ref_key]
            chk_manual = temp.chakra if temp.chakra is not None else 0
            dif_chk = chk_manual - regla["chakra"]
            dif_niv = temp.sellos - regla["nivel"]
            estado_chk = "OK" if dif_chk == 0 else (f"+{dif_chk}" if dif_chk > 0 else f"{dif_chk}")
            estado_niv = "OK" if dif_niv == 0 else (f"+{dif_niv}" if dif_niv > 0 else f"{dif_niv}")
            lbl_ref_comparacion.value = (
                f"Sugerido [{ref_key}] -> Chakra: {regla['chakra']} (Tu técnica: {temp.chakra if temp.chakra is not None else '--'} [{estado_chk}]) | "
                f"Nivel/Sellos: {regla['nivel']} (Tu técnica: {temp.sellos} [{estado_niv}]) | "
                f"Fórmula: {regla['formula']} | Slots eq.: {regla['slot']}"
            )
            lbl_ref_comparacion.color = COLOR_OK if (dif_chk == 0 and dif_niv == 0) else COLOR_WARN
        else:
            lbl_ref_comparacion.value = (
                "Selecciona un baremo de la Tabla de Moderación para comparar Chakra, Nivel y Fórmula con tu técnica."
            )
            lbl_ref_comparacion.color = COLOR_MUTED

        page.update()

    def aplicar_referencia_moderacion_click(e):
        ref_key = dd_ref_moderacion.value
        if not ref_key or ref_key not in TABLA_MODERACION:
            mostrar_mensaje("Primero selecciona un baremo en 'Referencia Doc Moderación'.", es_error=True)
            return
        regla = TABLA_MODERACION[ref_key]
        tf_tec_chakra.value = str(max(0, regla["chakra"]))
        tf_tec_nivel.value = str(max(0, regla["nivel"]))
        formula = regla["formula"]
        if "x" in formula:
            dd_tec_fx.value = "x"
            num_part = "".join(ch for ch in formula if ch.isdigit())
            if num_part:
                tf_tec_n.value = num_part
        elif "/" in formula:
            dd_tec_fx.value = "/"
            num_part = "".join(ch for ch in formula if ch.isdigit())
            if num_part:
                tf_tec_n.value = num_part
        if "MSTAT" in formula and not (dd_tec_stat.value or "").startswith("M"):
            dd_tec_stat.value = f"M{dd_tec_stat.value}" if dd_tec_stat.value else "MCCK"
        actualizar_preview_tecnica()
        mostrar_mensaje(f"Valores de '{ref_key}' aplicados al formulario de técnica.")

    def refrescar_opciones_dropdown_nodos():
        clan_obj = obtener_clan_actual()
        dd_nodo.options = [
            ft.dropdown.Option(
                key=cod,
                text=f"{cod} | {n.rama} - {n.nombre_jutsu if n.nombre_jutsu else (n.categoria or 'Vacío')}"
            )
            for cod, n in clan_obj.nodos.items()
        ]

    def cargar_nodo_en_formulario(cod_forzado: Optional[str] = None):
        clan_obj = obtener_clan_actual()
        if cod_forzado:
            dd_nodo.value = cod_forzado
        cod = dd_nodo.value or "001R"
        if cod not in clan_obj.nodos:
            cod = "001R"
            dd_nodo.value = cod
        n = clan_obj.nodos[cod]

        tf_tec_nombre.value = n.nombre_jutsu
        if n.categoria in CATEGORIAS_CLAN and n.categoria != "Otra (Escribir)":
            dd_tec_cat.value = n.categoria
            tf_tec_cat_custom.value = ""
            tf_tec_cat_custom.visible = False
        elif n.categoria:
            dd_tec_cat.value = "Otra (Escribir)"
            tf_tec_cat_custom.value = n.categoria
            tf_tec_cat_custom.visible = True
        else:
            dd_tec_cat.value = "Yang"
            tf_tec_cat_custom.value = ""
            tf_tec_cat_custom.visible = False

        tf_tec_nivel.value = str(n.sellos)
        tf_tec_chakra.value = str(n.chakra) if n.chakra is not None else ""
        sw_tec_mantenido.value = (n.mantenido.lower() == "si")
        dd_tec_stat.value = n.stat if n.stat in STATS_CLAN else ""
        dd_tec_fx.value = n.fx if n.fx in FX_VALIDOS else ""
        tf_tec_n.value = str(n.n) if n.n is not None else ""
        tf_tec_txt_ef.value = n.texto_efecto
        tf_tec_desc.value = n.descripcion

        refrescar_opciones_dropdown_nodos()
        actualizar_vista_clan()
        actualizar_preview_tecnica()

    def actualizar_vista_clan(e=None):
        lv_nodos_resumen.controls.clear()
        clan_obj = obtener_clan_actual()
        solo_activos = sw_solo_nodos_activos.value

        for cod, n in clan_obj.nodos.items():
            if solo_activos and not n.esta_activo:
                continue

            def make_cargar(c=cod):
                return lambda e: cargar_nodo_en_formulario(c)

            def make_copiar(nodo_ref=n):
                return lambda e: copiar_texto(nodo_ref.generar_txt(), f"Ficha {nodo_ref.id_unico}")

            def make_limpiar(c=cod):
                def _limpiar(e):
                    clan_obj.limpiar_nodo(c)
                    autoguardar_todo()
                    cargar_nodo_en_formulario(c)
                    mostrar_mensaje(f"Nodo {c} limpiado.")
                return _limpiar

            lv_nodos_resumen.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        f"[{n.id_unico}] {n.nombre_jutsu or '(Vacío)'}",
                                        weight=ft.FontWeight.BOLD,
                                        size=14,
                                        color=COLOR_TEXT,
                                    ),
                                    ft.Text(
                                        f"{n.rama} • {n.categoria or 'Sin categoría'} | Nivel: {n.sellos}",
                                        size=12,
                                        color=COLOR_MUTED,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                wrap=True,
                            ),
                            ft.Text(
                                f"Coste: {n.coste_formateado}   |   Efecto: {n.efecto_formateado}",
                                size=12,
                                color="#fbbf24",
                            ),
                            ft.Text(
                                n.descripcion if n.descripcion else "(Sin descripción)",
                                size=12,
                                color=COLOR_MUTED,
                                max_lines=2,
                            ),
                            ft.Row(
                                [
                                    crear_boton("Editar Nodo", make_cargar(), bgcolor=COLOR_PRIMARY),
                                    crear_boton("Copiar Ficha", make_copiar(), bgcolor="#2d2246", color="#d8b4fe"),
                                    crear_boton("Limpiar Nodo", make_limpiar(), bgcolor="#3f1d2b", color="#fca5a5"),
                                ],
                                spacing=8,
                                wrap=True,
                            ),
                        ],
                        spacing=6,
                    ),
                    padding=12,
                    bgcolor=COLOR_SURFACE,
                    border=borde_all(1, COLOR_BORDER),
                    border_radius=8,
                )
            )
        page.update()

    def guardar_nodo_click(e):
        clan_obj = obtener_clan_actual()
        temp = construir_nodo_temporal()
        errores = clan_obj.actualizar_nodo(
            temp.codigo_corto,
            nombre_jutsu=temp.nombre_jutsu,
            categoria=temp.categoria,
            sellos=temp.sellos,
            chakra=temp.chakra,
            mantenido=temp.mantenido,
            stat=temp.stat,
            fx=temp.fx,
            n=temp.n,
            texto_efecto=temp.texto_efecto,
            descripcion=temp.descripcion,
        )
        autoguardar_todo()
        refrescar_opciones_dropdown_nodos()
        actualizar_vista_clan()
        actualizar_preview_tecnica()
        if errores:
            mostrar_mensaje("Guardado con avisos: " + " | ".join(errores), es_error=True)
        else:
            mostrar_mensaje(f"Técnica [{temp.id_unico}] guardada y exportada a Clanes.txt.")

    def cambiar_clan_activo(e=None):
        if dd_clan_selector.value and dd_clan_selector.value in clanes:
            estado_ui["clan_actual"] = dd_clan_selector.value
            cargar_nodo_en_formulario("001R")

    def crear_clan_click(e):
        nuevo = tf_nuevo_clan.value.strip().upper()
        if not nuevo:
            mostrar_mensaje("Escribe el nombre del nuevo Clan/Árbol.", es_error=True)
            return
        if nuevo in clanes:
            mostrar_mensaje(f"El clan '{nuevo}' ya existe. Seleccionándolo...", es_error=False)
        else:
            clanes[nuevo] = ArbolClan(nuevo)
        estado_ui["clan_actual"] = nuevo
        dd_clan_selector.options = [ft.dropdown.Option(key=k, text=k) for k in clanes.keys()]
        dd_clan_selector.value = nuevo
        tf_nuevo_clan.value = ""
        autoguardar_todo()
        cargar_nodo_en_formulario("101B")
        mostrar_mensaje(f"Árbol de Clan '{nuevo}' listo con sus 31 nodos.")

    def renombrar_clan_click(e):
        nuevo = tf_nuevo_clan.value.strip().upper()
        actual = estado_ui["clan_actual"]
        if not nuevo:
            mostrar_mensaje("Escribe el nuevo nombre en el campo de texto.", es_error=True)
            return
        if nuevo in clanes and nuevo != actual:
            mostrar_mensaje(f"Ya existe otro clan llamado '{nuevo}'.", es_error=True)
            return
        clan_obj = clanes.pop(actual)
        clan_obj.renombrar(nuevo)
        clanes[nuevo] = clan_obj
        estado_ui["clan_actual"] = nuevo
        dd_clan_selector.options = [ft.dropdown.Option(key=k, text=k) for k in clanes.keys()]
        dd_clan_selector.value = nuevo
        tf_nuevo_clan.value = ""
        autoguardar_todo()
        cargar_nodo_en_formulario(dd_nodo.value)
        mostrar_mensaje(f"Clan renombrado a '{nuevo}'.")

    def eliminar_clan_click(e):
        actual = estado_ui["clan_actual"]
        if len(clanes) <= 1:
            mostrar_mensaje("Debe existir al menos 1 Clan en la biblioteca.", es_error=True)
            return
        del clanes[actual]
        estado_ui["clan_actual"] = next(iter(clanes.keys()))
        dd_clan_selector.options = [ft.dropdown.Option(key=k, text=k) for k in clanes.keys()]
        dd_clan_selector.value = estado_ui["clan_actual"]
        autoguardar_todo()
        cargar_nodo_en_formulario("101B")
        mostrar_mensaje(f"Clan '{actual}' eliminado.")

    # Conectar eventos reactivos de Crear Técnica
    if _DROPDOWN_USA_ON_SELECT:
        dd_clan_selector.on_select = cambiar_clan_activo
        dd_nodo.on_select = lambda e: cargar_nodo_en_formulario(dd_nodo.value)
        dd_tec_cat.on_select = actualizar_preview_tecnica
        dd_tec_stat.on_select = actualizar_preview_tecnica
        dd_tec_fx.on_select = actualizar_preview_tecnica
        dd_ref_moderacion.on_select = actualizar_preview_tecnica
    else:
        dd_clan_selector.on_change = cambiar_clan_activo
        dd_nodo.on_change = lambda e: cargar_nodo_en_formulario(dd_nodo.value)
        dd_tec_cat.on_change = actualizar_preview_tecnica
        dd_tec_stat.on_change = actualizar_preview_tecnica
        dd_tec_fx.on_change = actualizar_preview_tecnica
        dd_ref_moderacion.on_change = actualizar_preview_tecnica

    tf_tec_nombre.on_change = actualizar_preview_tecnica
    tf_tec_cat_custom.on_change = actualizar_preview_tecnica
    tf_tec_nivel.on_change = actualizar_preview_tecnica
    tf_tec_chakra.on_change = actualizar_preview_tecnica
    sw_tec_mantenido.on_change = actualizar_preview_tecnica
    tf_tec_n.on_change = actualizar_preview_tecnica
    tf_tec_txt_ef.on_change = actualizar_preview_tecnica
    sw_solo_nodos_activos.on_change = actualizar_vista_clan

    vista_clanes = ft.Column(
        [
            crear_titulo_seccion("CREAR TÉCNICA", "Gestión de múltiples Árboles de Clan (Plantilla oficial de 31 nodos)"),
            ft.Container(
                content=ft.Row(
                    [
                        dd_clan_selector,
                        tf_nuevo_clan,
                        crear_boton("Crear Clan", crear_clan_click, bgcolor=COLOR_PRIMARY),
                        crear_boton("Renombrar", renombrar_clan_click, bgcolor="#2d2246", color="#d8b4fe"),
                        crear_boton("Eliminar Clan", eliminar_clan_click, bgcolor="#3f1d2b", color="#fca5a5"),
                        crear_boton(
                            "Copiar Árbol Completo",
                            lambda e: copiar_texto(
                                obtener_clan_actual().generar_txt(ocultar_vacios=estado_ui["ocultar_vacios_clan"]),
                                f"Árbol {estado_ui['clan_actual']}"
                            ),
                            bgcolor="#1f2937",
                        ),
                    ],
                    wrap=True,
                    spacing=8,
                ),
                padding=12,
                bgcolor=COLOR_SURFACE,
                border=borde_all(1, COLOR_BORDER),
                border_radius=8,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                dd_nodo,
                                tf_tec_nombre,
                                boton_copiar_campo("Nombre", lambda: tf_tec_nombre.value),
                                tf_tec_id,
                                boton_copiar_campo("ID", lambda: tf_tec_id.value),
                            ],
                            wrap=True,
                            spacing=8,
                        ),
                        ft.Row(
                            [
                                tf_tec_arbol,
                                boton_copiar_campo("Árbol", lambda: tf_tec_arbol.value),
                                tf_tec_rama,
                                boton_copiar_campo("Rama", lambda: tf_tec_rama.value),
                                dd_tec_cat,
                                tf_tec_cat_custom,
                                boton_copiar_campo("Categoría", obtener_categoria_formulario),
                                tf_tec_nivel,
                                boton_copiar_campo("Nivel", lambda: tf_tec_nivel.value),
                            ],
                            wrap=True,
                            spacing=8,
                        ),
                        ft.Divider(color=COLOR_BORDER),
                        ft.Row(
                            [
                                dd_ref_moderacion,
                                crear_boton(
                                    "Aplicar Chakra/Nivel sugerido",
                                    aplicar_referencia_moderacion_click,
                                    bgcolor="#2d2246",
                                    color="#d8b4fe",
                                ),
                            ],
                            wrap=True,
                            spacing=8,
                        ),
                        lbl_ref_comparacion,
                        ft.Row(
                            [
                                tf_tec_chakra,
                                sw_tec_mantenido,
                                tf_tec_coste_preview,
                                boton_copiar_campo("Coste", lambda: tf_tec_coste_preview.value),
                            ],
                            wrap=True,
                            spacing=8,
                        ),
                        ft.Row(
                            [
                                dd_tec_stat,
                                dd_tec_fx,
                                tf_tec_n,
                                tf_tec_txt_ef,
                            ],
                            wrap=True,
                            spacing=8,
                        ),
                        ft.Row(
                            [
                                tf_tec_efecto_preview,
                                boton_copiar_campo("Efecto", lambda: tf_tec_efecto_preview.value),
                            ],
                            wrap=True,
                            spacing=8,
                        ),
                        tf_tec_desc,
                        ft.Row(
                            [
                                crear_boton("CREAR / GUARDAR TÉCNICA", guardar_nodo_click, bgcolor=COLOR_PRIMARY),
                                boton_copiar_campo("Descripción", lambda: tf_tec_desc.value),
                                crear_boton(
                                    "Copiar Ficha Completa",
                                    lambda e: copiar_texto(construir_nodo_temporal().generar_txt(), "Ficha de Técnica"),
                                    bgcolor="#2d2246",
                                    color="#d8b4fe",
                                ),
                            ],
                            wrap=True,
                            spacing=10,
                        ),
                    ],
                    spacing=10,
                ),
                padding=14,
                bgcolor=COLOR_SURFACE,
                border=borde_all(1, COLOR_BORDER),
                border_radius=8,
            ),
            ft.Row(
                [
                    ft.Text("NODOS DEL ÁRBOL ACTIVO", weight=ft.FontWeight.BOLD, size=14, color=COLOR_TEXT),
                    sw_solo_nodos_activos,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                wrap=True,
            ),
            lv_nodos_resumen,
        ],
        spacing=12,
    )

    # =================================================================
    # PESTAÑA 2: OBJETOS (CONSTRUCTOR DE ARMAS Y MODERACIÓN)
    # =================================================================
    dd_cargar_objeto = crear_dropdown(
        "CARGAR OBJETO POR ID",
        [("", "(Crear Nuevo Objeto)")] + [(a.codigo, f"{a.codigo} - {a.nombre}") for a in armas],
        value="",
        width=340,
    )
    tf_arma_codigo = crear_input("OBJETO ID *", width=180, hint_text="UCH502")
    tf_arma_nombre = crear_input("NOMBRE *", width=280, hint_text="Nombre del objeto o arma")
    dd_arma_tipo = crear_dropdown(
        "TIPO *",
        [("Empuñada", "Empuñada"), ("Arrojadiza", "Arrojadiza"), ("Otros", "Otros")],
        value="Empuñada",
        width=170,
    )
    tf_arma_mun = crear_input("MUNICIÓN", value="1", width=130, es_numero=True)
    dd_arma_tamano = crear_dropdown(
        "TAMAÑO *",
        [(t, t) for t in TAMANOS_VALIDOS],
        value="Mediano (armas)",
        width=210,
    )
    tf_arma_slots_preview = crear_input("SLOTS TOTALES", value="2", width=130, read_only=True)
    tf_arma_ryos_preview = crear_input("COSTE (RYOS)", value="490", width=160, read_only=True)

    selectores_efectos = []
    filas_efectos_ui = []
    for i in range(1, 4):
        dd_ef = crear_dropdown(
            f"EFECTO {i} (Doc Moderación)",
            [("", "(Ninguno)")] + [(ef, f"{ef} ({TABLA_MODERACION[ef]['slot']} Slots)") for ef in EFECTOS_VALIDOS],
            value="",
            width=250,
        )
        dd_st = crear_dropdown(
            f"STAT {i}",
            [(s, s if s else "(Sin Stat)") for s in STATS_ARMAS],
            value="",
            width=130,
        )
        tf_tx = crear_input(f" Qué produce Efecto {i} (ej. Daño, Radio)", width=280)
        tf_res = crear_input(f"EFECTO {i} (Resultado para el panel)", width=320, read_only=True)
        selectores_efectos.append((dd_ef, dd_st, tf_tx, tf_res))

        idx_ef = i - 1
        filas_efectos_ui.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row([dd_ef, dd_st, tf_tx], wrap=True, spacing=8),
                        ft.Row(
                            [
                                tf_res,
                                boton_copiar_campo(f"Efecto {i}", lambda idx=idx_ef: selectores_efectos[idx][3].value),
                            ],
                            wrap=True,
                            spacing=8,
                        ),
                    ],
                    spacing=6,
                ),
                padding=10,
                bgcolor=COLOR_BG,
                border=borde_all(1, COLOR_BORDER),
                border_radius=6,
            )
        )

    tf_arma_desc = crear_input("DESCRIPCIÓN *", multiline=True, min_lines=3, max_lines=6)
    lv_armas_creadas = ft.Column(spacing=8)

    def construir_arma_temporal() -> Arma:
        efs = []
        for dd_ef, dd_st, tf_tx, _ in selectores_efectos:
            if dd_ef.value:
                efs.append(EfectoArma(dd_ef.value, dd_st.value or "", tf_tx.value.strip()))
        mun_str = tf_arma_mun.value.strip()
        mun = int(mun_str) if mun_str.isdigit() else 1
        return Arma(
            nombre=tf_arma_nombre.value.strip(),
            codigo=tf_arma_codigo.value.strip(),
            tipo=dd_arma_tipo.value or "Empuñada",
            tamano=dd_arma_tamano.value or "Mediano (armas)",
            municion=mun,
            efectos=efs,
            descripcion=tf_arma_desc.value.strip(),
        )

    def actualizar_preview_arma(e=None):
        temp = construir_arma_temporal()
        tf_arma_slots_preview.value = str(temp.slots)
        tf_arma_ryos_preview.value = str(temp.ryos)
        for i, (dd_ef, dd_st, tf_tx, tf_res) in enumerate(selectores_efectos):
            if dd_ef.value:
                ef_temp = EfectoArma(dd_ef.value, dd_st.value or "", tf_tx.value.strip())
                tf_res.value = ef_temp.formatear_efecto()
            else:
                tf_res.value = ""
        page.update()

    def limpiar_formulario_arma(e=None):
        estado_ui["arma_editando_idx"] = None
        dd_cargar_objeto.value = ""
        tf_arma_codigo.value = ""
        tf_arma_nombre.value = ""
        dd_arma_tipo.value = "Empuñada"
        tf_arma_mun.value = "1"
        dd_arma_tamano.value = "Mediano (armas)"
        for dd_ef, dd_st, tf_tx, tf_res in selectores_efectos:
            dd_ef.value = ""
            dd_st.value = ""
            tf_tx.value = ""
            tf_res.value = ""
        tf_arma_desc.value = ""
        actualizar_preview_arma()

    def cargar_arma_en_formulario(idx: int):
        if not (0 <= idx < len(armas)):
            return
        a = armas[idx]
        estado_ui["arma_editando_idx"] = idx
        dd_cargar_objeto.value = a.codigo
        tf_arma_codigo.value = a.codigo
        tf_arma_nombre.value = a.nombre
        dd_arma_tipo.value = a.tipo if a.tipo in ("Empuñada", "Arrojadiza", "Otros") else "Otros"
        tf_arma_mun.value = str(a.municion)
        dd_arma_tamano.value = a.tamano if a.tamano in TAMANOS_VALIDOS else "Mediano (armas)"

        for i, (dd_ef, dd_st, tf_tx, tf_res) in enumerate(selectores_efectos):
            if i < len(a.efectos):
                dd_ef.value = a.efectos[i].tipo_efecto
                dd_st.value = a.efectos[i].stat
                tf_tx.value = a.efectos[i].texto_efecto
            else:
                dd_ef.value = ""
                dd_st.value = ""
                tf_tx.value = ""
        tf_arma_desc.value = a.descripcion
        actualizar_preview_arma()

    def cargar_objeto_desde_selector(e=None):
        cod = dd_cargar_objeto.value
        if not cod:
            limpiar_formulario_arma()
            return
        for i, a in enumerate(armas):
            if a.codigo == cod:
                cargar_arma_en_formulario(i)
                mostrar_mensaje(f"Objeto '{a.nombre}' cargado para edición.")
                return

    def refrescar_lista_armas():
        dd_cargar_objeto.options = [ft.dropdown.Option(key="", text="(Crear Nuevo Objeto)")] + [
            ft.dropdown.Option(key=a.codigo, text=f"{a.codigo} - {a.nombre}") for a in armas
        ]
        lv_armas_creadas.controls.clear()
        for idx, a in enumerate(armas):
            def make_editar(i=idx):
                return lambda e: cargar_arma_en_formulario(i)

            def make_copiar(arma_ref=a):
                return lambda e: copiar_texto(arma_ref.generar_txt(), f"Ficha {arma_ref.nombre}")

            def make_eliminar(i=idx):
                def _del(e):
                    eliminada = armas.pop(i)
                    if estado_ui["arma_editando_idx"] == i:
                        limpiar_formulario_arma()
                    autoguardar_todo()
                    refrescar_lista_armas()
                    page.update()
                    mostrar_mensaje(f"Objeto '{eliminada.nombre}' eliminado.")
                return _del

            efectos_txt = " | ".join(
                f"Ef.{j+1}: {ef.formatear_efecto()}" for j, ef in enumerate(a.efectos) if ef.tipo_efecto
            ) or "(Sin efectos)"

            lv_armas_creadas.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        f"[{a.codigo}] {a.nombre}",
                                        weight=ft.FontWeight.BOLD,
                                        size=14,
                                        color=COLOR_TEXT,
                                    ),
                                    ft.Text(
                                        f"{a.tipo} • {a.tamano} • Mun: {a.municion} • {a.slots} Slots ({a.ryos} Ryos)",
                                        size=12,
                                        color="#fbbf24",
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                wrap=True,
                            ),
                            ft.Text(efectos_txt, size=12, color="#c4b5fd"),
                            ft.Text(a.descripcion or "(Sin descripción)", size=12, color=COLOR_MUTED, max_lines=2),
                            ft.Row(
                                [
                                    crear_boton("Cargar / Editar", make_editar(), bgcolor=COLOR_PRIMARY),
                                    crear_boton("Copiar Ficha", make_copiar(), bgcolor="#2d2246", color="#d8b4fe"),
                                    crear_boton("Eliminar", make_eliminar(), bgcolor="#3f1d2b", color="#fca5a5"),
                                ],
                                spacing=8,
                                wrap=True,
                            ),
                        ],
                        spacing=6,
                    ),
                    padding=12,
                    bgcolor=COLOR_SURFACE,
                    border=borde_all(1, COLOR_BORDER),
                    border_radius=8,
                )
            )

    def guardar_arma_click(e):
        nueva = construir_arma_temporal()
        errores = ValidadorModeracion.validar_arma(nueva)
        if errores:
            mostrar_mensaje("ERROR DE VALIDACIÓN: " + " | ".join(errores), es_error=True)
            return

        idx_edicion = estado_ui["arma_editando_idx"]
        if idx_edicion is not None and 0 <= idx_edicion < len(armas):
            armas[idx_edicion] = nueva
            accion = "actualizado"
        else:
            # Si coincide por código con una existente, actualizarla
            existente = next((i for i, a in enumerate(armas) if a.codigo.lower() == nueva.codigo.lower()), None)
            if existente is not None:
                armas[existente] = nueva
                estado_ui["arma_editando_idx"] = existente
                accion = "actualizado"
            else:
                armas.append(nueva)
                estado_ui["arma_editando_idx"] = len(armas) - 1
                accion = "creado"

        autoguardar_todo()
        refrescar_lista_armas()
        dd_cargar_objeto.value = nueva.codigo
        page.update()
        mostrar_mensaje(f"¡Objeto '{nueva.nombre}' {accion} ({nueva.slots} Slots / {nueva.ryos} Ryos) y guardado en Armas.txt!")

    if _DROPDOWN_USA_ON_SELECT:
        dd_cargar_objeto.on_select = cargar_objeto_desde_selector
        dd_arma_tamano.on_select = actualizar_preview_arma
        for dd_ef, dd_st, tf_tx, _ in selectores_efectos:
            dd_ef.on_select = actualizar_preview_arma
            dd_st.on_select = actualizar_preview_arma
            tf_tx.on_change = actualizar_preview_arma
    else:
        dd_cargar_objeto.on_change = cargar_objeto_desde_selector
        dd_arma_tamano.on_change = actualizar_preview_arma
        for dd_ef, dd_st, tf_tx, _ in selectores_efectos:
            dd_ef.on_change = actualizar_preview_arma
            dd_st.on_change = actualizar_preview_arma
            tf_tx.on_change = actualizar_preview_arma

    vista_armas = ft.Column(
        [
            crear_titulo_seccion("OBJETOS", "Constructor de Armas y Equipamiento conectado a Doc Moderación"),
            ft.Container(
                content=ft.Row(
                    [
                        dd_cargar_objeto,
                        crear_boton("CARGAR", cargar_objeto_desde_selector, bgcolor=COLOR_PRIMARY),
                        crear_boton("NUEVO / LIMPIAR", limpiar_formulario_arma, bgcolor="#2d2246", color="#d8b4fe"),
                    ],
                    wrap=True,
                    spacing=8,
                ),
                padding=12,
                bgcolor=COLOR_SURFACE,
                border=borde_all(1, COLOR_BORDER),
                border_radius=8,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                tf_arma_codigo,
                                boton_copiar_campo("ID", lambda: tf_arma_codigo.value),
                                tf_arma_nombre,
                                boton_copiar_campo("Nombre", lambda: tf_arma_nombre.value),
                            ],
                            wrap=True,
                            spacing=8,
                        ),
                        ft.Row(
                            [
                                dd_arma_tipo,
                                tf_arma_mun,
                                boton_copiar_campo("Munición", lambda: tf_arma_mun.value),
                                dd_arma_tamano,
                                tf_arma_slots_preview,
                                tf_arma_ryos_preview,
                                boton_copiar_campo("Coste (Ryos)", lambda: tf_arma_ryos_preview.value),
                            ],
                            wrap=True,
                            spacing=8,
                        ),
                        filas_efectos_ui[0],
                        filas_efectos_ui[1],
                        filas_efectos_ui[2],
                        tf_arma_desc,
                        ft.Row(
                            [
                                crear_boton("GUARDAR OBJETO", guardar_arma_click, bgcolor=COLOR_PRIMARY),
                                boton_copiar_campo("Descripción", lambda: tf_arma_desc.value),
                                crear_boton(
                                    "Copiar Ficha Completa",
                                    lambda e: copiar_texto(construir_arma_temporal().generar_txt(), "Ficha de Objeto"),
                                    bgcolor="#2d2246",
                                    color="#d8b4fe",
                                ),
                            ],
                            wrap=True,
                            spacing=10,
                        ),
                    ],
                    spacing=10,
                ),
                padding=14,
                bgcolor=COLOR_SURFACE,
                border=borde_all(1, COLOR_BORDER),
                border_radius=8,
            ),
            ft.Text("CATÁLOGO DE OBJETOS REGISTRADOS", weight=ft.FontWeight.BOLD, size=14, color=COLOR_TEXT),
            lv_armas_creadas,
        ],
        spacing=12,
    )

    # =================================================================
    # PESTAÑA 3: LIQUIDACIÓN DE BINGO (EXPORTACIÓN A BINGO.TXT)
    # =================================================================
    tf_b_nombre = crear_input("Personaje", width=180)
    sw_b_seguro = ft.Switch(label="Modo Seguro", value=False, active_color=COLOR_PRIMARY)
    sw_b_muerto = ft.Switch(label="Muerto", value=False, active_color=COLOR_ERR)
    tf_b_ini = crear_input("Bingo Inicial", value="0", width=120, es_numero=True)
    tf_b_mis = crear_input("Bingo Misión", value="200", width=120, es_numero=True)
    tf_b_rec = crear_input("Reconocimiento", value="50", width=130, es_numero=True)
    tf_b_bajas = crear_input("Bajas reclamadas (toca los botones de abajo o escribe separado por comas)")

    fila_selectores_bajas = ft.Row(wrap=True, spacing=6)
    lv_tarjetas_bingo = ft.Column(spacing=8)
    txt_tabla_bingo = ft.Text(value="", font_family="monospace", size=12, selectable=True, color=COLOR_TEXT)

    def obtener_lista_bajas_actual() -> List[str]:
        return [x.strip() for x in tf_b_bajas.value.split(",") if x.strip()]

    def alternar_baja_en_formulario(nombre_victima: str):
        actuales = obtener_lista_bajas_actual()
        if nombre_victima in actuales:
            actuales = [x for x in actuales if x != nombre_victima]
        else:
            actuales.append(nombre_victima)
        tf_b_bajas.value = ", ".join(actuales)
        refrescar_vista_bingo()

    def cargar_participante_en_formulario(p: ParticipanteBingo):
        tf_b_nombre.value = p.nombre
        sw_b_seguro.value = p.modo_seguro
        sw_b_muerto.value = p.muerto
        tf_b_ini.value = f"{p.bingo_inicial:g}"
        tf_b_mis.value = f"{p.bingo_mision:g}"
        tf_b_rec.value = f"{p.reconocimiento:g}"
        tf_b_bajas.value = ", ".join(p.bajas)
        refrescar_vista_bingo()

    def limpiar_formulario_bingo(e=None):
        tf_b_nombre.value = ""
        sw_b_seguro.value = False
        sw_b_muerto.value = False
        tf_b_ini.value = "0"
        tf_b_mis.value = "200"
        tf_b_rec.value = "50"
        tf_b_bajas.value = ""
        refrescar_vista_bingo()

    def refrescar_vista_bingo():
        txt_tabla_bingo.value = bingo.generar_txt()

        # 1. Botones rápidos de selección de Bajas
        fila_selectores_bajas.controls.clear()
        bajas_seleccionadas = obtener_lista_bajas_actual()
        autor_actual = tf_b_nombre.value.strip()

        for nom_p, p_obj in bingo.participantes.items():
            if nom_p == autor_actual:
                continue
            seleccionado = nom_p in bajas_seleccionadas
            etiqueta_estado = "💀" if p_obj.muerto else "Vivo"
            bg = COLOR_PRIMARY if seleccionado else ("#3f1d2b" if p_obj.muerto else "#1f2937")
            fila_selectores_bajas.controls.append(
                crear_boton(
                    f"{'✓ ' if seleccionado else ''}{nom_p} ({etiqueta_estado})",
                    on_click=lambda e, nv=nom_p: alternar_baja_en_formulario(nv),
                    bgcolor=bg,
                )
            )

        # 2. Tarjetas táctiles por participante
        lv_tarjetas_bingo.controls.clear()
        for nom_p, p in list(bingo.participantes.items()):
            def make_cargar(part=p):
                return lambda e: cargar_participante_en_formulario(part)

            def make_toggle_muerto(part=p):
                def _tm(e):
                    part.muerto = not part.muerto
                    autoguardar_todo()
                    refrescar_vista_bingo()
                return _tm

            def make_toggle_seguro(part=p):
                def _ts(e):
                    part.modo_seguro = not part.modo_seguro
                    autoguardar_todo()
                    refrescar_vista_bingo()
                return _ts

            def make_eliminar_p(nombre_borrar=nom_p):
                def _del(e):
                    bingo.eliminar_participante(nombre_borrar)
                    autoguardar_todo()
                    refrescar_vista_bingo()
                    mostrar_mensaje(f"Participante '{nombre_borrar}' eliminado del Bingo.")
                return _del

            estado_badges = (
                f"{'🛡️ Seguro' if p.modo_seguro else '⚔️ Letal'}  |  "
                f"{'💀 MUERTO' if p.muerto else '🟢 VIVO'}  |  "
                f"Ascenso: {p.ascenso}"
            )
            metricas = (
                f"Pre-Calc: {p.bingo_pre_calculo:.1f}  •  Botín: {p.recompensa_bajas:.1f}  •  "
                f"Bingo Final: {p.bingo_final:.1f}  •  Madaras: {p.madaras:.0f}  •  "
                f"Ryos: {p.ryos:.1f}  •  Tobis: {p.tobis:.2f}  •  Exp: {p.exp}"
            )
            bajas_str = f"Bajas reclamadas: {', '.join(p.bajas)}" if p.bajas else "Sin bajas reclamadas"

            lv_tarjetas_bingo.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(p.nombre, weight=ft.FontWeight.BOLD, size=14, color=COLOR_TEXT),
                                    ft.Text(estado_badges, size=12, color="#fbbf24" if not p.muerto else "#fca5a5"),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                wrap=True,
                            ),
                            ft.Text(metricas, size=12, color="#c4b5fd"),
                            ft.Text(bajas_str, size=12, color=COLOR_MUTED),
                            ft.Row(
                                [
                                    crear_boton("Editar", make_cargar(), bgcolor=COLOR_PRIMARY),
                                    crear_boton(
                                        "Marcar Vivo" if p.muerto else "Marcar Muerto",
                                        make_toggle_muerto(),
                                        bgcolor="#2d2246",
                                        color="#d8b4fe",
                                    ),
                                    crear_boton(
                                        "Quitar Seguro" if p.modo_seguro else "Poner Seguro",
                                        make_toggle_seguro(),
                                        bgcolor="#1f2937",
                                    ),
                                    crear_boton("Eliminar", make_eliminar_p(), bgcolor="#3f1d2b", color="#fca5a5"),
                                ],
                                spacing=8,
                                wrap=True,
                            ),
                        ],
                        spacing=6,
                    ),
                    padding=12,
                    bgcolor=COLOR_SURFACE,
                    border=borde_all(1, COLOR_BORDER),
                    border_radius=8,
                )
            )
        page.update()

    def guardar_participante_bingo(e):
        nom = tf_b_nombre.value.strip()
        if not nom:
            mostrar_mensaje("Escribe el nombre del personaje.", es_error=True)
            return
        try:
            b_ini = float(tf_b_ini.value.strip() or 0.0)
            b_mis = float(tf_b_mis.value.strip() or 0.0)
            rec = float(tf_b_rec.value.strip() or 50.0)
        except ValueError:
            mostrar_mensaje("Los valores de Bingo Inicial, Misión y Reconocimiento deben ser numéricos.", es_error=True)
            return

        bajas_lista = obtener_lista_bajas_actual()
        bingo.agregar_participante(
            ParticipanteBingo(nom, sw_b_seguro.value, b_ini, b_mis, sw_b_muerto.value, rec, bajas_lista)
        )
        autoguardar_todo()
        avisos_b = ValidadorModeracion.validar_bingo(bingo)
        refrescar_vista_bingo()
        if avisos_b:
            mostrar_mensaje("Aviso en Bingo: " + " | ".join(avisos_b), es_error=True)
        else:
            mostrar_mensaje(f"Participante '{nom}' actualizado y exportado a Bingo.txt.")

    def vaciar_bingo_click(e):
        bingo.participantes.clear()
        autoguardar_todo()
        limpiar_formulario_bingo()
        mostrar_mensaje("Tabla de Bingo vaciada para una nueva liquidación de combate.")

    def exportar_y_copiar_bingo_txt(e):
        autoguardar_todo()
        copiar_texto(bingo.generar_txt(), f"Bingo.txt ({biblioteca.ruta_txt_bingo.name})")

    tf_b_bajas.on_change = lambda e: refrescar_vista_bingo()

    vista_bingo = ft.Column(
        [
            crear_titulo_seccion("LIQUIDACIÓN DE COMBATE Y LIBRO BINGO", "Calculadora de Recompensas, Divisas, Ascensos y Exportador Bingo.txt"),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [tf_b_nombre, sw_b_seguro, sw_b_muerto, tf_b_ini, tf_b_mis, tf_b_rec],
                            wrap=True,
                            spacing=10,
                        ),
                        tf_b_bajas,
                        ft.Text("Toca un participante para añadirlo/quitarlo como Baja reclamada:", size=12, color=COLOR_MUTED),
                        fila_selectores_bajas,
                        ft.Row(
                            [
                                crear_boton("REGISTRAR / RECALCULAR", guardar_participante_bingo, bgcolor=COLOR_PRIMARY),
                                crear_boton("Limpiar Campos", limpiar_formulario_bingo, bgcolor="#2d2246", color="#d8b4fe"),
                                crear_boton("Guardar y Copiar Bingo.txt", exportar_y_copiar_bingo_txt, bgcolor=COLOR_OK),
                                crear_boton("Nueva Liquidación (Vaciar)", vaciar_bingo_click, bgcolor="#3f1d2b", color="#fca5a5"),
                            ],
                            wrap=True,
                            spacing=8,
                        ),
                    ],
                    spacing=10,
                ),
                padding=14,
                bgcolor=COLOR_SURFACE,
                border=borde_all(1, COLOR_BORDER),
                border_radius=8,
            ),
            ft.Text("TABLA DE LIQUIDACIÓN (BINGO.TXT)", weight=ft.FontWeight.BOLD, size=14, color=COLOR_TEXT),
            ft.Container(
                content=ft.Row([txt_tabla_bingo], scroll=ft.ScrollMode.AUTO),
                padding=12,
                bgcolor=COLOR_INPUT,
                border=borde_all(1, COLOR_BORDER),
                border_radius=8,
            ),
            ft.Text("PARTICIPANTES REGISTRADOS (TOCA PARA EDITAR O ALTERNAR ESTADO)", weight=ft.FontWeight.BOLD, size=14, color=COLOR_TEXT),
            lv_tarjetas_bingo,
        ],
        spacing=12,
    )

    # =================================================================
    # PESTAÑA 4: BIBLIOTECA (3 ARCHIVOS .TXT SEPARADOS + GESTIÓN JSON)
    # =================================================================
    lbl_rutas_archivos = ft.Text("", size=12, color="#67e8f9")
    lbl_estado_validacion = ft.Text("", size=12, color=COLOR_OK)

    dd_selector_txt = crear_dropdown(
        "ARCHIVO .TXT A PREVISUALIZAR / COPIAR",
        [
            ("Clanes.txt", "1. Clanes.txt (Árboles de Clan y Técnicas)"),
            ("Armas.txt", "2. Armas.txt (Catálogo de Objetos)"),
            ("Bingo.txt", "3. Bingo.txt (Liquidación de Combate)"),
        ],
        value="Clanes.txt",
        width=340,
    )
    sw_ocultar_vacios_export = ft.Switch(
        label="Ocultar nodos vacíos en Clanes.txt",
        value=True,
        active_color=COLOR_PRIMARY,
    )
    tf_vista_txt_archivo = ft.TextField(
        label="Contenido del archivo .TXT seleccionado",
        multiline=True,
        min_lines=18,
        max_lines=24,
        bgcolor=COLOR_INPUT,
        text_style=ft.TextStyle(font_family="monospace", size=12, color=COLOR_TEXT),
    )

    cache_textos = {"Clanes.txt": "", "Armas.txt": "", "Bingo.txt": ""}

    def actualizar_vista_biblioteca_textos(txt_c: str, txt_a: str, txt_b: str):
        cache_textos["Clanes.txt"] = txt_c
        cache_textos["Armas.txt"] = txt_a
        cache_textos["Bingo.txt"] = txt_b
        lbl_rutas_archivos.value = (
            f"Carpeta: {biblioteca.ruta_biblioteca.resolve()}\n"
            f"• {biblioteca.ruta_txt_clanes.name}   |   • {biblioteca.ruta_txt_armas.name}   |   "
            f"• {biblioteca.ruta_txt_bingo.name}   |   • {biblioteca.ruta_db_json.name}"
        )
        avisos = ValidadorModeracion.validar_todo(clanes, armas, bingo)
        if avisos:
            lbl_estado_validacion.value = f"[!] {len(avisos)} aviso(s) de moderación: " + " | ".join(avisos[:3])
            lbl_estado_validacion.color = COLOR_WARN
        else:
            lbl_estado_validacion.value = "[OK] Validación de Moderación: Todos los Clanes, Objetos y Bingo cumplen las reglas."
            lbl_estado_validacion.color = COLOR_OK

        archivo_sel = dd_selector_txt.value or "Clanes.txt"
        tf_vista_txt_archivo.label = f"Previsualización de {archivo_sel}"
        tf_vista_txt_archivo.value = cache_textos.get(archivo_sel, txt_c)

    def cambiar_archivo_txt_preview(e=None):
        estado_ui["ocultar_vacios_clan"] = sw_ocultar_vacios_export.value
        autoguardar_todo()
        page.update()

    def exportar_3_txt_click(e):
        estado_ui["ocultar_vacios_clan"] = sw_ocultar_vacios_export.value
        autoguardar_todo()
        mostrar_mensaje("¡Se han guardado Clanes.txt, Armas.txt, Bingo.txt y datos_guardados.json!")

    def restaurar_datos_ejemplo_click(e):
        nuevos_clanes, nuevas_armas, nuevo_bingo = construir_datos_ejemplo()
        clanes.clear()
        clanes.update(nuevos_clanes)
        armas.clear()
        armas.extend(nuevas_armas)
        bingo.participantes.clear()
        bingo.participantes.update(nuevo_bingo.participantes)

        estado_ui["clan_actual"] = next(iter(clanes.keys()))
        dd_clan_selector.options = [ft.dropdown.Option(key=k, text=k) for k in clanes.keys()]
        dd_clan_selector.value = estado_ui["clan_actual"]

        autoguardar_todo()
        cargar_nodo_en_formulario("001R")
        limpiar_formulario_arma()
        refrescar_lista_armas()
        refrescar_vista_bingo()
        mostrar_mensaje("Datos de ejemplo restaurados y guardados en los 3 archivos .TXT.")

    if _DROPDOWN_USA_ON_SELECT:
        dd_selector_txt.on_select = cambiar_archivo_txt_preview
    else:
        dd_selector_txt.on_change = cambiar_archivo_txt_preview
    sw_ocultar_vacios_export.on_change = cambiar_archivo_txt_preview

    vista_exportar = ft.Column(
        [
            crear_titulo_seccion("BIBLIOTECA .TXT Y AUTOGUARDADO", "Exportación separada en Clanes.txt, Armas.txt y Bingo.txt"),
            ft.Container(
                content=ft.Column(
                    [
                        lbl_rutas_archivos,
                        lbl_estado_validacion,
                        ft.Row(
                            [
                                dd_selector_txt,
                                sw_ocultar_vacios_export,
                            ],
                            wrap=True,
                            spacing=12,
                        ),
                        ft.Row(
                            [
                                crear_boton("Guardar los 3 .TXT Ahora", exportar_3_txt_click, bgcolor=COLOR_OK),
                                crear_boton(
                                    "Copiar .TXT Seleccionado",
                                    lambda e: copiar_texto(tf_vista_txt_archivo.value, dd_selector_txt.value or "Archivo TXT"),
                                    bgcolor=COLOR_PRIMARY,
                                ),
                                crear_boton("Copiar Clanes.txt", lambda e: copiar_texto(cache_textos["Clanes.txt"], "Clanes.txt"), bgcolor="#2d2246", color="#d8b4fe"),
                                crear_boton("Copiar Armas.txt", lambda e: copiar_texto(cache_textos["Armas.txt"], "Armas.txt"), bgcolor="#2d2246", color="#d8b4fe"),
                                crear_boton("Copiar Bingo.txt", lambda e: copiar_texto(cache_textos["Bingo.txt"], "Bingo.txt"), bgcolor="#2d2246", color="#d8b4fe"),
                                crear_boton("Restaurar Datos de Ejemplo", restaurar_datos_ejemplo_click, bgcolor="#3f1d2b", color="#fca5a5"),
                            ],
                            wrap=True,
                            spacing=8,
                        ),
                    ],
                    spacing=10,
                ),
                padding=14,
                bgcolor=COLOR_SURFACE,
                border=borde_all(1, COLOR_BORDER),
                border_radius=8,
            ),
            tf_vista_txt_archivo,
        ],
        spacing=12,
    )

    # =================================================================
    # NAVEGACIÓN SUPERIOR COMPATIBLE CON TODAS LAS VERSIONES DE FLET
    # =================================================================
    vistas = [vista_clanes, vista_armas, vista_bingo, vista_exportar]
    nombres_tabs = ["1. CREAR TÉCNICA", "2. OBJETOS", "3. LIBRO BINGO", "4. BIBLIOTECA .TXT"]
    botones_nav = []
    contenedor_principal = ft.Container(content=vista_clanes, padding=padding_only(top=8))

    def seleccionar_tab(indice: int):
        contenedor_principal.content = vistas[indice]
        for i, btn in enumerate(botones_nav):
            activo = (i == indice)
            btn.bgcolor = COLOR_PRIMARY if activo else COLOR_SURFACE
        page.update()

    for idx_t, titulo_tab in enumerate(nombres_tabs):
        b = crear_boton(
            titulo_tab,
            on_click=lambda e, i=idx_t: seleccionar_tab(i),
            bgcolor=COLOR_PRIMARY if idx_t == 0 else COLOR_SURFACE,
            color="white",
        )
        botones_nav.append(b)

    barra_navegacion = ft.Container(
        content=ft.Row(botones_nav, wrap=True, spacing=8),
        padding=10,
        bgcolor="#140f21",
        border=borde_all(1, COLOR_BORDER),
        border_radius=8,
    )

    # Inicialización de vistas y primer guardado de los 3 archivos .txt
    cargar_nodo_en_formulario("001R")
    refrescar_lista_armas()
    actualizar_preview_arma()
    refrescar_vista_bingo()
    autoguardar_todo()

    page.add(barra_navegacion, contenedor_principal)


if __name__ == "__main__":
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(target=main)