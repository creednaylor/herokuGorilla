import React from 'react';
// import logo from './logo.svg';
import Anchorlink from './Anchorlink';

export default function Header(props) {
    return (
      <header className="App-header">
        <p>
          Hello {props.userName}!
        </p>
        <Anchorlink nameOfUser={props.userName}/>
      </header>
    )
}