import React from 'react';
import Plot from 'react-plotly.js';

function LiveChart({ data }) {
    const x = data.map(item => item.timestamp);
    const y = data.map(item => item.antenna_temp);

    const plotData = [
        {
            x: x,
            y: y,
            type: 'scatter',
            mode: 'lines',
            name: 'Antenna Temperature',
        }
    ];

    const layout = {
        title: 'Live Data',
        xaxis: {
            title: 'Timestamp',
        },
        yaxis: {
            title: 'Antenna Temperature',
        },
    };

    return (
        <Plot
            data={[
                {
                    x: x,
                    y: y,
                    type: 'scatter',
                    mode: 'lines+markers',
                    marker: {color: 'red'},
                },
            ]}
            layout={{ width: 720, height: 440, title: 'Live Data' }}
        />
    );
}