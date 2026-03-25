/**
 * k6 Load Test — UÚBA Recebe API
 *
 * Cenários:
 *  - smoke: 1 VU, 30s (sanity check)
 *  - load: 20 VUs, 2min (carga normal)
 *  - stress: 50 VUs, 1min (pico)
 *
 * Uso:
 *   k6 run tests/load/k6_stress.js --env BASE_URL=http://localhost:8000 --env API_KEY=sua-key
 *
 * Thresholds:
 *   - p(95) < 500ms
 *   - error rate < 1%
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const API_KEY = __ENV.API_KEY || "uuba-dev-key-change-me";
const HEADERS = {
  "Content-Type": "application/json",
  "X-API-Key": API_KEY,
};

// Custom metrics
const errorRate = new Rate("errors");
const listLatency = new Trend("list_clientes_duration");
const createLatency = new Trend("create_fatura_duration");

export const options = {
  scenarios: {
    smoke: {
      executor: "constant-vus",
      vus: 1,
      duration: "30s",
      exec: "smokeTest",
    },
    load: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "30s", target: 20 },
        { duration: "1m", target: 20 },
        { duration: "30s", target: 0 },
      ],
      exec: "loadTest",
      startTime: "35s",
    },
    stress: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "15s", target: 50 },
        { duration: "30s", target: 50 },
        { duration: "15s", target: 0 },
      ],
      exec: "stressTest",
      startTime: "3m",
    },
  },
  thresholds: {
    http_req_duration: ["p(95)<500"],
    errors: ["rate<0.01"],
    list_clientes_duration: ["p(95)<300"],
    create_fatura_duration: ["p(95)<500"],
  },
};

// --- Cenário: Smoke ---
export function smokeTest() {
  const health = http.get(`${BASE_URL}/health`);
  check(health, { "health 200": (r) => r.status === 200 });

  const clientes = http.get(`${BASE_URL}/api/v1/clientes`, { headers: HEADERS });
  check(clientes, { "list clientes 200": (r) => r.status === 200 });
  errorRate.add(clientes.status !== 200);

  sleep(1);
}

// --- Cenário: Load (leitura + escrita mista) ---
export function loadTest() {
  // 70% leitura
  if (Math.random() < 0.7) {
    const res = http.get(`${BASE_URL}/api/v1/clientes?limit=20`, {
      headers: HEADERS,
    });
    listLatency.add(res.timings.duration);
    check(res, { "list 200": (r) => r.status === 200 });
    errorRate.add(res.status !== 200);
  } else {
    // 30% escrita
    const cpf = `${Math.floor(10000000000 + Math.random() * 89999999999)}`;
    const payload = JSON.stringify({
      nome: `Load Test User ${__VU}-${__ITER}`,
      documento: cpf,
    });
    const res = http.post(`${BASE_URL}/api/v1/clientes`, payload, {
      headers: HEADERS,
    });
    // 201 ou 409 (documento duplicado) são ambos OK
    check(res, { "create 2xx/4xx": (r) => r.status < 500 });
    errorRate.add(res.status >= 500);

    if (res.status === 201) {
      const clienteId = JSON.parse(res.body).id;
      const faturaPayload = JSON.stringify({
        cliente_id: clienteId,
        valor: Math.floor(10000 + Math.random() * 990000),
        vencimento: "2026-06-01T00:00:00Z",
      });
      const fatRes = http.post(`${BASE_URL}/api/v1/faturas`, faturaPayload, {
        headers: HEADERS,
      });
      createLatency.add(fatRes.timings.duration);
      check(fatRes, { "create fatura 201": (r) => r.status === 201 });
      errorRate.add(fatRes.status >= 500);
    }
  }

  sleep(0.5);
}

// --- Cenário: Stress (endpoints de leitura sob pressão) ---
export function stressTest() {
  const endpoints = [
    "/api/v1/clientes?limit=50",
    "/api/v1/faturas?limit=50",
    "/api/v1/cobrancas?limit=50",
    "/health",
  ];

  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
  const res = http.get(`${BASE_URL}${endpoint}`, { headers: HEADERS });

  check(res, { "stress 200": (r) => r.status === 200 });
  errorRate.add(res.status >= 500);

  sleep(0.2);
}
