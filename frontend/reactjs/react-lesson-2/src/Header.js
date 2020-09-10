import React, { useState } from 'react';
// import logo from './logo.svg';
import Anchorlink from './Anchorlink';

export default function Header(props) {

  const [toggleState, setToggleState] = useState(true);
  
  const onNameChange = (event) => {
    let newNameOfPerson = event.target.value;
    props.setNameOfPerson(newNameOfPerson);
  }


  const [firstNumber, setFirstNumber] = useState(0);
  const [secondNumber, setSecondNumber] = useState(7);
  
  const onFirstNumberChange = (event) => {
    setFirstNumber(event.target.value);
  }


  // const [toggleState, setToggleState] = useState(true);
  
  // const onNameChange = (event) => {
  //   let newNameOfPerson = event.target.value;
  //   props.setNameOfPerson(newNameOfPerson);
  // }

  let sum = parseInt(firstNumber) + 7;

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
      <input type="text" onChange={onFirstNumberChange} defaultValue={firstNumber}/>&nbsp;+&nbsp;<input type="text" onChange={onFirstNumberChange} defaultValue={secondNumber}/> = {sum}
    </header>
  );
}