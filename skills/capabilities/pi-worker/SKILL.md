---
name: pi-worker
description: Delegate scoped tasks to Pi workers.
---

# Pi Worker

## Goal

Use Pi as a persistent worker through its native RPC interface. Keep responsibility for task scope, implementation review, and verification with the caller.

Use Pi's configured provider, model, and thinking level. Do not pass model-selection flags or change Pi settings as part of this workflow.

## Start a worker

Inspect repository instructions and the working tree. Give the worker a concrete goal, relevant context, permitted paths, constraints, and observable acceptance criteria. Avoid concurrent edits to the same files by the caller and worker.

Start Pi in the intended working directory using `exec_command` with `tty: true` and a short yield time:

```bash
pi --mode rpc --no-session
```

Retain the returned terminal `session_id` and use `write_stdin` for every subsequent interaction. This terminal ID is distinct from Pi's own session ID. Keep the process alive between turns; `--no-session` preserves in-process context but does not save it for recovery after exit.

Choose tools and resources appropriate to the task. For text-only consultation, disable tools with `--no-tools`. For a controlled invocation without extensions or MCP connections, also use `--no-extensions --no-mcp`. Keep repository context available for coding work. Pi's tool access is not limited by instructions in the task brief; use actual execution permissions and suitable tool restrictions for hard boundaries. Request additional permissions only for the concrete authorized operation that requires them.

Before sending work, query state and check the actual provider, model, and thinking level:

```json
{"id":"state-1","type":"get_state"}
```

If startup fails or the configured model is unavailable, report the failure; do not silently substitute another model. Consult the installed Pi help and bundled RPC documentation when protocol behavior differs from these examples.

## Exchange RPC messages

Send one JSON object per line, terminated by a newline. Serialize message text as JSON rather than interpolating it into shell commands. Use unique request IDs and match responses by ID, since responses can arrive out of order.

```json
{"id":"task-1","type":"prompt","message":"Inspect the target module and report the cause of the failing test. Do not modify files."}
```

Continue reading with `write_stdin` and empty input while work runs. A PTY can echo submitted commands and use CRLF; echoed commands are not responses. Avoid dumping long streams into context: summarize text updates, tool activity, final messages, and errors while retaining completion events. If output is truncated, query state and retrieve the last assistant text instead of inferring success from partial output.

A successful command response only confirms acceptance. A `prompt` disposition of `handled` means no run started for that command. For active work, wait for `agent_settled`; `agent_end` can be followed by retries, compaction, or queued work. Inspect errors and the `aborted` flag before treating the result as complete. Keep consuming output so stdout backpressure does not stall the worker.

## Continue or redirect work

Use the same process to retain context:

| Command | When to use it |
|---|---|
| `prompt` | Start a task or ask a question after the worker settles. |
| `steer` | Add a correction during execution; it takes effect at a subsequent execution boundary. |
| `follow_up` | Queue another instruction for after current work. |
| `get_state` | Inspect activity, configuration, and pending-message count. |
| `get_last_assistant_text` | Retrieve the latest assistant answer without replaying the stream. |
| `abort` | Interrupt current work while keeping the process available. |

```json
{"id":"steer-1","type":"steer","message":"Keep the public API unchanged; limit the fix to the parser."}
{"id":"follow-1","type":"follow_up","message":"Summarize changed files and verification results."}
{"id":"abort-1","type":"abort"}
```

Send only the command appropriate to the situation. Steering is not immediate cancellation; use `abort` when work must stop. After aborting, inspect state and any pending queue before issuing a replacement task. Use the installed RPC command reference for queue management when necessary.

Poll with bounded waits and communicate meaningful progress. If a request fails, distinguish command rejection from a provider failure after acceptance. Inspect state before retrying a mutation whose outcome is unknown. An unexpected process exit ends this ephemeral conversation; report it rather than claiming to have resumed the same worker.

## Review and close

Inspect the worker's actual changes and run checks appropriate to the task. A worker's success claim does not replace verification. Continue in the same process when corrections are needed.

When finished, abort any remaining active work, then close stdin to request orderly shutdown. In the tested PTY workflow, send Ctrl+D (`\u0004`) on an empty input line and confirm process exit. If graceful shutdown fails, terminate only the worker process owned by this invocation.

Report the adopted result, relevant changes, verification, and any remaining limitation. Do not leave an idle worker running after the delegated work is complete unless the user requests it.
