# DeepWiki Downloader

A single-page tool that exports any [DeepWiki](https://deepwiki.com) repository as a single Markdown file — no backend, no install required.

**Live:** https://mraffl98.github.io/deepwiki-downloader/

## Usage

1. Paste a DeepWiki URL (e.g. `https://deepwiki.com/openai/codex`)
2. Click **Export**
3. Download the resulting `.md` file

## How it works

DeepWiki pages are server-rendered Next.js pages. The tool fetches each page via a public CORS proxy, extracts the structured content from the embedded `__NEXT_DATA__` JSON, and concatenates all pages into one Markdown document.

## Security note

Requests are routed through public CORS proxies. Do not use this tool on private or sensitive wikis.
