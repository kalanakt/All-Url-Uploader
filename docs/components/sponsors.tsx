// Example from https://beta.reactjs.org/learn

import React, { useState, useEffect } from "react";
import styles from './sponsors.module.css'

function Sponsors() {
  return (
    <div className={styles.container}>
      <div className={styles.sponsor_card}>
        <div className={styles.sponsor_cardh}>
          <div className={styles.sponsor_img}>
            <img className={styles.simg} src='./tmwad.png' alt='TMWAD IMG' width={200} height={50}/>
          </div>
          <div className={styles.sponsor_links}>
            <a href="/" target="_blank">TMWAD Telegram ↗</a>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function MyApp() {
  return <Sponsors />
}
