from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
SOURCE_CSV = ROOT_DIR / "dados_vendas_50k.csv"
OUTPUT_JSON = ROOT_DIR / "docs" / "data" / "sales_dashboard.json"


def round_number(value: Any, digits: int = 2) -> float:
    return round(float(value), digits)


def to_records(frame: pd.DataFrame, digits: int = 2) -> list[dict[str, Any]]:
    data = frame.copy()
    for column in data.columns:
        if pd.api.types.is_numeric_dtype(data[column]):
            data[column] = data[column].astype(float).round(digits)
    return data.to_dict(orient="records")


def build_payload(frame: pd.DataFrame) -> dict[str, Any]:
    sales = frame.copy()
    sales["data_venda"] = pd.to_datetime(sales["data_venda"])
    sales["mes"] = sales["data_venda"].dt.to_period("M").astype(str)
    sales["trimestre"] = sales["data_venda"].dt.to_period("Q").astype(str)

    total_revenue = sales["receita"].sum()
    total_profit = sales["lucro"].sum()
    total_orders = len(sales)
    average_ticket = sales["receita"].mean()
    average_items = sales["qtd_vendida"].mean()
    profit_margin_pct = (total_profit / total_revenue) * 100 if total_revenue else 0

    monthly = (
        sales.groupby("mes", as_index=False)
        .agg(
            receita=("receita", "sum"),
            lucro=("lucro", "sum"),
            pedidos=("mes", "size"),
            itens=("qtd_vendida", "sum"),
        )
        .sort_values("mes")
    )
    monthly["ticket_medio"] = monthly["receita"] / monthly["pedidos"]

    quarterly = (
        sales.groupby("trimestre", as_index=False)
        .agg(receita=("receita", "sum"), lucro=("lucro", "sum"))
        .sort_values("trimestre")
    )

    categories = (
        sales.groupby("categoria", as_index=False)
        .agg(
            receita=("receita", "sum"),
            lucro=("lucro", "sum"),
            volume=("qtd_vendida", "sum"),
            pedidos=("categoria", "size"),
        )
        .sort_values(["receita", "lucro"], ascending=False)
    )
    categories["margem_pct"] = (categories["lucro"] / categories["receita"]) * 100
    categories["ticket_medio"] = categories["receita"] / categories["pedidos"]

    regions = (
        sales.groupby("regiao", as_index=False)
        .agg(
            receita=("receita", "sum"),
            lucro=("lucro", "sum"),
            pedidos=("regiao", "size"),
            volume=("qtd_vendida", "sum"),
        )
        .sort_values(["receita", "lucro"], ascending=False)
    )
    regions["margem_pct"] = (regions["lucro"] / regions["receita"]) * 100

    products = (
        sales.groupby(["produto", "categoria"], as_index=False)
        .agg(
            receita=("receita", "sum"),
            lucro=("lucro", "sum"),
            volume=("qtd_vendida", "sum"),
            pedidos=("produto", "size"),
        )
        .sort_values(["receita", "lucro"], ascending=False)
        .head(10)
    )
    products["margem_pct"] = (products["lucro"] / products["receita"]) * 100

    sellers = (
        sales.groupby("nome_vendedor", as_index=False)
        .agg(
            receita=("receita", "sum"),
            lucro=("lucro", "sum"),
            pedidos=("nome_vendedor", "size"),
            volume=("qtd_vendida", "sum"),
        )
        .sort_values(["receita", "lucro"], ascending=False)
        .head(10)
    )
    sellers["ticket_medio"] = sellers["receita"] / sellers["pedidos"]

    best_month = monthly.sort_values("receita", ascending=False).iloc[0]
    top_category = categories.iloc[0]
    highest_margin_category = categories.sort_values(["margem_pct", "receita"], ascending=False).iloc[0]
    lowest_margin_category = categories.sort_values(["margem_pct", "receita"], ascending=[True, False]).iloc[0]
    top_region = regions.iloc[0]
    top_seller = sellers.iloc[0]

    if len(monthly) >= 6:
        recent_average = monthly.tail(3)["receita"].mean()
        previous_average = monthly.iloc[-6:-3]["receita"].mean()
        revenue_trend_pct = ((recent_average / previous_average) - 1) * 100 if previous_average else 0
    else:
        revenue_trend_pct = 0

    highlights = [
        {
            "title": "Best revenue month",
            "metric": best_month["mes"],
            "description": (
                f"Revenue peaked at R$ {best_month['receita']:,.0f} and profit reached R$ {best_month['lucro']:,.0f}."
            ),
        },
        {
            "title": "Largest revenue driver",
            "metric": top_category["categoria"],
            "description": (
                f"This category generated R$ {top_category['receita']:,.0f}, representing "
                f"{(top_category['receita'] / total_revenue) * 100:.1f}% of total revenue."
            ),
        },
        {
            "title": "Highest commercial productivity",
            "metric": top_seller["nome_vendedor"],
            "description": (
                f"Top seller revenue reached R$ {top_seller['receita']:,.0f} with an average ticket of "
                f"R$ {top_seller['ticket_medio']:,.0f}."
            ),
        },
    ]

    recommendations = [
        (
            f"Increase commercial focus on {top_category['categoria']}, the highest-revenue category, and protect its "
            f"current {top_category['margem_pct']:.1f}% margin through pricing discipline."
        ),
        (
            f"Review cost structure and discount policy for {lowest_margin_category['categoria']}, whose margin of "
            f"{lowest_margin_category['margem_pct']:.1f}% is below the portfolio average of {profit_margin_pct:.1f}%."
        ),
        (
            f"Replicate the sales routines of {top_seller['nome_vendedor']} and benchmark the approach in {top_region['regiao']}, "
            f"the region with the strongest revenue concentration."
        ),
        (
            f"Monitor the latest rolling three-month trend of {revenue_trend_pct:.1f}% to react faster to demand shifts and "
            f"inventory planning changes."
        ),
    ]

    payload = {
        "project": {
            "title": "Data Analysis and Business Intelligence Dashboard",
            "subtitle": "Turning raw sales records into KPI monitoring, commercial insights and executive storytelling.",
            "description": (
                "This portfolio project organizes transactional sales data into a lightweight BI dashboard focused on "
                "revenue, profit, category mix, regional performance and salesperson productivity."
            ),
            "scope": [
                "50,000 simulated sales transactions",
                "Time series covering 2023 and 2024",
                "Analysis by category, region, product and seller",
                "Static site deployment ready for GitHub Pages",
            ],
        },
        "meta": {
                "generated_at": pd.Timestamp.now(tz="UTC").isoformat(),
            "records": int(total_orders),
            "period_start": sales["data_venda"].min().strftime("%Y-%m-%d"),
            "period_end": sales["data_venda"].max().strftime("%Y-%m-%d"),
            "products": int(sales["id_produto"].nunique()),
            "sellers": int(sales["id_vendedor"].nunique()),
        },
        "kpis": {
            "receita_total": round_number(total_revenue),
            "lucro_total": round_number(total_profit),
            "pedidos": int(total_orders),
            "ticket_medio": round_number(average_ticket),
            "itens_medios": round_number(average_items),
            "margem_lucro_pct": round_number(profit_margin_pct),
        },
        "highlights": highlights,
        "recommendations": recommendations,
        "series": {
            "monthly_performance": to_records(monthly),
            "quarterly_performance": to_records(quarterly),
        },
        "tables": {
            "category_performance": to_records(categories),
            "region_performance": to_records(regions),
            "top_products": to_records(products),
            "top_sellers": to_records(sellers),
            "highest_margin_category": {
                "categoria": highest_margin_category["categoria"],
                "margem_pct": round_number(highest_margin_category["margem_pct"]),
            },
        },
    }
    return payload


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"Sales dataset not found: {SOURCE_CSV}")

    sales = pd.read_csv(SOURCE_CSV)
    payload = build_payload(sales)

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Dashboard data generated at {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
