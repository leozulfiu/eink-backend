import React from 'react';
import './App.css';

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
            <h1> Pleses wait some time.... </h1> </div> ;

        return (
            <div className = "App">
                <h1> Fetch data from an api in react </h1>  {
                    items.map((item) => (
                    <ol key = { item.id } >
                        Full_Name: { item.name },
                        Birthdate: { item.birthdate }
                        </ol>
                    ))
                }
            </div>
        );
    }
}

export default App;
