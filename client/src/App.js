import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import FitnessClassManagement from "./FitnessClassManagement";
import AddClass from "./AddClass";

function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Fetch data from Flask backend
    fetch('http://localhost:5000/api/hello')
      .then((response) => response.json())
      .then((data) => setMessage(data.message))
      .catch((error) => console.error('Error:', error));
  }, []);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<FitnessClassManagement />} />
        <Route path="/add" element={<AddClass />} />
      </Routes>
    </Router>
  );
}


export default App;