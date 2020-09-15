import React, { useState, useEffect } from 'react';
// import logo from './logo.svg';
import './App.css';
import Header from './Header'


console.log("outside the function");


function App() {
  
  const [nameOfPerson, setNameOfPerson] = useState('Harry the Henderson');

  useEffect(() => {
    let newNameOfPerson = window.prompt('What is your name?', nameOfPerson);
    setNameOfPerson(newNameOfPerson);
  }, []);

  return (
    <div className="App">
      <Header userName={nameOfPerson} setNameOfPerson={setNameOfPerson}/>
    </div>
  );
}

export default App;
