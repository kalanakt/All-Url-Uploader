import styles from './extratox.module.css'

function ExtraTox() {
  return (
    <div className={styles.container}>
      <span className={styles.h}>Project Links</span>
      <div className={styles.sponsors}>
        <div className={styles.bg}>
          <a
            href="https://github.com/kalanakt/All-Url-Uploader"
            className={styles.text}
            target="_blank"
            rel="noreferrer"
          >
            Repository
          </a>
        </div>
      </div>
      <div className={styles.bgt}>
        <a
          href="https://github.com/kalanakt/All-Url-Uploader/discussions"
          className={styles.text}
          target="_blank"
          rel="noreferrer"
        >
          Discussions
        </a>
      </div>
    </div>
  )
}

export default ExtraTox
