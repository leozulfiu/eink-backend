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
  const [submittedName, setSubmittedName] = useState(null);
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

  const deleteRow = (id) => {
    setBirthdates(birthdates.filter(item => item.id !== id));
    fetch(`api/birthdays/${id}`, {
      method: 'DELETE'
    });
  }

  const createNewBirthday = () => {
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
            setHasError(false);
            setSubmitted(true);
            setSubmittedName(json.name);
            setBirthdates([...birthdates, { id: json.id, name: json.name, birthdate: json.birthdate }]);
            setFormValues({
              name: '',
              birthdate: ''
            });
            break;
          case 500:
          default:
            setHasError(true);
            setError({ status: status, message: JSON.stringify(json) });
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
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(isoFormatDate).toLocaleDateString('en-DE', options);
  }

  const birthdayIn = (isoFormatDate) => {
    const d1 = new Date(isoFormatDate);
    const d2 = new Date();

    let dm = d1.getMonth() - d2.getMonth();
    let dd = d1.getDate() - d2.getDate();

    if (dd < 0) { dm -= 1; dd += 30; }
    if (dm < 0) { dm += 12; }

    const monthsText = `in ${dm} month${dm > 0 ? 's' : ''} and`;
    return `${dm > 0 ? monthsText : 'in'} ${dd} day${dd > 1 ? 's' : ''}`;
  }

  const getNextBirthday = (date) => {
    const currentDate = new Date();

    const birthday = new Date(date);
    birthday.setFullYear(currentDate.getFullYear());

    if (birthday - currentDate < 0) {
      birthday.setFullYear(currentDate.getFullYear() + 1);
    }
    return birthday;
  }

  const sortDatesAsc = (a, b) => {
    return getNextBirthday(a.birthdate) - getNextBirthday(b.birthdate);
  }

  const closeNotification = () => {
    setSubmitted(false);
    setSubmittedName(null);
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
            <input className="input" type="text" placeholder="Name" value={formValues.name} onChange={handleNameInputChange} />
          </div>
          <div className="column">
            <input className="input" type="text" placeholder="Birthdate (e.g. 12.7.1999)" value={formValues.birthdate} onChange={handleBirthdateInputChange} />
          </div>
          <div className="column">
            <button className="button is-primary" onClick={() => createNewBirthday()}>
              Add
            </button>
          </div>
        </div>

        {submitted && <div className="notification">
          <button className="delete" onClick={() => closeNotification()}></button>
          Birthdate with name '{submittedName}' successfully added
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
              birthdates.sort(sortDatesAsc).map((birthdate) => (
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
