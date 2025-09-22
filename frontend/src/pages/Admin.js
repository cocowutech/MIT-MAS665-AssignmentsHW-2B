import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Users, BookOpen, TrendingUp, Download, Settings, Eye } from 'lucide-react';

const Admin = () => {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    // Simulate loading admin data
    const loadAdminData = async () => {
      // In a real app, you'd make API calls here
      setTimeout(() => {
        setStats({
          total_users: 1250,
          total_assessments: 3420,
          completed_assessments: 2890,
          average_completion_time: 18.5,
          cefr_distribution: {
            'A1': 120,
            'A2': 450,
            'B1': 890,
            'B2': 720,
            'C1': 380,
            'C2': 150
          },
          exam_readiness: {
            ket: 0.75,
            pet: 0.68,
            fce: 0.52
          }
        });

        setUsers([
          { id: 1, name: 'John Doe', email: 'john@example.com', age: 14, total_assessments: 3, created_at: '2024-01-15' },
          { id: 2, name: 'Jane Smith', email: 'jane@example.com', age: 12, total_assessments: 5, created_at: '2024-01-20' },
          { id: 3, name: 'Mike Johnson', email: 'mike@example.com', age: 16, total_assessments: 2, created_at: '2024-01-25' }
        ]);

        setAssessments([
          { id: 1, user_id: 1, assessment_type: 'reading', status: 'completed', cefr_level: 'B1', started_at: '2024-01-15T10:00:00Z' },
          { id: 2, user_id: 2, assessment_type: 'speaking', status: 'completed', cefr_level: 'A2', started_at: '2024-01-20T14:30:00Z' },
          { id: 3, user_id: 3, assessment_type: 'writing', status: 'in_progress', cefr_level: null, started_at: '2024-01-25T09:15:00Z' }
        ]);

        setLoading(false);
      }, 1000);
    };

    loadAdminData();
  }, []);

  const cefrData = stats ? Object.entries(stats.cefr_distribution).map(([level, count]) => ({
    level,
    count,
    percentage: ((count / stats.completed_assessments) * 100).toFixed(1)
  })) : [];

  const examData = stats ? [
    { name: 'KET', value: stats.exam_readiness.ket * 100 },
    { name: 'PET', value: stats.exam_readiness.pet * 100 },
    { name: 'FCE', value: stats.exam_readiness.fce * 100 }
  ] : [];

  const COLORS = ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ef4444', '#ec4899'];

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading admin dashboard...</p>
      </div>
    );
  }

  return (
    <div className="admin">
      <div className="container">
        <div className="admin-header">
          <h1>Admin Dashboard</h1>
          <div className="admin-actions">
            <button className="btn btn-secondary">
              <Download size={16} />
              Export Data
            </button>
            <button className="btn btn-primary">
              <Settings size={16} />
              Settings
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="admin-tabs">
          <button 
            className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`tab ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            Users
          </button>
          <button 
            className={`tab ${activeTab === 'assessments' ? 'active' : ''}`}
            onClick={() => setActiveTab('assessments')}
          >
            Assessments
          </button>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="overview-content">
            {/* Stats Cards */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">
                  <Users size={24} />
                </div>
                <div className="stat-content">
                  <h3>{stats?.total_users.toLocaleString()}</h3>
                  <p>Total Users</p>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">
                  <BookOpen size={24} />
                </div>
                <div className="stat-content">
                  <h3>{stats?.total_assessments.toLocaleString()}</h3>
                  <p>Total Assessments</p>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">
                  <TrendingUp size={24} />
                </div>
                <div className="stat-content">
                  <h3>{stats?.average_completion_time} min</h3>
                  <p>Avg. Completion Time</p>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">
                  <Eye size={24} />
                </div>
                <div className="stat-content">
                  <h3>{((stats?.completed_assessments / stats?.total_assessments) * 100).toFixed(1)}%</h3>
                  <p>Completion Rate</p>
                </div>
              </div>
            </div>

            {/* Charts */}
            <div className="charts-grid">
              <div className="chart-card">
                <h3>CEFR Level Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={cefrData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="level" />
                    <YAxis />
                    <Tooltip formatter={(value) => [value, 'Students']} />
                    <Bar dataKey="count" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-card">
                <h3>Exam Readiness</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={examData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {examData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="users-content">
            <div className="content-header">
              <h2>User Management</h2>
              <div className="content-actions">
                <input 
                  type="text" 
                  placeholder="Search users..." 
                  className="form-input"
                  style={{ width: '200px' }}
                />
                <button className="btn btn-primary">Add User</button>
              </div>
            </div>

            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Age</th>
                    <th>Assessments</th>
                    <th>Joined</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td>{user.name}</td>
                      <td>{user.email}</td>
                      <td>{user.age}</td>
                      <td>{user.total_assessments}</td>
                      <td>{new Date(user.created_at).toLocaleDateString()}</td>
                      <td>
                        <button className="btn btn-secondary btn-sm">
                          <Eye size={14} />
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Assessments Tab */}
        {activeTab === 'assessments' && (
          <div className="assessments-content">
            <div className="content-header">
              <h2>Assessment Management</h2>
              <div className="content-actions">
                <select className="form-input" style={{ width: '150px' }}>
                  <option>All Types</option>
                  <option>Reading</option>
                  <option>Speaking</option>
                  <option>Writing</option>
                </select>
                <select className="form-input" style={{ width: '150px' }}>
                  <option>All Status</option>
                  <option>Completed</option>
                  <option>In Progress</option>
                </select>
                <button className="btn btn-primary">Export</button>
              </div>
            </div>

            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>User</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>CEFR Level</th>
                    <th>Started</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {assessments.map((assessment) => (
                    <tr key={assessment.id}>
                      <td>{assessment.id}</td>
                      <td>User {assessment.user_id}</td>
                      <td className="capitalize">{assessment.assessment_type}</td>
                      <td>
                        <span className={`status-badge ${assessment.status}`}>
                          {assessment.status}
                        </span>
                      </td>
                      <td>{assessment.cefr_level || 'N/A'}</td>
                      <td>{new Date(assessment.started_at).toLocaleDateString()}</td>
                      <td>
                        <button className="btn btn-secondary btn-sm">
                          <Eye size={14} />
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .admin {
          padding: 2rem 0;
        }

        .admin-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
        }

        .admin-header h1 {
          font-size: 2.5rem;
          font-weight: 700;
          color: #1e293b;
        }

        .admin-actions {
          display: flex;
          gap: 1rem;
        }

        .admin-tabs {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 2rem;
          border-bottom: 1px solid #e2e8f0;
        }

        .tab {
          padding: 0.75rem 1.5rem;
          border: none;
          background: none;
          color: #64748b;
          font-weight: 500;
          cursor: pointer;
          border-bottom: 2px solid transparent;
          transition: all 0.2s ease;
        }

        .tab:hover {
          color: #3b82f6;
        }

        .tab.active {
          color: #3b82f6;
          border-bottom-color: #3b82f6;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin-bottom: 3rem;
        }

        .stat-card {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .stat-icon {
          width: 3rem;
          height: 3rem;
          background: #f0f9ff;
          border-radius: 0.75rem;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #3b82f6;
        }

        .stat-content h3 {
          font-size: 2rem;
          font-weight: 700;
          color: #1e293b;
          margin: 0 0 0.25rem 0;
        }

        .stat-content p {
          color: #64748b;
          margin: 0;
          font-size: 0.875rem;
        }

        .charts-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 2rem;
        }

        .chart-card {
          background: white;
          border-radius: 1rem;
          padding: 2rem;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .chart-card h3 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 1.5rem;
        }

        .content-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
        }

        .content-header h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1e293b;
        }

        .content-actions {
          display: flex;
          gap: 1rem;
          align-items: center;
        }

        .table-container {
          background: white;
          border-radius: 1rem;
          overflow: hidden;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .data-table {
          width: 100%;
          border-collapse: collapse;
        }

        .data-table th {
          background: #f8fafc;
          padding: 1rem;
          text-align: left;
          font-weight: 600;
          color: #374151;
          border-bottom: 1px solid #e2e8f0;
        }

        .data-table td {
          padding: 1rem;
          border-bottom: 1px solid #e2e8f0;
          color: #64748b;
        }

        .data-table tr:hover {
          background: #f8fafc;
        }

        .status-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 1rem;
          font-size: 0.75rem;
          font-weight: 500;
          text-transform: capitalize;
        }

        .status-badge.completed {
          background: #d1fae5;
          color: #065f46;
        }

        .status-badge.in_progress {
          background: #fef3c7;
          color: #92400e;
        }

        .btn-sm {
          padding: 0.5rem 1rem;
          font-size: 0.75rem;
        }

        .capitalize {
          text-transform: capitalize;
        }

        @media (max-width: 768px) {
          .admin-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
          }

          .admin-actions {
            width: 100%;
            justify-content: flex-start;
          }

          .charts-grid {
            grid-template-columns: 1fr;
          }

          .content-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
          }

          .content-actions {
            width: 100%;
            flex-wrap: wrap;
          }

          .table-container {
            overflow-x: auto;
          }
        }
      `}</style>
    </div>
  );
};

export default Admin;
