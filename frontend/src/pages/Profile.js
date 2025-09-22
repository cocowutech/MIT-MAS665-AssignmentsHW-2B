import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { useAuth } from '../contexts/AuthContext';
import { useAssessment } from '../contexts/AssessmentContext';
import { User, Mail, Calendar, Edit, Save, X } from 'lucide-react';

const Profile = () => {
  const { user, login } = useAuth();
  const { getUserAssessments } = useAssessment();
  const [assessments, setAssessments] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    age: user?.age || ''
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAssessments = async () => {
      if (user?.id) {
        const result = await getUserAssessments(user.id);
        if (result.success) {
          setAssessments(result.data);
        }
      }
      setLoading(false);
    };

    loadAssessments();
  }, [user, getUserAssessments]);

  const handleEdit = () => {
    setEditData({
      name: user?.name || '',
      email: user?.email || '',
      age: user?.age || ''
    });
    setIsEditing(true);
  };

  const handleSave = async () => {
    // In a real app, you'd make an API call to update the user
    // For now, we'll just simulate it
    console.log('Saving profile:', editData);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditData({
      name: user?.name || '',
      email: user?.email || '',
      age: user?.age || ''
    });
    setIsEditing(false);
  };

  const handleChange = (e) => {
    setEditData({
      ...editData,
      [e.target.name]: e.target.value
    });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getLatestCefrLevel = () => {
    const completedAssessments = assessments.filter(a => a.status === 'completed' && a.cefr_level);
    if (completedAssessments.length === 0) return 'N/A';
    
    return completedAssessments
      .sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at))[0]
      .cefr_level;
  };

  const getAssessmentStats = () => {
    const total = assessments.length;
    const completed = assessments.filter(a => a.status === 'completed').length;
    const inProgress = assessments.filter(a => a.status === 'in_progress').length;
    
    return { total, completed, inProgress };
  };

  const stats = getAssessmentStats();

  const chartData = assessments
    .filter(a => a.status === 'completed')
    .sort((a,b) => new Date(a.completed_at || a.started_at) - new Date(b.completed_at || b.started_at))
    .map((a, idx) => {
      const numericLexile = (typeof a.lexile_estimate === 'number')
        ? a.lexile_estimate
        : (typeof a.theta_score === 'number' ? Math.round(800 + (a.theta_score * 250)) : null);
      return { testIndex: idx + 1, lexile: typeof numericLexile === 'number' ? numericLexile : null };
    })
    .filter(d => typeof d.lexile === 'number');

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="profile">
      <div className="container">
        <h1>Profile</h1>

        {/* Profile Info */}
        <div className="profile-section">
          <div className="profile-header">
            <h2>Personal Information</h2>
            {!isEditing && (
              <button onClick={handleEdit} className="btn btn-secondary">
                <Edit size={16} />
                Edit Profile
              </button>
            )}
          </div>

          <div className="profile-info">
            <div className="profile-avatar">
              <User size={48} />
            </div>
            
            <div className="profile-details">
              {isEditing ? (
                <div className="edit-form">
                  <div className="form-group">
                    <label className="form-label">Name</label>
                    <input
                      type="text"
                      name="name"
                      value={editData.name}
                      onChange={handleChange}
                      className="form-input"
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Email</label>
                    <input
                      type="email"
                      name="email"
                      value={editData.email}
                      onChange={handleChange}
                      className="form-input"
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Age</label>
                    <input
                      type="number"
                      name="age"
                      value={editData.age}
                      onChange={handleChange}
                      className="form-input"
                      min="8"
                      max="16"
                    />
                  </div>
                  <div className="form-actions">
                    <button onClick={handleSave} className="btn btn-primary">
                      <Save size={16} />
                      Save Changes
                    </button>
                    <button onClick={handleCancel} className="btn btn-secondary">
                      <X size={16} />
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="profile-fields">
                  <div className="profile-field">
                    <User size={20} />
                    <div>
                      <label>Name</label>
                      <span>{user?.name}</span>
                    </div>
                  </div>
                  <div className="profile-field">
                    <Mail size={20} />
                    <div>
                      <label>Email</label>
                      <span>{user?.email}</span>
                    </div>
                  </div>
                  <div className="profile-field">
                    <Calendar size={20} />
                    <div>
                      <label>Age</label>
                      <span>{user?.age} years old</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Assessment Stats */}
        <div className="stats-section">
          <h2>Assessment Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">
                <User size={24} />
              </div>
              <div className="stat-content">
                <h3>{stats.total}</h3>
                <p>Total Assessments</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">
                <Calendar size={24} />
              </div>
              <div className="stat-content">
                <h3>{stats.completed}</h3>
                <p>Completed</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">
                <User size={24} />
              </div>
              <div className="stat-content">
                <h3>{getLatestCefrLevel()}</h3>
                <p>Latest CEFR Level</p>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Chart */}
        {chartData.length > 0 && (
          <div className="stats-section" style={{ marginTop: '1rem' }}>
            <h2>Reading Progress (Lexile)</h2>
            <div style={{ width: '100%', height: 260 }}>
              <ResponsiveContainer>
                <LineChart data={chartData} margin={{ top: 10, right: 20, bottom: 0, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" dataKey="testIndex" domain={[1, chartData.length || 1]} allowDecimals={false} tickFormatter={(v) => `Test ${v}`} />
                  <YAxis type="number" domain={[300, 1350]} ticks={[300,500,700,900,1100,1300]} allowDecimals={false} tickFormatter={(v) => `${v}`} />
                  <Tooltip formatter={(v) => `${Math.round(Number(v))}L`} />
                  <Line type="monotone" dataKey="lexile" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} isAnimationActive={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Recent Assessments removed per request */}

        {/* Smart Suggestions */}
        <div className="assessments-section" style={{ marginTop: '1rem' }}>
          <h2>Smart Suggestions</h2>
          <ul style={{ margin: 0, paddingLeft: '1.25rem', color: '#374151', lineHeight: 1.8 }}>
            <li>Read at {chartData.length ? `${Math.max(300, chartData[chartData.length-1].lexile - 100)}–${Math.min(1350, (chartData[chartData.length-1].lexile || 800) + 100)}L` : 'your recommended level'} for 20–30 minutes daily.</li>
            <li>Practice main idea and inference with short informational texts; summarize in 1–2 sentences.</li>
            <li>Build vocabulary: create flashcards for 8–10 new words per session; review with spaced repetition.</li>
            <li>Target weak skills first (detail lookbacks, vocab-in-context). Time each item to improve pace.</li>
          </ul>
        </div>
      </div>

      <style jsx>{`
        .profile {
          padding: 2rem 0;
        }

        .profile h1 {
          font-size: 2.5rem;
          font-weight: 700;
          color: #1e293b;
          margin-bottom: 2rem;
        }

        .profile-section {
          background: white;
          border-radius: 1rem;
          padding: 2rem;
          margin-bottom: 2rem;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }

        .profile-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
        }

        .profile-header h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1e293b;
        }

        .profile-info {
          display: flex;
          gap: 2rem;
          align-items: flex-start;
        }

        .profile-avatar {
          width: 4rem;
          height: 4rem;
          background: #f0f9ff;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #3b82f6;
          flex-shrink: 0;
        }

        .profile-details {
          flex: 1;
        }

        .profile-fields {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .profile-field {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .profile-field svg {
          color: #64748b;
        }

        .profile-field label {
          font-weight: 500;
          color: #374151;
          margin-right: 0.5rem;
        }

        .profile-field span {
          color: #64748b;
        }

        .edit-form {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .form-actions {
          display: flex;
          gap: 1rem;
          margin-top: 1rem;
        }

        .stats-section {
          background: white;
          border-radius: 1rem;
          padding: 2rem;
          margin-bottom: 2rem;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }

        .stats-section h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 1.5rem;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1.5rem;
        }

        .stat-card {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1.5rem;
          background: #f8fafc;
          border-radius: 0.75rem;
        }

        .stat-icon {
          width: 3rem;
          height: 3rem;
          background: #3b82f6;
          border-radius: 0.75rem;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
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

        .assessments-section {
          background: white;
          border-radius: 1rem;
          padding: 2rem;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }

        .assessments-section h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 1.5rem;
        }

        .assessments-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .assessment-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border: 1px solid #e2e8f0;
          border-radius: 0.75rem;
        }

        .assessment-info {
          display: flex;
          align-items: center;
          gap: 2rem;
        }

        .assessment-type {
          font-weight: 500;
          color: #374151;
        }

        .status-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 1rem;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .status-badge.completed {
          background: #d1fae5;
          color: #065f46;
        }

        .status-badge.in_progress {
          background: #fef3c7;
          color: #92400e;
        }

        .assessment-details {
          text-align: right;
        }

        .cefr-level {
          font-size: 0.875rem;
          color: #64748b;
          margin-bottom: 0.25rem;
        }

        .assessment-date {
          font-size: 0.75rem;
          color: #9ca3af;
        }

        .empty-state {
          text-align: center;
          padding: 2rem;
          color: #64748b;
        }

        @media (max-width: 768px) {
          .profile-info {
            flex-direction: column;
            align-items: center;
            text-align: center;
          }

          .assessment-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
          }

          .assessment-info {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
          }

          .assessment-details {
            text-align: left;
          }

          .form-actions {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default Profile;
