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
  sand: "#f4ead8",
};

const chartInstances = [];

document.addEventListener("DOMContentLoaded", () => {
  initDashboard().catch((error) => {
    renderError(error);
  });
});

async function initDashboard() {
  const response = await fetch("data/sales_dashboard.json");
  if (!response.ok) {
    throw new Error("Could not load dashboard data.");
  }

  const data = await response.json();
  renderHero(data);
  renderKpis(data);
  renderScope(data.project.scope);
  renderHighlights(data.highlights);
  renderRecommendations(data.recommendations);
  renderTables(data.tables);
  renderCharts(data.series, data.tables);
  document.getElementById("generatedAt").textContent = formatDateTime(data.meta.generated_at);
}

function renderHero(data) {
  document.getElementById("project-title").textContent = data.project.title;
  document.getElementById("project-subtitle").textContent = data.project.subtitle;
  document.getElementById("project-description").textContent = data.project.description;
  document.getElementById("meta-records").textContent = `${numberFormatter.format(data.meta.records)} rows`;
  document.getElementById("meta-period").textContent = `${formatDate(data.meta.period_start)} - ${formatDate(data.meta.period_end)}`;
  document.getElementById("meta-products").textContent = numberFormatter.format(data.meta.products);
  document.getElementById("meta-sellers").textContent = numberFormatter.format(data.meta.sellers);
}

function renderKpis(data) {
  const kpiGrid = document.getElementById("kpi-grid");
  const cards = [
    {
      label: "Total revenue",
      value: currencyFormatter.format(data.kpis.receita_total),
      detail: `${numberFormatter.format(data.meta.records)} orders analyzed`,
    },
    {
      label: "Total profit",
      value: currencyFormatter.format(data.kpis.lucro_total),
      detail: `${percentFormatter.format(data.kpis.margem_lucro_pct)}% profit margin`,
    },
    {
      label: "Average ticket",
      value: preciseCurrencyFormatter.format(data.kpis.ticket_medio),
      detail: `${percentFormatter.format(data.kpis.itens_medios)} items per order`,
    },
    {
      label: "Active catalog",
      value: numberFormatter.format(data.meta.products),
      detail: "Distinct products sold",
    },
    {
      label: "Salesforce",
      value: numberFormatter.format(data.meta.sellers),
      detail: "Active sellers in the dataset",
    },
    {
      label: "Highest margin category",
      value: data.tables.highest_margin_category.categoria,
      detail: `${percentFormatter.format(data.tables.highest_margin_category.margem_pct)}% margin`,
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
  document.getElementById("productsTable").innerHTML = tables.top_products
    .map(
      (item) => `
        <tr>
          <td>${item.produto}</td>
          <td>${item.categoria}</td>
          <td>${currencyFormatter.format(item.receita)}</td>
          <td>${percentFormatter.format(item.margem_pct)}%</td>
        </tr>
      `,
    )
    .join("");

  document.getElementById("categoriesTable").innerHTML = tables.category_performance
    .map(
      (item) => `
        <tr>
          <td>${item.categoria}</td>
          <td>${currencyFormatter.format(item.receita)}</td>
          <td>${currencyFormatter.format(item.lucro)}</td>
          <td>${percentFormatter.format(item.margem_pct)}%</td>
        </tr>
      `,
    )
    .join("");
}

function renderCharts(series, tables) {
  destroyCharts();
  renderMonthlyChart(series.monthly_performance);
  renderCategoryChart(tables.category_performance);
  renderRegionChart(tables.region_performance);
  renderSellerChart(tables.top_sellers);
}

function renderMonthlyChart(monthlyData) {
  const canvas = document.getElementById("monthlyChart");
  const context = canvas.getContext("2d");
  const gradient = context.createLinearGradient(0, 0, 0, 320);
  gradient.addColorStop(0, "rgba(202, 124, 49, 0.28)");
  gradient.addColorStop(1, "rgba(202, 124, 49, 0.02)");

  const chart = new Chart(context, {
    type: "line",
    data: {
      labels: monthlyData.map((item) => item.mes),
      datasets: [
        {
          label: "Revenue",
          data: monthlyData.map((item) => item.receita),
          borderColor: chartPalette.amber,
          backgroundColor: gradient,
          fill: true,
          tension: 0.32,
          borderWidth: 3,
          pointRadius: 2,
        },
        {
          label: "Profit",
          data: monthlyData.map((item) => item.lucro),
          borderColor: chartPalette.forest,
          backgroundColor: "rgba(35, 66, 61, 0.08)",
          fill: false,
          tension: 0.32,
          borderWidth: 3,
          pointRadius: 2,
        },
      ],
    },
    options: baseChartOptions({
      yAsCurrency: true,
    }),
  });

  chartInstances.push(chart);
}

function renderCategoryChart(categoryData) {
  const canvas = document.getElementById("categoryChart");
  const context = canvas.getContext("2d");
  const chart = new Chart(context, {
    type: "bar",
    data: {
      labels: categoryData.map((item) => item.categoria),
      datasets: [
        {
          label: "Revenue",
          data: categoryData.map((item) => item.receita),
          backgroundColor: [
            "#23423d",
            "#648a64",
            "#ca7c31",
            "#d8ad5a",
            "#b7552f",
          ],
          borderRadius: 12,
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

function renderRegionChart(regionData) {
  const canvas = document.getElementById("regionChart");
  const context = canvas.getContext("2d");
  const chart = new Chart(context, {
    type: "bar",
    data: {
      labels: regionData.map((item) => item.regiao),
      datasets: [
        {
          label: "Profit margin",
          data: regionData.map((item) => item.margem_pct),
          backgroundColor: ["#23423d", "#648a64", "#ca7c31", "#d8ad5a", "#b7552f"],
          borderRadius: 12,
        },
      ],
    },
    options: baseChartOptions({
      legend: false,
      ySuffix: "%",
    }),
  });

  chartInstances.push(chart);
}

function renderSellerChart(sellerData) {
  const canvas = document.getElementById("sellerChart");
  const context = canvas.getContext("2d");
  const chart = new Chart(context, {
    type: "bar",
    data: {
      labels: sellerData.map((item) => item.nome_vendedor),
      datasets: [
        {
          label: "Revenue",
          data: sellerData.map((item) => item.receita),
          backgroundColor: "rgba(35, 66, 61, 0.88)",
          borderRadius: 12,
        },
      ],
    },
    options: baseChartOptions({
      indexAxis: "y",
      legend: false,
      yAsCurrency: true,
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
