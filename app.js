import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Pie, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const App = () => {
  const [sentimentData, setSentimentData] = useState({ sentiments: [], dates: [] });
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());
  const [filter, setFilter] = useState('');

  useEffect(() => {
    fetchSentimentData();
  }, [startDate, endDate, filter]);

  async function fetchSentimentData() {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/sentiments`, {
        params: { startDate, endDate, filter },
      });
      setSentimentData(response.data);
    } catch (error) {
      console.error('Error fetching sentiment data:', error);
    }
  }

  const { sentiments, dates } = sentimentData;

  const pieData = {
    labels: sentiments.map((data) => data.label),
    datasets: [
      {
        data: sentiments.map((data) => data.value),
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
        hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
      },
    ],
  };

  const lineData = {
    labels: dates,
    datasets: [
      {
        label: 'Sentiment Over Time',
        fill: false,
        lineTension: 0.1,
        backgroundColor: 'rgba(75,192,192,0.4)',
        borderColor: 'rgba(75,192,192,1)',
        borderCapStyle: 'butt',
        borderDash: [],
        borderDashOffset: 0.0,
        borderJoinStyle: 'miter',
        pointBorderColor: 'rgba(75,192,192,1)',
        pointBackgroundColor: '#fff',
        pointBorderWidth: 1,
        pointHoverRadius: 5,
        pointHoverBackgroundColor: 'rgba(75,192,192,1)',
        pointHoverBorderColor: 'rgba(220,220,220,1)',
        pointHoverBorderWidth: 2,
        pointRadius: 1,
        pointHitRadius: 10,
        data: sentiments.map((data) => data.value),
      },
    ],
  };

  return (
    <div className="App">
      <h1>Sentiment Analysis Tool</h1>
      <div>
        <DatePicker selected={startDate} onChange={(date) => setStartDate(date)} />
        <DatePicker selected={endDate} onChange={(date) => setEndDate(date)} />
        <input type="text" value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Filter by Source/Label"/>
      </div>
      <div>
        <h2>Sentiment Distribution</h2>
        <Pie data={pieData} />
      </div>
      <div>
        <h2>Sentiment Timeline</h2>
        <Line data={lineData} />
      </div>
    </div>
  );
};

export default App;