"""Week 02 case: enterprise data model and business object mapping."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Field:
    name: str
    dtype: str
    nullable: bool = False
    description: str = ""


@dataclass(frozen=True)
class Entity:
    name: str
    primary_key: str
    fields: list[Field]
    description: str


@dataclass(frozen=True)
class Relationship:
    source: str
    target: str
    cardinality: str
    foreign_key: str
    description: str


ENTITIES = [
    Entity(
        name="customers",
        primary_key="customer_id",
        description="客户维度表，描述客户身份、地区、渠道与等级。",
        fields=[
            Field("customer_id", "TEXT", description="客户唯一标识"),
            Field("customer_name", "TEXT", description="客户名称"),
            Field("region", "TEXT", description="地区"),
            Field("segment", "TEXT", description="客户分层"),
        ],
    ),
    Entity(
        name="products",
        primary_key="product_id",
        description="产品维度表，描述产品类别、价格与成本。",
        fields=[
            Field("product_id", "TEXT", description="产品唯一标识"),
            Field("product_name", "TEXT", description="产品名称"),
            Field("category", "TEXT", description="产品类别"),
            Field("unit_price", "DOUBLE", description="标准售价"),
            Field("unit_cost", "DOUBLE", description="单位成本"),
        ],
    ),
    Entity(
        name="orders",
        primary_key="order_id",
        description="订单事实表，记录客户购买产品的交易事件。",
        fields=[
            Field("order_id", "TEXT", description="订单唯一标识"),
            Field("customer_id", "TEXT", description="客户外键"),
            Field("product_id", "TEXT", description="产品外键"),
            Field("order_date", "DATE", description="下单日期"),
            Field("quantity", "INTEGER", description="购买数量"),
            Field("promised_date", "DATE", description="承诺交付日期"),
            Field("actual_date", "DATE", nullable=True, description="实际交付日期"),
        ],
    ),
    Entity(
        name="inventory",
        primary_key="inventory_id",
        description="库存快照表，记录产品在仓库中的状态。",
        fields=[
            Field("inventory_id", "TEXT", description="库存记录唯一标识"),
            Field("product_id", "TEXT", description="产品外键"),
            Field("warehouse_id", "TEXT", description="仓库标识"),
            Field("snapshot_date", "DATE", description="库存快照日期"),
            Field("on_hand_qty", "INTEGER", description="现有库存"),
        ],
    ),
]

RELATIONSHIPS = [
    Relationship("customers", "orders", "1:N", "orders.customer_id", "一个客户可以产生多个订单。"),
    Relationship("products", "orders", "1:N", "orders.product_id", "一个产品可以出现在多个订单中。"),
    Relationship("products", "inventory", "1:N", "inventory.product_id", "一个产品可在多个仓库形成库存记录。"),
]


def create_table_sql(entity: Entity) -> str:
    lines = []
    for field in entity.fields:
        null_clause = "" if not field.nullable else " NULL"
        pk_clause = " PRIMARY KEY" if field.name == entity.primary_key else ""
        lines.append(f"  {field.name} {field.dtype}{pk_clause}{null_clause}")
    return f"CREATE TABLE {entity.name} (\n" + ",\n".join(lines) + "\n);"


def markdown_data_dictionary() -> str:
    rows = ["| 表 | 字段 | 类型 | 主键 | 允许缺失 | 含义 |", "|---|---|---|---|---|---|"]
    for entity in ENTITIES:
        for field in entity.fields:
            rows.append(
                "| "
                + " | ".join(
                    [
                        entity.name,
                        field.name,
                        field.dtype,
                        "是" if field.name == entity.primary_key else "否",
                        "是" if field.nullable else "否",
                        field.description,
                    ]
                )
                + " |"
            )
    return "\n".join(rows)


def business_object_mapping() -> dict[str, list[str]]:
    return {
        "Customer": ["customers"],
        "Product": ["products"],
        "Order": ["orders", "customers", "products"],
        "InventoryPosition": ["inventory", "products"],
    }


if __name__ == "__main__":
    print("-- DDL")
    for entity in ENTITIES:
        print(create_table_sql(entity))
        print()
    print("-- Data Dictionary")
    print(markdown_data_dictionary())
    print()
    print("-- Business Object Mapping")
    for object_name, tables in business_object_mapping().items():
        print(f"{object_name}: {', '.join(tables)}")

