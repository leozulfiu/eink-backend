import React, { useState, useEffect } from 'react';
import './App.css';
import 'bulma/css/bulma.min.css';

function App() {
  const [birthdates, setBirthdates] = useState([]);
  const [formValues, setFormValues] = useState({
    name: '',
    birthdate: ''
  });
  const [submitted, setSubmitted] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        await fetch('api/birthdays')
        .then(response => response.json())
        .then(data => setBirthdates(data));
      } catch (e) {
        console.error('Error fetching api data', e);
      };
    };
    fetchData();
  }, []);

  function deleteRow(id) {
    setBirthdates(birthdates.filter(item => item.id !== id));
    fetch(`api/birthdays/${id}`, {
      method: 'DELETE'
    });
  }

  function createNewBirthday() {
    fetch('api/birthdays', {
      method: 'POST',
      headers: {
        "Content-type": "application/json"
      },
      body: JSON.stringify({
        name: formValues.name,
        birthdate: formValues.birthdate
      })
    }).then((response) => {
      return new Promise((resolve) => response.json()
        .then((json) => resolve({
          status: response.status,
          ok: response.ok,
          json,
        })));
    })
    .then(({ status, json, ok }) => {
      const message = json.message;
      switch (status) {
        case 201:
        case 200:
          setSubmitted(true);
          setBirthdates([...birthdates, {id: json.id, name: json.name, birthdate: json.birthdate}]);
          setFormValues({
            name: '',
            birthdate: ''
          });
          break;
        case 500:
        default:
          setHasError(true);
          setError({status: status, message: JSON.stringify(json)});
      }
    });
  }

  const handleNameInputChange = (event) => {
    setSubmitted(false);
    event.persist();
    setFormValues((values) => ({
      ...values,
      name: event.target.value,
    }));
  };

  const handleBirthdateInputChange = (event) => {
    event.persist();
    setFormValues((values) => ({
      ...values,
      birthdate: event.target.value,
    }));
  };

  const formatDate = (isoFormatDate) => {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(isoFormatDate).toLocaleDateString('en-DE', options);
  }

  const birthdayIn = (isoFormatDate) => {
    return 'in 3 months and 14 days';
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

          <div className="columns">
            <div className="column">
              <input className="input" type="text" placeholder="Name" value={formValues.name} onChange={handleNameInputChange}/>
            </div>
            <div className="column">
              <input className="input" type="text" placeholder="Birthdate (e.g. 12.7.1999)" value={formValues.birthdate} onChange={handleBirthdateInputChange}/>
            </div>
            <div className="column">
            <button className="button is-primary" onClick={() => createNewBirthday()}>
              Add
            </button>
            </div>
          </div>

          {submitted && <div className="notification">
            Birthdate with name '{formValues.name}' successfully added
          </div>}
          {hasError && <div className="notification is-warning">
            There was an error during submission. {error.status}. {error.message}
          </div>}

          <table className="table">
            <thead>
              <tr>
                <th>Id</th>
                <th>Name</th>
                <th>Date of birth</th>
                <th>Birthday in</th>
                <th>Remove</th>
              </tr>
            </thead>
            <tbody>
              {
                birthdates.map((birthdate) => (
                  <tr key={birthdate.id}>
                    <td>{birthdate.id}</td>
                    <td>{birthdate.name}</td>
                    <td>{formatDate(birthdate.birthdate)}</td>
                    <td>{birthdayIn(birthdate.birthdate)}</td>
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
