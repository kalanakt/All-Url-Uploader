import React from 'react'
import { DocsThemeConfig } from 'nextra-theme-docs'
import ExtraTox from './components/extratox'

const config: DocsThemeConfig = {
  head: (
    <>
      <meta charSet="UTF-8" />
      <meta name="author" content="kalanakt" />
      <meta name="keywords" content="telegram, telegram bot, url uploader" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta property="og:title" content="All Url Uploader Docs" />
      <meta property="og:description" content="A simple telegram Bot, Upload Media File| video To telegram using the direct download link." />
      <link rel="shortcut icon" href="/favicon.ico" />
      <title>All Url Uploader Docs</title>
    </>
  ),
  banner: {
    key: '2.0-release',
    text: <a href="https://github.com/kalanakt/All-Url-Uploader" target="_blank">
      🎉 All-Url-Uploader 2.0 is released. Read more →
    </a>,
  },
  logo: <span>All Url Uploader</span>,
  project: {
    link: 'https://github.com/kalanakt/All-Url-Uploader',
  },
  chat: {
    link: 'https://t.me/TMWAD',
    icon: <svg fill="currentColor" width="32px" height="32px" viewBox="0 0 256 256" id="SVGRepoEditor" xmlns="http://www.w3.org/2000/svg" stroke="currentColor" strokeWidth="2"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g> <path d="M228.646,34.7676a11.96514,11.96514,0,0,0-12.21778-2.0752L31.87109,105.19729a11.99915,11.99915,0,0,0,2.03467,22.93457L84,138.15139v61.833a11.8137,11.8137,0,0,0,7.40771,11.08593,12.17148,12.17148,0,0,0,4.66846.94434,11.83219,11.83219,0,0,0,8.40918-3.5459l28.59619-28.59619L175.2749,217.003a11.89844,11.89844,0,0,0,7.88819,3.00195,12.112,12.112,0,0,0,3.72265-.59082,11.89762,11.89762,0,0,0,8.01319-8.73925L232.5127,46.542A11.97177,11.97177,0,0,0,228.646,34.7676ZM32.2749,116.71877a3.86572,3.86572,0,0,1,2.522-4.07617L203.97217,46.18044,87.07227,130.60769,35.47461,120.28811A3.86618,3.86618,0,0,1,32.2749,116.71877Zm66.55322,86.09375A3.99976,3.99976,0,0,1,92,199.9844V143.72048l35.064,30.85669ZM224.71484,44.7549,187.10107,208.88772a4.0003,4.0003,0,0,1-6.5415,2.10937l-86.1543-75.8164,129.66309-93.645A3.80732,3.80732,0,0,1,224.71484,44.7549Z"></path> </svg>,
  },
  toc: {
    extraContent: <ExtraTox />,
  },
  docsRepositoryBase: 'https://github.com/kalanakt/All-Url-Uploader/docs',
  footer: {
    component: null,
  },
  faviconGlyph: '(o)'
}

export default config
