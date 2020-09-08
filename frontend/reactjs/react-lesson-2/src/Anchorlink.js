import React from 'react';

export default function Anchorlink(props) {
    return (
        <a
        className="App-link"
        href="https://reactjs.org"
        target="_blank"
        rel="noopener noreferrer">
        Learn a little bit of React, {props.nameOfUser}
        </a>
    )
}
