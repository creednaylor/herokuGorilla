import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import AppName from './App1';
import {App2 as AppTwo} from './App2';
import * as serviceWorker from './serviceWorker';

ReactDOM.render(
  <React.StrictMode>
    <AppName />
  </React.StrictMode>,
  document.getElementById('root1')
);

ReactDOM.render(
  <React.StrictMode>
    <AppTwo />
  </React.StrictMode>,
  document.getElementById('root2')
);


// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
