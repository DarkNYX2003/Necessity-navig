import React from 'react';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
    const navigate = useNavigate();

    const handleLocationAccessClick = () => {
        navigate('/location-access');
    };

    return (
        <div>
            <h1>Dashboard</h1>
            <p>Welcome to the dashboard!</p>
            <button onClick={handleLocationAccessClick}>HEALTHCARE FACILITIES</button>
        </div>
    );
}

export default Dashboard;
