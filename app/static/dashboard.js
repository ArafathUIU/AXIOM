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
  endpointTable: document.querySelector("#endpoint-table"),
  recentLogs: document.querySelector("#recent-logs"),
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

async function refreshDashboard() {
  selectors.refreshButton.disabled = true;
  try {
    const [health, summary, traffic, latency, anomalies, endpoints, logs] = await Promise.all([
      fetchJson("/health"),
      fetchJson("/analytics/summary"),
      fetchJson("/analytics/traffic?interval=hour"),
      fetchJson("/analytics/latency-percentiles"),
      fetchJson("/anomalies/summary"),
      fetchJson("/analytics/endpoints?limit=8"),
      fetchJson("/logs/recent?limit=8"),
    ]);

    selectors.health.textContent = health.status === "ok" ? "Online" : "Unknown";
    selectors.totalRequests.textContent = formatNumber(summary.total_requests);
    selectors.errorCount.textContent = formatNumber(summary.error_count);
    selectors.errorRate.textContent = `${summary.error_rate}%`;
    selectors.averageLatency.textContent = `${summary.average_response_time_ms} ms`;
    renderTraffic(traffic);
    renderLatency(latency);
    renderAnomalies(anomalies);
    renderEndpoints(endpoints);
    renderLogs(logs);
    selectors.lastRefresh.textContent = new Date().toLocaleTimeString();
  } catch (error) {
    selectors.health.textContent = "Error";
    selectors.recentLogs.innerHTML = `<p class="empty">${error.message}</p>`;
  } finally {
    selectors.refreshButton.disabled = false;
  }
}

selectors.refreshButton.addEventListener("click", refreshDashboard);
refreshDashboard();
