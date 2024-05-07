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

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement);

const App = () => {
  const [sentimentData, setSentimentData] = useState({ sentiments: [], dates: [] });
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());
  const [filter, setFilter] = useState('');

  useEffect(() => {
    const fetchSentimentData = async () => {
      try {
        const { data } = await axios.get(`${process.env.REACT_APP_API_URL}/sentiments`, {
          params: { startDate, endDate, filter },
        });
        setSentimentData(data);
      } catch (error) {
        console.error('Error fetching sentiment data:', error);
      }
    };

    fetchSentimentData();
  }, [startDate, endDate, filter]);

  const downloadCSV = () => {
    const header = 'Date,Label,Value\n';
    const rows = sentimentData.dates.flatMap((date, index) =>
      sentimentData.sentiments.map(sentiment => `${date},${sentiment.label},${sentiment.value}`)
    );
    const csvString = [header, ...rows].join('\n');
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'sentiment_analysis_data.csv';
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const createChartData = (labels, data, backgroundColors = ['#FF6384', '#36A2EB', '#FFCE56']) => ({
    labels,
    datasets: [{
      data,
      backgroundColor: backgroundColors,
      hoverBackgroundColor: backgroundColors,
    }],
  });

  const pieData = createChartData(
    sentimentData.sentiments.map(s => s.label),
    sentimentData.sentiments.map(s => s.value),
  );

  const lineData = {
    labels: sentimentData.dates,
    datasets: [{
      label: 'Sentiment Over Time',
      ...lineChartDatasetOptions,
      data: sentimentData.sentiments.map(s => s.value),
    }],
  };

  return (
    <div className="App">
      <h1>Sentiment Analysis Tool</h1>
      <div>
        <DatePicker selected={startDate} onChange={date => setStartDate(date)} />
        <DatePicker selected={endDate} onChange={date => setEndDate(date)} />
        <input type="text" value={filter} onChange={e => setFilter(e.target.value)} placeholder="Filter by Source/Label"/>
        <button onClick={downloadCSV}>Download CSV</button>
      </div>
      <PieChartSection data={pieData} />
      <LineChartSection data={lineData} />
    </div>
  );
};

const chartSectionStyles = { marginBottom: 40 };

const PieChartSection = ({ data }) => (
  <div style={chartSectionStyles}>
    <h2>Sentiment Distribution</h2>
    <Pie data={data} />
  </div>
);

const LineChartSection = ({ data }) => (
  <div style={chartSectionStyles}>
    <h2>Sentiment Timeline</h2>
    <Line data={data} />
  </div>
);

const lineChartDatasetOptions = {
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
};

export default App;