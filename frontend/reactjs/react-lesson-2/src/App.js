import React from 'react';
import logo from './logo.svg';
import './App.css';
import Header from './Header'


function App() {
  
  let nameOfPerson = window.prompt("Please enter your name", "Harry Potter");

  return (
    <div className="App">
      <Header userName={nameOfPerson}/>
    </div>
  );
}

export default App;
