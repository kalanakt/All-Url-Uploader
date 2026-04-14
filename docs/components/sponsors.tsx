import styles from './sponsors.module.css'

function Sponsors() {
  return (
    <div className={styles.container}>
      <div className={styles.sponsor_card}>
        <div className={styles.sponsor_cardh}>
          <div className={styles.sponsor_links}>
            <a
              href="https://github.com/kalanakt/All-Url-Uploader"
              target="_blank"
              rel="noreferrer"
            >
              Project repository ↗
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function SponsorsWidget() {
  return <Sponsors />
}
