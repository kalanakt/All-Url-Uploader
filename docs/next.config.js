const withNextra = require('nextra')({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.tsx',
  basePath: '/All-Url-Uploader/docs',
})

module.exports = withNextra()
