import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Play, Pause, Square, Upload } from 'lucide-react';

const AudioRecorder = ({ onRecordingComplete, disabled = false }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioURL, setAudioURL] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [prepTime, setPrepTime] = useState(30);
  const [isPreparing, setIsPreparing] = useState(true);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);
  const intervalRef = useRef(null);
  const prepIntervalRef = useRef(null);

  useEffect(() => {
    // Start preparation timer
    if (isPreparing) {
      prepIntervalRef.current = setInterval(() => {
        setPrepTime(prev => {
          if (prev <= 1) {
            setIsPreparing(false);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => {
      if (prepIntervalRef.current) {
        clearInterval(prepIntervalRef.current);
      }
    };
  }, [isPreparing]);

  useEffect(() => {
    if (isRecording && !isPaused) {
      intervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isRecording, isPaused]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(audioBlob);
        setAudioURL(URL.createObjectURL(audioBlob));
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordingTime(0);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Unable to access microphone. Please check your permissions.');
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (isPaused) {
        mediaRecorderRef.current.resume();
        setIsPaused(false);
      } else {
        mediaRecorderRef.current.pause();
        setIsPaused(true);
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
    }
  };

  const playRecording = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const handleSubmit = () => {
    if (audioBlob && onRecordingComplete) {
      onRecordingComplete(audioBlob);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isPreparing) {
    return (
      <div className="audio-recorder preparing">
        <div className="prep-timer">
          <h3>Preparation Time</h3>
          <div className="timer-display">
            {prepTime}
          </div>
          <p>Think about what you want to say</p>
        </div>
      </div>
    );
  }

  return (
    <div className="audio-recorder">
      {!audioBlob ? (
        <div className="recording-section">
          <div className="recording-controls">
            {!isRecording ? (
              <button
                onClick={startRecording}
                disabled={disabled}
                className="record-button start"
              >
                <Mic size={24} />
                Start Recording
              </button>
            ) : (
              <div className="recording-active">
                <div className="recording-status">
                  <div className="recording-dot"></div>
                  <span>Recording {formatTime(recordingTime)}</span>
                </div>
                <div className="recording-buttons">
                  <button
                    onClick={pauseRecording}
                    className="btn btn-secondary"
                  >
                    {isPaused ? <Play size={16} /> : <Pause size={16} />}
                    {isPaused ? 'Resume' : 'Pause'}
                  </button>
                  <button
                    onClick={stopRecording}
                    className="btn btn-danger"
                  >
                    <Square size={16} />
                    Stop
                  </button>
                </div>
              </div>
            )}
          </div>
          
          <div className="recording-info">
            <p>Maximum recording time: 60 seconds</p>
            <p>Speak clearly and at a normal pace</p>
          </div>
        </div>
      ) : (
        <div className="playback-section">
          <div className="playback-controls">
            <button
              onClick={playRecording}
              className="btn btn-primary"
            >
              {isPlaying ? <Pause size={16} /> : <Play size={16} />}
              {isPlaying ? 'Pause' : 'Play'} Recording
            </button>
            <button
              onClick={() => {
                setAudioBlob(null);
                setAudioURL(null);
                setRecordingTime(0);
              }}
              className="btn btn-secondary"
            >
              Record Again
            </button>
          </div>
          
          <div className="playback-info">
            <p>Duration: {formatTime(recordingTime)}</p>
            <p>Click play to review your recording</p>
          </div>

          <button
            onClick={handleSubmit}
            disabled={disabled}
            className="btn btn-success submit-btn"
          >
            <Upload size={16} />
            Submit Recording
          </button>

          <audio
            ref={audioRef}
            src={audioURL}
            onEnded={() => setIsPlaying(false)}
            onPause={() => setIsPlaying(false)}
            onPlay={() => setIsPlaying(true)}
          />
        </div>
      )}

      <style jsx>{`
        .audio-recorder {
          padding: 2rem;
          background: #f8fafc;
          border-radius: 1rem;
          text-align: center;
        }

        .audio-recorder.preparing {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        .prep-timer h3 {
          font-size: 1.5rem;
          font-weight: 600;
          margin-bottom: 1rem;
        }

        .timer-display {
          font-size: 4rem;
          font-weight: 700;
          margin-bottom: 1rem;
        }

        .prep-timer p {
          font-size: 1.125rem;
          opacity: 0.9;
        }

        .recording-section {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 2rem;
        }

        .record-button {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 1rem 2rem;
          border: none;
          border-radius: 2rem;
          font-size: 1.125rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .record-button.start {
          background: #ef4444;
          color: white;
        }

        .record-button.start:hover:not(:disabled) {
          background: #dc2626;
          transform: scale(1.05);
        }

        .record-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .recording-active {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
        }

        .recording-status {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #ef4444;
          font-weight: 600;
          font-size: 1.125rem;
        }

        .recording-dot {
          width: 0.75rem;
          height: 0.75rem;
          background: #ef4444;
          border-radius: 50%;
          animation: blink 1s infinite;
        }

        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }

        .recording-buttons {
          display: flex;
          gap: 1rem;
        }

        .recording-info {
          color: #64748b;
          font-size: 0.875rem;
        }

        .recording-info p {
          margin: 0.25rem 0;
        }

        .playback-section {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1.5rem;
        }

        .playback-controls {
          display: flex;
          gap: 1rem;
        }

        .playback-info {
          color: #64748b;
          font-size: 0.875rem;
        }

        .playback-info p {
          margin: 0.25rem 0;
        }

        .submit-btn {
          background: #10b981;
          color: white;
          padding: 1rem 2rem;
          font-size: 1.125rem;
          font-weight: 600;
        }

        .submit-btn:hover:not(:disabled) {
          background: #059669;
          transform: translateY(-1px);
        }

        @media (max-width: 768px) {
          .recording-buttons,
          .playback-controls {
            flex-direction: column;
            width: 100%;
          }

          .recording-buttons .btn,
          .playback-controls .btn {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default AudioRecorder;