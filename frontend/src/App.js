import React, { useState, useEffect } from 'react';
import socketIOClient from 'socket.io-client';
import LiveChart from './LiveChart';

const endpoint = 'http://localhost:3000';

const App = () => {
    const [data, setData] = useState([]);

    useEffect(() => {
        const socket = socketIOClient(endpoint);

        socket.on('data', (incomingData) => {
            setData(prevData => [...prevData, incomingData]);
        });
        return () => socket.disconnect();
    }, []);

    return (
        <div>
            <h1>Jupiter's Synchrotron Emission from Juno's Perspective</h1>
            <LiveChart data={data} />
        </div>
    );
}

export default App;