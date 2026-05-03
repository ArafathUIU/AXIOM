const selectors = {
  health: document.querySelector("#health-status"),
  lastRefresh: document.querySelector("#last-refresh"),
  totalRequests: document.querySelector("#total-requests"),
  errorCount: document.querySelector("#error-count"),
  errorRate: document.querySelector("#error-rate"),
  averageLatency: document.querySelector("#average-latency"),
  trafficChart: document.querySelector("#traffic-chart"),
  latencyList: document.querySelector("#latency-list"),
  anomalySummary: document.querySelector("#anomaly-summary"),
  statusCodes: document.querySelector("#status-codes"),
  endpointTable: document.querySelector("#endpoint-table"),
  recentLogs: document.querySelector("#recent-logs"),
  recentAnomalies: document.querySelector("#recent-anomalies"),
  insightForm: document.querySelector("#insight-form"),
  insightPrompt: document.querySelector("#insight-prompt"),
  insightResult: document.querySelector("#insight-result"),
  adminToken: document.querySelector("#admin-token"),
  refreshButton: document.querySelector("#refresh-button"),
};

async function fetchJson(url) {
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(`${url} returned ${response.status}`);
  return response.json();
}

function formatNumber(value) {
  return new Intl.NumberFormat().format(value ?? 0);
}

function renderTraffic(buckets) {
  if (!buckets.length) {
    selectors.trafficChart.innerHTML = '<p class="empty">No traffic has been captured yet.</p>';
    return;
  }
  const max = Math.max(...buckets.map((bucket) => bucket.request_count), 1);
  selectors.trafficChart.innerHTML = buckets.slice(-12).map((bucket) => {
    const height = Math.max((bucket.request_count / max) * 100, 4);
    const label = bucket.bucket.replace("T", " ").slice(5, 16);
    return `<div class="bar"><span style="height:${height}%"></span><small>${label}</small></div>`;
  }).join("");
}

function renderLatency(percentiles) {
  const rows = [
    ["P50", percentiles.p50_ms],
    ["P90", percentiles.p90_ms],
    ["P95", percentiles.p95_ms],
    ["P99", percentiles.p99_ms],
  ];
  selectors.latencyList.innerHTML = rows.map(([label, value]) => (
    `<div class="pill-row"><span>${label}</span><strong>${value ?? 0} ms</strong></div>`
  )).join("");
}

function renderAnomalies(summary) {
  if (!summary.total) {
    selectors.anomalySummary.innerHTML = '<p class="empty">No persisted anomalies yet.</p>';
    return;
  }
  selectors.anomalySummary.innerHTML = [
    `<div class="pill-row"><span>Total</span><strong>${summary.total}</strong></div>`,
    ...summary.by_severity.map((item) => `<div class="pill-row"><span>${item.name}</span><strong>${item.count}</strong></div>`),
    ...summary.by_type.map((item) => `<div class="pill-row"><span>${item.name}</span><strong>${item.count}</strong></div>`),
  ].join("");
}

function renderStatusCodes(statusCodes) {
  if (!statusCodes.length) {
    selectors.statusCodes.innerHTML = '<p class="empty">No status code data yet.</p>';
    return;
  }
  selectors.statusCodes.innerHTML = statusCodes.map((item) => (
    `<div class="pill-row"><span>HTTP ${item.status_code}</span><strong>${item.count}</strong></div>`
  )).join("");
}

function renderEndpoints(endpoints) {
  if (!endpoints.length) {
    selectors.endpointTable.innerHTML = '<tr><td colspan="5" class="empty">No endpoint analytics yet.</td></tr>';
    return;
  }
  selectors.endpointTable.innerHTML = endpoints.map((endpoint) => `
    <tr>
      <td>${endpoint.method}</td>
      <td>${endpoint.path}</td>
      <td>${endpoint.request_count}</td>
      <td>${endpoint.error_count}</td>
      <td>${endpoint.average_response_time_ms}</td>
    </tr>
  `).join("");
}

function renderLogs(logs) {
  if (!logs.length) {
    selectors.recentLogs.innerHTML = '<p class="empty">No recent logs yet. Visit a few API endpoints to generate traffic.</p>';
    return;
  }
  selectors.recentLogs.innerHTML = logs.map((log) => `
    <div class="log-row">
      <span>${log.method} ${log.path}</span>
      <strong>${log.status_code} · ${log.response_time_ms.toFixed(2)} ms</strong>
    </div>
  `).join("");
}

function renderRecentAnomalies(payload) {
  const anomalies = payload.items ?? [];
  if (!anomalies.length) {
    selectors.recentAnomalies.innerHTML = '<p class="empty">No anomalies have been persisted yet.</p>';
    return;
  }
  selectors.recentAnomalies.innerHTML = anomalies.map((anomaly) => `
    <div class="log-row">
      <span>${anomaly.severity} · ${anomaly.type}</span>
      <strong>${anomaly.observed_value} / ${anomaly.threshold}</strong>
    </div>
  `).join("");
}

async function refreshDashboard() {
  selectors.refreshButton.disabled = true;
  try {
    const [health, summary, traffic, latency, anomalies, statusCodes, endpoints, logs, recentAnomalies] = await Promise.all([
      fetchJson("/health"),
      fetchJson("/analytics/summary"),
      fetchJson("/analytics/traffic?interval=hour"),
      fetchJson("/analytics/latency-percentiles"),
      fetchJson("/anomalies/summary"),
      fetchJson("/analytics/status-codes"),
      fetchJson("/analytics/endpoints?limit=8"),
      fetchJson("/logs/recent?limit=8"),
      fetchJson("/anomalies?limit=5&offset=0"),
    ]);

    selectors.health.textContent = health.status === "ok" ? "Online" : "Unknown";
    selectors.totalRequests.textContent = formatNumber(summary.total_requests);
    selectors.errorCount.textContent = formatNumber(summary.error_count);
    selectors.errorRate.textContent = `${summary.error_rate}%`;
    selectors.averageLatency.textContent = `${summary.average_response_time_ms} ms`;
    renderTraffic(traffic);
    renderLatency(latency);
    renderAnomalies(anomalies);
    renderStatusCodes(statusCodes);
    renderEndpoints(endpoints);
    renderLogs(logs);
    renderRecentAnomalies(recentAnomalies);
    selectors.lastRefresh.textContent = new Date().toLocaleTimeString();
  } catch (error) {
    selectors.health.textContent = "Error";
    selectors.recentLogs.innerHTML = `<p class="empty">${error.message}</p>`;
  } finally {
    selectors.refreshButton.disabled = false;
  }
}

async function generateInsight(event) {
  event.preventDefault();
  const button = selectors.insightForm.querySelector("button");
  button.disabled = true;
  selectors.insightResult.textContent = "Generating insight...";
  try {
    const headers = { "Content-Type": "application/json", Accept: "application/json" };
    if (selectors.adminToken.value) headers["X-Admin-Token"] = selectors.adminToken.value;
    const response = await fetch("/insights", {
      method: "POST",
      headers,
      body: JSON.stringify({ prompt: selectors.insightPrompt.value }),
    });
    if (!response.ok) throw new Error(`/insights returned ${response.status}`);
    const insight = await response.json();
    selectors.insightResult.textContent = insight.summary;
  } catch (error) {
    selectors.insightResult.textContent = error.message;
  } finally {
    button.disabled = false;
  }
}

selectors.refreshButton.addEventListener("click", refreshDashboard);
selectors.insightForm.addEventListener("submit", generateInsight);
refreshDashboard();
