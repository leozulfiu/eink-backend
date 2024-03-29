import React, { useState, useEffect } from "react";
import "./App.css";
import "bulma/css/bulma.min.css";

function App() {
  const [birthdates, setBirthdates] = useState([]);
  const [formValues, setFormValues] = useState({
    name: "",
    birthdate: "",
  });
  const [submitted, setSubmitted] = useState(false);
  const [submittedName, setSubmittedName] = useState(null);
  const [hasError, setHasError] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        await fetch("api/birthdays")
          .then((response) => response.json())
          .then((data) => setBirthdates(data));
      } catch (e) {
        console.error("Error fetching api data", e);
      }
    }
    fetchData();
  }, []);

  const deleteRow = (id) => {
    setBirthdates(birthdates.filter((item) => item.id !== id));
    fetch(`api/birthdays/${id}`, {
      method: "DELETE",
    });
  };

  const createNewBirthday = () => {
    fetch("api/birthdays", {
      method: "POST",
      headers: {
        "Content-type": "application/json",
      },
      body: JSON.stringify({
        name: formValues.name,
        birthdate: formValues.birthdate,
      }),
    })
      .then((response) => {
        return new Promise((resolve) =>
          response.json().then((json) =>
            resolve({
              status: response.status,
              ok: response.ok,
              json,
            })
          )
        );
      })
      .then(({ status, json, ok }) => {
        const message = json.message;
        switch (status) {
          case 201:
          case 200:
            setHasError(false);
            setSubmitted(true);
            setSubmittedName(json.name);
            setBirthdates([
              ...birthdates,
              { id: json.id, name: json.name, birthdate: json.birthdate },
            ]);
            setFormValues({
              name: "",
              birthdate: "",
            });
            break;
          case 500:
          default:
            setHasError(true);
            setError({ status: status, message: JSON.stringify(json) });
        }
      });
  };

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
    const options = { year: "numeric", month: "long", day: "numeric" };
    return new Date(isoFormatDate).toLocaleDateString("en-DE", options);
  };

  const birthdayIn = (isoFormatDate) => {
    const targetDate = new Date(isoFormatDate);
    const currentDate = new Date();

    targetDate.setFullYear(currentDate.getFullYear());
    if (targetDate < currentDate) {
      targetDate.setFullYear(currentDate.getFullYear() + 1);
    }

    if (
      targetDate.getDate() === currentDate.getDate() &&
      targetDate.getMonth() === currentDate.getMonth()
    ) {
      return "today";
    }

    let monthDifference = targetDate.getMonth() - currentDate.getMonth();
    let dayDifference = targetDate.getDate() - currentDate.getDate();

    if (dayDifference < 0) {
      monthDifference--;
      const prevMonthLastDay = new Date(
        targetDate.getFullYear(),
        targetDate.getMonth(),
        0
      ).getDate();
      dayDifference += prevMonthLastDay;
    }

    if (monthDifference < 0) {
      // Borrow months from the next year
      monthDifference += 12;
    }

    const monthsText =
      monthDifference > 0
        ? `in ${monthDifference} month${monthDifference !== 1 ? "s" : ""} and `
        : "in ";
    return `${monthsText}${dayDifference} day${dayDifference !== 1 ? "s" : ""}`;
  };

  const getNextBirthday = (date) => {
    const currentDate = new Date();

    const birthday = new Date(date);
    birthday.setFullYear(currentDate.getFullYear());

    if (birthday - currentDate < 0) {
      birthday.setFullYear(currentDate.getFullYear() + 1);
    }
    return birthday;
  };

  const isToday = (date) => {
    const today = new Date();
    return (
      date.getDate() === today.getDate() && date.getMonth() === today.getMonth()
    );
  };

  const sortDatesAsc = (a, b) => {
    const nextBirthdayA = getNextBirthday(a.birthdate);
    const nextBirthdayB = getNextBirthday(b.birthdate);

    const isAToday = isToday(nextBirthdayA);
    const isBToday = isToday(nextBirthdayB);

    if (isAToday && !isBToday) {
      return -1;
    } else if (!isAToday && isBToday) {
      return 1;
    }
    return nextBirthdayA - nextBirthdayB;
  };

  const closeNotification = () => {
    setSubmitted(false);
    setSubmittedName(null);
  };

  return (
    <div className="container">
      <section className="section">
        <h1 className="title">Birthday management</h1>
        <p className="subtitle">
          Manage the birthdates of your friends and family here.
        </p>

        <div className="columns">
          <div className="column">
            <input
              className="input"
              type="text"
              placeholder="Name"
              value={formValues.name}
              onChange={handleNameInputChange}
            />
          </div>
          <div className="column">
            <input
              className="input"
              type="text"
              placeholder="Birthdate (e.g. 12.7.1999)"
              value={formValues.birthdate}
              onChange={handleBirthdateInputChange}
            />
          </div>
          <div className="column">
            <button
              className="button is-primary"
              onClick={() => createNewBirthday()}
            >
              Add
            </button>
          </div>
        </div>

        {submitted && (
          <div className="notification is-primary">
            <button
              className="delete"
              onClick={() => closeNotification()}
            ></button>
            Birthdate with name '{submittedName}' successfully added
          </div>
        )}
        {hasError && (
          <div className="notification is-warning">
            There was an error adding the birthday. {error.status}.{" "}
            {error.message}
          </div>
        )}
      </section>
      <section className="section pt-0">
        <table className="table is-striped is-hoverable is-fullwidth">
          <thead>
            <tr>
              <th>Name</th>
              <th>Date of birth</th>
              <th>Birthday in</th>
              <th>Remove</th>
            </tr>
          </thead>
          <tbody>
            {birthdates.sort(sortDatesAsc).map((birthdate) => (
              <tr key={birthdate.id}>
                <td title={"Id: " + birthdate.id}>{birthdate.name}</td>
                <td>{formatDate(birthdate.birthdate)}</td>
                <td>{birthdayIn(birthdate.birthdate)}</td>
                <td>
                  <button
                    className="delete"
                    onClick={() => deleteRow(birthdate.id)}
                  ></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

export default App;
