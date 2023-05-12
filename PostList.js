import React, { useState, useEffect } from "react";
import fetch from "isomorphic-fetch";
import { v4 as uuidv4 } from 'uuid';

function PostList() {
  const [tweets, setTweets] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    async function fetchTweets() {
      const response = await fetch("http://localhost:8000/tweets", {
        credentials: 'include' // include cookies in the request
      });
      const data = await response.json();
      setTweets(data.tweets);
    }

    fetchTweets();
  }, []);

  useEffect(() => {
    const searchTermCookie = getCookie("search_term");
    if (searchTermCookie) {
      setSearchTerm(searchTermCookie);
    }
  }, []);

  const handleSearch = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
    setCookie("search_term", value);
  };

  const filteredTweets = tweets.filter((tweet) =>
    tweet.search_term.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      <input
        type="text"
        placeholder="Search tweets by search term"
        value={searchTerm}
        onChange={handleSearch}
      />
      {filteredTweets.map((tweet) => (
        <div key={uuidv4()}>
          <h2>{tweet.search_term}</h2>
          {tweet.tweets.map((t) => (
            <p key={uuidv4()}>{t.text}</p>
          ))}
        </div>
      ))}
    </div>
  );
}

function setCookie(key, value) {
  document.cookie = `${key}=${value}; path=/;`;
}

function getCookie(key) {
  const name = `${key}=`;
  const decodedCookie = decodeURIComponent(document.cookie);
  const cookieArray = decodedCookie.split(';');
  for(let i = 0; i <cookieArray.length; i++) {
    let cookie = cookieArray[i];
    while (cookie.charAt(0) === ' ') {
      cookie = cookie.substring(1);
    }
    if (cookie.indexOf(name) === 0) {
      return cookie.substring(name.length, cookie.length);
    }
  }
  return "";
}

export default PostList;
