// Example from https://beta.reactjs.org/learn

import React, { useState, useEffect } from "react";
import ReactMarkdown from 'react-markdown'
import styles from './releases.module.css'
import gfm from 'remark-gfm'

function dateformate(date){
  const event = new Date(date)
  return event.toDateString()
}
function Releases() {
  const [books, setBooks] = useState(null);

  useEffect(() => {
    getData();

    async function getData() {
      try {
        const response = await fetch(
          "https://api.github.com/repos/kalanakt/All-Url-Uploader/releases"
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
          {books.map((book: {
            [x: string]: any; commit: { message: string | number | boolean | React.ReactElement<any, string | React.JSXElementConstructor<any>> | React.ReactFragment | React.ReactPortal; author: { date: string; }; comment_count: string | number | boolean | React.ReactElement<any, string | React.JSXElementConstructor<any>> | React.ReactFragment | React.ReactPortal; verification: { verified: string | number | boolean | React.ReactElement<any, string | React.JSXElementConstructor<any>> | React.ReactFragment | React.ReactPortal; }; }; html_url: string; comments_url: string; author: {
            [x: string]: string; login: string; avatar_url: string; 
}; }, index: React.Key) => {
            return (
              <div key={index} className={styles.tmtimelineitem}>
                <span><a href={book.html_url}>{book.tag_name}</a> <span className={styles.uktextmuted}>({dateformate(book.published_at)})</span></span>
                <div className={styles.tmtimelineentry}>
                  <div className={styles.tmtimelineentrylabel}>
                    <span className={styles.ukbadge}>{book.draft ? <span className={styles.ukbadgesuccess}>Darft</span> : book.prerelease ? <span className={styles.ukbadgewarning}>Pre release</span> : <span className={styles.ukbadgesuccess}>Release</span>}</span>
                  </div>
                  <div className={styles.tmtimelineentrydata}>
                    <ReactMarkdown remarkPlugins={[gfm]}>{book.body.split(' ').slice(0, 20).join(' ')}</ReactMarkdown>
                  </div>
                  <a href={book.html_url}><span className={styles.readmore}>Read More ...</span></a>
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
  return <Releases />
}
