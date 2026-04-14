import React, { useEffect, useState } from 'react'
import styles from './changelog.module.css'

type CommitItem = {
  html_url: string
  commit: {
    message: string
    author?: { date?: string }
    comment_count?: number
    verification?: { verified?: boolean }
  }
  author?: {
    html_url?: string
    avatar_url?: string
  } | null
}

function formatDate(date?: string) {
  if (!date) return 'Unknown date'
  return new Date(date).toDateString()
}

function ChangeLog() {
  const [commits, setCommits] = useState<CommitItem[] | null>(null)

  useEffect(() => {
    async function getData() {
      try {
        const response = await fetch(
          'https://api.github.com/repos/kalanakt/All-Url-Uploader/commits'
        )
        const data = (await response.json()) as CommitItem[]
        setCommits(data)
      } catch (error) {
        console.error(error)
        setCommits([])
      }
    }

    void getData()
  }, [])

  if (commits === null) {
    return <span>Loading commits...</span>
  }

  if (commits.length === 0) {
    return <span>No changelog data is available right now.</span>
  }

  return (
    <div className={styles.container}>
      <div className="books">
        {commits.map((commitItem, index) => (
          <div key={index} className={styles.tmtimelineitem}>
            <h2>
              Commit <span className={styles.uktextmuted}>({formatDate(commitItem.commit.author?.date)})</span>
            </h2>
            <div className={styles.tmtimelineentry}>
              <div className={styles.tmtimelineentrylabel}>
                <span className={styles.ukbadge}>
                  {commitItem.commit.verification?.verified ? (
                    <span className={styles.ukbadgesuccess}>Verified</span>
                  ) : (
                    <span className={styles.ukbadgedanger}>Unverified</span>
                  )}
                </span>
              </div>
              <div className={styles.tmtimelineentrydata}>
                <a href={commitItem.html_url}>{commitItem.commit.message}</a>
              </div>
            </div>
            <div className={styles.iconset}>
              <div className={styles.bicon}>
                Committer:{' '}
                {commitItem.author?.html_url && commitItem.author.avatar_url ? (
                  <a href={commitItem.author.html_url}>
                    <img
                      className={styles.avatar}
                      alt="GitHub avatar"
                      src={commitItem.author.avatar_url}
                      width={25}
                      height={25}
                    />
                  </a>
                ) : (
                  'Unknown'
                )}
              </div>
              <div className={styles.bicon}>
                Comments: {commitItem.commit.comment_count ?? 0}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function ChangelogWidget() {
  return <ChangeLog />
}
