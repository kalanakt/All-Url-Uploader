// Example from https://beta.reactjs.org/learn

import React, { useState, useEffect } from "react";
import styles from './followers.module.css'

function Followers() {
  const [books, setBooks] = useState(null);

  useEffect(() => {
    getData();

    async function getData() {
      try {
        const response = await fetch(
          "https://api.github.com/users/kalanakt/followers"
        );
        const data = await response.json();
  
        setBooks(data);      
      } catch (error) {
        console.log(error);       
      }
    }
  }, []);
  return (
    <div className={styles.container}>
      {books ? (
        <div className={styles.avatars}>
          {books.map((book: {
            [x: string]: any; commit: { message: string; author: { date: string; };  verification: { verified: string | number | boolean | React.ReactElement<any, string | React.JSXElementConstructor<any>> | React.ReactFragment | React.ReactPortal; }; }; html_url: string; comments_url: string; author: {
            [x: string]: string; login: string; avatar_url: string; 
}; }, index: React.Key) => {
            return (
                  <div className={styles.avatars__item}>
                  <a href={book.html_url} target="_blank">
                      <img className={styles.avatars__image} src={book.avatar_url} alt={book.login} width={40} height={40} />
                  </a>
                  </div>
            );
          })}
          <a href="https://github.com/kalanakt" target="_blank"><div className={styles.more}>+</div></a>
        </div>
      ) :
      (
        <div>
          <span>404 Page Not Found.</span>
        </div>
      )} 
    </div>
  )
}

export default function MyApp() {
  return <Followers />
}
