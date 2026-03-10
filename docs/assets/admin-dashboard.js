const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  maximumFractionDigits: 0,
});

const preciseCurrencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  maximumFractionDigits: 2,
});

const numberFormatter = new Intl.NumberFormat("pt-BR");
const percentFormatter = new Intl.NumberFormat("pt-BR", {
  maximumFractionDigits: 1,
});

const chartPalette = {
  forest: "#23423d",
  moss: "#648a64",
  amber: "#ca7c31",
  clay: "#b7552f",
  gold: "#d8ad5a",
  ink: "#17201d",
};

const chartInstances = [];
const dashboardDataPath = document.body.dataset.dashboardDataPath || "../data/admin_dashboard.json";

document.addEventListener("DOMContentLoaded", () => {
  initDashboard().catch((error) => {
    renderError(error);
  });
});

async function initDashboard() {
  const response = await fetch(dashboardDataPath);
  if (!response.ok) {
    throw new Error("Could not load administrative dashboard data.");
  }

  const data = await response.json();
  renderHero(data);
  renderKpis(data);
  renderScope(data.project.scope);
  renderHighlights(data.highlights);
  renderRecommendations(data.recommendations);
  renderTables(data.tables);
  renderCharts(data.series);
  document.getElementById("generatedAt").textContent = formatDateTime(data.meta.generated_at);
}

function renderHero(data) {
  document.getElementById("project-title").textContent = data.project.title;
  document.getElementById("project-subtitle").textContent = data.project.subtitle;
  document.getElementById("project-description").textContent = data.project.description;

  document.getElementById("meta-records").textContent = `${numberFormatter.format(data.meta.records)} records`;
  document.getElementById("meta-period").textContent = `${formatDate(data.meta.period_start)} - ${formatDate(data.meta.period_end)}`;
  document.getElementById("meta-departments").textContent = numberFormatter.format(data.meta.departments);
  document.getElementById("meta-approvers").textContent = numberFormatter.format(data.meta.approvers);
}

function renderKpis(data) {
  const kpiGrid = document.getElementById("kpi-grid");
  const cards = [
    {
      label: "Total process value",
      value: currencyFormatter.format(data.kpis.valor_total_processos),
      detail: `${numberFormatter.format(data.meta.records)} total workflows`,
    },
    {
      label: "Approved value",
      value: currencyFormatter.format(data.kpis.valor_aprovado),
      detail: `${percentFormatter.format(data.kpis.taxa_aprovacao_pct)}% approval rate`,
    },
    {
      label: "Average approval time",
      value: `${percentFormatter.format(data.kpis.tempo_medio_aprovacao_dias)} days`,
      detail: "Average cycle for approved workflows",
    },
    {
      label: "Pending workflows",
      value: numberFormatter.format(data.kpis.processos_pendentes),
      detail: "Processes waiting for decision",
    },
    {
      label: "Rejected or canceled",
      value: numberFormatter.format(data.kpis.processos_rejeitados_cancelados),
      detail: "Critical backlog requiring action",
    },
    {
      label: "Average approved ticket",
      value: preciseCurrencyFormatter.format(
        data.kpis.valor_aprovado / Math.max(data.kpis.processos_aprovados, 1),
      ),
      detail: "Reference ratio for process value density",
    },
  ];

  kpiGrid.innerHTML = cards
    .map(
      (card) => `
        <article class="kpi-card">
          <p class="kpi-label">${card.label}</p>
          <p class="kpi-value">${card.value}</p>
          <p class="kpi-detail">${card.detail}</p>
        </article>
      `,
    )
    .join("");
}

function renderScope(scopeItems) {
  const scopeList = document.getElementById("scope-list");
  scopeList.innerHTML = scopeItems
    .map((item) => `<div class="scope-item">${item}</div>`)
    .join("");
}

function renderHighlights(highlights) {
  const wrapper = document.getElementById("highlights");
  wrapper.innerHTML = highlights
    .map(
      (highlight) => `
        <article class="highlight-card">
          <p>${highlight.title}</p>
          <strong>${highlight.metric}</strong>
          <p>${highlight.description}</p>
        </article>
      `,
    )
    .join("");
}

function renderRecommendations(recommendations) {
  const list = document.getElementById("recommendations");
  list.innerHTML = recommendations.map((item) => `<li>${item}</li>`).join("");
}

function renderTables(tables) {
  document.getElementById("departmentsTable").innerHTML = tables.department_performance
    .map(
      (item) => `
        <tr>
          <td>${item.departamento}</td>
          <td>${currencyFormatter.format(item.valor_total)}</td>
          <td>${percentFormatter.format(item.taxa_aprovacao_pct)}%</td>
          <td>${percentFormatter.format(item.tempo_medio_aprovacao_dias || 0)} days</td>
        </tr>
      `,
    )
    .join("");

  document.getElementById("bottlenecksTable").innerHTML = tables.approval_bottlenecks
    .map(
      (item) => `
        <tr>
          <td>${item.departamento}</td>
          <td>${numberFormatter.format(item.processos_criticos)}</td>
          <td>${currencyFormatter.format(item.valor_em_risco)}</td>
          <td>${numberFormatter.format(item.pendentes)}</td>
        </tr>
      `,
    )
    .join("");
}

function renderCharts(series) {
  destroyCharts();
  renderMonthlyChart(series.monthly_pipeline);
  renderStatusChart(series.status_distribution);
  renderDepartmentChart(series.department_performance);
  renderApproverChart(series.top_approvers);
}

function renderMonthlyChart(monthly) {
  const canvas = document.getElementById("monthlyAdminChart");
  const context = canvas.getContext("2d");

  const chart = new Chart(context, {
    type: "line",
    data: {
      labels: monthly.map((item) => item.mes),
      datasets: [
        {
          label: "Total processes",
          data: monthly.map((item) => item.processos),
          borderColor: chartPalette.forest,
          backgroundColor: "rgba(35, 66, 61, 0.18)",
          fill: true,
          tension: 0.3,
          borderWidth: 3,
          pointRadius: 2,
        },
        {
          label: "Approved",
          data: monthly.map((item) => item.aprovados),
          borderColor: chartPalette.amber,
          backgroundColor: "rgba(202, 124, 49, 0.08)",
          fill: false,
          tension: 0.3,
          borderWidth: 3,
          pointRadius: 2,
        },
      ],
    },
    options: baseChartOptions(),
  });

  chartInstances.push(chart);
}

function renderStatusChart(statusDistribution) {
  const canvas = document.getElementById("statusChart");
  const context = canvas.getContext("2d");
  const chart = new Chart(context, {
    type: "doughnut",
    data: {
      labels: statusDistribution.map((item) => item.status),
      datasets: [
        {
          label: "Processes",
          data: statusDistribution.map((item) => item.quantidade),
          backgroundColor: ["#23423d", "#648a64", "#ca7c31", "#b7552f"],
          borderColor: "rgba(255,255,255,0.8)",
          borderWidth: 2,
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: chartPalette.ink,
            font: {
              family: "Space Grotesk",
            },
          },
        },
        tooltip: {
          callbacks: {
            label(context) {
              return `${context.label}: ${numberFormatter.format(context.parsed)}`;
            },
          },
        },
      },
    },
  });

  chartInstances.push(chart);
}

function renderDepartmentChart(departments) {
  const canvas = document.getElementById("departmentChart");
  const context = canvas.getContext("2d");

  const chart = new Chart(context, {
    type: "bar",
    data: {
      labels: departments.map((item) => item.departamento),
      datasets: [
        {
          label: "Approval rate",
          data: departments.map((item) => item.taxa_aprovacao_pct),
          backgroundColor: "rgba(35, 66, 61, 0.84)",
          borderRadius: 10,
        },
      ],
    },
    options: baseChartOptions({
      indexAxis: "y",
      ySuffix: "%",
      legend: false,
    }),
  });

  chartInstances.push(chart);
}

function renderApproverChart(approvers) {
  const canvas = document.getElementById("approverChart");
  const context = canvas.getContext("2d");

  const chart = new Chart(context, {
    type: "bar",
    data: {
      labels: approvers.map((item) => item.aprovador),
      datasets: [
        {
          label: "Approved value",
          data: approvers.map((item) => item.valor_aprovado),
          backgroundColor: "rgba(202, 124, 49, 0.86)",
          borderRadius: 10,
        },
      ],
    },
    options: baseChartOptions({
      indexAxis: "y",
      yAsCurrency: true,
      legend: false,
    }),
  });

  chartInstances.push(chart);
}

function baseChartOptions({ indexAxis = "x", yAsCurrency = false, ySuffix = "", legend = true } = {}) {
  const isHorizontal = indexAxis === "y";
  return {
    indexAxis,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: legend,
        labels: {
          color: chartPalette.ink,
          font: {
            family: "Space Grotesk",
            weight: 700,
          },
        },
      },
      tooltip: {
        backgroundColor: "rgba(23, 32, 29, 0.92)",
        titleFont: {
          family: "Space Grotesk",
          weight: 700,
        },
        bodyFont: {
          family: "Space Grotesk",
        },
        callbacks: {
          label(context) {
            const raw = context.parsed.x ?? context.parsed.y;
            if (yAsCurrency) {
              return `${context.dataset.label}: ${currencyFormatter.format(raw)}`;
            }
            if (ySuffix) {
              return `${context.dataset.label}: ${percentFormatter.format(raw)}${ySuffix}`;
            }
            return `${context.dataset.label}: ${numberFormatter.format(raw)}`;
          },
        },
      },
    },
    scales: {
      x: {
        ticks: {
          color: chartPalette.ink,
          callback(value) {
            const raw = this.getLabelForValue ? this.getLabelForValue(value) : value;
            if (isHorizontal) {
              if (yAsCurrency) {
                return currencyFormatter.format(raw);
              }
              if (ySuffix) {
                return `${percentFormatter.format(raw)}${ySuffix}`;
              }
            }
            return raw;
          },
        },
        grid: {
          color: "rgba(23, 32, 29, 0.08)",
        },
      },
      y: {
        ticks: {
          color: chartPalette.ink,
          callback(value) {
            const raw = this.getLabelForValue ? this.getLabelForValue(value) : value;
            if (!isHorizontal && yAsCurrency) {
              return currencyFormatter.format(raw);
            }
            if (!isHorizontal && ySuffix) {
              return `${percentFormatter.format(raw)}${ySuffix}`;
            }
            return raw;
          },
        },
        grid: {
          color: "rgba(23, 32, 29, 0.08)",
        },
      },
    },
  };
}

function destroyCharts() {
  while (chartInstances.length > 0) {
    const chart = chartInstances.pop();
    chart.destroy();
  }
}

function renderError(error) {
  const kpiGrid = document.getElementById("kpi-grid");
  kpiGrid.innerHTML = `<div class="error-message">${error.message}</div>`;
}

function formatDate(value) {
  const [year, month, day] = value.split("-").map(Number);
  return new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC" }).format(
    new Date(Date.UTC(year, month - 1, day)),
  );
}

function formatDateTime(value) {
  return new Date(value).toLocaleString("pt-BR", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}
