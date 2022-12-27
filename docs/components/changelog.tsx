// Example from https://beta.reactjs.org/learn

import React, { useState, useEffect } from "react";
import styles from './changelog.module.css'

function dateformate(date){
  const event = new Date(date)
  return event.toDateString()
}
function ChangeLog() {
  const [books, setBooks] = useState(null);

  useEffect(() => {
    getData();

    async function getData() {
      try {
        const response = await fetch(
          "https://api.github.com/repos/kalanakt/All-Url-Uploader/commits"
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
        <div className="books">
          {books.map((book: { commit: { message: string | number | boolean | React.ReactElement<any, string | React.JSXElementConstructor<any>> | React.ReactFragment | React.ReactPortal; author: { date: string | number | boolean | React.ReactElement<any, string | React.JSXElementConstructor<any>> | React.ReactFragment | React.ReactPortal; }; comment_count: string | number | boolean | React.ReactElement<any, string | React.JSXElementConstructor<any>> | React.ReactFragment | React.ReactPortal; verification: { verified: string | number | boolean | React.ReactElement<any, string | React.JSXElementConstructor<any>> | React.ReactFragment | React.ReactPortal; }; }; html_url: string; comments_url: string; author: {
            [x: string]: string; login: string; avatar_url: string; 
}; }, index: React.Key) => {
            return (
              <div key={index} className={styles.tmtimelineitem}>
                <h2>1.0.4 <span className={styles.uktextmuted}>({dateformate(book.commit.author.date)})</span></h2>
                <div className={styles.tmtimelineentry}>
                  <div className={styles.tmtimelineentrylabel}>
                    <span className={styles.ukbadge}>{book.commit.verification.verified ? <span className={styles.ukbadgesuccess}>Success</span> : <span className={styles.ukbadgedanger}>Fail</span>}</span>
                  </div>
                  <div className={styles.tmtimelineentrydata}>
                    <a href={book.html_url}>{book.commit.message}</a>
                  </div>
                </div>
                <div className={styles.iconset}>
                  <div className={styles.bicon}>Committer : <a href={book.author.html_url}><img className={styles.avatar} alt="github icon" src={book.author.avatar_url} width={25} height={25} /></a></div>
                  <div className={styles.bicon}> Comments : {book.commit.comment_count}</div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <span>404 : Page Not Found</span>
      )}
    </div>
  )
}

export default function MyApp() {
  return <ChangeLog />
}
