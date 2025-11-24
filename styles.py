"""
CSS styles for the AI Navigator application.
"""
CUSTOM_CSS = """
<style>
    /* 1. Global Reset & Dark Mode optimization + Animated Background */
    .stApp {
        background-color: #0e1117;
        background: radial-gradient(circle at 50% 10%, #1c202b 0%, #0e1117 40%, #0e1117 100%);
        background-size: 200% 200%;
        animation: backgroundShift 20s ease infinite;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        padding-left: 0rem;
        padding-right: 0rem;
        max-width: 100% !important;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* --- ANIMATION KEYFRAMES --- */
    @keyframes backgroundShift {
        0% { background-position: 50% 0%; }
        50% { background-position: 50% 20%; }
        100% { background-position: 50% 0%; }
    }

    @keyframes slideUpFade {
        from { opacity: 0; transform: translateY(40px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(50px); }
        to { opacity: 1; transform: translateX(0); }
    }

    @keyframes popIn {
        0% { opacity: 0; transform: scale(0.8); }
        60% { opacity: 1; transform: scale(1.05); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    @keyframes softPulse {
        0% { transform: scale(1); box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        50% { transform: scale(1.02); box-shadow: 0 0 25px rgba(0, 170, 255, 0.4); }
        100% { transform: scale(1); box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    }

    @keyframes breathingGlow {
        0% { box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.05); }
        50% { box-shadow: 0 15px 50px rgba(0, 100, 255, 0.15); border: 1px solid rgba(0, 100, 255, 0.3); }
        100% { box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.05); }
    }
    
    @keyframes ripple {
        0% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.2); }
        70% { box-shadow: 0 0 0 10px rgba(255, 255, 255, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0); }
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    @keyframes inputSkeleton {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; transform: translateY(0) scale(1); }
        to { opacity: 0; transform: translateY(-10px) scale(0.95); }
    }

    /* 2. Map Container Styling - ENHANCED ANIMATION */
    .stDeckGlJsonChart {
        width: 70% !important;
        min-width: 600px !important;
        height: 70vh !important;
        min-height: 500px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        display: block !important;
        border-radius: 20px !important;
        overflow: hidden !important;
        /* Breathing Animation */
        animation: slideUpFade 1.2s cubic-bezier(0.2, 0.8, 0.2, 1), breathingGlow 6s ease-in-out infinite 1.2s;
        transition: all 0.5s ease;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    iframe {
        width: 100% !important;
        height: 100% !important;
        border-radius: 20px !important;
    }

    /* 3. Floating Input Box Styling */
    div[data-testid="stForm"] {
        width: 100% !important;
        max-width: 600px;
        min-width: 300px;
        margin: 0 auto !important;
        margin-top: 0 !important; 
        position: relative;
        z-index: 9999;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
        background: transparent !important;
        /* Entry Animation (Delayed slightly) */
        animation: slideUpFade 1.4s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    /* REMOVE "Press Enter to apply" text completely */
    div[data-testid="InputInstructions"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    /* INPUT FIELD STYLING - High Tech Feel */
    div[data-baseweb="input"],
    div[data-testid="stTextInput"] > div,
    div[data-testid="stTextInput"] > div > div {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 30px !important; 
    }

    .stTextInput input {
        background-color: rgba(15, 17, 22, 0.85) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 30px !important;
        padding: 22px !important;
        font-size: 16px !important;
        line-height: 1.2 !important;
        backdrop-filter: blur(15px);
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        outline: none !important;
        letter-spacing: 0.5px;
    }
    
    /* FOCUS STATE: Dynamic Glow */
    .stTextInput input:focus {
        background-color: rgba(20, 22, 28, 0.95) !important; 
        border: 1px solid rgba(100, 180, 255, 0.5) !important; 
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.8), 0 0 20px rgba(0, 100, 255, 0.2) !important; 
        transform: scale(1.03) translateY(-4px); 
    }
    
    /* Button Hover Animation (targeting the form submit button) */
    button[kind="secondaryFormSubmit"] {
        display: none !important;
    }

    /* 4. Missing Key State */
    .missing-keys input {
        background-color: rgba(20, 20, 20, 0.3) !important;
        cursor: not-allowed;
    }
    
    /* Input Form Wrapper */
    .input-form-wrapper {
        position: relative;
        width: 50% !important;
        max-width: 600px;
        min-width: 300px;
        margin: 0 auto !important;
        margin-top: -100px !important;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    /* Thinking Indicator - Positioned above entire form container, centered */
    .input-form-wrapper .thinking-indicator {
        text-align: center;
        margin-bottom: 15px;
        margin-top: 0;
        padding: 0;
        animation: fadeIn 0.3s ease-out forwards;
        width: 100%;
        max-width: 600px;
        min-width: 300px;
        position: relative;
        z-index: 10000;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .thinking-indicator {
        text-align: center;
        margin-bottom: 15px;
        margin-top: 0;
        padding: 0;
        animation: fadeIn 0.3s ease-out forwards;
        width: 100%;
        max-width: 600px;
        min-width: 300px;
        margin-left: auto;
        margin-right: auto;
        position: relative;
        z-index: 10000;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .thinking-text {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.85rem;
        font-weight: 500;
        letter-spacing: 1px;
        text-transform: uppercase;
        display: inline-block;
        padding: 4px 0;
        text-align: center;
    }
    
    /* Skeleton Loading for Input */
    .input-skeleton-loading input,
    input[disabled].input-skeleton-loading {
        background: linear-gradient(90deg, 
            rgba(15, 17, 22, 0.85) 0%, 
            rgba(30, 32, 38, 0.95) 50%, 
            rgba(15, 17, 22, 0.85) 100%) !important;
        background-size: 200% 100% !important;
        animation: inputSkeleton 1.5s infinite linear !important;
    }
    
    /* Target input when processing */
    .input-form-wrapper[class*="processing"] input,
    .input-form-wrapper input[disabled] {
        background: linear-gradient(90deg, 
            rgba(15, 17, 22, 0.85) 0%, 
            rgba(30, 32, 38, 0.95) 50%, 
            rgba(15, 17, 22, 0.85) 100%) !important;
        background-size: 200% 100% !important;
        animation: inputSkeleton 1.5s infinite linear !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    .skeleton-map {
        height: 70vh;
        width: 70%;
        min-width: 600px;
        margin: 0 auto;
        border-radius: 20px;
        background: #1f1f1f;
        background-image: linear-gradient(to right, #1f1f1f 0%, #2a2a2a 20%, #1f1f1f 40%, #1f1f1f 100%);
        background-repeat: no-repeat;
        background-size: 2000px 100%; 
        animation: shimmer 1.5s infinite linear; 
        display: flex;
        align-items: center;
        justify-content: center;
        color: #555;
        font-size: 1.2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* RESULT SECTION STYLING */
    .result-spacer {
        margin-top: 130px; 
        margin-bottom: 30px;
        width: 100%;
        height: 1px;
    }

    /* Styled Alert Cards with Slide-In Animation - Enhanced */
    .alert-card {
        background: linear-gradient(135deg, rgba(40, 44, 52, 0.95), rgba(35, 39, 47, 0.9));
        border-left: 4px solid #ff4b4b;
        padding: 20px 24px;
        margin-bottom: 16px;
        border-radius: 12px;
        color: #e0e0e0;
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 16px;
        align-items: start;
        /* Enhanced Physics Animation */
        opacity: 0; 
        animation: slideInRight 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        transition: transform 0.3s ease, background-color 0.3s, box-shadow 0.3s, border-left-width 0.3s;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.05);
    }
    .alert-card:hover {
        transform: translateX(5px) translateY(-2px);
        background: linear-gradient(135deg, rgba(50, 55, 65, 0.98), rgba(45, 50, 60, 0.95));
        box-shadow: 0 8px 25px rgba(0,0,0,0.5);
        border-left-width: 6px;
    }
    
    .alert-card.warning { border-left-color: #ffa500; }
    
    .alert-main {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    .alert-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 4px;
    }
    
    .alert-title {
        color: white;
        font-size: 1.15em;
        font-weight: 600;
        letter-spacing: 0.3px;
        margin: 0;
    }
    
    .alert-temp {
        display: inline-block;
        background: rgba(255,255,255,0.1);
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.9em;
        font-weight: 500;
        margin-left: 8px;
        border: 1px solid rgba(255,255,255,0.15);
    }
    
    .alert-loc {
        font-size: 0.95em;
        color: #b0b0b0;
        display: flex;
        align-items: center;
        gap: 6px;
        margin-top: 4px;
    }
    
    .alert-time {
        text-align: right;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 4px;
        min-width: 100px;
    }
    
    .alert-time-label {
        font-size: 0.75em;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    
    .alert-time-value {
        font-size: 1em;
        color: #d0d0d0;
        font-weight: 500;
        white-space: nowrap;
    }
    
    /* Metric Boxes with Pop-In & Hover Physics */
    .metric-box {
        background: rgba(26, 28, 36, 0.8);
        padding: 25px 20px;
        border-radius: 16px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.4s, border-color 0.4s;
        /* Entry Animation */
        animation: popIn 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) backwards;
    }
    .metric-box:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        border-color: rgba(255,255,255,0.2);
        background: rgba(30, 35, 45, 0.9);
    }
    
    .timeline-header {
        text-align: center;
        color: #d0d0d0;
        margin-bottom: 25px;
        font-size: 1.1em;
        background: rgba(255,255,255,0.03);
        padding: 12px 25px;
        border-radius: 30px;
        width: fit-content;
        margin-left: auto;
        margin-right: auto;
        border: 1px solid rgba(255,255,255,0.05);
        animation: slideUpFade 1s ease-out backwards;
        transition: background 0.3s;
    }
    .timeline-header:hover {
        background: rgba(255,255,255,0.08);
    }

    /* Analyzing Pulse Animation Class - Enhanced */
    .analyzing-pulse {
        animation: softPulse 2s infinite ease-in-out, ripple 2s infinite;
    }
    
    /* Error Pill Fade Animations */
    .error-pill-fadein {
        /* Base class - actual animation timing set inline */
    }
    
    .error-pill-fadeout {
        animation: fadeOut 0.4s cubic-bezier(0.55, 0.055, 0.675, 0.19) forwards;
    }

</style>
"""

