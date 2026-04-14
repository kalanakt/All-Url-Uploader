import React, { useEffect, useState } from 'react'
import styles from './followers.module.css'

type Follower = {
  html_url: string
  login: string
  avatar_url: string
}

function Followers() {
  const [followers, setFollowers] = useState<Follower[] | null>(null)

  useEffect(() => {
    async function getData() {
      try {
        const response = await fetch('https://api.github.com/users/kalanakt/followers')
        const data = (await response.json()) as Follower[]
        setFollowers(data)
      } catch (error) {
        console.error(error)
        setFollowers([])
      }
    }

    void getData()
  }, [])

  if (followers === null) {
    return <span>Loading followers...</span>
  }

  if (followers.length === 0) {
    return <span>No follower data is available right now.</span>
  }

  return (
    <div className={styles.container}>
      <div className={styles.avatars}>
        {followers.map((follower) => (
          <div key={follower.login} className={styles.avatars__item}>
            <a href={follower.html_url} target="_blank" rel="noreferrer">
              <img
                className={styles.avatars__image}
                src={follower.avatar_url}
                alt={follower.login}
                width={40}
                height={40}
              />
            </a>
          </div>
        ))}
        <a href="https://github.com/kalanakt" target="_blank" rel="noreferrer">
          <div className={styles.more}>+</div>
        </a>
      </div>
    </div>
  )
}

export default function FollowersWidget() {
  return <Followers />
}
