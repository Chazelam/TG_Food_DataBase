from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url = "sqlite+aiosqlite:///db.sqlite3")
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class Shops(Base):
    __tablename__ = "shops"
    id: Mapped[int] = mapped_column(primary_key = True)
    shop_name: Mapped[str] = mapped_column(String(25))

class Ingredients(Base):
    __tablename__ = "ingredients"
    id: Mapped[int] = mapped_column(primary_key = True)

    ingredient_name: Mapped[str] = mapped_column(String(25))
    shop: Mapped[int] = mapped_column(ForeignKey("shops.id"))

    price: Mapped[str] = mapped_column(String(25))
    weight: Mapped[str] = mapped_column(String(25))
    relation_to_water: Mapped[str] = mapped_column(String(25))
    calories: Mapped[str] = mapped_column(String(25))
    proteins: Mapped[str] = mapped_column(String(25))
    fats: Mapped[str] = mapped_column(String(25))
    carbs: Mapped[str] = mapped_column(String(25))

class Standalone(Base):
    __tablename__ = "standalone"
    id: Mapped[int] = mapped_column(primary_key = True)

    ingredient_name: Mapped[str] = mapped_column(String(25))
    shop: Mapped[int] = mapped_column(ForeignKey("shops.id"))

    price: Mapped[str] = mapped_column(String(25))
    weight: Mapped[str] = mapped_column(String(25))
    calories: Mapped[str] = mapped_column(String(25))
    proteins: Mapped[str] = mapped_column(String(25))
    fats: Mapped[str] = mapped_column(String(25))
    carbs: Mapped[str] = mapped_column(String(25))

class Recipes(Base):
    __tablename__ = "recipes"
    id: Mapped[int] = mapped_column(primary_key = True)

    recipe_name: Mapped[str] = mapped_column(String(25))
    ingredient: Mapped[str] = mapped_column(String(25))
    weight: Mapped[str] = mapped_column(String(25))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)