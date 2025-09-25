import React, { createContext, useContext, useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const AssessmentContext = createContext();

export const useAssessment = () => {
  const context = useContext(AssessmentContext);
  if (!context) {
    throw new Error('useAssessment must be used within an AssessmentProvider');
  }
  return context;
};

export const AssessmentProvider = ({ children }) => {
  const [currentAssessment, setCurrentAssessment] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [responses, setResponses] = useState([]);
  const [loading, setLoading] = useState(false);

  const toErrorMessage = (error, fallback) => {
    const detail = error?.response?.data?.detail;
    if (!detail) return fallback;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      const msgs = detail.map((d) => d?.msg || (typeof d === 'string' ? d : null)).filter(Boolean);
      if (msgs.length) return msgs.join('; ');
      try { return JSON.stringify(detail); } catch { return fallback; }
    }
    if (typeof detail === 'object') {
      if (detail.msg) return detail.msg;
      try { return JSON.stringify(detail); } catch { return fallback; }
    }
    return fallback;
  };

  const startAssessment = async (assessmentType) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/assessment/start', {
        assessment_type: assessmentType
      });
      
      const { assessment_id, question, progress } = response.data;
      
      setCurrentAssessment({
        id: assessment_id,
        type: assessmentType,
        progress
      });
      setCurrentQuestion(question);
      setResponses([]);
      
      return { success: true, assessmentId: assessment_id };
    } catch (error) {
      const message = toErrorMessage(error, 'Failed to start assessment');
      toast.error(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const submitResponse = async (questionId, responseData) => {
    try {
      setLoading(true);
      const response = await axios.post(`/api/assessment/${currentAssessment.id}/respond`, {
        question_id: questionId,
        ...responseData
      });
      
      const { 
        response_id, 
        is_correct, 
        feedback, 
        next_question_available, 
        completed: submissionCompleted = false, 
        result: submissionResult 
      } = response.data;
      
      // Add response to our state
      const newResponse = {
        id: response_id,
        questionId,
        ...responseData,
        is_correct,
        feedback
      };
      setResponses(prev => [...prev, newResponse]);
      
      if (next_question_available) {
        // Get next question
        const nextResponse = await axios.get(`/api/assessment/${currentAssessment.id}/next`);

        if (nextResponse.data.completed) {
          setCurrentQuestion(null);
          setCurrentAssessment(prev => ({
            ...prev,
            progress: {
              current: prev?.progress?.total || 0,
              total: prev?.progress?.total || 0
            }
          }));
          return { success: true, completed: true, result: nextResponse.data.result };
        }

        if (nextResponse.data.question) {
          setCurrentQuestion(nextResponse.data.question);
          setCurrentAssessment(prev => ({
            ...prev,
            progress: nextResponse.data.progress
          }));
          return { success: true, completed: false };
        }

        // Fallback: treat as completed if no question returned
        setCurrentQuestion(null);
        return { success: true, completed: true, result: nextResponse.data };
      }

      if (submissionCompleted) {
        setCurrentQuestion(null);
        setCurrentAssessment(prev => ({
          ...prev,
          progress: {
            current: prev?.progress?.total || 0,
            total: prev?.progress?.total || 0
          }
        }));
        return { success: true, completed: true, result: submissionResult };
      }
      
      return { success: true, completed: false };
    } catch (error) {
      const message = toErrorMessage(error, 'Failed to submit response');
      toast.error(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const uploadAudioResponse = async (questionId, audioFile) => {
    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('audio_file', audioFile);
      
      const response = await axios.post(
        `/api/assessment/${currentAssessment.id}/upload-audio`,
        formData,
        {
          params: { question_id: questionId },
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );
      
      const { transcript, fluency_metrics, ai_scores, response_id } = response.data;
      
      // Add response to our state
      const newResponse = {
        id: response_id,
        questionId,
        response_text: transcript,
        fluency_metrics,
        ai_scores,
        is_correct: true
      };
      setResponses(prev => [...prev, newResponse]);
      
      // Get next question
      const nextResponse = await axios.get(`/api/assessment/${currentAssessment.id}/next`);

      if (nextResponse.data.completed) {
        setCurrentQuestion(null);
        setCurrentAssessment(prev => ({
          ...prev,
          progress: {
            current: prev?.progress?.total || 0,
            total: prev?.progress?.total || 0
          }
        }));
        return { success: true, completed: true, result: nextResponse.data.result };
      }

      if (nextResponse.data.question) {
        setCurrentQuestion(nextResponse.data.question);
        setCurrentAssessment(prev => ({
          ...prev,
          progress: nextResponse.data.progress
        }));
        return { success: true, completed: false };
      }

      setCurrentQuestion(null);
      return { success: true, completed: true, result: nextResponse.data };
    } catch (error) {
      const message = toErrorMessage(error, 'Failed to upload audio');
      toast.error(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const uploadWritingResponse = async (questionId, text, imageFile) => {
    try {
      setLoading(true);
      const formData = new FormData();
      if (imageFile) {
        formData.append('image_file', imageFile);
      }
      if (text) {
        formData.append('text', text);
      }
      
      const response = await axios.post(
        `/api/assessment/${currentAssessment.id}/upload-writing`,
        formData,
        {
          params: { question_id: questionId },
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );
      
      const { text: responseText, ai_scores, response_id } = response.data;
      
      // Add response to our state
      const newResponse = {
        id: response_id,
        questionId,
        response_text: responseText,
        ai_scores,
        is_correct: true
      };
      setResponses(prev => [...prev, newResponse]);
      
      // Get next question
      const nextResponse = await axios.get(`/api/assessment/${currentAssessment.id}/next`);

      if (nextResponse.data.completed) {
        setCurrentQuestion(null);
        setCurrentAssessment(prev => ({
          ...prev,
          progress: {
            current: prev?.progress?.total || 0,
            total: prev?.progress?.total || 0
          }
        }));
        return { success: true, completed: true, result: nextResponse.data.result };
      }

      if (nextResponse.data.question) {
        setCurrentQuestion(nextResponse.data.question);
        setCurrentAssessment(prev => ({
          ...prev,
          progress: nextResponse.data.progress
        }));
        return { success: true, completed: false };
      }

      setCurrentQuestion(null);
      return { success: true, completed: true, result: nextResponse.data };
    } catch (error) {
      const message = toErrorMessage(error, 'Failed to upload writing');
      toast.error(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const getAssessmentResult = async (assessmentId) => {
    try {
      const response = await axios.get(`/api/assessment/${assessmentId}/result`);
      return { success: true, data: response.data };
    } catch (error) {
      const message = toErrorMessage(error, 'Failed to get assessment result');
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const submitAssessment = async (assessmentId) => {
    try {
      setLoading(true);
      const response = await axios.post(`/api/assessment/${assessmentId}/submit`);
      return { success: true, data: response.data };
    } catch (error) {
      const message = toErrorMessage(error, 'Failed to submit assessment');
      toast.error(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const getUserAssessments = async (userId) => {
    try {
      const response = await axios.get(`/api/assessment/user/${userId}/assessments`);
      return { success: true, data: response.data };
    } catch (error) {
      const message = toErrorMessage(error, 'Failed to get user assessments');
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const resetAssessment = () => {
    setCurrentAssessment(null);
    setCurrentQuestion(null);
    setResponses([]);
  };

  const value = {
    currentAssessment,
    currentQuestion,
    responses,
    loading,
    startAssessment,
    submitResponse,
    uploadAudioResponse,
    uploadWritingResponse,
    getAssessmentResult,
    submitAssessment,
    getUserAssessments,
    resetAssessment
  };

  return (
    <AssessmentContext.Provider value={value}>
      {children}
    </AssessmentContext.Provider>
  );
};
