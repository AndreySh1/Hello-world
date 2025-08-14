from typing import List, Dict

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlmodel import Session, select

from .db import init_db, get_session, engine
from .models import GameComplex, Part, ComplexPart


class ComplexCreate(BaseModel):
    name: str
    description: str | None = None


class PartCreate(BaseModel):
    name: str
    unit: str | None = None


class AddPartToComplex(BaseModel):
    part_id: int
    quantity: int


class Selection(BaseModel):
    complex_id: int
    count: int


class CountRequest(BaseModel):
    selections: List[Selection]


app = FastAPI(title="Complex Parts Counter")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_if_empty() -> None:
    with Session(engine) as session:
        any_part = session.exec(select(Part)).first()
        any_complex = session.exec(select(GameComplex)).first()
        if any_part or any_complex:
            return
        bolt = Part(name="Болт", unit="шт")
        nut = Part(name="Гайка", unit="шт")
        panel = Part(name="Панель", unit="шт")
        rope = Part(name="Канат", unit="м")
        session.add_all([bolt, nut, panel, rope])
        session.commit()
        session.refresh(bolt); session.refresh(nut); session.refresh(panel); session.refresh(rope)

        c1 = GameComplex(name="Площадка A", description="Базовый набор")
        c2 = GameComplex(name="Площадка B", description="Расширенный набор")
        session.add_all([c1, c2])
        session.commit()
        session.refresh(c1); session.refresh(c2)

        session.add_all([
            ComplexPart(game_complex_id=c1.id, part_id=bolt.id, quantity=40),
            ComplexPart(game_complex_id=c1.id, part_id=nut.id, quantity=40),
            ComplexPart(game_complex_id=c1.id, part_id=panel.id, quantity=10),
            ComplexPart(game_complex_id=c2.id, part_id=bolt.id, quantity=80),
            ComplexPart(game_complex_id=c2.id, part_id=nut.id, quantity=80),
            ComplexPart(game_complex_id=c2.id, part_id=panel.id, quantity=20),
            ComplexPart(game_complex_id=c2.id, part_id=rope.id, quantity=15),
        ])
        session.commit()


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    seed_if_empty()


# ---------- Helpers ----------

def complex_to_dict(gc: GameComplex, session: Session) -> Dict:
    link_rows = session.exec(
        select(ComplexPart).where(ComplexPart.game_complex_id == gc.id)
    ).all()
    parts: List[Dict] = []
    for link in link_rows:
        part = session.get(Part, link.part_id)
        if part is None:
            continue
        parts.append({
            "part_id": part.id,
            "name": part.name,
            "unit": part.unit,
            "quantity": link.quantity,
        })
    return {
        "id": gc.id,
        "name": gc.name,
        "description": gc.description,
        "parts": parts,
    }


# ---------- Parts ----------

@app.get("/api/parts")
def list_parts(session: Session = Depends(get_session)) -> List[Dict]:
    parts = session.exec(select(Part).order_by(Part.name)).all()
    return [
        {"id": p.id, "name": p.name, "unit": p.unit}
        for p in parts
    ]


@app.post("/api/parts", status_code=201)
def create_part(data: PartCreate, session: Session = Depends(get_session)) -> Dict:
    exists = session.exec(select(Part).where(Part.name == data.name)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Деталь с таким именем уже существует")
    part = Part(name=data.name, unit=data.unit)
    session.add(part)
    session.commit()
    session.refresh(part)
    return {"id": part.id, "name": part.name, "unit": part.unit}


# ---------- Complexes ----------

@app.get("/api/complexes")
def list_complexes(session: Session = Depends(get_session)) -> List[Dict]:
    complexes = session.exec(select(GameComplex).order_by(GameComplex.name)).all()
    return [complex_to_dict(gc, session) for gc in complexes]


@app.post("/api/complexes", status_code=201)
def create_complex(data: ComplexCreate, session: Session = Depends(get_session)) -> Dict:
    gc = GameComplex(name=data.name, description=data.description)
    session.add(gc)
    session.commit()
    session.refresh(gc)
    return complex_to_dict(gc, session)


@app.get("/api/complexes/{complex_id}")
def get_complex(complex_id: int, session: Session = Depends(get_session)) -> Dict:
    gc = session.get(GameComplex, complex_id)
    if gc is None:
        raise HTTPException(status_code=404, detail="Комплекс не найден")
    return complex_to_dict(gc, session)


@app.post("/api/complexes/{complex_id}/parts", status_code=201)
def add_part_to_complex(
    complex_id: int,
    data: AddPartToComplex,
    session: Session = Depends(get_session),
) -> Dict:
    gc = session.get(GameComplex, complex_id)
    if gc is None:
        raise HTTPException(status_code=404, detail="Комплекс не найден")
    part = session.get(Part, data.part_id)
    if part is None:
        raise HTTPException(status_code=404, detail="Деталь не найдена")

    link = session.get(ComplexPart, (complex_id, data.part_id))
    if link is None:
        link = ComplexPart(game_complex_id=complex_id, part_id=data.part_id, quantity=max(0, data.quantity))
        session.add(link)
    else:
        link.quantity = max(0, data.quantity)

    session.commit()
    return complex_to_dict(gc, session)


# ---------- Counting ----------

@app.post("/api/count")
def count_parts(body: CountRequest, session: Session = Depends(get_session)) -> Dict:
    totals: Dict[int, Dict] = {}
    for sel in body.selections:
        if sel.count <= 0:
            continue
        gc = session.get(GameComplex, sel.complex_id)
        if gc is None:
            raise HTTPException(status_code=404, detail=f"Комплекс {sel.complex_id} не найден")
        links = session.exec(
            select(ComplexPart).where(ComplexPart.game_complex_id == sel.complex_id)
        ).all()
        for link in links:
            part = session.get(Part, link.part_id)
            if part is None:
                continue
            add_qty = link.quantity * sel.count
            if link.part_id not in totals:
                totals[link.part_id] = {
                    "part_id": link.part_id,
                    "name": part.name,
                    "unit": part.unit,
                    "total_quantity": add_qty,
                }
            else:
                totals[link.part_id]["total_quantity"] += add_qty

    result = list(totals.values())
    result.sort(key=lambda x: x["name"])
    return {"items": result}


# ---------- Static frontend ----------

# Mount after API routes to avoid shadowing
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")