import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAssessment } from '../contexts/AssessmentContext';
import { ArrowLeft, Target, BookOpen, Gauge, Activity, Lightbulb } from 'lucide-react';

const levelColor = (level) => {
  const map = {
    A1: '#f97316',
    A2: '#fbbf24',
    B1: '#22c55e',
    B2: '#3b82f6',
    C1: '#8b5cf6',
    C2: '#ec4899'
  };
  return map[level] || '#64748b';
};

const formatPercent = (value) => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '—';
  }
  return `${(value * 100).toFixed(0)}%`;
};

const CLASS_SCHEDULES = {
  A2: 'Thursdays 4:00-5:30 PM ET (Zoom)',
  B1: 'Saturdays 9:30-11:00 AM ET (Zoom)',
  B2: 'Sundays 7:30-9:00 PM ET (Zoom)',
};

const getLearningSuggestion = (level, lexile, schedules) => {
  const lexileLabel = lexile ? `${lexile}L` : 'your current';

  if (level === 'A2') {
    return `For A2: Join Coco's THINK1 reading class. This THINK1 reading class happens on ${schedules.A2}.`;
  }
  if (level === 'B1') {
    return `For B1: Join Coco's THINK2 reading class. This THINK2 reading class happens on ${schedules.B1}.`;
  }
  if (level === 'B2') {
    return `For B2: Join Coco's THINK3 reading class. This THINK3 reading class happens on ${schedules.B2}.`;
  }
  if (!level || level === 'A1' || level === 'PRE-A2') {
    return `Ask Coco for reading suggestions for your ${lexileLabel} level! And remember to come back to test in 3 months.`;
  }
  return `Ask Coco for reading suggestions for your ${lexileLabel} level! You are on your way to excellence.`;
};

const Results = () => {
  const { assessmentId } = useParams();
  const navigate = useNavigate();
  const { getAssessmentResult } = useAssessment();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  const questionHistory = useMemo(() => result?.question_history ?? [], [result]);
  const fallbackCorrect = useMemo(() => questionHistory.filter((q) => q.is_correct).length, [questionHistory]);
  const totalQuestions = result?.questions_answered ?? questionHistory.length;
  const correctQuestions = result?.questions_correct ?? fallbackCorrect;
  const learningSuggestion = useMemo(() => {
    return getLearningSuggestion(result?.cefr_level, result?.lexile_estimate, CLASS_SCHEDULES);
  }, [result]);

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

  const accuracy = result?.raw_score ?? 0;
  const lexileEstimate = result?.lexile_estimate ? `${result.lexile_estimate}L` : 'N/A';
  const lexileRange =
    result?.lexile_ci_low && result?.lexile_ci_high
      ? `${result.lexile_ci_low}L – ${result.lexile_ci_high}L`
      : null;

  return (
    <div className="results-page">
      <div className="results-toolbar">
        <button onClick={() => navigate('/dashboard')} className="btn btn-secondary">
          <ArrowLeft size={16} />
          Back to Dashboard
        </button>
      </div>

      <div className="results-grid">
        <section className="results-column results-column--left">
          <div className="results-card results-card--primary">
            <div className="results-card__header">
              <Gauge size={20} />
              <span>Placement Overview</span>
            </div>
            <div className="results-card__body">
              <div className="results-cefr">
                <span className="results-cefr__label">CEFR Level</span>
                <span
                  className="results-cefr__value"
                  style={{ color: levelColor(result.cefr_level) }}
                >
                  {result.cefr_level || '—'}
                </span>
              </div>
              <div className="results-lexile">
                <BookOpen size={18} />
                <div>
                  <div className="results-lexile__value">{lexileEstimate}</div>
                  <div className="results-lexile__hint">
                    {lexileRange ? `Confidence: ${lexileRange}` : 'Not enough data for Lexile range'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="results-card">
            <div className="results-card__header">
              <Target size={18} />
              <span>Correction Rate</span>
            </div>
            <div className="results-card__body">
              <div className="results-metric">
                <span className="results-metric__value">{formatPercent(accuracy)}</span>
                <span className="results-metric__hint">
                  {totalQuestions > 0
                    ? `${correctQuestions}/${totalQuestions} questions correct`
                    : 'No questions recorded'}
                </span>
              </div>
              <div className="results-metric__confidence">
                <Activity size={16} />
                <span>Measurement error ±{result.standard_error?.toFixed(2) ?? '—'}</span>
              </div>
            </div>
          </div>
        </section>

        <section className="results-column results-column--right">
          <div className="results-card results-card--suggestion">
            <div className="results-card__header">
              <Lightbulb size={18} />
              <span>Learning suggestions with Coco</span>
            </div>
            <div className="results-card__body results-card__body--suggestion">
              <p className="results-suggestion__copy">{learningSuggestion}</p>
              <p className="results-suggestion__contact">
                Questions or to enroll: email Coco at{' '}
                <a href="mailto:rongwu@gse.harvard.edu">rongwu@gse.harvard.edu</a>
              </p>
            </div>
          </div>
        </section>
      </div>

      <div className="results-next">
        <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
          Return to dashboard
        </button>
      </div>
    </div>
  );
};

export default Results;
