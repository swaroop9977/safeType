/**
 * API Service for SafeType+ Backend
 * Handles all HTTP requests to the Flask backend
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
const API_KEY = process.env.REACT_APP_API_KEY || '';

export interface ScanTextRequest {
  text: string;
  include_suggestions?: boolean;
  include_highlights?: boolean;
}

export interface ScanImageRequest {
  image: File;
  preprocess?: boolean;
}

export interface PIIDetection {
  type: string;
  value: string;
  start: number;
  end: number;
  confidence: number;
}

export interface Highlight {
  start: number;
  end: number;
  text: string;
  type: string;
  category: string;
  severity: string;
}

export interface Suggestion {
  type: string;
  text: string;
  explanation: string;
  confidence: number;
}

export interface ScanResponse {
  risk_score: number;
  risk_level: string;
  confidence_interval: {
    lower: number;
    upper: number;
  };
  module_breakdown: {
    pii: number;
    nlp: number;
    ocr: number;
  };
  reasons: string[];
  detected_pii: PIIDetection[];
  intent_analysis: {
    probabilities: Record<string, number>;
    manipulation_detected: any;
  };
  highlights?: Highlight[];
  highlighted_text?: string;
  explanation_tokens?: string[];
  safer_suggestions?: Suggestion[];
  detection_summary: any;
  metadata: any;
  ocr_data?: {
    extracted_text: string;
    confidence: number;
    metadata: any;
    highlighted_text?: string;
  };
}

class APIService {
  private client: AxiosInstance;

  constructor() {
    const defaultHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (API_KEY) {
      defaultHeaders['X-API-Key'] = API_KEY;
    }

    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: defaultHeaders,
    });
  }

  async scanText(request: ScanTextRequest): Promise<ScanResponse> {
    try {
      const response = await this.client.post<ScanResponse>('/scan/text', request);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async scanImage(request: ScanImageRequest): Promise<ScanResponse> {
    try {
      const formData = new FormData();
      formData.append('image', request.image);
      formData.append('preprocess', request.preprocess ? 'true' : 'false');

      const imageHeaders: Record<string, string> = {
        'Content-Type': 'multipart/form-data',
      };
      if (API_KEY) {
        imageHeaders['X-API-Key'] = API_KEY;
      }

      const response = await this.client.post<ScanResponse>('/scan/image', formData, {
        headers: imageHeaders,
      });

      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async checkStatus(): Promise<any> {
    try {
      const response = await axios.get(`${API_BASE_URL.replace('/api', '')}/api/status`);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  private handleError(error: any): Error {
    if (error.response) {
      // Server responded with error
      const message = error.response.data?.error || 'Server error occurred';
      return new Error(message);
    } else if (error.request) {
      // No response received
      return new Error('Could not connect to server. Please check if the backend is running.');
    } else {
      // Request setup error
      return new Error(error.message || 'An unexpected error occurred');
    }
  }
}

export const apiService = new APIService();
