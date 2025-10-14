
import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [goal, setGoal] = useState('');
  const [plan, setPlan] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePlanGeneration = async () => {
    if (!goal) {
      setError('Please enter a goal.');
      return;
    }

    setLoading(true);
    setError('');
    setPlan('');

    try {
      const response = await axios.post('http://127.0.0.1:5000/plan', { goal });
      setPlan(response.data.plan);
    } catch (err) {
      setError('Failed to generate plan. Please ensure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveChat = async () => {
    if (!goal || !plan) {
      setError('No chat to save.');
      return;
    }

    try {
      await axios.post('http://127.0.0.1:5000/save_chat', {
        user_query: goal,
        llm_answer: plan,
      });
      alert('Chat saved successfully!');
    } catch (err) {
      setError('Failed to save chat.');
      console.error(err);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Smart Task Planner</h1>
        <div className="input-container">
          <input
            type="text"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="Enter your goal (e.g., Launch a product in 2 weeks)"
          />
          <button onClick={handlePlanGeneration} disabled={loading}>
            {loading ? 'Generating...' : 'Generate Plan'}
          </button>
        </div>
        {error && <p className="error">{error}</p>}
        {plan && (
          <div className="plan-container">
            <h2>Generated Plan:</h2>
            <pre>{plan}</pre>
            <button onClick={handleSaveChat}>Save Chat</button>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
