import streamlit as st

def load_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Animasi cahaya bergerak */
    @keyframes shineEffect {
        0% { left: -100%; }
        100% { left: 120%; }
    }
    
    /* Premium Header */
    .premium-header {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #FC5000 0%, #FC5000 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }
    
    .premium-header::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 60%;
        height: 100%;
        background: linear-gradient(
            120deg,
            rgba(255,255,255,0) 0%,
            rgba(255,255,255,0.4) 50%,
            rgba(255,255,255,0) 100%
        );
        transform: skewX(-25deg);
        animation: shineEffect 3.5s infinite;
    }
    
    .premium-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    /* Progress Tracker Premium */
    .progress-premium {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin: 2rem 0;
    }
    
    .step-indicator {
        display: flex;
        justify-content: space-between;
        position: relative;
        margin: 2rem 0;
    }
    
    .step-indicator::before {
        content: '';
        position: absolute;
        top: 30px;
        left: 0;
        width: 100%;
        height: 4px;
        background: #e0e0e0;
        z-index: 1;
    }
    
    .step-item {
        flex: 1;
        text-align: center;
        position: relative;
        z-index: 2;
    }
    
    .step-badge {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: white;
        border: 4px solid #e0e0e0;
        margin: 0 auto 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: 700;
        color: #666;
        transition: all 0.3s ease;
        position: relative;
        background: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    .step-badge.completed {
        background: #4caf50;
        border-color: #4caf50;
        color: white;
        animation: pulse 1s;
    }
    
    .step-badge.active {
        border-color: #FC5000;
        color: #FC5000;
        transform: scale(1.1);
        box-shadow: 0 0 0 6px rgba(252, 80, 0, 0.2);
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    /* Form Premium */
    .premium-form {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    
    .form-section {
        background: #f8faff;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid rgba(252, 80, 0, 0.1);
    }
    
    .form-section h3 {
        color: #333;
        font-weight: 600;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .form-section h3 i {
        color: #FC5000;
    }
    
    /* Cards */
    .premium-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.03);
        border: 1px solid #f0f0f0;
        margin-bottom: 1rem;
    }
    
    .info-card {
        background: linear-gradient(135deg, #fff5e6 0%, #ffe6d5 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #FC5000;
    }
    
    .success-card {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #4caf50;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #ff9800;
    }
    
    /* Login Styles */
    .login-container {
        max-width: 450px;
        margin: 5rem auto;
        padding: 2.5rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        animation: slideUp 0.5s ease;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-header h1 {
        color: #FC5000;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .login-header i {
        font-size: 3rem;
        color: #FC5000;
        margin-bottom: 1rem;
    }
    
    /* Sidebar Styles */
    .sidebar-profile {
        padding: 1.5rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .sidebar-profile i {
        font-size: 3rem;
        color: #FC5000;
        margin-bottom: 0.5rem;
    }
    
    .sidebar-profile h4 {
        color: #333;
        margin-bottom: 0.25rem;
    }
    
    .sidebar-profile p {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 0;
    }
    
    /* Dashboard Styles */
    .dashboard-header {
        background: linear-gradient(135deg, #FC5000 0%, #FF7A00 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(252, 80, 0, 0.3);
    }
    
    .dashboard-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border: 1px solid #f0f0f0;
        transition: transform 0.3s ease;
    }
    
    .dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    </style>
    
    <!-- Font Awesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    """, unsafe_allow_html=True)
