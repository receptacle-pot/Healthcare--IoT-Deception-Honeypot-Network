const rows = document.querySelector("#event-rows");
const totalEvents = document.querySelector("#total-events");
const topSource = document.querySelector("#top-source");
const topService = document.querySelector("#top-service");
const topTechnique = document.querySelector("#top-technique");
const originList = document.querySelector("#origin-list");
const serviceList = document.querySelector("#service-list");
const commandList = document.querySelector("#command-list");
const techniqueList = document.querySelector("#technique-list");
const exportButton = document.querySelector("#export-json");

let events = [];

function text(value) {
  return value === null || value === undefined || value === "" ? "-" : String(value);
}

function eventPayload(event) {
  return event.command || event.payload || event.path || event.user_agent || "-";
}

function formatTime(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function riskClass(score) {
  if (score >= 70) return "risk high";
  if (score >= 40) return "risk medium";
  return "risk low";
}

function renderRows() {
  const latest = events.slice(-120).reverse();
  rows.innerHTML = latest.map((event) => `
    <tr>
      <td>${formatTime(event.ts)}</td>
      <td><span class="mono">${text(event.src_ip)}</span><small>${text(event.geo_country)}</small></td>
      <td><span class="service ${text(event.service)}">${text(event.service)}</span></td>
      <td>${text(event.event_type)}</td>
      <td class="payload">${text(eventPayload(event))}</td>
      <td><span class="${riskClass(event.risk_score)}">${event.risk_score}</span></td>
    </tr>
  `).join("");
}

function renderList(target, pairs) {
  if (!pairs || pairs.length === 0) {
    target.innerHTML = "<p class='empty'>No data yet</p>";
    return;
  }
  const max = Math.max(...pairs.map(([, count]) => count), 1);
  target.innerHTML = pairs.map(([label, count]) => `
    <div class="bar-row">
      <div class="bar-label"><span>${text(label)}</span><strong>${count}</strong></div>
      <div class="bar-track"><span style="width:${Math.max(8, (count / max) * 100)}%"></span></div>
    </div>
  `).join("");
}

async function refreshSummary() {
  const response = await fetch("/api/summary");
  const summary = await response.json();
  totalEvents.textContent = summary.total_events;
  topSource.textContent = summary.src_ips?.[0]?.[0] || "-";
  topService.textContent = summary.services?.[0]?.[0] || "-";
  topTechnique.textContent = summary.techniques?.[0]?.[0] || "-";
  renderList(originList, summary.src_ips);
  renderList(serviceList, summary.services);
  renderList(commandList, summary.commands);
  renderList(techniqueList, summary.techniques);
}

async function loadInitial() {
  const response = await fetch("/api/events?limit=200");
  events = await response.json();
  renderRows();
  await refreshSummary();
}

function startStream() {
  const lastId = events.length ? events[events.length - 1].id : 0;
  const source = new EventSource(`/api/stream?after_id=${lastId}`);
  source.addEventListener("honeypot-event", (message) => {
    const event = JSON.parse(message.data);
    if (!events.some((existing) => existing.id === event.id)) {
      events.push(event);
      renderRows();
    }
  });
  source.onerror = () => {
    source.close();
    setTimeout(startStream, 2000);
  };
}

exportButton.addEventListener("click", () => {
  window.location.href = "/api/export.json";
});

loadInitial().then(startStream);
setInterval(refreshSummary, 3000);

