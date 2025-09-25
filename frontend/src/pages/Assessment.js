import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAssessment } from '../contexts/AssessmentContext';
import { ArrowLeft, ArrowRight, Clock } from 'lucide-react';

const Assessment = () => {
  const { type } = useParams();
  const navigate = useNavigate();
  const { 
    currentAssessment, 
    currentQuestion, 
    startAssessment, 
    submitResponse,
    submitAssessment,
    loading 
  } = useAssessment();

  const [selectedOption, setSelectedOption] = useState('');
  const [responseTime, setResponseTime] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(120); // 2 minutes per question
  const [questionStartTime, setQuestionStartTime] = useState(null);

  useEffect(() => {
    setSelectedOption('');
  }, [currentQuestion?.id]);

  const handleSubmit = useCallback(async () => {
    if (isSubmitting || !currentQuestion) return;
    setIsSubmitting(true);
    try {
      let responseData = {
        question_id: currentQuestion.id,
        response_time: responseTime
      };
      if (!selectedOption) {
        responseData.response_text = currentQuestion.options?.[0];
      } else {
        responseData.response_text = selectedOption;
      }
      const result = await submitResponse(currentQuestion.id, responseData);
      if (result.completed) {
        navigate(`/results/${currentAssessment.id}`);
      } else {
        setSelectedOption('');
        setTimeRemaining(120);
        setQuestionStartTime(Date.now());
      }
    } catch (error) {
      console.error('Error submitting response:', error);
      alert('Failed to submit response. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }, [isSubmitting, currentQuestion, responseTime, selectedOption, submitResponse, navigate, currentAssessment]);

  const handleFinalSubmit = useCallback(async () => {
    if (!currentAssessment) return;
    setIsSubmitting(true);
    try {
      const res = await submitAssessment(currentAssessment.id);
      if (res.success) {
        navigate(`/results/${currentAssessment.id}`);
      }
    } catch (e) {
      console.error('Error submitting assessment:', e);
      alert('Failed to submit assessment.');
    } finally {
      setIsSubmitting(false);
    }
  }, [currentAssessment, submitAssessment, navigate]);

  useEffect(() => {
    if (type !== 'reading') {
      navigate('/assessment/reading', { replace: true });
      return;
    }
    if (!currentAssessment) {
      startAssessment('reading');
    }
    if (currentQuestion) {
      // setStartTime(Date.now());
      setResponseTime(0);
      setTimeRemaining(120); // Reset to 2 minutes per question
      setQuestionStartTime(Date.now());
    }
  }, [currentAssessment, currentQuestion, type, startAssessment, navigate]);

  useEffect(() => {
    let interval;
    if (questionStartTime && !isSubmitting) {
      interval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - questionStartTime) / 1000);
        setResponseTime(elapsed);
        setTimeRemaining(Math.max(0, 120 - elapsed));
        
        // Auto-submit when time is up
        if (elapsed >= 120) {
          handleSubmit();
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [questionStartTime, isSubmitting, handleSubmit]);

  const handleOptionSelect = (option) => {
    setSelectedOption(option);
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading assessment...</p>
      </div>
    );
  }

  if (!currentAssessment || !currentQuestion) {
    return (
      <div className="assessment-error">
        <h2>Assessment not found</h2>
        <p>Please try starting a new assessment.</p>
        <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
          Back to Dashboard
        </button>
      </div>
    );
  }

  const progress = currentAssessment.progress ? 
    (currentAssessment.progress.current / currentAssessment.progress.total) * 100 : 0;

  return (
    <div className="assessment">
      <div className="container">
        {/* Header */}
        <div className="assessment-header">
          <button 
            onClick={() => navigate('/dashboard')} 
            className="btn btn-secondary"
          >
            <ArrowLeft size={16} />
            Back to Dashboard
          </button>
          
          <div className="assessment-info">
            <h1>Reading Placement</h1>
            <div className="progress-info">
              <span>Question {currentAssessment.progress?.current || 1} of {currentAssessment.progress?.total || 15}</span>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Question Content */}
        <div className="question-container">
          <div className="question-content">
            {/* Reading Passage */}
            {currentQuestion.passage && (
              <div className="question-passage">
                <h3>Reading Passage</h3>
                <p>{currentQuestion.passage}</p>
              </div>
            )}

            {/* Question Text */}
            <div className="question-text">
              <h3>Question {currentAssessment.progress?.current || 1}</h3>
              <p>{currentQuestion.content}</p>
            </div>

            {/* Reading Assessment - Multiple Choice */}
            {currentQuestion.options && (
              <div className="question-options">
                {currentQuestion.options.map((option, index) => (
                  <label 
                    key={index} 
                    className={`option ${selectedOption === option ? 'selected' : ''}`}
                  >
                    <input
                      type="radio"
                      name="answer"
                      value={option}
                      checked={selectedOption === option}
                      onChange={() => handleOptionSelect(option)}
                    />
                    <span>{option}</span>
                  </label>
                ))}
              </div>
            )}

          </div>

          {/* Submit Button or Final Submit */}
          <div className="question-actions">
            {currentAssessment.progress?.current >= (currentAssessment.progress?.total || 15) ? (
              <button
                onClick={handleFinalSubmit}
                disabled={isSubmitting}
                className="btn btn-primary"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Test'}
                <ArrowRight size={16} />
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={isSubmitting || !selectedOption}
                className="btn btn-primary"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Answer'}
                <ArrowRight size={16} />
              </button>
            )}
          </div>

          {/* Response Time */}
          <div className="response-time">
            <Clock size={16} />
            <span>Time Remaining: {Math.floor(timeRemaining / 60)}:{(timeRemaining % 60).toString().padStart(2, '0')}</span>
          </div>
        </div>
      </div>

      <style jsx>{`
        .assessment {
          padding: 2rem 0;
          min-height: 100vh;
        }

        .assessment-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 2rem;
          flex-wrap: wrap;
          gap: 1rem;
        }

        .assessment-info h1 {
          font-size: 2rem;
          font-weight: 700;
          color: #1e293b;
          margin-bottom: 0.5rem;
        }

        .progress-info {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .progress-info span {
          font-size: 0.875rem;
          color: #64748b;
          white-space: nowrap;
        }

        .progress-bar {
          width: 200px;
          height: 0.5rem;
          background: #e2e8f0;
          border-radius: 0.25rem;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: #3b82f6;
          transition: width 0.3s ease;
        }

        .question-container {
          max-width: 800px;
          margin: 0 auto;
        }

        .question-content {
          background: white;
          border-radius: 1rem;
          padding: 2rem;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
          margin-bottom: 2rem;
        }

        .question-passage {
          background: #f8fafc;
          padding: 1.5rem;
          border-radius: 0.75rem;
          margin-bottom: 1.5rem;
          border-left: 4px solid #3b82f6;
        }

        .question-passage h3 {
          font-size: 1.125rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 0.75rem;
        }

        .question-passage p {
          line-height: 1.7;
          color: #374151;
        }

        .question-text h3 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 0.75rem;
        }

        .question-text p {
          font-size: 1.125rem;
          line-height: 1.7;
          color: #374151;
          margin-bottom: 1.5rem;
        }

        .question-options {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .option {
          display: flex;
          align-items: center;
          padding: 1rem;
          border: 2px solid #e2e8f0;
          border-radius: 0.75rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .option:hover {
          border-color: #3b82f6;
          background: #f0f9ff;
        }

        .option.selected {
          border-color: #3b82f6;
          background: #dbeafe;
        }

        .option input[type="radio"] {
          margin-right: 0.75rem;
        }

        .question-actions {
          display: flex;
          justify-content: center;
          margin-bottom: 1rem;
        }

        .response-time {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          color: #64748b;
          font-size: 0.875rem;
        }

        .assessment-error {
          text-align: center;
          padding: 4rem 2rem;
        }

        .assessment-error h2 {
          font-size: 2rem;
          font-weight: 700;
          color: #1e293b;
          margin-bottom: 1rem;
        }

        .assessment-error p {
          color: #64748b;
          margin-bottom: 2rem;
        }

        @media (max-width: 768px) {
          .assessment-header {
            flex-direction: column;
            align-items: flex-start;
          }

          .progress-info {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
          }

          .progress-bar {
            width: 100%;
          }

          .question-content {
            padding: 1.5rem;
          }
        }
      `}</style>
    </div>
  );
};

export default Assessment;
