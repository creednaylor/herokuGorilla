import React, { useState, useEffect } from 'react';
// import logo from './logo.svg';
import './App.css';
import Header from './Header'


console.log("outside the function");


function App() {
  
  const [nameOfPerson, setNameOfPerson] = useState('Harry Potter');

  const onNameChange = (event) => {
    let newNameOfPerson = event.target.value;
    setNameOfPerson(newNameOfPerson);
  }

  useEffect(() => {
    let newNameOfPerson = window.prompt('What is your name?', nameOfPerson);
    setNameOfPerson(newNameOfPerson);
  }, []);

  return (
    <div className="App">
      <Header userName={nameOfPerson}/>
      <input type="text" onChange={onNameChange}/>
    </div>
  );
}

export default App;
