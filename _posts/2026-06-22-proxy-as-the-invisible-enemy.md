---
layout: post
title: "The Proxy Variable Trap: Why Your Service Is \"Down\" When It's Fine"
subtitle: "A debugging pattern that wastes hours — and a fix that takes five lines"
date: 2026-06-22
author: danmi
tags: [debugging, systems, networking, devops]
---

Here's a scenario I've seen trip up engineers more than once: a service that's clearly running — health check passes, you can `curl` it directly, logs show nothing wrong — refuses to respond when called from a script or automated process.

The instinct is to blame the service. Restart it. Add retry logic. Increase timeouts. Check if a port changed.

Almost always, the service is fine. The problem is the environment.

---

## The Setup

You have an internal service on a private network. Something like a Jupyter kernel, a local API, a database. Localhost or LAN address. No external routing needed.

Your automation environment — a script, a cron job, a subprocess spawned by another process — inherits a set of environment variables from its parent. Among those variables, quietly sitting there: `HTTP_PROXY`, `HTTPS_PROXY`, or lowercase variants.

The proxy was set somewhere upstream. Maybe a global shell profile for reaching the public internet. Maybe a tool that configures it and forgets to clean up. Maybe a CI system with broad proxy settings.

Now your script tries to connect to `http://192.168.1.10:8888`. Python's `urllib` or `websocket-client` reads the proxy variables. It routes your LAN request through the external proxy. The proxy either rejects it (wrong network segment), silently drops it, or returns something malformed.

Your service is perfectly healthy. Your connection never arrives.

---

## Why It's Hard to See

The error messages are unhelpful. You might get:

- `WebSocketProxyException: list index out of range` — unhelpful exception from deep in the websocket library
- A long hang followed by a timeout — no error at all, just silence
- `Connection refused` — which looks like the service is down, because the proxy rejected it
- Intermittent failures — because some proxy configurations work for some destinations and not others

None of these point at proxy misconfiguration. They all *look* like the service is unreachable.

Meanwhile, manual testing works fine: when you open a terminal and `curl http://192.168.1.10:8888/api/status`, you probably don't have proxy variables set in your interactive shell. The problem only appears in automated contexts — cron jobs, subprocesses, daemon scripts — that inherit a polluted environment.

This asymmetry between "works manually, fails automatically" is the tell.

---

## The Diagnostic Move

Before anything else, print the environment:

```python
import os
for k, v in os.environ.items():
    if 'proxy' in k.lower():
        print(f"{k}={v}")
```

Or from the shell:

```bash
env | grep -i proxy
```

If you see proxy variables pointing at an external proxy, and your target is internal — that's your bug. Not the service, not the timeout, not the retry count.

---

## The Fix

The clean fix is to strip proxy variables from the process environment before making internal connections. Don't rely on the caller to `unset` them — that's fragile, especially in automated pipelines where you can't control the parent environment.

```python
import os

def strip_proxy_env():
    """Remove all proxy-related env vars so internal connections go direct."""
    keys_to_remove = [k for k in os.environ if 'proxy' in k.lower()]
    for k in keys_to_remove:
        os.environ.pop(k, None)
    os.environ['no_proxy'] = '*'
    os.environ['NO_PROXY'] = '*'

# Call at module import time — before any connection libraries initialize
strip_proxy_env()
```

A few things worth noting about this approach:

**Do it at import time, not connection time.** Some libraries read proxy configuration during module initialization. If you wait until the first connection, it may be too late.

**Set `no_proxy=*` as a belt-and-suspenders measure.** Some libraries check `no_proxy` even after you've removed the proxy address. Setting it to `*` tells them: bypass proxy for everything.

**This is scoped to the process.** You're not unsetting the variables system-wide. The parent process and other tools are unaffected. Each script that needs direct internal access cleans its own environment.

---

## The Broader Pattern

Proxy variables are just one instance of a general class of bugs: **environment state that leaks across contexts**.

The same pattern appears with:
- `PYTHONPATH` or `LD_LIBRARY_PATH` pointing at the wrong version
- `AWS_DEFAULT_REGION` or other service configuration set for one context, silently affecting another
- `DATABASE_URL` or `REDIS_URL` pointing at production in a job that should hit staging
- `TZ` being set to something unexpected, corrupting timestamp comparisons

The common thread: the automated context inherits something from its environment that was meant for a different purpose, and the resulting failure looks nothing like an "environment variable problem."

Debugging these is genuinely hard because the error manifests far from the cause. The thing that fails (connection, query, time comparison) has no obvious relationship to the thing that's wrong (an env var set five levels up the process tree).

The practical defense: for any script that will run in automated or inherited environments, explicitly set the environment it needs rather than inheriting whatever shows up. Don't assume the environment is clean. Check it.

---

## Recognizing the Pattern

The signal to look for: a service or operation that works when you test it manually but fails consistently in automated contexts. That asymmetry — **interactive works, automated fails** — is almost always an environment problem.

When you see it, don't add more retry logic or increase timeouts. Print the environment. Look for variables that don't belong. The service is probably fine.
