import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import 'bulma/css/bulma.min.css';

function App() {
  // This is needed, otherwise the initial request would be executed twice
  const hasFetchedData = useRef(false);
  const [birthdates, setItems] = useState([]);
  
  useEffect(() => {
    async function fetchData() {
      try {
        await fetch('api/birthdays')
        .then(response => response.json())
        .then(data => setItems(data));
      } catch (e) {
        console.error('Error fetching api data', e);
      };
    };
    if (hasFetchedData.current === false) {
      fetchData();
      hasFetchedData.current = true;
    }
  }, []);

  function deleteRow(id) {
    setItems(birthdates.filter(item => item.id !== id));
    
  }

  return (
    <section className="section">
        <div className="container">
          <h1 className="title">
            Birthday management
          </h1>
          <p className="subtitle">
            Manage the birthdates of your friends and family here.
          </p>

          <table className="table">
            <thead>
              <tr>
                <th>Id</th>
                <th>Name</th>
                <th>Date of birth</th>
                <th>Remove</th>
              </tr>
            </thead>
            <tbody>
              {
                birthdates.map((birthdate) => (
                  <tr key={birthdate.id}>
                    <td>{birthdate.id}</td>
                    <td>{birthdate.name}</td>
                    <td>{birthdate.birthdate}</td>
                    <td><button className="delete" onClick={() => deleteRow(birthdate.id)}></button></td>
                  </tr>
                ))
              }
            </tbody>
          </table>
        </div>
      </section>
  );
 }

export default App;
