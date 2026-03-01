import React, { useEffect, useState } from 'react';
import { getTrades, getSummary, startBot, stopBot } from './api';
import { Play, Square, TrendingUp, TrendingDown, DollarSign, Activity, AlertTriangle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const [trades, setTrades] = useState([]);
  const [summary, setSummary] = useState([]);
  const [status, setStatus] = useState('Active');
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    try {
      const tradesData = await getTrades();
      const summaryData = await getSummary();
      setTrades(tradesData);
      setSummary(summaryData);
    } catch (error) {
      console.error("Error fetching data", error);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    setLoading(true);
    await startBot();
    setStatus('Active');
    setLoading(false);
  };

  const handleStop = async () => {
    setLoading(true);
    await stopBot();
    setStatus('Stopped');
    setLoading(false);
  };

  // Calculate totals for cards
  const todaySummary = summary.length > 0 ? summary[0] : { total_trades: 0, wins: 0, losses: 0, total_pnl: 0 };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex justify-between items-center bg-gray-800 p-4 rounded-lg shadow-lg">
          <div>
            <h1 className="text-2xl font-bold text-blue-400 flex items-center gap-2">
              <Activity /> AlgoTrading Pro Dashboard
            </h1>
            <p className="text-gray-400 text-sm">Automated NIFTY/BANKNIFTY Trading Bot</p>
          </div>
          <div className="flex items-center gap-4">
            <div className={`px-3 py-1 rounded-full text-sm font-semibold ${status === 'Active' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
              Status: {status}
            </div>
            <button 
              onClick={handleStart} 
              disabled={loading || status === 'Active'}
              className="p-2 bg-green-600 hover:bg-green-700 rounded-md disabled:opacity-50 transition"
            >
              <Play size={20} />
            </button>
            <button 
              onClick={handleStop} 
              disabled={loading || status === 'Stopped'}
              className="p-2 bg-red-600 hover:bg-red-700 rounded-md disabled:opacity-50 transition"
            >
              <Square size={20} />
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
            <div className="text-gray-400 text-sm flex items-center gap-2"><DollarSign size={16}/> Today's P&L</div>
            <div className={`text-2xl font-bold ${todaySummary.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              ₹{todaySummary.total_pnl.toFixed(2)}
            </div>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
            <div className="text-gray-400 text-sm flex items-center gap-2"><TrendingUp size={16}/> Win Rate</div>
            <div className="text-2xl font-bold text-blue-400">
              {todaySummary.total_trades > 0 ? ((todaySummary.wins / todaySummary.total_trades) * 100).toFixed(0) : 0}%
            </div>
            <div className="text-xs text-gray-500">{todaySummary.wins} Wins / {todaySummary.losses} Losses</div>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
            <div className="text-gray-400 text-sm flex items-center gap-2"><Activity size={16}/> Total Trades</div>
            <div className="text-2xl font-bold text-purple-400">{todaySummary.total_trades}</div>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
            <div className="text-gray-400 text-sm flex items-center gap-2"><AlertTriangle size={16}/> Drawdown</div>
            <div className="text-2xl font-bold text-orange-400">₹{todaySummary.max_drawdown || 0}</div>
          </div>
        </div>

        {/* Chart */}
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 h-80">
          <h2 className="text-lg font-semibold mb-4 text-gray-300">Daily Performance</h2>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={summary}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
              <Legend />
              <Line type="monotone" dataKey="total_pnl" stroke="#60A5FA" strokeWidth={2} name="P&L" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Trades Table */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="p-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-gray-300">Recent Trades</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-gray-700 text-gray-400 uppercase text-xs">
                <tr>
                  <th className="p-4">Time</th>
                  <th className="p-4">Symbol</th>
                  <th className="p-4">Type</th>
                  <th className="p-4">Entry</th>
                  <th className="p-4">Exit</th>
                  <th className="p-4">P&L</th>
                  <th className="p-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700 text-sm">
                {trades.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="p-4 text-center text-gray-500">No trades today</td>
                  </tr>
                ) : (
                  trades.map((trade) => (
                    <tr key={trade.id} className="hover:bg-gray-750">
                      <td className="p-4">{new Date(trade.entry_time).toLocaleTimeString()}</td>
                      <td className="p-4 font-medium text-white">{trade.symbol}</td>
                      <td className={`p-4 font-bold ${trade.option_type === 'CE' ? 'text-green-400' : 'text-red-400'}`}>
                        {trade.option_type}
                      </td>
                      <td className="p-4">{trade.entry_price}</td>
                      <td className="p-4">{trade.exit_price || '-'}</td>
                      <td className={`p-4 font-bold ${trade.pnl > 0 ? 'text-green-400' : trade.pnl < 0 ? 'text-red-400' : 'text-gray-400'}`}>
                        {trade.pnl ? `₹${trade.pnl.toFixed(2)}` : '-'}
                      </td>
                      <td className="p-4">
                        <span className={`px-2 py-1 rounded text-xs ${trade.status === 'OPEN' ? 'bg-blue-900 text-blue-300' : 'bg-gray-700 text-gray-300'}`}>
                          {trade.status}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
