import React from 'react';
import logo from './logo.svg';
import Anchorlink from './Anchorlink';

export default function Header(props) {
    return (
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Hello {props.userName}!
        </p>
        <Anchorlink nameOfUser={props.userName}/>
      </header>
    )
}