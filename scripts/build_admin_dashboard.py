from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
SOURCE_CSV = ROOT_DIR / "dados_processos_50k.csv"
OUTPUT_JSON = ROOT_DIR / "docs" / "data" / "admin_dashboard.json"


def to_records(frame: pd.DataFrame, digits: int = 2) -> list[dict[str, Any]]:
    result = frame.copy()
    for column in result.columns:
        if pd.api.types.is_numeric_dtype(result[column]):
            result[column] = result[column].astype(float).round(digits)
    return result.to_dict(orient="records")


def safe_pct(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return (numerator / denominator) * 100


def build_payload(frame: pd.DataFrame) -> dict[str, Any]:
    proc = frame.copy()
    proc["data_solicitacao"] = pd.to_datetime(proc["data_solicitacao"])
    proc["data_aprovacao"] = pd.to_datetime(proc["data_aprovacao"], errors="coerce")
    proc["valor"] = pd.to_numeric(proc["valor"], errors="coerce").fillna(0)
    proc["dias_para_aprovacao"] = pd.to_numeric(proc["dias_para_aprovacao"], errors="coerce")

    proc["mes"] = proc["data_solicitacao"].dt.to_period("M").astype(str)
    proc["is_aprovado"] = proc["status"].eq("Aprovado")
    proc["is_pendente"] = proc["status"].eq("Pendente")
    proc["is_rejeitado_cancelado"] = proc["status"].isin(["Rejeitado", "Cancelado"])
    proc["valor_aprovado"] = proc["valor"].where(proc["is_aprovado"], 0)
    proc["dias_aprovado"] = proc["dias_para_aprovacao"].where(proc["is_aprovado"])

    total_processos = int(len(proc))
    total_valor = float(proc["valor"].sum())
    aprovados = int(proc["is_aprovado"].sum())
    pendentes = int(proc["is_pendente"].sum())
    rejeitados_cancelados = int(proc["is_rejeitado_cancelado"].sum())
    valor_aprovado = float(proc["valor_aprovado"].sum())
    taxa_aprovacao_pct = safe_pct(aprovados, total_processos)
    tempo_medio_aprovacao = float(proc["dias_aprovado"].mean()) if aprovados else 0

    monthly = (
        proc.groupby("mes", as_index=False)
        .agg(
            processos=("id_contrato", "size"),
            valor_total=("valor", "sum"),
            valor_aprovado=("valor_aprovado", "sum"),
            aprovados=("is_aprovado", "sum"),
            pendentes=("is_pendente", "sum"),
            rejeitados_cancelados=("is_rejeitado_cancelado", "sum"),
            tempo_medio_aprovacao_dias=("dias_aprovado", "mean"),
        )
        .sort_values("mes")
    )
    monthly["taxa_aprovacao_pct"] = monthly.apply(
        lambda row: safe_pct(row["aprovados"], row["processos"]), axis=1
    )

    status_distribution = (
        proc.groupby("status", as_index=False)
        .agg(quantidade=("status", "size"), valor_total=("valor", "sum"))
        .sort_values("quantidade", ascending=False)
    )

    departments = (
        proc.groupby("departamento", as_index=False)
        .agg(
            processos=("id_contrato", "size"),
            valor_total=("valor", "sum"),
            valor_aprovado=("valor_aprovado", "sum"),
            aprovados=("is_aprovado", "sum"),
            pendentes=("is_pendente", "sum"),
            rejeitados_cancelados=("is_rejeitado_cancelado", "sum"),
            tempo_medio_aprovacao_dias=("dias_aprovado", "mean"),
        )
        .sort_values("valor_total", ascending=False)
    )
    departments["taxa_aprovacao_pct"] = departments.apply(
        lambda row: safe_pct(row["aprovados"], row["processos"]), axis=1
    )

    contract_types = (
        proc.groupby("tipo_contrato", as_index=False)
        .agg(
            processos=("id_contrato", "size"),
            valor_total=("valor", "sum"),
            valor_aprovado=("valor_aprovado", "sum"),
            aprovados=("is_aprovado", "sum"),
        )
        .sort_values("valor_total", ascending=False)
    )
    contract_types["taxa_aprovacao_pct"] = contract_types.apply(
        lambda row: safe_pct(row["aprovados"], row["processos"]), axis=1
    )

    top_approvers = (
        proc[proc["is_aprovado"] & proc["aprovador"].notna()]
        .groupby("aprovador", as_index=False)
        .agg(
            processos_aprovados=("id_contrato", "size"),
            valor_aprovado=("valor", "sum"),
            tempo_medio_aprovacao_dias=("dias_para_aprovacao", "mean"),
        )
        .sort_values(["valor_aprovado", "processos_aprovados"], ascending=False)
        .head(10)
    )

    bottlenecks = (
        proc[~proc["is_aprovado"]]
        .groupby("departamento", as_index=False)
        .agg(
            processos_criticos=("id_contrato", "size"),
            valor_em_risco=("valor", "sum"),
            pendentes=("is_pendente", "sum"),
            rejeitados_cancelados=("is_rejeitado_cancelado", "sum"),
        )
        .sort_values("valor_em_risco", ascending=False)
    )

    top_department = departments.iloc[0]
    highest_approval_department = departments.sort_values(
        ["taxa_aprovacao_pct", "processos"], ascending=False
    ).iloc[0]
    bottleneck_department = bottlenecks.iloc[0] if not bottlenecks.empty else None
    best_month = monthly.sort_values("taxa_aprovacao_pct", ascending=False).iloc[0]

    pending_value = float(proc.loc[proc["is_pendente"], "valor"].sum())
    rejected_value = float(proc.loc[proc["is_rejeitado_cancelado"], "valor"].sum())

    highlights = [
        {
            "title": "Highest approval month",
            "metric": str(best_month["mes"]),
            "description": (
                f"Approval rate reached {best_month['taxa_aprovacao_pct']:.1f}% with "
                f"{int(best_month['processos'])} processes and R$ {best_month['valor_aprovado']:,.0f} approved value."
            ),
        },
        {
            "title": "Largest administrative pipeline",
            "metric": str(top_department["departamento"]),
            "description": (
                f"This department handled R$ {top_department['valor_total']:,.0f} across "
                f"{int(top_department['processos'])} processes."
            ),
        },
        {
            "title": "Best operational conversion",
            "metric": str(highest_approval_department["departamento"]),
            "description": (
                f"Approval efficiency reached {highest_approval_department['taxa_aprovacao_pct']:.1f}% with "
                f"an average of {highest_approval_department['tempo_medio_aprovacao_dias']:.1f} days."
            ),
        },
    ]

    recommendations = [
        (
            f"Prioritize pending processes totaling R$ {pending_value:,.0f} with weekly review routines and SLA checkpoints "
            "for each department."
        ),
        (
            f"Create recovery plans for rejected and canceled workflows currently representing R$ {rejected_value:,.0f} "
            "in blocked pipeline value."
        ),
        (
            f"Replicate the approval routines of {highest_approval_department['departamento']} across the other administrative "
            "areas to improve conversion and cycle time."
        ),
    ]

    if bottleneck_department is not None:
        recommendations.append(
            (
                f"Implement root-cause analysis in {bottleneck_department['departamento']}, the area with the highest value at "
                f"risk (R$ {bottleneck_department['valor_em_risco']:,.0f})."
            )
        )

    payload = {
        "project": {
            "title": "Administrative Process Optimization",
            "subtitle": "Improving workflow visibility and operational governance through structured analytics.",
            "description": (
                "This project analyzes internal administrative workflows to identify inefficiencies, monitor approval "
                "performance and support decision-making through data-driven reporting."
            ),
            "scope": [
                "50,000 administrative process records",
                "Coverage from 2023 to 2024",
                "Monitoring by status, department, approver and contract type",
                "Executive reporting focused on operational transparency",
            ],
        },
        "meta": {
            "generated_at": pd.Timestamp.now(tz="UTC").isoformat(),
            "records": total_processos,
            "period_start": proc["data_solicitacao"].min().strftime("%Y-%m-%d"),
            "period_end": proc["data_solicitacao"].max().strftime("%Y-%m-%d"),
            "departments": int(proc["departamento"].nunique()),
            "approvers": int(proc["aprovador"].dropna().nunique()),
        },
        "kpis": {
            "valor_total_processos": round(total_valor, 2),
            "valor_aprovado": round(valor_aprovado, 2),
            "taxa_aprovacao_pct": round(taxa_aprovacao_pct, 2),
            "tempo_medio_aprovacao_dias": round(tempo_medio_aprovacao, 2),
            "processos_aprovados": aprovados,
            "processos_pendentes": pendentes,
            "processos_rejeitados_cancelados": rejeitados_cancelados,
        },
        "highlights": highlights,
        "recommendations": recommendations,
        "series": {
            "monthly_pipeline": to_records(monthly),
            "status_distribution": to_records(status_distribution),
            "department_performance": to_records(departments),
            "contract_type_mix": to_records(contract_types),
            "top_approvers": to_records(top_approvers),
        },
        "tables": {
            "department_performance": to_records(departments),
            "contract_type_mix": to_records(contract_types),
            "approval_bottlenecks": to_records(bottlenecks),
            "top_approvers": to_records(top_approvers),
        },
    }

    return payload


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"Administrative dataset not found: {SOURCE_CSV}")

    frame = pd.read_csv(SOURCE_CSV)
    payload = build_payload(frame)

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Administrative dashboard data generated at {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
