import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAssessment } from '../contexts/AssessmentContext';
import { ArrowLeft, Download, Share2, Trophy, Target, TrendingUp, BookOpen, Mic, PenTool } from 'lucide-react';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

const Results = () => {
  const { assessmentId } = useParams();
  const navigate = useNavigate();
  const { getAssessmentResult } = useAssessment();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadResult = async () => {
      const response = await getAssessmentResult(assessmentId);
      if (response.success) {
        setResult(response.data);
      }
      setLoading(false);
    };

    loadResult();
  }, [assessmentId, getAssessmentResult]);

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading results...</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="results-error">
        <h2>Results not found</h2>
        <p>Unable to load assessment results.</p>
        <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
          Back to Dashboard
        </button>
      </div>
    );
  }

  const cefrLevels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
  const cefrIndex = cefrLevels.indexOf(result.cefr_level);
  const cefrProgress = ((cefrIndex + 1) / cefrLevels.length) * 100;

  const examReadiness = [
    { name: 'KET', value: result.ket_readiness * 100, color: '#3b82f6' },
    { name: 'PET', value: result.pet_readiness * 100, color: '#10b981' },
    { name: 'FCE', value: result.fce_readiness * 100, color: '#8b5cf6' }
  ];

  const subScoreData = result.sub_scores?.map(score => ({
    skill: score.skill.replace(/_/g, ' ').toUpperCase(),
    score: (score.score / score.max_score) * 100,
    fullMark: 100
  })) || [];

  const getCefrColor = (level) => {
    const colors = {
      'A1': '#ef4444',
      'A2': '#f59e0b',
      'B1': '#10b981',
      'B2': '#3b82f6',
      'C1': '#8b5cf6',
      'C2': '#ec4899'
    };
    return colors[level] || '#64748b';
  };

  const getRecommendations = () => {
    const recommendations = [];
    
    if (result.ket_readiness > 0.8) {
      recommendations.push('You are well-prepared for the KET exam!');
    } else if (result.ket_readiness > 0.6) {
      recommendations.push('You are approaching readiness for the KET exam.');
    }

    if (result.pet_readiness > 0.8) {
      recommendations.push('You are well-prepared for the PET exam!');
    } else if (result.pet_readiness > 0.6) {
      recommendations.push('You are approaching readiness for the PET exam.');
    }

    if (result.fce_readiness > 0.8) {
      recommendations.push('You are well-prepared for the FCE exam!');
    } else if (result.fce_readiness > 0.6) {
      recommendations.push('You are approaching readiness for the FCE exam.');
    }

    return recommendations;
  };

  return (
    <div className="results">
      <div className="container">
        {/* Header */}
        <div className="results-header">
          <button 
            onClick={() => navigate('/dashboard')} 
            className="btn btn-secondary"
          >
            <ArrowLeft size={16} />
            Back to Dashboard
          </button>
          
          <div className="header-actions">
            <button className="btn btn-secondary">
              <Download size={16} />
              Download Report
            </button>
            <button className="btn btn-secondary">
              <Share2 size={16} />
              Share
            </button>
          </div>
        </div>

        {/* Main Results */}
        <div className="results-main">
          <div className="cefr-result">
            <div className="cefr-badge" style={{ backgroundColor: getCefrColor(result.cefr_level) }}>
              <Trophy size={32} />
              <div>
                <h2>CEFR Level {result.cefr_level}</h2>
                <p>Your English Proficiency Level</p>
              </div>
            </div>
            
            <div className="cefr-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ 
                    width: `${cefrProgress}%`,
                    backgroundColor: getCefrColor(result.cefr_level)
                  }}
                ></div>
              </div>
              <div className="cefr-levels">
                {cefrLevels.map((level, index) => (
                  <span 
                    key={level}
                    className={`cefr-level ${level === result.cefr_level ? 'current' : ''}`}
                    style={{ color: level === result.cefr_level ? getCefrColor(level) : '#64748b' }}
                  >
                    {level}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Scores Grid */}
          <div className="scores-grid">
            <div className="score-card">
              <div className="score-icon">
                <Target size={24} />
              </div>
              <div className="score-content">
                <h3>{(result.raw_score * 100).toFixed(1)}%</h3>
                <p>Overall Score</p>
              </div>
            </div>
            
            <div className="score-card">
              <div className="score-icon">
                <TrendingUp size={24} />
              </div>
              <div className="score-content">
                <h3>{result.theta_score?.toFixed(2) || 'N/A'}</h3>
                <p>Theta Score</p>
                <small style={{ color: '#64748b' }}>Higher means tougher texts feel easier</small>
              </div>
            </div>
            
            <div className="score-card">
              <div className="score-icon">
                <Trophy size={24} />
              </div>
              <div className="score-content">
                <h3>±{result.standard_error?.toFixed(2) || 'N/A'}</h3>
                <p>Confidence Band</p>
                <small style={{ color: '#64748b' }}>Smaller is better (more consistent)</small>
              </div>
            </div>

            {/* Lexile */}
            <div className="score-card">
              <div className="score-icon">
                <BookOpen size={24} />
              </div>
              <div className="score-content">
                <h3>
                  {result.lexile_estimate ? `${result.lexile_estimate}L` : 'N/A'}
                </h3>
                <p>
                  {result.lexile_ci_low && result.lexile_ci_high
                    ? `CI ${result.lexile_ci_low}–${result.lexile_ci_high}L`
                    : 'Lexile Estimate'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* CEFR vs Exam/IELTS correlation (overview) */}
        <div className="exam-readiness">
          <h2>Level Guide</h2>
          <p style={{ color: '#64748b', marginBottom: '1rem' }}>
            CEFR maps to common exams. This is a rough guide to help parents and students:
            KET≈A2, PET≈B1, FCE≈B2. Many IELTS takers tend to be around B1→B2 (≈4.5–6.5).
          </p>
        </div>

        {/* Exam Readiness */}
        <div className="exam-readiness">
          <h2>Exam Readiness</h2>
          <div className="exam-chart">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={examReadiness}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Readiness']} />
                <Bar dataKey="value" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          
          <div className="exam-cards">
            {examReadiness.map((exam, index) => (
              <div key={index} className="exam-card">
                <div className="exam-name">{exam.name}</div>
                <div className="exam-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ 
                        width: `${exam.value}%`,
                        backgroundColor: exam.color
                      }}
                    ></div>
                  </div>
                  <span className="exam-percentage">{exam.value.toFixed(1)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sub-scores */}
        {subScoreData.length > 0 && (
          <div className="sub-scores">
            <h2>Skill Breakdown</h2>
            <div className="sub-scores-chart">
              <ResponsiveContainer width="100%" height={400}>
                <RadarChart data={subScoreData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="skill" />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} />
                  <Radar
                    name="Your Score"
                    dataKey="score"
                    stroke="#3b82f6"
                    fill="#3b82f6"
                    fillOpacity={0.3}
                  />
                  <Radar
                    name="Full Mark"
                    dataKey="fullMark"
                    stroke="#e2e8f0"
                    fill="transparent"
                    strokeDasharray="5 5"
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
            
            <div className="sub-scores-list">
              {result.sub_scores?.map((score, index) => (
                <div key={index} className="sub-score-item">
                  <div className="sub-score-info">
                    <h4>{score.skill.replace(/_/g, ' ').toUpperCase()}</h4>
                    <p>{score.description}</p>
                  </div>
                  <div className="sub-score-value">
                    <div className="sub-score-bar">
                      <div 
                        className="sub-score-fill" 
                        style={{ width: `${(score.score / score.max_score) * 100}%` }}
                      ></div>
                    </div>
                    <span>{score.score.toFixed(1)}/{score.max_score}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        <div className="recommendations">
          <h2>Next Steps</h2>
          <div className="recommendations-grid">
            <div className="recommendation-card">
              <BookOpen size={24} />
              <h3>Reading Practice</h3>
              <p>Continue reading materials at your CEFR level to improve comprehension and vocabulary.</p>
            </div>
            <div className="recommendation-card">
              <Mic size={24} />
              <h3>Speaking Practice</h3>
              <p>Practice speaking regularly to improve fluency and confidence in conversation.</p>
            </div>
            <div className="recommendation-card">
              <PenTool size={24} />
              <h3>Writing Practice</h3>
              <p>Write regularly on various topics to improve organization and language control.</p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="results-actions">
          <Link to="/dashboard" className="btn btn-primary">
            Take Another Assessment
          </Link>
          <Link to="/profile" className="btn btn-secondary">
            View Progress
          </Link>
        </div>
      </div>

      <style jsx>{`
        .results {
          padding: 2rem 0;
          min-height: 100vh;
        }

        .results-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 3rem;
          flex-wrap: wrap;
          gap: 1rem;
        }

        .header-actions {
          display: flex;
          gap: 1rem;
        }

        .results-main {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 2rem;
          margin-bottom: 3rem;
        }

        .cefr-result {
          background: white;
          border-radius: 1rem;
          padding: 2rem;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }

        .cefr-badge {
          display: flex;
          align-items: center;
          gap: 1rem;
          color: white;
          margin-bottom: 2rem;
        }

        .cefr-badge h2 {
          font-size: 2rem;
          font-weight: 700;
          margin: 0;
        }

        .cefr-badge p {
          margin: 0;
          opacity: 0.9;
        }

        .cefr-progress {
          margin-top: 1rem;
        }

        .cefr-levels {
          display: flex;
          justify-content: space-between;
          margin-top: 0.5rem;
          font-size: 0.875rem;
          font-weight: 500;
        }

        .cefr-level.current {
          font-weight: 700;
          font-size: 1rem;
        }

        .scores-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 1rem;
        }

        .score-card {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .score-icon {
          width: 3rem;
          height: 3rem;
          background: #f0f9ff;
          border-radius: 0.75rem;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #3b82f6;
        }

        .score-content h3 {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1e293b;
          margin: 0 0 0.25rem 0;
        }

        .score-content p {
          color: #64748b;
          margin: 0;
          font-size: 0.875rem;
        }

        .exam-readiness {
          background: white;
          border-radius: 1rem;
          padding: 2rem;
          margin-bottom: 3rem;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }

        .exam-readiness h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 2rem;
        }

        .exam-chart {
          margin-bottom: 2rem;
        }

        .exam-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }

        .exam-card {
          padding: 1rem;
          border: 1px solid #e2e8f0;
          border-radius: 0.75rem;
        }

        .exam-name {
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 0.5rem;
        }

        .exam-progress {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .exam-percentage {
          font-size: 0.875rem;
          font-weight: 600;
          color: #64748b;
        }

        .sub-scores {
          background: white;
          border-radius: 1rem;
          padding: 2rem;
          margin-bottom: 3rem;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }

        .sub-scores h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 2rem;
        }

        .sub-scores-chart {
          margin-bottom: 2rem;
        }

        .sub-scores-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .sub-score-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border: 1px solid #e2e8f0;
          border-radius: 0.75rem;
        }

        .sub-score-info h4 {
          font-size: 1rem;
          font-weight: 600;
          color: #1e293b;
          margin: 0 0 0.25rem 0;
        }

        .sub-score-info p {
          color: #64748b;
          margin: 0;
          font-size: 0.875rem;
        }

        .sub-score-value {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .sub-score-bar {
          width: 100px;
          height: 0.5rem;
          background: #e2e8f0;
          border-radius: 0.25rem;
          overflow: hidden;
        }

        .sub-score-fill {
          height: 100%;
          background: #3b82f6;
          transition: width 0.3s ease;
        }

        .recommendations {
          background: white;
          border-radius: 1rem;
          padding: 2rem;
          margin-bottom: 3rem;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }

        .recommendations h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 2rem;
        }

        .recommendations-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
        }

        .recommendation-card {
          padding: 1.5rem;
          border: 1px solid #e2e8f0;
          border-radius: 0.75rem;
          text-align: center;
        }

        .recommendation-card svg {
          color: #3b82f6;
          margin-bottom: 1rem;
        }

        .recommendation-card h3 {
          font-size: 1.125rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 0.5rem;
        }

        .recommendation-card p {
          color: #64748b;
          margin: 0;
          line-height: 1.5;
        }

        .results-actions {
          display: flex;
          gap: 1rem;
          justify-content: center;
          flex-wrap: wrap;
        }

        .results-error {
          text-align: center;
          padding: 4rem 2rem;
        }

        .results-error h2 {
          font-size: 2rem;
          font-weight: 700;
          color: #1e293b;
          margin-bottom: 1rem;
        }

        .results-error p {
          color: #64748b;
          margin-bottom: 2rem;
        }

        @media (max-width: 768px) {
          .results-main {
            grid-template-columns: 1fr;
          }

          .results-header {
            flex-direction: column;
            align-items: flex-start;
          }

          .header-actions {
            width: 100%;
            justify-content: flex-start;
          }

          .sub-score-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
          }

          .sub-score-value {
            width: 100%;
            justify-content: space-between;
          }

          .sub-score-bar {
            flex: 1;
          }

          .results-actions {
            flex-direction: column;
          }

          .results-actions .btn {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default Results;
