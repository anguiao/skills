---
name: uniapp-wechatide
description: Use when a Vue 3 uni-app project's mp-weixin target needs WeChat DevTools runtime debugging, automation, preview, or upload.
---

# uni-app WeChat DevTools

Use the repository's uni-app toolchain to produce mp-weixin output, then use `wechatide-skill` for WeChat DevTools runtime operations.

Inspect the repository instructions and package scripts to resolve the actual development command, production command, and output directories. Treat `dist/dev/mp-weixin` and `dist/build/mp-weixin` only as conventional defaults.

For development, debugging, screenshots, and automation, reuse or start the repository's mp-weixin development watcher and operate on its output. For release-like preview or upload, run a fresh production build and operate on the production output. Upload requires an explicit user request.

Before the first `wechatide` call, read and follow `wechatide-skill`. Pass the resolved generated-project path as an absolute `--project` value and use only the capabilities needed for the request.

Do not edit generated output to fix a source issue. Trace the problem back to the uni-app source, rebuild, and verify the new output. Avoid native-only operations such as single-file WXML/WXSS compilation, generated `project.config.json` editing, or WeChat npm building unless the project provides concrete evidence that they are needed.

Preserve the repository's existing build and IDE scripts. Keep build commands pure, and run validation or WeChat DevTools actions separately.
