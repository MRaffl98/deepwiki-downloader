# DeepWiki Downloader

A single-page tool that exports any [DeepWiki](https://deepwiki.com) repository as a single Markdown file — no backend, no install required.

**Live:** https://mraffl98.github.io/deepwiki-downloader/

## Usage

1. Paste a DeepWiki URL (e.g. `https://deepwiki.com/openai/codex`)
2. Click **Export**
3. Download the resulting `.md` file

## How it works

DeepWiki is a Next.js App Router site. When you request any page, the server embeds the full wiki content in the HTML as RSC (React Server Components) flight data — a series of `self.__next_f.push([1, "..."])` script tags. The tool fetches the index page once via a public CORS proxy, reconstructs the RSC stream, extracts all `T<hex-length>,<content>` text chunks, and concatenates them into one Markdown document. No individual page requests needed.

## Security note

Requests are routed through public CORS proxies. Do not use this tool on private or sensitive wikis.
