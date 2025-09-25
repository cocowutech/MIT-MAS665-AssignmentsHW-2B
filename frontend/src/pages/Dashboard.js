import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useAssessment } from '../contexts/AssessmentContext';
import { BookOpen, BarChart3, Clock, CheckCircle, TrendingUp } from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const { getUserAssessments } = useAssessment();
  const [assessments, setAssessments] = useState([]);
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

  const readingAssessments = assessments.filter(a => a.assessment_type === 'reading');

  const assessmentTypes = [
    {
      type: 'reading',
      title: 'Reading Placement',
      description: "Benchmark your reading comprehension and receive Coco's guidance.",
      icon: <BookOpen size={24} />,
      color: '#3b82f6',
      duration: '15-20 min'
    }
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} color="#10b981" />;
      case 'in_progress':
        return <Clock size={16} color="#f59e0b" />;
      default:
        return <Clock size={16} color="#64748b" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return '#10b981';
      case 'in_progress':
        return '#f59e0b';
      default:
        return '#64748b';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="container">
        {/* Header */}
        <div className="dashboard-header">
          <h1>Welcome back, {user?.name}!</h1>
          <p>Start or review your Vico Education reading placement.</p>
        </div>

        {/* Quick Stats */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">
              <BarChart3 size={24} />
            </div>
            <div className="stat-content">
              <h3>{readingAssessments.length}</h3>
              <p>Total Placements</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">
              <CheckCircle size={24} />
            </div>
            <div className="stat-content">
              <h3>{readingAssessments.filter(a => a.status === 'completed').length}</h3>
              <p>Completed Placements</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">
              <TrendingUp size={24} />
            </div>
            <div className="stat-content">
              <h3>
                {readingAssessments.filter(a => a.status === 'completed' && a.cefr_level).length > 0 
                  ? readingAssessments.filter(a => a.status === 'completed' && a.cefr_level)
                      .sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at))[0]?.cefr_level
                  : 'N/A'
                }
              </h3>
              <p>Latest Reading CEFR</p>
            </div>
          </div>
        </div>

        {/* Assessment Types */}
        <div className="assessment-section">
          <h2>Start New Reading Placement</h2>
          <div className="assessment-grid">
            {assessmentTypes.map((assessment, index) => (
              <div key={index} className="assessment-card">
                <div className="assessment-icon" style={{ backgroundColor: assessment.color }}>
                  {assessment.icon}
                </div>
                <h3>{assessment.title}</h3>
                <p>{assessment.description}</p>
                <div className="assessment-meta">
                  <span className="duration">⏱️ {assessment.duration}</span>
                </div>
                <Link 
                  to={`/assessment/${assessment.type}`} 
                  className="btn btn-primary"
                  style={{ 
                    width: '100%', 
                    marginTop: '1rem',
                    backgroundColor: assessment.color,
                    borderColor: assessment.color
                  }}
                >
                  Start Placement
                </Link>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Assessments */}
        {readingAssessments.length > 0 && (
          <div className="recent-assessments">
            <h2>Recent Placements</h2>
            <div className="assessments-list">
              {readingAssessments
                .filter(a => a.status === 'completed')
                .slice(0, 5)
                .map((assessment) => (
                <div key={assessment.id} className="assessment-item">
                  <div className="assessment-info">
                    <div className="assessment-type">
                      <BookOpen size={16} />
                      <span>Reading</span>
                    </div>
                    <div className="assessment-status">
                      {getStatusIcon(assessment.status)}
                      <span style={{ color: getStatusColor(assessment.status) }}>
                        {assessment.status.charAt(0).toUpperCase() + assessment.status.slice(1)}
                      </span>
                    </div>
                  </div>
                  <div className="assessment-details">
                    {assessment.cefr_level && (
                      <div className="cefr-level">
                        CEFR: <strong>{assessment.cefr_level}</strong>
                      </div>
                    )}
                    <div className="assessment-date">
                      {formatDate(assessment.started_at)}
                    </div>
                  </div>
                  <div className="assessment-actions">
                    <Link 
                      to={`/results/${assessment.id}`} 
                      className="btn btn-secondary"
                    >
                      View Results
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {readingAssessments.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">
              <BarChart3 size={48} />
            </div>
            <h3>No placements yet</h3>
            <p>Start your first reading placement to discover your current level.</p>
            <div className="empty-actions">
              {assessmentTypes.map((assessment, index) => (
                <Link 
                  key={index}
                  to={`/assessment/${assessment.type}`} 
                  className="btn btn-primary"
                >
                  {assessment.icon}
                  {assessment.title}
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .dashboard {
          padding: 2rem 0;
        }

        .dashboard-header {
          text-align: center;
          margin-bottom: 3rem;
        }

        .dashboard-header h1 {
          font-size: 2.5rem;
          font-weight: 700;
          color: #1e293b;
          margin-bottom: 0.5rem;
        }

        .dashboard-header p {
          color: #64748b;
          font-size: 1.125rem;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
          margin-bottom: 0.25rem;
        }

        .stat-content p {
          color: #64748b;
          font-size: 0.875rem;
        }

        .assessment-section {
          margin-bottom: 3rem;
        }

        .assessment-section h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 1.5rem;
        }

        .assessment-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1.5rem;
        }

        .assessment-card {
          background: white;
          border-radius: 1rem;
          padding: 2rem;
          text-align: center;
          border: 2px solid transparent;
          transition: all 0.2s ease;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .assessment-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }

        .assessment-icon {
          width: 3rem;
          height: 3rem;
          border-radius: 0.75rem;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1rem;
          color: white;
        }

        .assessment-card h3 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 0.5rem;
        }

        .assessment-card p {
          color: #64748b;
          margin-bottom: 1rem;
        }

        .assessment-meta {
          margin: 1rem 0;
          font-size: 0.875rem;
          color: #64748b;
        }

        .recent-assessments h2 {
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
          background: white;
          border-radius: 0.75rem;
          padding: 1.5rem;
          display: flex;
          align-items: center;
          justify-content: space-between;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .assessment-info {
          display: flex;
          align-items: center;
          gap: 2rem;
        }

        .assessment-type {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-weight: 500;
          color: #374151;
        }

        .assessment-status {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.875rem;
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
          padding: 4rem 2rem;
          background: white;
          border-radius: 1rem;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .empty-icon {
          width: 4rem;
          height: 4rem;
          background: #f0f9ff;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1rem;
          color: #3b82f6;
        }

        .empty-state h3 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 0.5rem;
        }

        .empty-state p {
          color: #64748b;
          margin-bottom: 2rem;
        }

        .empty-actions {
          display: flex;
          gap: 1rem;
          justify-content: center;
          flex-wrap: wrap;
        }

        .empty-actions .btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        @media (max-width: 768px) {
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

          .assessment-actions {
            width: 100%;
          }

          .assessment-actions .btn {
            width: 100%;
          }

          .empty-actions {
            flex-direction: column;
            align-items: center;
          }

          .empty-actions .btn {
            width: 200px;
          }
        }
      `}</style>
    </div>
  );
};

export default Dashboard;
