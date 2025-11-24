"""Einfache Kommandozeilen-App für Handwerksbetriebe.

Die Anwendung speichert Projekte, Aufgaben und Materialbedarf in einer
JSON-Datei (standardmäßig ``handwerk_data.json``) und bietet Befehle für
häufige Arbeitsabläufe.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

DATA_FILE = Path("handwerk_data.json")
DEFAULT_DATA: Dict[str, list] = {"projects": [], "inventory": []}


@dataclass
class Task:
    title: str
    due_date: Optional[str] = None
    status: str = "offen"

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "title": self.title,
            "due_date": self.due_date,
            "status": self.status,
        }


@dataclass
class Material:
    name: str
    quantity: float
    unit: str = "Stk"

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
        }


@dataclass
class Project:
    id: int
    name: str
    customer: str
    address: Optional[str] = None
    due_date: Optional[str] = None
    status: str = "offen"
    notes: Optional[str] = None
    tasks: List[Dict[str, Optional[str]]] = field(default_factory=list)
    materials: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "customer": self.customer,
            "address": self.address,
            "due_date": self.due_date,
            "status": self.status,
            "notes": self.notes,
            "tasks": self.tasks,
            "materials": self.materials,
        }


def load_data() -> Dict[str, list]:
    if not DATA_FILE.exists():
        return DEFAULT_DATA.copy()
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_data(data: Dict[str, list]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def next_project_id(data: Dict[str, list]) -> int:
    return max((p.get("id", 0) for p in data.get("projects", [])), default=0) + 1


def find_project(data: Dict[str, list], project_id: int) -> Optional[Dict[str, object]]:
    return next((p for p in data.get("projects", []) if p.get("id") == project_id), None)


def cmd_project_add(args: argparse.Namespace) -> None:
    data = load_data()
    new_project = Project(
        id=next_project_id(data),
        name=args.name,
        customer=args.customer,
        address=args.address,
        due_date=args.due_date,
        status=args.status,
        notes=args.notes,
    )
    data.setdefault("projects", []).append(new_project.to_dict())
    save_data(data)
    print(f"Projekt {new_project.id} angelegt: {new_project.name} für {new_project.customer}")


def cmd_project_list(args: argparse.Namespace) -> None:
    data = load_data()
    projects = data.get("projects", [])
    if args.status:
        projects = [p for p in projects if p.get("status") == args.status]

    if not projects:
        print("Keine Projekte gefunden.")
        return

    print("ID  | Projekt                     | Kunde               | Status  | Termin")
    print("-" * 76)
    for proj in projects:
        print(
            f"{proj.get('id'):>3} | "
            f"{proj.get('name','')[:25]:<25} | "
            f"{proj.get('customer','')[:18]:<18} | "
            f"{proj.get('status',''):7} | "
            f"{proj.get('due_date') or '-'}"
        )


def cmd_project_detail(args: argparse.Namespace) -> None:
    data = load_data()
    project = find_project(data, args.project_id)
    if not project:
        print(f"Projekt {args.project_id} nicht gefunden.")
        return

    print(f"Projekt {project['id']}: {project['name']}")
    print(f"Kunde: {project['customer']}")
    if project.get("address"):
        print(f"Adresse: {project['address']}")
    if project.get("due_date"):
        print(f"Fällig am: {project['due_date']}")
    print(f"Status: {project.get('status', '-')}")
    if project.get("notes"):
        print(f"Notizen: {project['notes']}")

    tasks = project.get("tasks", [])
    if tasks:
        print("\nAufgaben:")
        for idx, task in enumerate(tasks, start=1):
            due = task.get("due_date") or "-"
            print(f" {idx:>2}. [{task.get('status','-')}] {task.get('title')} (bis {due})")
    else:
        print("\nKeine Aufgaben erfasst.")

    materials = project.get("materials", [])
    if materials:
        print("\nMaterialbedarf:")
        for mat in materials:
            print(f" - {mat.get('name')} ({mat.get('quantity')} {mat.get('unit')})")
    else:
        print("\nKein Material hinterlegt.")


def cmd_task_add(args: argparse.Namespace) -> None:
    data = load_data()
    project = find_project(data, args.project_id)
    if not project:
        print(f"Projekt {args.project_id} nicht gefunden.")
        return

    task = Task(title=args.title, due_date=args.due_date, status=args.status)
    project.setdefault("tasks", []).append(task.to_dict())
    save_data(data)
    print(f"Aufgabe für Projekt {project['id']} gespeichert: {task.title}")


def cmd_material_add(args: argparse.Namespace) -> None:
    data = load_data()
    material = Material(name=args.name, quantity=args.quantity, unit=args.unit)

    if args.project_id:
        project = find_project(data, args.project_id)
        if not project:
            print(f"Projekt {args.project_id} nicht gefunden.")
            return
        project.setdefault("materials", []).append(material.to_dict())
        context = f"Projekt {project['id']}"
    else:
        data.setdefault("inventory", []).append(material.to_dict())
        context = "Lagerbestand"

    save_data(data)
    print(f"Material hinzugefügt zu {context}: {material.quantity} {material.unit} {material.name}")


def cmd_inventory_list(_: argparse.Namespace) -> None:
    data = load_data()
    inventory = data.get("inventory", [])
    if not inventory:
        print("Kein Lagerbestand erfasst.")
        return

    print("Lagerbestand:")
    for item in inventory:
        print(f" - {item.get('name')} ({item.get('quantity')} {item.get('unit')})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Werkzeug für Handwerksbetriebe")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Projektbefehle
    project_parser = subparsers.add_parser("project", help="Projekte verwalten")
    project_sub = project_parser.add_subparsers(dest="project_command", required=True)

    project_add = project_sub.add_parser("add", help="Neues Projekt anlegen")
    project_add.add_argument("name", help="Name des Projekts")
    project_add.add_argument("customer", help="Auftraggeber")
    project_add.add_argument("--address", help="Adresse der Baustelle")
    project_add.add_argument("--due-date", help="Geplanter Abschlusstermin (YYYY-MM-DD)")
    project_add.add_argument("--status", default="offen", help="Status, z.B. offen oder erledigt")
    project_add.add_argument("--notes", help="Kurznotiz zum Projekt")
    project_add.set_defaults(func=cmd_project_add)

    project_list = project_sub.add_parser("list", help="Projekte anzeigen")
    project_list.add_argument("--status", help="Nach Status filtern")
    project_list.set_defaults(func=cmd_project_list)

    project_detail = project_sub.add_parser("detail", help="Details zu einem Projekt")
    project_detail.add_argument("project_id", type=int, help="Projekt-ID")
    project_detail.set_defaults(func=cmd_project_detail)

    # Aufgaben
    task_parser = subparsers.add_parser("task", help="Aufgaben verwalten")
    task_sub = task_parser.add_subparsers(dest="task_command", required=True)

    task_add = task_sub.add_parser("add", help="Aufgabe zu Projekt hinzufügen")
    task_add.add_argument("project_id", type=int, help="Projekt-ID")
    task_add.add_argument("title", help="Aufgabenbeschreibung")
    task_add.add_argument("--due-date", help="Fälligkeitsdatum (YYYY-MM-DD)")
    task_add.add_argument("--status", default="offen", help="Status, z.B. offen oder erledigt")
    task_add.set_defaults(func=cmd_task_add)

    # Material
    material_parser = subparsers.add_parser("material", help="Materialbedarf erfassen")
    material_sub = material_parser.add_subparsers(dest="material_command", required=True)

    material_add = material_sub.add_parser("add", help="Material hinzufügen")
    material_add.add_argument("name", help="Materialbezeichnung")
    material_add.add_argument("quantity", type=float, help="Menge")
    material_add.add_argument("--unit", default="Stk", help="Einheit (z.B. Stk, m, kg)")
    material_add.add_argument("--project-id", type=int, help="Projekt-ID für projektbezogenen Bedarf")
    material_add.set_defaults(func=cmd_material_add)

    # Lagerbestand anzeigen
    inventory_parser = subparsers.add_parser("inventory", help="Lagerbestand anzeigen")
    inventory_sub = inventory_parser.add_subparsers(dest="inventory_command", required=True)
    inventory_list = inventory_sub.add_parser("list", help="Lagerbestand listen")
    inventory_list.set_defaults(func=cmd_inventory_list)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
