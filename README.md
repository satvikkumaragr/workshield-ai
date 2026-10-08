# WorkShield AI

"Predict workforce risks before they become business risks."

WorkShield AI is a workforce resilience platform built for the **AI for Karaikal Hackathon 2026**. 
It identifies critical employees, analyzes dependency risks, simulates business impact if an employee becomes unavailable, and recommends actionable continuity plans.

## Features

- **Executive Dashboard:** High-level view of company resilience, risk vs. dependency.
- **Employee Risk & Dependency:** Detailed breakdown of work risk (burnout, delays) and organizational dependency (skills, projects).
- **Knowledge Risk:** Analysis of poorly documented, single-owner processes.
- **What-If Simulator:** Simulates the business impact of losing a critical employee.
- **Replacement Matching:** AI-driven matching of internal candidates for backup.
- **AI HR Copilot:** Generates actionable HR plans (Knowledge Transfer, Task Redistribution).
- **Workforce Resilience:** Global score calculating the company's preparedness.

## Requirements

- Python 3.8+
- Requirements listed in `requirements.txt`

## Local Deployment

To run this application locally, follow these exact steps:

1. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## Environment Variables

This application is designed to function as a fully working local prototype *without* needing an external API key (uses deterministic local logic for the AI copilot to guarantee the demo works). 

If you extend this to use an LLM API later, you can create a `.env` file and add your keys (e.g., `OPENAI_API_KEY` or `GEMINI_API_KEY`).

## Known Limitations

- The data is synthetic and hardcoded in `data.py` for hackathon demo purposes.
- The AI HR Copilot uses localized deterministic fallback responses to guarantee functionality during the presentation without an API key.
- The matching algorithm uses a weighted heuristic based on the mock data attributes.

## 2-Minute Demo Script

1. **Dashboard:** "WorkShield gives management a real-time view of workforce resilience. Here we see our overall score is 72, with 8 critical employees and 14 without backup."
2. **Employee Risk:** "Looking at Rahul Sharma, we see he has a high risk score of 87 and critical dependency of 93. He's a single point of failure for key projects and documentation is only 18%."
3. **What-If Simulator:** "If we simulate his unavailability, the impact is CRITICAL. 3 projects are affected, 4 critical skills are lost, and backup coverage is 0%."
4. **Replacement Matching:** "Our engine identifies Priya Kumar as an 89% match based on skills and availability. Let's assign her as a backup." *(Click Assign)*
5. **AI HR Copilot:** "Finally, our AI Copilot generates an immediate action plan: initiate knowledge transfer to Priya, assign her as secondary owner, and redistribute tasks."
6. **Workforce Resilience:** "Now we can see our company-level score and focus on our primary improvement opportunity."
