const isGithubActions = process.env.GITHUB_ACTIONS || false

let assetPrefix = 'docs'
let basePath = 'docs/'

if (isGithubActions) {
  const repo = process.env.GITHUB_REPOSITORY.replace(/.*?\//, '')

  assetPrefix = `/${repo}/docs/`
  basePath = `/${repo}/docs`
}

const withNextra = require('nextra')({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.tsx',
  assetPrefix: assetPrefix,
  basePath: basePath,
  images: {
    loader: 'imgix',
    path: 'the "domain" of your Imigix source',
  },
})

module.exports = withNextra()
