import React, { useState } from 'react';
import logo from './logo.svg';
import './App.css';

function App() {

  const [inputText, setInputText] = useState('');
  
  console.log('start');

  const getReverseString = () => inputText.split('').reduce(
    
    (accum, letter) => {

      console.log('accum: ', accum);
      console.log(`letter: ${letter}`);

      return letter + accum;
    },
    ''
  );

  const onChangeHandler = (event) => {
    setInputText(event.target.value);
  }  
  


  return (
    <div className="App">
      <input type="text" onChange={onChangeHandler} defaultValue=""/>
      <br></br>
      {getReverseString()}

      {/* <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header> */}
    </div>
  );
}

export default App;
