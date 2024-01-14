import dataclasses
import datetime
import enum


@dataclasses.dataclass
class Client:
    name: str
    email: str


@dataclasses.dataclass
class Company:
    name: str
    email: str


class Unit(enum.Enum):
    PCS = "PCS"
    HOURLY = "hourly"


@dataclasses.dataclass
class LineItem:
    description: str
    qty: float
    unit: Unit
    price: float
    total: float


@dataclasses.dataclass
class Currency:
    symbol: str
    text: str


@dataclasses.dataclass
class Invoice:
    company: Company
    client: Client
    number: str
    date: datetime.date
    line_items: list[LineItem]
    total: float
    currency: Currency


