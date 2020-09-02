import React from 'react';
import logo from './logo.svg';
import Anchorlink from './Anchorlink';

export default function Header() {
    return (
        <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Change <code>src/App.js</code> and save to reload.
        </p>
        <Anchorlink/>
      </header>
    )
}