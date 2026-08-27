document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("market-chart");
  if (!canvas) return;
  const state = document.getElementById("chart-state");
  const table = document.getElementById("chart-table");
  if (typeof Chart === "undefined") { state.textContent = "بارگذاری نمودار ممکن نشد."; return; }
  let chart;
  let range = "7d";
  let metric = "reference_price_toman";
  const labels = {reference_price_toman: "قیمت مرجع", global_value_toman: "ارزش جهانی", premium_pct: "حباب"};
  const format = value => value == null ? "—" : new Intl.NumberFormat("fa-IR", {maximumFractionDigits: 2}).format(value);
  const renderTable = points => { table.innerHTML = `<table><caption class="sr-only">جدول داده نمودار</caption><thead><tr><th>زمان</th><th>${labels[metric]}</th></tr></thead><tbody>${points.map(p => `<tr><td>${new Date(p.timestamp).toLocaleString("fa-IR")}</td><td>${format(p[metric])}</td></tr>`).join("")}</tbody></table>`; };
  async function load() {
    state.textContent = "در حال دریافت داده…";
    try {
      const response = await fetch(`/api/v1/market/history?range=${range}`, {headers: {Accept: "application/json"}});
      if (!response.ok) throw new Error("history unavailable");
      const points = (await response.json()).points;
      if (!points.length) { state.textContent = "برای این بازه داده‌ای ثبت نشده است."; table.innerHTML = ""; if (chart) chart.destroy(); return; }
      state.textContent = "";
      if (chart) chart.destroy();
      chart = new Chart(canvas, {type: "line", data: {labels: points.map(p => new Date(p.timestamp).toLocaleDateString("fa-IR")), datasets: [{label: labels[metric], data: points.map(p => p[metric]), borderColor: "#9b282e", backgroundColor: "#9b282e22", borderWidth: 2, pointRadius: 0, pointHitRadius: 22, tension: .25, fill: true}]}, options: {responsive: true, maintainAspectRatio: false, animation: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? false : {duration: 300}, interaction: {mode: "index", intersect: false}, plugins: {legend: {display: true, labels: {font: {family: "IRANYekan"}}}, tooltip: {rtl: true, callbacks: {label: context => `${labels[metric]}: ${format(context.raw)}`}}}, scales: {x: {ticks: {maxTicksLimit: 7, font: {family: "IRANYekan"}}}, y: {ticks: {callback: value => format(value), font: {family: "IRANYekan"}}}}}});
      renderTable(points);
    } catch (_) { state.textContent = "دریافت نمودار ممکن نشد. دوباره تلاش کنید."; }
  }
  document.querySelectorAll("[data-range]").forEach(button => button.addEventListener("click", () => {document.querySelectorAll("[data-range]").forEach(b => {b.classList.remove("active"); b.setAttribute("aria-pressed", "false");}); button.classList.add("active"); button.setAttribute("aria-pressed", "true"); range = button.dataset.range; load();}));
  document.querySelectorAll("[data-metric]").forEach(button => button.addEventListener("click", () => {document.querySelectorAll("[data-metric]").forEach(b => {b.classList.remove("active"); b.setAttribute("aria-pressed", "false");}); button.classList.add("active"); button.setAttribute("aria-pressed", "true"); metric = button.dataset.metric; load();}));
  load();
});
