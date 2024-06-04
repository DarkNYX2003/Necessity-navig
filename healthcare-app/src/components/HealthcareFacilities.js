import React, { useState, useEffect } from 'react';
import axios from 'axios';

const HealthcareFacilities = () => {
    const [facilities, setFacilities] = useState([]);
    const location = JSON.parse(localStorage.getItem('userLocation'));

    useEffect(() => {
        if (location) {
            fetchFacilities(location);
        }
    }, [location]);

    const fetchFacilities = async (location) => {
        try {
            const response = await axios.post('http://localhost:8000/api/facilities/', location);
            setFacilities(response.data);
        } catch (error) {
            alert('Error fetching facilities');
        }
    };

    return (
        <div>
            <h2>Healthcare Facilities Near You</h2>
            <ul>
                {facilities.map((facility, index) => (
                    <li key={index}>
                        <h3>{facility.name}</h3>
                        <p>{facility.address}</p>
                        <p>Average Pricing: ${facility.average_pricing}</p>
                        <p>Estimated Travel Time: {facility.travel_time}</p>
                        <p>Distance:{facility.distance}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default HealthcareFacilities;
