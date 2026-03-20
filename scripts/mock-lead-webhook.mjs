#!/usr/bin/env node

import { createServer } from "node:http";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const DEFAULT_PORT = 8787;
const DEFAULT_MODE = "success";
const DEFAULT_PATH = "/lead";
const DEFAULT_STATUS_BY_MODE = {
  success: 200,
  failure: 500,
};

function printHelp() {
  console.log(`Usage: node scripts/mock-lead-webhook.mjs [options]

Options:
  --mode <success|failure>  Response mode. Default: ${DEFAULT_MODE}
  --port <number>           Port to bind. Default: ${DEFAULT_PORT}
  --path <pathname>         Path to accept POST requests on. Default: ${DEFAULT_PATH}
  --capture-file <path>     Optional JSON file that stores the latest captured request
  --help                    Show this message

Examples:
  node scripts/mock-lead-webhook.mjs
  node scripts/mock-lead-webhook.mjs --mode failure --port 8788
  node scripts/mock-lead-webhook.mjs --capture-file .tmp/mock-lead-webhook/latest.json
`);
}

function parseArgs(argv) {
  const options = {
    mode: DEFAULT_MODE,
    port: DEFAULT_PORT,
    path: DEFAULT_PATH,
    captureFile: null,
    help: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === "--help") {
      options.help = true;
      continue;
    }

    if (!arg.startsWith("--")) {
      throw new Error(`Unexpected argument: ${arg}`);
    }

    const value = argv[index + 1];
    if (!value || value.startsWith("--")) {
      throw new Error(`Missing value for ${arg}`);
    }

    switch (arg) {
      case "--mode":
        options.mode = value;
        break;
      case "--port":
        options.port = Number.parseInt(value, 10);
        break;
      case "--path":
        options.path = value.startsWith("/") ? value : `/${value}`;
        break;
      case "--capture-file":
        options.captureFile = value;
        break;
      default:
        throw new Error(`Unknown option: ${arg}`);
    }

    index += 1;
  }

  if (!Object.hasOwn(DEFAULT_STATUS_BY_MODE, options.mode)) {
    throw new Error(`Unsupported mode "${options.mode}". Use success or failure.`);
  }

  if (!Number.isInteger(options.port) || options.port <= 0 || options.port > 65535) {
    throw new Error(`Invalid port "${options.port}". Use a valid TCP port.`);
  }

  return options;
}

function sendJson(response, statusCode, body) {
  response.writeHead(statusCode, {
    "access-control-allow-headers": "content-type",
    "access-control-allow-methods": "OPTIONS, POST",
    "access-control-allow-origin": "*",
    "content-type": "application/json; charset=utf-8",
  });
  response.end(JSON.stringify(body, null, 2));
}

async function persistCapture(captureFile, payload) {
  if (!captureFile) {
    return;
  }

  const absolutePath = resolve(captureFile);
  await mkdir(dirname(absolutePath), { recursive: true });
  await writeFile(absolutePath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
}

function getNextRequestId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
}

async function readBody(request) {
  const chunks = [];

  for await (const chunk of request) {
    chunks.push(chunk);
  }

  return Buffer.concat(chunks).toString("utf8");
}

async function main() {
  const options = parseArgs(process.argv.slice(2));

  if (options.help) {
    printHelp();
    return;
  }

  const server = createServer(async (request, response) => {
    if (request.method === "OPTIONS") {
      response.writeHead(204, {
        "access-control-allow-headers": "content-type",
        "access-control-allow-methods": "OPTIONS, POST",
        "access-control-allow-origin": "*",
      });
      response.end();
      return;
    }

    const requestUrl = new URL(request.url ?? "/", `http://${request.headers.host ?? "127.0.0.1"}`);

    if (request.method !== "POST" || requestUrl.pathname !== options.path) {
      sendJson(response, 404, {
        ok: false,
        error: "Not Found",
        expected: {
          method: "POST",
          path: options.path,
        },
      });
      return;
    }

    const rawBody = await readBody(request);
    let jsonBody;

    try {
      jsonBody = rawBody ? JSON.parse(rawBody) : {};
    } catch (error) {
      sendJson(response, 400, {
        ok: false,
        error: "Invalid JSON body",
        details: error instanceof Error ? error.message : String(error),
      });
      return;
    }

    const capturedRequest = {
      requestId: getNextRequestId(),
      mode: options.mode,
      method: request.method,
      path: requestUrl.pathname,
      receivedAt: new Date().toISOString(),
      headers: request.headers,
      body: jsonBody,
    };

    await persistCapture(options.captureFile, capturedRequest);

    console.log(`\n[mock-lead-webhook] Captured request ${capturedRequest.requestId}`);
    console.log(JSON.stringify(capturedRequest, null, 2));

    const statusCode = DEFAULT_STATUS_BY_MODE[options.mode];
    const message =
      options.mode === "success"
        ? "Intentional success response for lead verification."
        : "Intentional failure response for lead verification.";

    sendJson(response, statusCode, {
      ok: options.mode === "success",
      mode: options.mode,
      message,
      requestId: capturedRequest.requestId,
      persisted: Boolean(options.captureFile),
    });
  });

  server.listen(options.port, "127.0.0.1", async () => {
    console.log(
      `[mock-lead-webhook] Listening on http://127.0.0.1:${options.port}${options.path} (${options.mode} mode)`,
    );

    if (options.captureFile) {
      const absolutePath = resolve(options.captureFile);
      const captureExists = await readFile(absolutePath, "utf8").catch(() => null);
      if (captureExists === null) {
        console.log(`[mock-lead-webhook] Latest capture file will be written to ${absolutePath}`);
      } else {
        console.log(`[mock-lead-webhook] Overwriting existing capture file at ${absolutePath}`);
      }
    }
  });

  const shutdown = () => {
    server.close(() => {
      console.log("[mock-lead-webhook] Server stopped");
      process.exit(0);
    });
  };

  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

main().catch((error) => {
  console.error(`[mock-lead-webhook] ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});
