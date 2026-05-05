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
  requestDetail: document.querySelector("#request-detail"),
  insightForm: document.querySelector("#insight-form"),
  insightPrompt: document.querySelector("#insight-prompt"),
  insightResult: document.querySelector("#insight-result"),
  adminToken: document.querySelector("#admin-token"),
  refreshButton: document.querySelector("#refresh-button"),
};

async function fetchJson(url) {
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(await responseErrorMessage(response, url));
  return response.json();
}

async function responseErrorMessage(response, url) {
  try {
    const payload = await response.json();
    if (payload.detail) return payload.detail;
  } catch (error) {
    // Fall through to the status-based message when the response is not JSON.
  }
  return `${url} returned ${response.status}`;
}

function formatNumber(value) {
  return new Intl.NumberFormat().format(value ?? 0);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDateTime(value) {
  if (!value) return "Unknown";
  return new Date(value).toLocaleString();
}

function statusClass(statusCode) {
  return statusCode < 400 ? "ok" : "";
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
      <td><span class="method-badge">${escapeHtml(endpoint.method)}</span></td>
      <td>${escapeHtml(endpoint.path)}</td>
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
    <button class="log-row" type="button" data-log-id="${log.id}">
      <span class="log-main">
        <span class="method-badge">${escapeHtml(log.method)}</span>
        <span class="log-path">${escapeHtml(log.path)}</span>
        <span class="log-meta">${escapeHtml(log.client_ip || "unknown origin")} · ${formatDateTime(log.created_at)}</span>
      </span>
      <span class="log-status">
        <span class="status-badge ${statusClass(log.status_code)}">${log.status_code}</span>
        ${log.response_time_ms.toFixed(2)} ms
      </span>
    </button>
  `).join("");
}

function renderRequestDetail(log) {
  selectors.requestDetail.classList.remove("empty");
  selectors.requestDetail.innerHTML = `
    <div class="detail-row"><span>Request</span><strong>${escapeHtml(log.method)} ${escapeHtml(log.path)}</strong></div>
    <div class="detail-row"><span>Status</span><strong>${log.status_code}</strong></div>
    <div class="detail-row"><span>Latency</span><strong>${log.response_time_ms.toFixed(2)} ms</strong></div>
    <div class="detail-row"><span>Client IP</span><strong>${escapeHtml(log.client_ip || "Unknown")}</strong></div>
    <div class="detail-row"><span>User Agent</span><code>${escapeHtml(log.user_agent || "Unknown")}</code></div>
    <div class="detail-row"><span>Timestamp</span><strong>${formatDateTime(log.created_at)}</strong></div>
  `;
}

async function inspectRequest(logId) {
  selectors.requestDetail.classList.add("empty");
  selectors.requestDetail.textContent = "Loading request detail...";
  try {
    const log = await fetchJson(`/logs/${logId}`);
    renderRequestDetail(log);
  } catch (error) {
    selectors.requestDetail.textContent = error.message;
  }
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
    if (!response.ok) {
      const message = await responseErrorMessage(response, "/insights");
      throw new Error(
        response.status === 403 ? `${message}. Enter the configured admin token to generate insights.` : message,
      );
    }
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
selectors.recentLogs.addEventListener("click", (event) => {
  const row = event.target.closest("[data-log-id]");
  if (row) inspectRequest(row.dataset.logId);
});
refreshDashboard();
