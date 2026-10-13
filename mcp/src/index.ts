import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");

const rememberSchema = z.object({
  content: z.string().min(1).max(32_000),
  user_id: z.string().min(1).max(256),
  agent_id: z.string().max(256).optional(),
  run_id: z.string().max(256).optional(),
  infer: z.boolean().optional(),
  metadata: z.record(z.unknown()).optional(),
});

const recallSchema = z.object({
  query: z.string().min(1).max(8_000),
  user_id: z.string().min(1).max(256),
  top_k: z.number().int().min(1).max(50).optional(),
  agent_id: z.string().max(256).optional(),
  run_id: z.string().max(256).optional(),
});

const forgetSchema = z.object({
  memory_id: z
    .string()
    .min(1)
    .max(128)
    .refine((v) => !/[;&|`$]/.test(v), "invalid memory_id"),
});

function runBakeoff(subcommand: string, jsonPayload?: Record<string, unknown>): Promise<string> {
  return new Promise((resolve, reject) => {
    const args = ["run", "memory-bakeoff", subcommand];
    if (jsonPayload !== undefined) {
      args.push("--json", JSON.stringify(jsonPayload));
    }
    const child = spawn("uv", args, {
      cwd: repoRoot,
      env: {
        ...process.env,
        MEM0_TELEMETRY: process.env.MEM0_TELEMETRY ?? "False",
      },
      stdio: ["ignore", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk: Buffer) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk: Buffer) => {
      stderr += chunk.toString();
    });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(`memory-bakeoff exited ${code}: ${stderr || stdout}`));
        return;
      }
      resolve(stdout.trim());
    });
  });
}

const server = new Server(
  { name: "mem0-memory-bakeoff", version: "0.1.0" },
  { capabilities: { tools: {} } },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "remember",
      description: "Add a memory via mem0ai (infer=false by default).",
      inputSchema: {
        type: "object",
        properties: {
          content: { type: "string" },
          user_id: { type: "string" },
          agent_id: { type: "string" },
          run_id: { type: "string" },
          infer: { type: "boolean" },
          metadata: { type: "object" },
        },
        required: ["content", "user_id"],
      },
    },
    {
      name: "recall",
      description: "Semantic search memories for a user.",
      inputSchema: {
        type: "object",
        properties: {
          query: { type: "string" },
          user_id: { type: "string" },
          top_k: { type: "number" },
          agent_id: { type: "string" },
          run_id: { type: "string" },
        },
        required: ["query", "user_id"],
      },
    },
    {
      name: "forget",
      description: "Delete a memory by mem0 memory_id.",
      inputSchema: {
        type: "object",
        properties: { memory_id: { type: "string" } },
        required: ["memory_id"],
      },
    },
    {
      name: "scorecard_path",
      description: "Return paths to the latest Memory Scorecard markdown and JSON reports.",
      inputSchema: { type: "object", properties: {} },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  try {
    if (name === "remember") {
      const payload = rememberSchema.parse(args ?? {});
      const text = await runBakeoff("remember", payload);
      return { content: [{ type: "text", text }] };
    }
    if (name === "recall") {
      const payload = recallSchema.parse(args ?? {});
      const text = await runBakeoff("recall", payload);
      return { content: [{ type: "text", text }] };
    }
    if (name === "forget") {
      const payload = forgetSchema.parse(args ?? {});
      const text = await runBakeoff("forget", payload);
      return { content: [{ type: "text", text }] };
    }
    if (name === "scorecard_path") {
      const text = await runBakeoff("scorecard-path");
      return { content: [{ type: "text", text }] };
    }
    throw new Error(`Unknown tool: ${name}`);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return { content: [{ type: "text", text: JSON.stringify({ error: message }) }], isError: true };
  }
});

async function main(): Promise<void> {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
