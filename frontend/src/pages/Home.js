import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { BookOpen, CheckCircle, Users, BarChart3 } from 'lucide-react';

const Home = () => {
  const { isAuthenticated } = useAuth();

  const features = [
    {
      icon: <BookOpen size={32} />,
      title: 'Adaptive Reading Assessment',
      description: 'AI-powered comprehension questions that adjust in real time to give you a precise CEFR placement.'
    },
    {
      icon: <BarChart3 size={32} />,
      title: 'Lexile-Calibrated Bank',
      description: 'Curated passages across A2–C2 ensure confident Lexile estimates you can plan around.'
    },
    {
      icon: <Users size={32} />,
      title: 'Guidance from Coco',
      description: "Direct placement into Coco's THINK reading classes plus personalized follow-up support."
    }
  ];

  const assessmentTypes = [
    {
      type: 'reading',
      title: 'Reading Placement',
      description: 'A focused diagnostic that benchmarks your reading skills for Vico Education.',
      icon: <BookOpen size={24} />,
      duration: '15-20 minutes',
      features: ['Adaptive difficulty', 'CEFR alignment', 'Lexile estimate + recommendations']
    }
  ];

  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <h1>Vico Education Reading Placement</h1>
          <p>
            A single, focused reading assessment that adapts to your level and powers Coco's personalized guidance.
          </p>
          <div className="hero-actions">
            {isAuthenticated ? (
              <Link to="/dashboard" className="btn btn-primary">
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary">
                  Get Started
                </Link>
                <Link to="/login" className="btn btn-secondary">
                  Sign In
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="container">
          <h2 style={{ textAlign: 'center', marginBottom: '1rem' }}>
            Why learners choose Vico's reading placement
          </h2>
          <p style={{ textAlign: 'center', color: '#64748b', marginBottom: '2rem' }}>
            Built for Vico Education families who want a clear reading benchmark and next-step guidance from Coco.
          </p>
          
          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">
                  {feature.icon}
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Assessment Types Section */}
      <section className="assessment-types">
        <div className="container">
          <h2 style={{ textAlign: 'center', marginBottom: '1rem' }}>
            Start your reading placement
          </h2>
          <p style={{ textAlign: 'center', color: '#64748b', marginBottom: '2rem' }}>
            A single adaptive route designed to uncover your current reading level and recommended Vico class.
          </p>
          
          <div className="assessment-grid">
            {assessmentTypes.map((assessment, index) => (
              <div key={index} className="assessment-card">
                <div className="assessment-icon">
                  {assessment.icon}
                </div>
                <h3>{assessment.title}</h3>
                <p>{assessment.description}</p>
                <div className="assessment-meta">
                  <span className="duration">⏱️ {assessment.duration}</span>
                </div>
                <ul className="assessment-features">
                  {assessment.features.map((feature, idx) => (
                    <li key={idx}>✓ {feature}</li>
                  ))}
                </ul>
                {isAuthenticated ? (
                  <Link 
                    to={`/assessment/${assessment.type}`} 
                    className="btn btn-primary"
                    style={{ marginTop: '1rem' }}
                  >
                    Start Assessment
                  </Link>
                ) : (
                  <Link 
                    to="/register" 
                    className="btn btn-primary"
                    style={{ marginTop: '1rem' }}
                  >
                    Sign Up to Start
                  </Link>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="benefits" style={{ padding: '4rem 0', background: 'white' }}>
        <div className="container">
          <div className="grid grid-cols-3">
            <div className="benefit-item" style={{ textAlign: 'center' }}>
              <CheckCircle size={48} color="#10b981" />
              <h3>Accurate Placement</h3>
              <p>Get precise CEFR level assessment with confidence intervals</p>
            </div>
            <div className="benefit-item" style={{ textAlign: 'center' }}>
              <Users size={48} color="#3b82f6" />
              <h3>Personalized Learning</h3>
              <p>Receive tailored recommendations based on your specific needs</p>
            </div>
            <div className="benefit-item" style={{ textAlign: 'center' }}>
              <BarChart3 size={48} color="#8b5cf6" />
              <h3>Progress Tracking</h3>
              <p>Monitor your improvement over time with detailed analytics</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta" style={{ 
        padding: '4rem 0', 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        textAlign: 'center'
      }}>
        <div className="container">
          <h2 style={{ marginBottom: '1rem' }}>Ready to Get Started?</h2>
          <p style={{ marginBottom: '2rem', opacity: 0.9 }}>
            Take your reading placement and discover your current Vico classroom fit
          </p>
          {isAuthenticated ? (
            <Link to="/dashboard" className="btn" style={{ 
              background: 'white', 
              color: '#3b82f6',
              fontSize: '1.125rem',
              padding: '1rem 2rem'
            }}>
              Go to Dashboard
            </Link>
          ) : (
            <Link to="/register" className="btn" style={{ 
              background: 'white', 
              color: '#3b82f6',
              fontSize: '1.125rem',
              padding: '1rem 2rem'
            }}>
              Create Free Account
            </Link>
          )}
        </div>
      </section>

      <style jsx>{`
        .assessment-meta {
          margin: 1rem 0;
          font-size: 0.875rem;
          color: #64748b;
        }

        .assessment-features {
          list-style: none;
          padding: 0;
          margin: 1rem 0;
          font-size: 0.875rem;
        }

        .assessment-features li {
          padding: 0.25rem 0;
          color: #64748b;
        }

        .benefit-item {
          padding: 2rem 1rem;
        }

        .benefit-item h3 {
          margin: 1rem 0 0.5rem;
          font-size: 1.25rem;
        }

        .benefit-item p {
          color: #64748b;
          line-height: 1.6;
        }

        @media (max-width: 768px) {
          .grid-cols-3 {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default Home;
