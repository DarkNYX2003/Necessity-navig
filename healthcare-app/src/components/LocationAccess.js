import React from 'react';
import { useNavigate } from 'react-router-dom';

const LocationAccess = () => {
    const navigate = useNavigate();

    const requestLocation = () => {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const location = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                };
                localStorage.setItem('userLocation', JSON.stringify(location));
                navigate('/facilities');
            },
            (error) => {
                alert(error.message);
            }
        );
    };

    return (
        <div>
            <h2>Allow Location Access</h2>
            <button onClick={requestLocation}>Allow Location Access</button>
        </div>
    );
};

export default LocationAccess;
