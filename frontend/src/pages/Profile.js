import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useAssessment } from '../contexts/AssessmentContext';
import { User, Mail, Calendar, Edit, Save, X, PartyPopper } from 'lucide-react';

const Profile = () => {
  const { user, login } = useAuth();
  const { getUserAssessments, getAssessmentResult } = useAssessment();
  const [assessments, setAssessments] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    age: user?.age || ''
  });
  const [loading, setLoading] = useState(true);
  const [bestPlacementDetail, setBestPlacementDetail] = useState(null);
  const [bestPlacementDuration, setBestPlacementDuration] = useState(null);

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

  const readingAssessments = useMemo(
    () => assessments.filter((a) => a.assessment_type === 'reading'),
    [assessments]
  );

  const stats = useMemo(() => {
    const total = readingAssessments.length;
    const completed = readingAssessments.filter((a) => a.status === 'completed').length;
    const inProgress = readingAssessments.filter((a) => a.status === 'in_progress').length;
    return { total, completed, inProgress };
  }, [readingAssessments]);

  const sanitizeLexile = (value) => {
    if (typeof value !== 'number' || Number.isNaN(value) || !Number.isFinite(value)) {
      return null;
    }
    const rounded = Math.round(value);
    const lowerBound = 200;
    const upperBound = 1350;
    if (rounded < lowerBound) {
      return lowerBound;
    }
    if (rounded > upperBound) {
      return upperBound;
    }
    return rounded;
  };

  const deriveLexile = (assessment) => {
    if (typeof assessment?.lexile_estimate === 'number') {
      return sanitizeLexile(assessment.lexile_estimate);
    }
    if (typeof assessment?.theta_score === 'number') {
      const theta = Math.max(-4, Math.min(4, assessment.theta_score));
      return sanitizeLexile(800 + theta * 250);
    }
    return null;
  };

  const completedPlacements = useMemo(
    () => readingAssessments.filter((a) => a.status === 'completed'),
    [readingAssessments]
  );

  const bestPlacement = useMemo(() => {
    if (!completedPlacements.length) return null;
    return completedPlacements.reduce((best, current) => {
      const lexile = deriveLexile(current);
      if (typeof lexile !== 'number') {
        return best;
      }
      if (!best || lexile > best.lexile) {
        return {
          ...current,
          lexile
        };
      }
      return best;
    }, null);
  }, [completedPlacements]);

  const latestPlacement = useMemo(() => {
    if (!completedPlacements.length) return null;
    return [...completedPlacements]
      .sort((a, b) => new Date(b.completed_at || b.started_at) - new Date(a.completed_at || a.started_at))
      .map((placement) => ({
        ...placement,
        lexile: deriveLexile(placement)
      }))[0];
  }, [completedPlacements]);

  const recommendedRange = useMemo(() => {
    if (!latestPlacement?.lexile) {
      return 'your recommended level';
    }
    const low = Math.max(300, latestPlacement.lexile - 100);
    const high = Math.min(1350, latestPlacement.lexile + 100);
    return `${low}–${high}L`;
  }, [latestPlacement]);

  const durationFromTimestamps = (start, end) => {
    if (!start || !end) return null;
    const startTime = new Date(start).getTime();
    const endTime = new Date(end).getTime();
    if (Number.isNaN(startTime) || Number.isNaN(endTime) || endTime <= startTime) return null;
    return Math.max(0, Math.round((endTime - startTime) / 1000));
  };

  const formatDuration = (totalSeconds) => {
    if (!Number.isFinite(totalSeconds) || totalSeconds <= 0) {
      return 'N/A';
    }

    if (totalSeconds < 60) {
      return `${totalSeconds}s`;
    }

    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    const segments = [];
    if (hours) {
      segments.push(`${hours}h`);
    }
    segments.push(`${minutes}m`);
    if (seconds && !hours) {
      segments.push(`${seconds}s`);
    }

    return segments.join(' ');
  };

  const fallbackDurationSeconds = useMemo(() => {
    if (!bestPlacement?.started_at || !bestPlacement?.completed_at) {
      return null;
    }
    return durationFromTimestamps(bestPlacement.started_at, bestPlacement.completed_at);
  }, [bestPlacement]);

  useEffect(() => {
    let isCancelled = false;

    const loadBestPlacementDetail = async () => {
      if (!bestPlacement?.id) {
        setBestPlacementDetail(null);
        setBestPlacementDuration(null);
        return;
      }

      const result = await getAssessmentResult(bestPlacement.id);
      if (isCancelled) return;

      if (result.success) {
        setBestPlacementDetail(result.data);
        const questionHistory = Array.isArray(result.data?.question_history)
          ? result.data.question_history
          : [];
        const summedSeconds = questionHistory.reduce((total, item) => {
          const value = Number(item?.response_time);
          if (Number.isFinite(value) && value > 0) {
            return total + value;
          }
          return total;
        }, 0);
        if (summedSeconds > 0) {
          setBestPlacementDuration(Math.round(summedSeconds));
        } else {
          setBestPlacementDuration(null);
        }
      } else {
        setBestPlacementDetail(null);
        setBestPlacementDuration(null);
      }
    };

    loadBestPlacementDetail();

    return () => {
      isCancelled = true;
    };
  }, [bestPlacement, getAssessmentResult]);

  const displayedDurationSeconds = bestPlacementDuration ?? fallbackDurationSeconds;

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

        {/* Placement Highlight */}
        <div className="stats-section" style={{ marginTop: '1rem' }}>
          <h2>Placement Highlight</h2>
          {bestPlacement ? (
            <div className="placement-highlight">
              <div className="placement-highlight__icon"><PartyPopper size={28} /></div>
              <div className="placement-highlight__details">
                <div className="placement-highlight__row">
                  <span className="label">Best Lexile</span>
                  <strong>{bestPlacement.lexile || 'N/A'}L</strong>
                </div>
                <div className="placement-highlight__row">
                  <span className="label">CEFR Level</span>
                  <strong>{bestPlacement.cefr_level || 'N/A'}</strong>
                </div>
                <div className="placement-highlight__row">
                  <span className="label">Completed On</span>
                  <strong>{formatDate(bestPlacement.completed_at || bestPlacement.started_at)}</strong>
                </div>
                <div className="placement-highlight__row">
                  <span className="label">Time to Finish</span>
                  <strong>{formatDuration(displayedDurationSeconds)}</strong>
                </div>
              </div>
            </div>
          ) : (
            <p style={{ color: '#64748b', margin: 0 }}>Complete your first placement to unlock detailed insights.</p>
          )}
        </div>

        {/* Smart Suggestions */}
        <div className="assessments-section" style={{ marginTop: '1rem' }}>
          <h2>Smart Suggestions</h2>
          <ul style={{ margin: 0, paddingLeft: '1.25rem', color: '#374151', lineHeight: 1.8 }}>
            <li>Read at {recommendedRange} for 20–30 minutes daily.</li>
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

        .placement-highlight {
          display: flex;
          align-items: center;
          gap: 1.5rem;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 1rem;
          padding: 1.5rem;
        }

        .placement-highlight__icon {
          width: 3rem;
          height: 3rem;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(59, 130, 246, 0.12);
          color: #1d4ed8;
        }

        .placement-highlight__details {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
          gap: 1rem;
          width: 100%;
        }

        .placement-highlight__row {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .placement-highlight__row .label {
          text-transform: uppercase;
          font-size: 0.75rem;
          color: #64748b;
          letter-spacing: 0.08em;
        }

        .placement-highlight__row strong {
          font-size: 1.1rem;
          color: #0f172a;
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
