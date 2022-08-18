import React from 'react';
import './App.css';
import 'bulma/css/bulma.min.css';

class App extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      items: [],
      dataIsLoaded: false
    };
  }

  componentDidMount() {
    fetch("api/birthdays")
      .then((res) => res.json())
      .then((json) => {
        this.setState({
          items: json,
          dataIsLoaded: true
        });
      })
  }
  render() {
    const { dataIsLoaded, items } = this.state;
    if (!dataIsLoaded) return <div>
      <h1> Pleses wait some time.... </h1> </div>;

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
                items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.name}</td>
                    <td>{item.birthdate}</td>
                    <td><button className="delete"></button></td>
                  </tr>

                ))
              }
            </tbody>
          </table>
        </div>
      </section>
    );
  }
}

export default App;
