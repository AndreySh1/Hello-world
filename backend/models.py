from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class GameComplex(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None

    parts: List["ComplexPart"] = Relationship(back_populates="game_complex")


class Part(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    unit: Optional[str] = None

    complexes: List["ComplexPart"] = Relationship(back_populates="part")


class ComplexPart(SQLModel, table=True):
    game_complex_id: int = Field(foreign_key="gamecomplex.id", primary_key=True)
    part_id: int = Field(foreign_key="part.id", primary_key=True)
    quantity: int = Field(default=1, ge=0)

    game_complex: GameComplex = Relationship(back_populates="parts")
    part: Part = Relationship(back_populates="complexes")