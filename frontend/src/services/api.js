const API_BASE = '/api';

const getHeaders = () => {
  const token = localStorage.getItem('edunexus_token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

export const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    ...options,
    headers: {
      ...getHeaders(),
      ...(options.headers || {})
    }
  };

  try {
    const response = await fetch(url, config);
    
    if (response.status === 401 && !endpoint.includes('/auth/login')) {
      // Gracefully handle token expiration without infinite loop
      localStorage.removeItem('edunexus_token');
      localStorage.removeItem('edunexus_user');
      if (window.location.search.includes('session_expired')) {
        window.history.replaceState({}, document.title, window.location.pathname);
      }
      throw new Error("Session expired. Please log in again.");
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Server returned status ${response.status}`);
    }

    return await response.json();
  } catch (err) {
    console.error(`API Call Error [${endpoint}]:`, err);
    throw err;
  }
};

export const loginApi = (username_or_email, password, selected_role) => apiCall('/auth/login', {
  method: 'POST',
  body: JSON.stringify({ username_or_email, password, selected_role })
});

export const getStudentDashboardApi = () => apiCall('/student/dashboard');

export const createMentorRequestApi = (faculty_id, topic, message) => apiCall('/student/mentor-request', {
  method: 'POST',
  body: JSON.stringify({ faculty_id, topic, message })
});

export const getFacultyDashboardApi = () => apiCall('/faculty/dashboard');

export const toggleFacultyAvailabilityApi = (is_available) => apiCall('/faculty/availability', {
  method: 'PATCH',
  body: JSON.stringify({ is_available_for_mentorship: is_available })
});

export const actionMentorRequestApi = (request_id, status) => apiCall('/faculty/mentor-request/action', {
  method: 'POST',
  body: JSON.stringify({ request_id, status })
});

export const sendDepartmentMessageApi = (recipient_student_id, title, message) => apiCall('/faculty/messages', {
  method: 'POST',
  body: JSON.stringify({ recipient_student_id, title, message })
});

export const getAdminDashboardApi = () => apiCall('/admin/dashboard');

export const getAdminPredictionsApi = () => apiCall('/admin/predictions');

export const agentChatApi = (query) => apiCall('/agent/chat', {
  method: 'POST',
  body: JSON.stringify({ query })
});
