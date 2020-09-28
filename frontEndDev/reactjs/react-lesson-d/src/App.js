import React, { useState } from 'react';
import logo from './logo.svg';
import './App.css';


function App() {

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [messageToPrint, setMessageToPrint] = useState('');

  const submitButtonHandler = () => {

    if (username == 'username' && password == 'a') {
      setMessageToPrint(`Login successful. Username: ${username}. Password: ${password}.`);
    }
    else {
      setMessageToPrint(`Login failed.`)
    }

  }

  const usernameHandler = (event) => {
    setUsername(event.target.value);
  }

  const passwordHandler = (event) => {
    setPassword(event.target.value);
  }

  return (
    <div className="App">
      <form>
        Username: <input type="text" defaultValue="" onChange={usernameHandler}/>
        <br></br>
        Password: <input type="password" defaultValue="" onChange={passwordHandler} pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}" title="Must contain at least one number and one uppercase and lowercase letter, and at least 8 or more characters" required/>
        <br></br>
        <input type="submit" value="Submit" onClick={submitButtonHandler} />
      </form>
      {messageToPrint}
    </div>
  );
}

export default App;
