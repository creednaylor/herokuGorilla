import React, { useState } from 'react';
// import logo from './logo.svg';
import Anchorlink from './Anchorlink';

export default function Header(props) {

  const [toggleState, setToggleState] = useState(true);
  
  const onNameChange = (event) => {
    let newNameOfPerson = event.target.value;
    props.setNameOfPerson(newNameOfPerson);
  }


  const [firstInput, setfirstInput] = useState('');
  const [secondInput, setsecondInput] = useState('');
  
  const onfirstInputChange = (event) => {
    setfirstInput(event.target.value);
  }  
  
  const onsecondInputChange = (event) => {
    setsecondInput(event.target.value);
  }


  const getOutput = () => {

    const firstNumber = Number.parseInt(firstInput);
    const secondNumber = Number.parseInt(secondInput);

    const isValid = !Number.isNaN(firstNumber) && !Number.isNaN(secondNumber);

    return isValid ? (firstNumber + secondNumber) : '';

  }


  function handleClick(event) {
    setToggleState(!toggleState);
  }


  return (
    <header className="App-header">
      Enter your name: <input type="text" onChange={onNameChange}/>
      <div onClick={handleClick}>
        {
          toggleState ? (<p>Hello, {props.userName}!</p>) : (<p>Welcome, {props.userName}, to this React site!</p>)
        } 
      </div>
      <Anchorlink nameOfUser={props.userName}/>
      <p>Calculate the sum of two numbers:</p>
      <input type="text" onChange={onfirstInputChange} defaultValue={firstInput}/>&nbsp;+&nbsp;<input type="text" onChange={onsecondInputChange} defaultValue={secondInput}/> = {getOutput()}
    </header>
  );
}