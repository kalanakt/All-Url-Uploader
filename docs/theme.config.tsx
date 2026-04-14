import React from 'react'
import { DocsThemeConfig } from 'nextra-theme-docs'

const config: DocsThemeConfig = {
  head: (
    <>
      <meta charSet="UTF-8" />
      <meta name="author" content="kalanakt" />
      <meta name="keywords" content="telegram, telegram bot, aiogram, yt-dlp, url uploader" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta property="og:title" content="All Url Uploader Docs" />
      <meta
        property="og:description"
        content="Documentation for the aiogram-based All Url Uploader bot."
      />
      <link rel="shortcut icon" href="/favicon.ico" />
      <title>All Url Uploader Docs</title>
    </>
  ),
  banner: {
    key: 'aiogram-migration',
    text: <a href="https://github.com/kalanakt/All-Url-Uploader" target="_blank" rel="noreferrer">
      All Url Uploader now runs on aiogram with a root-first project layout.
    </a>,
  },
  logo: <span>All Url Uploader</span>,
  project: {
    link: 'https://github.com/kalanakt/All-Url-Uploader',
  },
  chat: {
    link: 'https://github.com/kalanakt/All-Url-Uploader/discussions',
    icon: <span>GitHub</span>,
  },
  docsRepositoryBase: 'https://github.com/kalanakt/All-Url-Uploader/tree/main/docs',
  footer: {
    component: null,
  },
  faviconGlyph: '(o)'
}

export default config
