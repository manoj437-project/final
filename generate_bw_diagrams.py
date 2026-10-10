# -*- coding: utf-8 -*-
"""
Generate High-Visibility Black & White / High-Contrast Diagrams for EduMentor AI
Features:
- Extra-large, crystal-clear typography (13px - 22px bold)
- Clear white label boxes on EVERY single data flow arrow
- Rotated 90 degrees counter-clockwise to fill a full A4 portrait page vertically
- Crisp high-resolution rendering with Microsoft Edge Headless
"""

import os
import subprocess
from PIL import Image

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

output_dir = r"d:\project\edumentor-landing\diagram_images"
os.makedirs(output_dir, exist_ok=True)

def wrap_bw_html(svg_content, width=1350, height=900):
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Times New Roman', Times, serif;
    background: #ffffff;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 10px;
  }}
  .canvas {{
    background: #ffffff;
    width: {width}px;
    height: {height}px;
    display: flex;
    justify-content: center;
    align-items: center;
  }}
</style>
</head>
<body>
<div class="canvas">
  {svg_content}
</div>
</body>
</html>"""

# ==============================================================================
# 1. LEVEL 0 DFD (Context Diagram) - High Visibility 1300 x 850
# ==============================================================================
dfd0_svg = """
<svg viewBox="0 0 1300 850" width="1300" height="850" xmlns="http://www.w3.org/2000/svg" font-family="'Times New Roman', serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#000000"/>
    </marker>
  </defs>

  <!-- External Entity: STUDENT -->
  <rect x="40" y="290" width="230" height="250" rx="12" fill="#ffffff" stroke="#000000" stroke-width="2.8"/>
  <text x="155" y="332" fill="#000000" font-size="22" font-weight="bold" text-anchor="middle">STUDENT</text>
  <line x1="55" y1="345" x2="255" y2="345" stroke="#000000" stroke-width="1.8"/>
  <text x="155" y="375" fill="#000000" font-size="15" font-weight="bold" text-anchor="middle">Primary Learner Entity</text>
  <text x="155" y="405" fill="#000000" font-size="14" font-weight="bold" text-anchor="middle">&#8226; Register / Login Account</text>
  <text x="155" y="433" fill="#000000" font-size="14" font-weight="bold" text-anchor="middle">&#8226; Take Scheduled Daily Quiz</text>
  <text x="155" y="461" fill="#000000" font-size="14" font-weight="bold" text-anchor="middle">&#8226; Review Explanatory Scorecard</text>
  <text x="155" y="489" fill="#000000" font-size="14" font-weight="bold" text-anchor="middle">&#8226; Ask 24/7 AI Tutor Doubts</text>
  <text x="155" y="517" fill="#000000" font-size="14" font-weight="bold" text-anchor="middle">&#8226; Flag Comprehension Deficit</text>

  <!-- External Entity: MENTOR / FACULTY -->
  <rect x="1030" y="290" width="230" height="250" rx="12" fill="#ffffff" stroke="#000000" stroke-width="2.8"/>
  <text x="1145" y="332" fill="#000000" font-size="22" font-weight="bold" text-anchor="middle">MENTOR / FACULTY</text>
  <line x1="1045" y1="345" x2="1245" y2="345" stroke="#000000" stroke-width="1.8"/>
  <text x="1145" y="375" fill="#000000" font-size="15" font-weight="bold" text-anchor="middle">Departmental Faculty Entity</text>
  <text x="1145" y="405" fill="#000000" font-size="14" font-weight="bold" text-anchor="middle">&#8226; Manage Weekly Timetables</text>
  <text x="1145" y="433" fill="#000000" font-size="14" font-weight="bold" text-anchor="middle">&#8226; Schedule Daily Syllabus Topic</text>
  <text x="1145" y="461" fill="#000000" font-size="14" font-weight="bold" text-anchor="middle">&#8226; Trigger AI Quiz Synthesis</text>
  <text x="1145" y="489" fill="#000000" font-size="14" font-weight="bold" text-anchor="middle">&#8226; Monitor Cohort Performance</text>
  <text x="1145" y="517" fill="#000000" font-size="14" font-weight="bold" text-anchor="middle">&#8226; Dispatch Remedial Guidance</text>

  <!-- External Entity: GOOGLE GEMINI AI -->
  <rect x="510" y="20" width="280" height="120" rx="12" fill="#ffffff" stroke="#000000" stroke-width="2.8"/>
  <text x="650" y="58" fill="#000000" font-size="21" font-weight="bold" text-anchor="middle">GOOGLE GEMINI AI</text>
  <line x1="525" y1="72" x2="775" y2="72" stroke="#000000" stroke-width="1.8"/>
  <text x="650" y="98" fill="#000000" font-size="15" font-weight="bold" text-anchor="middle">Generative Multimodal LLM Engine</text>
  <text x="650" y="122" fill="#000000" font-size="14" text-anchor="middle">Assessment &amp; Socratic Synthesis</text>

  <!-- External Entity: SMTP EMAIL SERVER -->
  <rect x="510" y="700" width="280" height="120" rx="12" fill="#ffffff" stroke="#000000" stroke-width="2.8"/>
  <text x="650" y="738" fill="#000000" font-size="21" font-weight="bold" text-anchor="middle">SMTP EMAIL SERVER</text>
  <line x1="525" y1="752" x2="775" y2="752" stroke="#000000" stroke-width="1.8"/>
  <text x="650" y="778" fill="#000000" font-size="15" font-weight="bold" text-anchor="middle">Mail Gateway Service (Port 587)</text>
  <text x="650" y="802" fill="#000000" font-size="14" text-anchor="middle">TLS At-Risk Remedial Dispatch</text>

  <!-- Central System: 0.0 EDUMENTOR AI -->
  <circle cx="650" cy="415" r="160" fill="#ffffff" stroke="#000000" stroke-width="3"/>
  <text x="650" y="375" fill="#000000" font-size="28" font-weight="bold" text-anchor="middle">0.0</text>
  <text x="650" y="415" fill="#000000" font-size="24" font-weight="bold" text-anchor="middle">EDUMENTOR AI</text>
  <text x="650" y="448" fill="#000000" font-size="16" font-weight="bold" text-anchor="middle">Continuous Assessment</text>
  <text x="650" y="475" fill="#000000" font-size="16" font-weight="bold" text-anchor="middle">&amp; Automated Mentorship Hub</text>

  <!-- ==================== FLOWS: STUDENT <-> 0.0 ==================== -->
  <!-- Flow 1: Student Registration / Login -->
  <line x1="270" y1="330" x2="495" y2="330" stroke="#000000" stroke-width="2.2" marker-end="url(#arr)"/>
  <rect x="280" y="314" width="200" height="28" rx="5" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="380" y="333" font-size="13.5" font-weight="bold" text-anchor="middle">Registration / Credentials</text>

  <!-- Flow 2: Return Auth Claims & Active Quiz -->
  <line x1="495" y1="380" x2="270" y2="380" stroke="#000000" stroke-width="2.2" marker-end="url(#arr)"/>
  <rect x="280" y="364" width="200" height="28" rx="5" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="380" y="383" font-size="13.5" font-weight="bold" text-anchor="middle">JWT Token &amp; Active Daily Quiz</text>

  <!-- Flow 3: Submit Quiz Answers -->
  <line x1="270" y1="440" x2="495" y2="440" stroke="#000000" stroke-width="2.2" marker-end="url(#arr)"/>
  <rect x="280" y="424" width="200" height="28" rx="5" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="380" y="443" font-size="13.5" font-weight="bold" text-anchor="middle">Answer Vector &amp; Boredom Flag</text>

  <!-- Flow 4: Return Instant Evaluated Scorecard -->
  <line x1="495" y1="500" x2="270" y2="500" stroke="#000000" stroke-width="2.2" marker-end="url(#arr)"/>
  <rect x="280" y="484" width="200" height="28" rx="5" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="380" y="503" font-size="13.5" font-weight="bold" text-anchor="middle">Evaluated Scorecard &amp; Hints</text>

  <!-- ==================== FLOWS: MENTOR <-> 0.0 ==================== -->
  <!-- Flow 5: Mentor Auth -->
  <line x1="1030" y1="330" x2="805" y2="330" stroke="#000000" stroke-width="2.2" marker-end="url(#arr)"/>
  <rect x="820" y="314" width="200" height="28" rx="5" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="920" y="333" font-size="13.5" font-weight="bold" text-anchor="middle">Staff Credentials &amp; Login</text>

  <!-- Flow 6: Timetable & Topic Setup -->
  <line x1="1030" y1="380" x2="805" y2="380" stroke="#000000" stroke-width="2.2" marker-end="url(#arr)"/>
  <rect x="815" y="364" width="210" height="28" rx="5" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="920" y="383" font-size="13.5" font-weight="bold" text-anchor="middle">Timetable Slots &amp; Topic Quotas</text>

  <!-- Flow 7: Return Cohort Analytics -->
  <line x1="805" y1="440" x2="1030" y2="440" stroke="#000000" stroke-width="2.2" marker-end="url(#arr)"/>
  <rect x="820" y="424" width="200" height="28" rx="5" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="920" y="443" font-size="13.5" font-weight="bold" text-anchor="middle">Cohort Performance Analytics</text>

  <!-- Flow 8: Return At-Risk Roster -->
  <line x1="805" y1="500" x2="1030" y2="500" stroke="#000000" stroke-width="2.2" marker-end="url(#arr)"/>
  <rect x="815" y="484" width="210" height="28" rx="5" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="920" y="503" font-size="13.5" font-weight="bold" text-anchor="middle">At-Risk Diagnostic Roster (&lt;40%)</text>

  <!-- ==================== FLOWS: GEMINI AI <-> 0.0 ==================== -->
  <!-- Prompt to Gemini -->
  <line x1="600" y1="260" x2="600" y2="145" stroke="#000000" stroke-width="2.2" marker-end="url(#arr)"/>
  <rect x="420" y="185" width="170" height="28" rx="5" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="505" y="204" font-size="13.5" font-weight="bold" text-anchor="middle">Syllabus Prompt &amp; Schema</text>

  <!-- Response from Gemini -->
  <line x1="700" y1="145" x2="700" y2="260" stroke="#000000" stroke-width="2.2" marker-end="url(#arr)"/>
  <rect x="710" y="185" width="180" height="28" rx="5" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="800" y="204" font-size="13.5" font-weight="bold" text-anchor="middle">Synthesized Quiz JSON / Hints</text>

  <!-- ==================== FLOWS: 0.0 -> SMTP SERVER ==================== -->
  <line x1="650" y1="575" x2="650" y2="695" stroke="#000000" stroke-width="2.2" marker-end="url(#arr)"/>
  <rect x="510" y="620" width="280" height="28" rx="5" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="650" y="639" font-size="14" font-weight="bold" text-anchor="middle">TLS Outbound Remedial Emails (Port 587)</text>
</svg>
"""

# ==============================================================================
# 2. LEVEL 1 DFD (Overall Architecture) - High Visibility 1380 x 940
# ==============================================================================
dfd1_svg = """
<svg viewBox="0 0 1380 940" width="1380" height="940" xmlns="http://www.w3.org/2000/svg" font-family="'Times New Roman', serif">
  <defs>
    <marker id="arr1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#000000"/>
    </marker>
  </defs>

  <!-- ENTITY: STUDENT -->
  <rect x="30" y="40" width="170" height="110" rx="10" fill="#ffffff" stroke="#000000" stroke-width="2.8"/>
  <text x="115" y="82" font-size="19" font-weight="bold" text-anchor="middle">STUDENT</text>
  <line x1="45" y1="92" x2="185" y2="92" stroke="#000000" stroke-width="1.5"/>
  <text x="115" y="118" font-size="14" font-weight="bold" text-anchor="middle">Primary Learner Actor</text>

  <!-- ENTITY: MENTOR -->
  <rect x="1180" y="40" width="170" height="110" rx="10" fill="#ffffff" stroke="#000000" stroke-width="2.8"/>
  <text x="1265" y="82" font-size="19" font-weight="bold" text-anchor="middle">MENTOR</text>
  <line x1="1195" y1="92" x2="1335" y2="92" stroke="#000000" stroke-width="1.5"/>
  <text x="1265" y="118" font-size="14" font-weight="bold" text-anchor="middle">Faculty / Curriculum Lead</text>

  <!-- ENTITY: GEMINI AI -->
  <rect x="1180" y="760" width="170" height="110" rx="10" fill="#ffffff" stroke="#000000" stroke-width="2.8"/>
  <text x="1265" y="802" font-size="18" font-weight="bold" text-anchor="middle">GEMINI AI</text>
  <line x1="1195" y1="812" x2="1335" y2="812" stroke="#000000" stroke-width="1.5"/>
  <text x="1265" y="838" font-size="14" font-weight="bold" text-anchor="middle">GenAI LLM Engine</text>

  <!-- ENTITY: SMTP SERVER -->
  <rect x="30" y="760" width="170" height="110" rx="10" fill="#ffffff" stroke="#000000" stroke-width="2.8"/>
  <text x="115" y="802" font-size="18" font-weight="bold" text-anchor="middle">SMTP SERVER</text>
  <line x1="45" y1="812" x2="185" y2="812" stroke="#000000" stroke-width="1.5"/>
  <text x="115" y="838" font-size="14" font-weight="bold" text-anchor="middle">TLS Mail Dispatcher</text>

  <!-- PROCESS 1.0: AUTHENTICATION -->
  <ellipse cx="340" cy="95" rx="90" ry="50" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="340" y="86" font-size="16" font-weight="bold" text-anchor="middle">1.0</text>
  <text x="340" y="108" font-size="15" font-weight="bold" text-anchor="middle">Authentication</text>

  <!-- PROCESS 2.0: TIMETABLE & TOPICS -->
  <ellipse cx="1000" cy="95" rx="100" ry="50" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="1000" y="86" font-size="16" font-weight="bold" text-anchor="middle">2.0</text>
  <text x="1000" y="108" font-size="15" font-weight="bold" text-anchor="middle">Timetable &amp; Topic</text>

  <!-- PROCESS 3.0: AI QUIZ GENERATION -->
  <ellipse cx="1000" cy="365" rx="100" ry="52" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="1000" y="356" font-size="16" font-weight="bold" text-anchor="middle">3.0</text>
  <text x="1000" y="378" font-size="15" font-weight="bold" text-anchor="middle">AI Quiz Engine</text>

  <!-- PROCESS 4.0: QUIZ EVALUATION -->
  <ellipse cx="340" cy="365" rx="100" ry="52" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="340" y="356" font-size="16" font-weight="bold" text-anchor="middle">4.0</text>
  <text x="340" y="378" font-size="15" font-weight="bold" text-anchor="middle">Quiz Evaluation</text>

  <!-- PROCESS 5.0: AI TUTOR CHATBOT -->
  <ellipse cx="340" cy="610" rx="100" ry="52" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="340" y="601" font-size="16" font-weight="bold" text-anchor="middle">5.0</text>
  <text x="340" y="623" font-size="15" font-weight="bold" text-anchor="middle">AI Tutor Chat</text>

  <!-- PROCESS 6.0: WEAK-STUDENT REMEDIATION -->
  <ellipse cx="670" cy="495" rx="100" ry="52" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="670" y="486" font-size="16" font-weight="bold" text-anchor="middle">6.0</text>
  <text x="670" y="508" font-size="15" font-weight="bold" text-anchor="middle">Remedial Engine</text>

  <!-- PROCESS 7.0: MENTOR ANALYTICS -->
  <ellipse cx="1000" cy="610" rx="100" ry="52" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="1000" y="601" font-size="16" font-weight="bold" text-anchor="middle">7.0</text>
  <text x="1000" y="623" font-size="15" font-weight="bold" text-anchor="middle">Mentor Analytics</text>

  <!-- DATA STORES -->
  <!-- D1: Users -->
  <g>
    <line x1="580" y1="75" x2="760" y2="75" stroke="#000000" stroke-width="2.8"/>
    <line x1="580" y1="115" x2="760" y2="115" stroke="#000000" stroke-width="2.8"/>
    <text x="670" y="101" font-size="14.5" font-weight="bold" text-anchor="middle">D1: students / mentors</text>
  </g>

  <!-- D2: Daily Topics -->
  <g>
    <line x1="580" y1="210" x2="760" y2="210" stroke="#000000" stroke-width="2.8"/>
    <line x1="580" y1="250" x2="760" y2="250" stroke="#000000" stroke-width="2.8"/>
    <text x="670" y="236" font-size="14.5" font-weight="bold" text-anchor="middle">D2: daily_topics</text>
  </g>

  <!-- D3: Topic History -->
  <g>
    <line x1="580" y1="340" x2="760" y2="340" stroke="#000000" stroke-width="2.8"/>
    <line x1="580" y1="380" x2="760" y2="380" stroke="#000000" stroke-width="2.8"/>
    <text x="670" y="366" font-size="14.5" font-weight="bold" text-anchor="middle">D3: topic_history</text>
  </g>

  <!-- D4: Student Scores -->
  <g>
    <line x1="580" y1="635" x2="760" y2="635" stroke="#000000" stroke-width="2.8"/>
    <line x1="580" y1="675" x2="760" y2="675" stroke="#000000" stroke-width="2.8"/>
    <text x="670" y="661" font-size="14.5" font-weight="bold" text-anchor="middle">D4: student_scores</text>
  </g>

  <!-- D5: Chat History -->
  <g>
    <line x1="580" y1="765" x2="760" y2="765" stroke="#000000" stroke-width="2.8"/>
    <line x1="580" y1="805" x2="760" y2="805" stroke="#000000" stroke-width="2.8"/>
    <text x="670" y="791" font-size="14.5" font-weight="bold" text-anchor="middle">D5: chat_messages</text>
  </g>

  <!-- ==================== FLOWS & CLEAR PILL LABELS ==================== -->
  <!-- Student -> 1.0 -->
  <line x1="200" y1="95" x2="245" y2="95" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="202" y="78" width="46" height="22" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1"/>
  <text x="225" y="94" font-size="12" font-weight="bold" text-anchor="middle">Login</text>

  <!-- Mentor -> 1.0 -->
  <line x1="1180" y1="70" x2="1100" y2="70" stroke="#000000" stroke-width="2.2"/>
  <line x1="1100" y1="70" x2="435" y2="70" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="740" y="58" width="115" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="797" y="75" font-size="13" font-weight="bold" text-anchor="middle">Mentor Auth</text>

  <!-- 1.0 <-> D1 -->
  <line x1="430" y1="95" x2="575" y2="95" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="445" y="83" width="130" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="510" y="100" font-size="12.5" font-weight="bold" text-anchor="middle">Verify Password Hash</text>

  <!-- Mentor -> 2.0 -->
  <line x1="1180" y1="95" x2="1105" y2="95" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="1108" y="82" width="72" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1"/>
  <text x="1144" y="99" font-size="12.5" font-weight="bold" text-anchor="middle">Set Topic</text>

  <!-- 2.0 -> D2 -->
  <line x1="900" y1="95" x2="760" y2="95" stroke="#000000" stroke-width="2.2"/>
  <line x1="760" y1="95" x2="690" y2="205" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="730" y="140" width="135" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="797" y="157" font-size="12.5" font-weight="bold" text-anchor="middle">Upsert Daily Topic</text>

  <!-- 2.0 -> 3.0 -->
  <line x1="1000" y1="150" x2="1000" y2="310" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="920" y="220" width="160" height="26" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="1000" y="238" font-size="13" font-weight="bold" text-anchor="middle">Topic &amp; Format Quotas</text>

  <!-- 3.0 <-> GEMINI AI -->
  <line x1="1095" y1="385" x2="1180" y2="770" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="1090" y="555" width="135" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="1157" y="572" font-size="12.5" font-weight="bold" text-anchor="middle">Prompt &amp; Schema</text>

  <line x1="1180" y1="800" x2="1075" y2="410" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="1070" y="590" width="150" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="1145" y="607" font-size="12.5" font-weight="bold" text-anchor="middle">Synthesized Quiz JSON</text>

  <!-- 3.0 -> D3 -->
  <line x1="900" y1="365" x2="765" y2="365" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="770" y="353" width="125" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="832" y="370" font-size="12.5" font-weight="bold" text-anchor="middle">Store Question Pool</text>

  <!-- D3 -> 4.0 -->
  <line x1="580" y1="365" x2="445" y2="365" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="460" y="353" width="120" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="520" y="370" font-size="12.5" font-weight="bold" text-anchor="middle">Fetch Active Quiz</text>

  <!-- Student -> 4.0 -->
  <line x1="120" y1="150" x2="270" y2="335" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="110" y="225" width="145" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="182" y="242" font-size="12.5" font-weight="bold" text-anchor="middle">Submit Answer Vector</text>

  <!-- 4.0 -> Student -->
  <line x1="250" y1="350" x2="105" y2="155" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="95" y="255" width="135" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="162" y="272" font-size="12.5" font-weight="bold" text-anchor="middle">Instant Scorecard</text>

  <!-- 4.0 -> D4 -->
  <line x1="425" y1="390" x2="600" y2="630" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="445" y="495" width="135" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="512" y="512" font-size="12.5" font-weight="bold" text-anchor="middle">Commit Scores &amp; Marks</text>

  <!-- Student -> 5.0 -->
  <line x1="115" y1="150" x2="115" y2="610" stroke="#000000" stroke-width="2.2"/>
  <line x1="115" y1="610" x2="235" y2="610" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="120" y="445" width="135" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="187" y="462" font-size="12.5" font-weight="bold" text-anchor="middle">Socratic Doubt Query</text>

  <!-- 5.0 -> Student -->
  <line x1="240" y1="630" x2="85" y2="630" stroke="#000000" stroke-width="2.2"/>
  <line x1="85" y1="630" x2="85" y2="155" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="50" y="380" width="135" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="117" y="397" font-size="12.5" font-weight="bold" text-anchor="middle">Guided AI Response</text>

  <!-- 5.0 <-> D5 -->
  <line x1="435" y1="635" x2="575" y2="770" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="460" y="700" width="130" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="525" y="717" font-size="12.5" font-weight="bold" text-anchor="middle">Append Chat Turn</text>

  <!-- 5.0 <-> GEMINI AI -->
  <line x1="440" y1="610" x2="1175" y2="820" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="740" y="715" width="170" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="825" y="732" font-size="12.5" font-weight="bold" text-anchor="middle">Socratic Prompt &amp; Clue</text>

  <!-- D4 -> 6.0 -->
  <line x1="670" y1="630" x2="670" y2="550" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="610" y="580" width="120" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="670" y="597" font-size="12.5" font-weight="bold" text-anchor="middle">Scan Scores &lt;40%</text>

  <!-- 6.0 -> 7.0 -->
  <line x1="770" y1="510" x2="905" y2="585" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="770" y="540" width="135" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="837" y="557" font-size="12.5" font-weight="bold" text-anchor="middle">At-Risk Student List</text>

  <!-- 7.0 -> Mentor -->
  <line x1="1000" y1="555" x2="1000" y2="155" stroke="#000000" stroke-width="2.2"/>
  <line x1="1000" y1="155" x2="1175" y2="115" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="1005" y="270" width="150" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="1080" y="287" font-size="12.5" font-weight="bold" text-anchor="middle">Telemetry &amp; Low Scores</text>

  <!-- Mentor -> 6.0 -->
  <line x1="1265" y1="155" x2="1265" y2="480" stroke="#000000" stroke-width="2.2"/>
  <line x1="1265" y1="480" x2="775" y2="495" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="990" y="475" width="150" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="1065" y="492" font-size="12.5" font-weight="bold" text-anchor="middle">Trigger Remedial Alert</text>

  <!-- 6.0 -> SMTP SERVER -->
  <line x1="570" y1="510" x2="205" y2="780" stroke="#000000" stroke-width="2.2" marker-end="url(#arr1)"/>
  <rect x="330" y="650" width="170" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="415" y="667" font-size="12.5" font-weight="bold" text-anchor="middle">Dispatch Remedial Email</text>
</svg>
"""

# ==============================================================================
# 3. LEVEL 2 DFD - STUDENT SUBSYSTEM
# ==============================================================================
dfd2_student_svg = """
<svg viewBox="0 0 1300 850" width="1300" height="850" xmlns="http://www.w3.org/2000/svg" font-family="'Times New Roman', serif">
  <defs>
    <marker id="arr2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#000000"/>
    </marker>
  </defs>

  <!-- EXTERNAL ACTOR: STUDENT -->
  <rect x="40" y="320" width="180" height="180" rx="10" fill="#ffffff" stroke="#000000" stroke-width="2.8"/>
  <text x="130" y="390" font-size="20" font-weight="bold" text-anchor="middle">STUDENT</text>
  <line x1="55" y1="405" x2="205" y2="405" stroke="#000000" stroke-width="1.5"/>
  <text x="130" y="435" font-size="15" font-weight="bold" text-anchor="middle">Learner User</text>
  <text x="130" y="465" font-size="13" text-anchor="middle">Portal Session Active</text>

  <!-- EXTERNAL ACTOR: GEMINI AI -->
  <rect x="1080" y="60" width="180" height="130" rx="10" fill="#ffffff" stroke="#000000" stroke-width="2.8"/>
  <text x="1170" y="115" font-size="19" font-weight="bold" text-anchor="middle">GEMINI AI</text>
  <line x1="1095" y1="128" x2="1245" y2="128" stroke="#000000" stroke-width="1.5"/>
  <text x="1170" y="155" font-size="14" font-weight="bold" text-anchor="middle">Socratic Tutor Engine</text>

  <!-- PROCESS 4.1: Fetch Active Quiz -->
  <ellipse cx="430" cy="130" rx="105" ry="52" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="430" y="122" font-size="16" font-weight="bold" text-anchor="middle">4.1</text>
  <text x="430" y="144" font-size="15" font-weight="bold" text-anchor="middle">Fetch Active Quiz</text>

  <!-- PROCESS 4.2: Verify Countdown -->
  <ellipse cx="780" cy="130" rx="105" ry="52" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="780" y="122" font-size="16" font-weight="bold" text-anchor="middle">4.2</text>
  <text x="780" y="144" font-size="15" font-weight="bold" text-anchor="middle">Verify Countdown</text>

  <!-- PROCESS 4.3: Auto-Evaluate Answers -->
  <ellipse cx="430" cy="380" rx="105" ry="52" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="430" y="372" font-size="16" font-weight="bold" text-anchor="middle">4.3</text>
  <text x="430" y="394" font-size="15" font-weight="bold" text-anchor="middle">Auto-Evaluate Answers</text>

  <!-- PROCESS 4.4: Record Score to DB -->
  <ellipse cx="780" cy="380" rx="105" ry="52" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="780" y="372" font-size="16" font-weight="bold" text-anchor="middle">4.4</text>
  <text x="780" y="394" font-size="15" font-weight="bold" text-anchor="middle">Record Score to DB</text>

  <!-- PROCESS 5.1: Socratic AI Doubt Clearing -->
  <ellipse cx="600" cy="650" rx="115" ry="55" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="600" y="642" font-size="16" font-weight="bold" text-anchor="middle">5.1</text>
  <text x="600" y="664" font-size="15" font-weight="bold" text-anchor="middle">Socratic Doubt Resolver</text>

  <!-- DATA STORES -->
  <g>
    <line x1="1080" y1="360" x2="1260" y2="360" stroke="#000000" stroke-width="2.8"/>
    <line x1="1080" y1="400" x2="1260" y2="400" stroke="#000000" stroke-width="2.8"/>
    <text x="1170" y="386" font-size="14.5" font-weight="bold" text-anchor="middle">D4: student_scores</text>
  </g>
  <g>
    <line x1="1080" y1="480" x2="1260" y2="480" stroke="#000000" stroke-width="2.8"/>
    <line x1="1080" y1="520" x2="1260" y2="520" stroke="#000000" stroke-width="2.8"/>
    <text x="1170" y="506" font-size="14.5" font-weight="bold" text-anchor="middle">D4: quiz_attempts</text>
  </g>
  <g>
    <line x1="1080" y1="630" x2="1260" y2="630" stroke="#000000" stroke-width="2.8"/>
    <line x1="1080" y1="670" x2="1260" y2="670" stroke="#000000" stroke-width="2.8"/>
    <text x="1170" y="656" font-size="14.5" font-weight="bold" text-anchor="middle">D5: chat_messages</text>
  </g>

  <!-- FLOWS -->
  <!-- Student -> 4.1 -->
  <line x1="180" y1="320" x2="350" y2="170" stroke="#000000" stroke-width="2.2" marker-end="url(#arr2)"/>
  <rect x="210" y="210" width="135" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="277" y="227" font-size="12.5" font-weight="bold" text-anchor="middle">Request Daily Quiz</text>

  <!-- 4.1 -> 4.2 -->
  <line x1="535" y1="130" x2="670" y2="130" stroke="#000000" stroke-width="2.2" marker-end="url(#arr2)"/>
  <rect x="545" y="118" width="115" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="602" y="135" font-size="12.5" font-weight="bold" text-anchor="middle">Topic &amp; Deadline</text>

  <!-- 4.2 -> Student -->
  <line x1="720" y1="170" x2="225" y2="350" stroke="#000000" stroke-width="2.2" marker-end="url(#arr2)"/>
  <rect x="420" y="240" width="155" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="497" y="257" font-size="12.5" font-weight="bold" text-anchor="middle">Render Active Questions</text>

  <!-- Student -> 4.3 -->
  <line x1="220" y1="380" x2="320" y2="380" stroke="#000000" stroke-width="2.2" marker-end="url(#arr2)"/>
  <rect x="225" y="368" width="95" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="272" y="385" font-size="12.5" font-weight="bold" text-anchor="middle">Submit Vector</text>

  <!-- 4.3 -> 4.4 -->
  <line x1="535" y1="380" x2="670" y2="380" stroke="#000000" stroke-width="2.2" marker-end="url(#arr2)"/>
  <rect x="545" y="368" width="115" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="602" y="385" font-size="12.5" font-weight="bold" text-anchor="middle">Computed Score</text>

  <!-- 4.4 -> D4 scores -->
  <line x1="885" y1="380" x2="1075" y2="380" stroke="#000000" stroke-width="2.2" marker-end="url(#arr2)"/>
  <rect x="910" y="368" width="145" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="982" y="385" font-size="12.5" font-weight="bold" text-anchor="middle">Insert Score Record</text>

  <!-- 4.4 -> D4 attempts -->
  <line x1="860" y1="410" x2="1075" y2="490" stroke="#000000" stroke-width="2.2" marker-end="url(#arr2)"/>
  <rect x="915" y="445" width="140" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="985" y="462" font-size="12.5" font-weight="bold" text-anchor="middle">Log Detailed Answers</text>

  <!-- 4.4 -> Student -->
  <line x1="720" y1="415" x2="225" y2="465" stroke="#000000" stroke-width="2.2" marker-end="url(#arr2)"/>
  <rect x="420" y="435" width="145" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="492" y="452" font-size="12.5" font-weight="bold" text-anchor="middle">Instant Scorecard &amp; %</text>

  <!-- Student -> 5.1 -->
  <line x1="180" y1="500" x2="490" y2="635" stroke="#000000" stroke-width="2.2" marker-end="url(#arr2)"/>
  <rect x="270" y="565" width="145" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="342" y="582" font-size="12.5" font-weight="bold" text-anchor="middle">Socratic Query Input</text>

  <!-- 5.1 <-> GEMINI AI -->
  <line x1="710" y1="620" x2="1110" y2="195" stroke="#000000" stroke-width="2.2" marker-end="url(#arr2)"/>
  <rect x="860" y="380" width="150" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="935" y="397" font-size="12.5" font-weight="bold" text-anchor="middle">Prompt Context / Hints</text>

  <!-- 5.1 -> D5 -->
  <line x1="715" y1="650" x2="1075" y2="650" stroke="#000000" stroke-width="2.2" marker-end="url(#arr2)"/>
  <rect x="850" y="638" width="155" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="927" y="655" font-size="12.5" font-weight="bold" text-anchor="middle">Commit Chat Message</text>

  <!-- 5.1 -> Student -->
  <line x1="485" y1="670" x2="180" y2="520" stroke="#000000" stroke-width="2.2" marker-end="url(#arr2)"/>
  <rect x="260" y="605" width="155" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="337" y="622" font-size="12.5" font-weight="bold" text-anchor="middle">Guided Socratic Advice</text>
</svg>
"""

# ==============================================================================
# 4. LEVEL 2 DFD - MENTOR SUBSYSTEM
# ==============================================================================
dfd2_mentor_svg = """
<svg viewBox="0 0 1300 850" width="1300" height="850" xmlns="http://www.w3.org/2000/svg" font-family="'Times New Roman', serif">
  <defs>
    <marker id="arr3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#000000"/>
    </marker>
  </defs>

  <!-- EXTERNAL ACTOR: MENTOR -->
  <rect x="40" y="330" width="185" height="180" rx="10" fill="#ffffff" stroke="#000000" stroke-width="2.8"/>
  <text x="132" y="395" font-size="20" font-weight="bold" text-anchor="middle">MENTOR</text>
  <line x1="55" y1="410" x2="210" y2="410" stroke="#000000" stroke-width="1.5"/>
  <text x="132" y="440" font-size="15" font-weight="bold" text-anchor="middle">Faculty Advisor</text>
  <text x="132" y="470" font-size="13" text-anchor="middle">Curriculum Manager</text>

  <!-- EXTERNAL ACTOR: GEMINI AI -->
  <rect x="40" y="70" width="185" height="130" rx="10" fill="#ffffff" stroke="#000000" stroke-width="2.8"/>
  <text x="132" y="125" font-size="19" font-weight="bold" text-anchor="middle">GEMINI AI</text>
  <line x1="55" y1="138" x2="210" y2="138" stroke="#000000" stroke-width="1.5"/>
  <text x="132" y="165" font-size="14" font-weight="bold" text-anchor="middle">Quiz Synthesizer</text>

  <!-- EXTERNAL ACTOR: SMTP SERVER -->
  <rect x="1080" y="710" width="185" height="120" rx="10" fill="#ffffff" stroke="#000000" stroke-width="2.8"/>
  <text x="1172" y="760" font-size="19" font-weight="bold" text-anchor="middle">SMTP SERVER</text>
  <line x1="1095" y1="772" x2="1250" y2="772" stroke="#000000" stroke-width="1.5"/>
  <text x="1172" y="798" font-size="14" font-weight="bold" text-anchor="middle">Port 587 TLS Mailer</text>

  <!-- PROCESS 2.1: Set Timetable Matrix -->
  <ellipse cx="430" cy="115" rx="105" ry="50" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="430" y="107" font-size="16" font-weight="bold" text-anchor="middle">2.1</text>
  <text x="430" y="129" font-size="15" font-weight="bold" text-anchor="middle">Set Timetable Matrix</text>

  <!-- PROCESS 2.2: Set Active Topic -->
  <ellipse cx="780" cy="115" rx="105" ry="50" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="780" y="107" font-size="16" font-weight="bold" text-anchor="middle">2.2</text>
  <text x="780" y="129" font-size="15" font-weight="bold" text-anchor="middle">Set Active Topic</text>

  <!-- PROCESS 3.1: Trigger Gemini Synthesis -->
  <ellipse cx="430" cy="380" rx="105" ry="50" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="430" y="372" font-size="16" font-weight="bold" text-anchor="middle">3.1</text>
  <text x="430" y="394" font-size="15" font-weight="bold" text-anchor="middle">AI Quiz Generation</text>

  <!-- PROCESS 7.1: Aggregate Analytics -->
  <ellipse cx="780" cy="380" rx="105" ry="50" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="780" y="372" font-size="16" font-weight="bold" text-anchor="middle">7.1</text>
  <text x="780" y="394" font-size="15" font-weight="bold" text-anchor="middle">Aggregate Analytics</text>

  <!-- PROCESS 6.1: Scan Cohort Scores -->
  <ellipse cx="430" cy="670" rx="105" ry="50" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="430" y="662" font-size="16" font-weight="bold" text-anchor="middle">6.1</text>
  <text x="430" y="684" font-size="15" font-weight="bold" text-anchor="middle">Scan Cohort Scores</text>

  <!-- PROCESS 6.2: Dispatch SMTP Alert -->
  <ellipse cx="780" cy="670" rx="105" ry="50" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
  <text x="780" y="662" font-size="16" font-weight="bold" text-anchor="middle">6.2</text>
  <text x="780" y="684" font-size="15" font-weight="bold" text-anchor="middle">Dispatch SMTP Alert</text>

  <!-- DATA STORES -->
  <g>
    <line x1="1080" y1="95" x2="1260" y2="95" stroke="#000000" stroke-width="2.8"/>
    <line x1="1080" y1="135" x2="1260" y2="135" stroke="#000000" stroke-width="2.8"/>
    <text x="1170" y="121" font-size="14" font-weight="bold" text-anchor="middle">D2: weekly_timetables</text>
  </g>
  <g>
    <line x1="1080" y1="210" x2="1260" y2="210" stroke="#000000" stroke-width="2.8"/>
    <line x1="1080" y1="250" x2="1260" y2="250" stroke="#000000" stroke-width="2.8"/>
    <text x="1170" y="236" font-size="14" font-weight="bold" text-anchor="middle">D2: daily_topics</text>
  </g>
  <g>
    <line x1="1080" y1="360" x2="1260" y2="360" stroke="#000000" stroke-width="2.8"/>
    <line x1="1080" y1="400" x2="1260" y2="400" stroke="#000000" stroke-width="2.8"/>
    <text x="1170" y="386" font-size="14" font-weight="bold" text-anchor="middle">D4: student_scores</text>
  </g>
  <g>
    <line x1="1080" y1="645" x2="1260" y2="645" stroke="#000000" stroke-width="2.8"/>
    <line x1="1080" y1="685" x2="1260" y2="685" stroke="#000000" stroke-width="2.8"/>
    <text x="1170" y="671" font-size="14" font-weight="bold" text-anchor="middle">D7: mentor_actions</text>
  </g>

  <!-- FLOWS -->
  <!-- Mentor -> 2.1 -->
  <line x1="180" y1="330" x2="350" y2="155" stroke="#000000" stroke-width="2.2" marker-end="url(#arr3)"/>
  <rect x="200" y="220" width="145" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="272" y="237" font-size="12.5" font-weight="bold" text-anchor="middle">Define 6-Day Grid</text>

  <!-- 2.1 -> D2 timetables -->
  <line x1="535" y1="115" x2="1075" y2="115" stroke="#000000" stroke-width="2.2" marker-end="url(#arr3)"/>
  <rect x="680" y="103" width="155" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="757" y="120" font-size="12.5" font-weight="bold" text-anchor="middle">Save Timetable Rows</text>

  <!-- Mentor -> 2.2 -->
  <line x1="180" y1="350" x2="700" y2="145" stroke="#000000" stroke-width="2.2" marker-end="url(#arr3)"/>
  <rect x="360" y="210" width="155" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="437" y="227" font-size="12.5" font-weight="bold" text-anchor="middle">Set Active Day Topic</text>

  <!-- 2.2 -> D2 daily_topics -->
  <line x1="885" y1="135" x2="1075" y2="215" stroke="#000000" stroke-width="2.2" marker-end="url(#arr3)"/>
  <rect x="910" y="160" width="145" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="982" y="177" font-size="12.5" font-weight="bold" text-anchor="middle">Upsert Active Topic</text>

  <!-- 2.2 -> 3.1 -->
  <line x1="720" y1="155" x2="495" y2="340" stroke="#000000" stroke-width="2.2" marker-end="url(#arr3)"/>
  <rect x="570" y="225" width="145" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="642" y="242" font-size="12.5" font-weight="bold" text-anchor="middle">Topic &amp; Format Quotas</text>

  <!-- 3.1 -> GEMINI AI -->
  <line x1="375" y1="340" x2="185" y2="185" stroke="#000000" stroke-width="2.2" marker-end="url(#arr3)"/>
  <rect x="220" y="245" width="140" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="290" y="262" font-size="12.5" font-weight="bold" text-anchor="middle">Syllabus Prompt JSON</text>

  <!-- GEMINI AI -> 3.1 -->
  <line x1="185" y1="200" x2="345" y2="345" stroke="#000000" stroke-width="2.2" marker-end="url(#arr3)"/>
  <rect x="210" y="285" width="135" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="277" y="302" font-size="12.5" font-weight="bold" text-anchor="middle">Generated Quiz JSON</text>

  <!-- D4 -> 7.1 -->
  <line x1="1080" y1="380" x2="890" y2="380" stroke="#000000" stroke-width="2.2" marker-end="url(#arr3)"/>
  <rect x="925" y="368" width="135" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="992" y="385" font-size="12.5" font-weight="bold" text-anchor="middle">Raw Cohort Scores</text>

  <!-- 7.1 -> Mentor -->
  <line x1="675" y1="380" x2="230" y2="380" stroke="#000000" stroke-width="2.2" marker-end="url(#arr3)"/>
  <rect x="365" y="368" width="165" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="447" y="385" font-size="12.5" font-weight="bold" text-anchor="middle">Cohort Analytics &amp; KPIs</text>

  <!-- D4 -> 6.1 -->
  <line x1="1165" y1="405" x2="1165" y2="520" stroke="#000000" stroke-width="2.2"/>
  <line x1="1165" y1="520" x2="525" y2="640" stroke="#000000" stroke-width="2.2" marker-end="url(#arr3)"/>
  <rect x="760" y="525" width="160" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="840" y="542" font-size="12.5" font-weight="bold" text-anchor="middle">Filter Submissions &lt;40%</text>

  <!-- 6.1 -> Mentor -->
  <line x1="330" y1="645" x2="185" y2="485" stroke="#000000" stroke-width="2.2" marker-end="url(#arr3)"/>
  <rect x="180" y="555" width="145" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="252" y="572" font-size="12.5" font-weight="bold" text-anchor="middle">At-Risk Student Roster</text>

  <!-- Mentor -> 6.2 -->
  <line x1="225" y1="460" x2="695" y2="640" stroke="#000000" stroke-width="2.2" marker-end="url(#arr3)"/>
  <rect x="375" y="535" width="170" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="460" y="552" font-size="12.5" font-weight="bold" text-anchor="middle">Trigger Remedial Dispatch</text>

  <!-- 6.2 -> D7 -->
  <line x1="885" y1="670" x2="1075" y2="670" stroke="#000000" stroke-width="2.2" marker-end="url(#arr3)"/>
  <rect x="915" y="658" width="135" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="982" y="675" font-size="12.5" font-weight="bold" text-anchor="middle">Log Action Record</text>

  <!-- 6.2 -> SMTP SERVER -->
  <line x1="885" y1="700" x2="1075" y2="765" stroke="#000000" stroke-width="2.2" marker-end="url(#arr3)"/>
  <rect x="905" y="730" width="160" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>
  <text x="985" y="747" font-size="12.5" font-weight="bold" text-anchor="middle">Remedial Email Packets</text>
</svg>
"""

# ==============================================================================
# 5. ENTITY-RELATIONSHIP (ER) DIAGRAM - High Visibility 1380 x 940
# ==============================================================================
er_svg = """
<svg viewBox="0 0 1380 940" width="1380" height="940" xmlns="http://www.w3.org/2000/svg" font-family="'Times New Roman', serif">
  <defs>
    <marker id="arr-er" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#000000"/>
    </marker>
  </defs>

  <!-- TABLE 1: mentors -->
  <g transform="translate(30, 40)">
    <rect x="0" y="0" width="260" height="200" rx="8" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
    <rect x="0" y="0" width="260" height="38" rx="8" fill="#000000"/>
    <rect x="0" y="24" width="260" height="14" fill="#000000"/>
    <text x="130" y="26" fill="#ffffff" font-size="16" font-weight="bold" text-anchor="middle">mentors</text>
    <text x="14" y="62" fill="#000000" font-size="13" font-weight="bold">PK  id (INTEGER)</text>
    <text x="14" y="86" fill="#000000" font-size="13">      name (VARCHAR)</text>
    <text x="14" y="110" fill="#000000" font-size="13">      dept (VARCHAR)</text>
    <text x="14" y="134" fill="#000000" font-size="13">      identity (VARCHAR, UQ)</text>
    <text x="14" y="158" fill="#000000" font-size="13">      password_hash (VARCHAR)</text>
    <text x="14" y="182" fill="#000000" font-size="13">      created_at (TIMESTAMP)</text>
  </g>

  <!-- TABLE 2: daily_topics -->
  <g transform="translate(420, 40)">
    <rect x="0" y="0" width="280" height="250" rx="8" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
    <rect x="0" y="0" width="280" height="38" rx="8" fill="#000000"/>
    <rect x="0" y="24" width="280" height="14" fill="#000000"/>
    <text x="140" y="26" fill="#ffffff" font-size="16" font-weight="bold" text-anchor="middle">daily_topics</text>
    <text x="14" y="62" fill="#000000" font-size="13" font-weight="bold">PK  id (INTEGER)</text>
    <text x="14" y="86" fill="#000000" font-size="13">      year (VARCHAR, UQ)</text>
    <text x="14" y="110" fill="#000000" font-size="13">      subject (VARCHAR)</text>
    <text x="14" y="134" fill="#000000" font-size="13">      topic (VARCHAR)</text>
    <text x="14" y="158" fill="#000000" font-size="13">      counts (JSON)</text>
    <text x="14" y="182" fill="#000000" font-size="13">      date (VARCHAR)</text>
    <text x="14" y="206" fill="#000000" font-size="13">      due_date / due_time</text>
    <text x="14" y="230" fill="#000000" font-size="13">      updated_at (TIMESTAMP)</text>
  </g>

  <!-- TABLE 3: students -->
  <g transform="translate(830, 40)">
    <rect x="0" y="0" width="270" height="250" rx="8" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
    <rect x="0" y="0" width="270" height="38" rx="8" fill="#000000"/>
    <rect x="0" y="24" width="270" height="14" fill="#000000"/>
    <text x="135" y="26" fill="#ffffff" font-size="16" font-weight="bold" text-anchor="middle">students</text>
    <text x="14" y="62" fill="#000000" font-size="13" font-weight="bold">PK  id (INTEGER)</text>
    <text x="14" y="86" fill="#000000" font-size="13">      username (VARCHAR)</text>
    <text x="14" y="110" fill="#000000" font-size="13">      regno (VARCHAR, UQ)</text>
    <text x="14" y="134" fill="#000000" font-size="13">      dept (VARCHAR)</text>
    <text x="14" y="158" fill="#000000" font-size="13">      year (VARCHAR)</text>
    <text x="14" y="182" fill="#000000" font-size="13">      email (VARCHAR, UQ)</text>
    <text x="14" y="206" fill="#000000" font-size="13">      password_hash (VARCHAR)</text>
    <text x="14" y="230" fill="#000000" font-size="13">      created_at (TIMESTAMP)</text>
  </g>

  <!-- TABLE 4: weekly_timetables -->
  <g transform="translate(30, 370)">
    <rect x="0" y="0" width="260" height="190" rx="8" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
    <rect x="0" y="0" width="260" height="38" rx="8" fill="#000000"/>
    <rect x="0" y="24" width="260" height="14" fill="#000000"/>
    <text x="130" y="26" fill="#ffffff" font-size="16" font-weight="bold" text-anchor="middle">weekly_timetables</text>
    <text x="14" y="62" fill="#000000" font-size="13" font-weight="bold">PK  id (INTEGER)</text>
    <text x="14" y="86" fill="#000000" font-size="13">      year (VARCHAR)</text>
    <text x="14" y="110" fill="#000000" font-size="13">      day (Mon - Sat)</text>
    <text x="14" y="134" fill="#000000" font-size="13">      period (P1 - P5)</text>
    <text x="14" y="158" fill="#000000" font-size="13">      subject (VARCHAR)</text>
    <text x="14" y="180" fill="#000000" font-size="13">      topic (VARCHAR)</text>
  </g>

  <!-- TABLE 5: student_scores -->
  <g transform="translate(830, 370)">
    <rect x="0" y="0" width="270" height="210" rx="8" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
    <rect x="0" y="0" width="270" height="38" rx="8" fill="#000000"/>
    <rect x="0" y="24" width="270" height="14" fill="#000000"/>
    <text x="135" y="26" fill="#ffffff" font-size="16" font-weight="bold" text-anchor="middle">student_scores</text>
    <text x="14" y="62" fill="#000000" font-size="13" font-weight="bold">PK  id (INTEGER)</text>
    <text x="14" y="86" fill="#000000" font-size="13" font-weight="bold">FK  student_id (INTEGER)</text>
    <text x="14" y="110" fill="#000000" font-size="13">      topic (VARCHAR)</text>
    <text x="14" y="134" fill="#000000" font-size="13">      score (VARCHAR)</text>
    <text x="14" y="158" fill="#000000" font-size="13">      percentage (INTEGER)</text>
    <text x="14" y="182" fill="#000000" font-size="13">      date (VARCHAR)</text>
    <text x="14" y="204" fill="#000000" font-size="13">      timestamp (TIMESTAMP)</text>
  </g>

  <!-- TABLE 6: mentor_actions -->
  <g transform="translate(30, 680)">
    <rect x="0" y="0" width="260" height="210" rx="8" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
    <rect x="0" y="0" width="260" height="38" rx="8" fill="#000000"/>
    <rect x="0" y="24" width="260" height="14" fill="#000000"/>
    <text x="130" y="26" fill="#ffffff" font-size="16" font-weight="bold" text-anchor="middle">mentor_actions</text>
    <text x="14" y="62" fill="#000000" font-size="13" font-weight="bold">PK  id (INTEGER)</text>
    <text x="14" y="86" fill="#000000" font-size="13" font-weight="bold">FK  mentor_id (INTEGER)</text>
    <text x="14" y="110" fill="#000000" font-size="13">      year (VARCHAR)</text>
    <text x="14" y="134" fill="#000000" font-size="13">      action_type (VARCHAR)</text>
    <text x="14" y="158" fill="#000000" font-size="13">      description (TEXT)</text>
    <text x="14" y="182" fill="#000000" font-size="13">      student_count (INTEGER)</text>
    <text x="14" y="204" fill="#000000" font-size="13">      created_at (TIMESTAMP)</text>
  </g>

  <!-- TABLE 7: chat_messages -->
  <g transform="translate(420, 680)">
    <rect x="0" y="0" width="280" height="180" rx="8" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
    <rect x="0" y="0" width="280" height="38" rx="8" fill="#000000"/>
    <rect x="0" y="24" width="280" height="14" fill="#000000"/>
    <text x="140" y="26" fill="#ffffff" font-size="16" font-weight="bold" text-anchor="middle">chat_messages</text>
    <text x="14" y="62" fill="#000000" font-size="13" font-weight="bold">PK  id (INTEGER)</text>
    <text x="14" y="86" fill="#000000" font-size="13" font-weight="bold">FK  student_id (INTEGER)</text>
    <text x="14" y="110" fill="#000000" font-size="13">      sender ('student'|'ai')</text>
    <text x="14" y="134" fill="#000000" font-size="13">      message (TEXT)</text>
    <text x="14" y="158" fill="#000000" font-size="13">      timestamp (TIMESTAMP)</text>
  </g>

  <!-- TABLE 8: quiz_attempts -->
  <g transform="translate(830, 680)">
    <rect x="0" y="0" width="270" height="210" rx="8" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
    <rect x="0" y="0" width="270" height="38" rx="8" fill="#000000"/>
    <rect x="0" y="24" width="270" height="14" fill="#000000"/>
    <text x="135" y="26" fill="#ffffff" font-size="16" font-weight="bold" text-anchor="middle">quiz_attempts</text>
    <text x="14" y="62" fill="#000000" font-size="13" font-weight="bold">PK  id (INTEGER)</text>
    <text x="14" y="86" fill="#000000" font-size="13" font-weight="bold">FK  student_id (INTEGER)</text>
    <text x="14" y="110" fill="#000000" font-size="13">      topic (VARCHAR)</text>
    <text x="14" y="134" fill="#000000" font-size="13">      score (VARCHAR)</text>
    <text x="14" y="158" fill="#000000" font-size="13">      percentage (INTEGER)</text>
    <text x="14" y="182" fill="#000000" font-size="13">      answers (JSON)</text>
    <text x="14" y="204" fill="#000000" font-size="13">      created_at (TIMESTAMP)</text>
  </g>

  <!-- ==================== RELATIONSHIPS & CARDINALITY ==================== -->
  <!-- mentors -> daily_topics (1:N) -->
  <line x1="290" y1="120" x2="420" y2="120" stroke="#000000" stroke-width="2.2" marker-end="url(#arr-er)"/>
  <rect x="315" y="108" width="80" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1"/>
  <text x="355" y="125" font-size="12" font-weight="bold" text-anchor="middle">1 : N Sets</text>

  <!-- daily_topics -> students (Evaluates) -->
  <line x1="700" y1="120" x2="830" y2="120" stroke="#000000" stroke-width="2.2" marker-end="url(#arr-er)"/>
  <rect x="725" y="108" width="80" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1"/>
  <text x="765" y="125" font-size="12" font-weight="bold" text-anchor="middle">Evaluates</text>

  <!-- mentors -> weekly_timetables (1:N) -->
  <line x1="160" y1="240" x2="160" y2="370" stroke="#000000" stroke-width="2.2" marker-end="url(#arr-er)"/>
  <rect x="110" y="295" width="100" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1"/>
  <text x="160" y="312" font-size="12" font-weight="bold" text-anchor="middle">1 : N Configures</text>

  <!-- students -> student_scores (1:N) -->
  <line x1="965" y1="290" x2="965" y2="370" stroke="#000000" stroke-width="2.2" marker-end="url(#arr-er)"/>
  <rect x="915" y="320" width="100" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1"/>
  <text x="965" y="337" font-size="12" font-weight="bold" text-anchor="middle">1 : N Achieves</text>

  <!-- students -> chat_messages (1:N) -->
  <line x1="830" y1="260" x2="560" y2="680" stroke="#000000" stroke-width="2.2" marker-end="url(#arr-er)"/>
  <rect x="670" y="470" width="90" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1"/>
  <text x="715" y="487" font-size="12" font-weight="bold" text-anchor="middle">1 : N Chats</text>

  <!-- students -> quiz_attempts (1:N) -->
  <line x1="1020" y1="580" x2="1020" y2="680" stroke="#000000" stroke-width="2.2" marker-end="url(#arr-er)"/>
  <rect x="970" y="620" width="100" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1"/>
  <text x="1020" y="637" font-size="12" font-weight="bold" text-anchor="middle">1 : N Submits</text>

  <!-- mentors -> mentor_actions (1:N) -->
  <line x1="160" y1="560" x2="160" y2="680" stroke="#000000" stroke-width="2.2" marker-end="url(#arr-er)"/>
  <rect x="110" y="610" width="100" height="24" rx="4" fill="#ffffff" stroke="#000000" stroke-width="1"/>
  <text x="160" y="627" font-size="12" font-weight="bold" text-anchor="middle">1 : N Executes</text>
</svg>
"""

# ==============================================================================
# 6. OVERALL USE CASE DIAGRAM - High Visibility 1380 x 920
# ==============================================================================
usecase_overall_svg = """
<svg viewBox="0 0 1380 920" width="1380" height="920" xmlns="http://www.w3.org/2000/svg" font-family="'Times New Roman', serif">
  <!-- SYSTEM BOUNDARY -->
  <rect x="250" y="25" width="880" height="870" rx="14" fill="#ffffff" stroke="#000000" stroke-width="2.8"/>
  <text x="690" y="62" font-size="20" font-weight="bold" text-anchor="middle">EDUMENTOR AI SYSTEM BOUNDARY</text>

  <!-- ACTOR 1: STUDENT (Stick figure) -->
  <g transform="translate(100, 360)">
    <circle cx="20" cy="20" r="16" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
    <line x1="20" y1="36" x2="20" y2="95" stroke="#000000" stroke-width="2.5"/>
    <line x1="20" y1="55" x2="-8" y2="75" stroke="#000000" stroke-width="2.5"/>
    <line x1="20" y1="55" x2="48" y2="75" stroke="#000000" stroke-width="2.5"/>
    <line x1="20" y1="95" x2="-5" y2="140" stroke="#000000" stroke-width="2.5"/>
    <line x1="20" y1="95" x2="45" y2="140" stroke="#000000" stroke-width="2.5"/>
    <text x="20" y="170" font-size="18" font-weight="bold" text-anchor="middle">Student</text>
    <text x="20" y="192" font-size="13" text-anchor="middle">(Primary Actor)</text>
  </g>

  <!-- ACTOR 2: MENTOR (Stick figure) -->
  <g transform="translate(1250, 360)">
    <circle cx="20" cy="20" r="16" fill="#ffffff" stroke="#000000" stroke-width="2.5"/>
    <line x1="20" y1="36" x2="20" y2="95" stroke="#000000" stroke-width="2.5"/>
    <line x1="20" y1="55" x2="-8" y2="75" stroke="#000000" stroke-width="2.5"/>
    <line x1="20" y1="55" x2="48" y2="75" stroke="#000000" stroke-width="2.5"/>
    <line x1="20" y1="95" x2="-5" y2="140" stroke="#000000" stroke-width="2.5"/>
    <line x1="20" y1="95" x2="45" y2="140" stroke="#000000" stroke-width="2.5"/>
    <text x="20" y="170" font-size="18" font-weight="bold" text-anchor="middle">Mentor</text>
    <text x="20" y="192" font-size="13" text-anchor="middle">(Faculty Lead)</text>
  </g>

  <!-- USE CASES -->
  <!-- UC-01 -->
  <ellipse cx="690" cy="105" rx="190" ry="26" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="690" y="111" font-size="14" font-weight="bold" text-anchor="middle">UC-01: Multi-Role Auth &amp; Session Guard</text>

  <!-- UC-02 -->
  <ellipse cx="690" cy="180" rx="190" ry="26" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="690" y="186" font-size="14" font-weight="bold" text-anchor="middle">UC-02: Manage Weekly Departmental Grid</text>

  <!-- UC-03 -->
  <ellipse cx="690" cy="255" rx="190" ry="26" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="690" y="261" font-size="14" font-weight="bold" text-anchor="middle">UC-03: Set Daily Syllabus Topic &amp; Rules</text>

  <!-- UC-04 -->
  <ellipse cx="690" cy="330" rx="190" ry="26" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="690" y="336" font-size="14" font-weight="bold" text-anchor="middle">UC-04: Synthesize Bloom's Assessment (Gemini)</text>

  <!-- UC-05 -->
  <ellipse cx="690" cy="405" rx="190" ry="26" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="690" y="411" font-size="14" font-weight="bold" text-anchor="middle">UC-05: Take Daily Timed Assessment</text>

  <!-- UC-06 -->
  <ellipse cx="690" cy="480" rx="190" ry="26" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="690" y="486" font-size="14" font-weight="bold" text-anchor="middle">UC-06: Auto-Evaluate Answers &amp; Feedback</text>

  <!-- UC-07 -->
  <ellipse cx="690" cy="555" rx="190" ry="26" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="690" y="561" font-size="14" font-weight="bold" text-anchor="middle">UC-07: Socratic 24/7 AI Doubt Resolution</text>

  <!-- UC-08 -->
  <ellipse cx="690" cy="630" rx="190" ry="26" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="690" y="636" font-size="14" font-weight="bold" text-anchor="middle">UC-08: View Continuous Mastery Analytics</text>

  <!-- UC-09 -->
  <ellipse cx="690" cy="705" rx="190" ry="26" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="690" y="711" font-size="14" font-weight="bold" text-anchor="middle">UC-09: Automated Low-Scoring Detection (&lt;40%)</text>

  <!-- UC-10 -->
  <ellipse cx="690" cy="780" rx="190" ry="26" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="690" y="786" font-size="14" font-weight="bold" text-anchor="middle">UC-10: Trigger TLS Remedial Email Alert</text>

  <!-- ACTOR CONNECTORS -->
  <!-- Student lines -->
  <line x1="160" y1="420" x2="500" y2="105" stroke="#000000" stroke-width="1.8"/>
  <line x1="160" y1="420" x2="500" y2="405" stroke="#000000" stroke-width="1.8"/>
  <line x1="160" y1="420" x2="500" y2="480" stroke="#000000" stroke-width="1.8"/>
  <line x1="160" y1="420" x2="500" y2="555" stroke="#000000" stroke-width="1.8"/>
  <line x1="160" y1="420" x2="500" y2="630" stroke="#000000" stroke-width="1.8"/>

  <!-- Mentor lines -->
  <line x1="1230" y1="420" x2="880" y2="105" stroke="#000000" stroke-width="1.8"/>
  <line x1="1230" y1="420" x2="880" y2="180" stroke="#000000" stroke-width="1.8"/>
  <line x1="1230" y1="420" x2="880" y2="255" stroke="#000000" stroke-width="1.8"/>
  <line x1="1230" y1="420" x2="880" y2="330" stroke="#000000" stroke-width="1.8"/>
  <line x1="1230" y1="420" x2="880" y2="630" stroke="#000000" stroke-width="1.8"/>
  <line x1="1230" y1="420" x2="880" y2="705" stroke="#000000" stroke-width="1.8"/>
  <line x1="1230" y1="420" x2="880" y2="780" stroke="#000000" stroke-width="1.8"/>
</svg>
"""

# Dictionary of all diagrams to compile & rotate
diagrams_dict = {
    "bw_dfd0.html": (dfd0_svg, 1300, 850, "bw_dfd0.png", True),
    "bw_dfd1.html": (dfd1_svg, 1380, 940, "bw_dfd1.png", True),
    "bw_dfd2_student.html": (dfd2_student_svg, 1300, 850, "bw_dfd2_student.png", True),
    "bw_dfd2_mentor.html": (dfd2_mentor_svg, 1300, 850, "bw_dfd2_mentor.png", True),
    "bw_er_diagram.html": (er_svg, 1380, 940, "bw_er_diagram_rot.png", True),
    "bw_usecase_overall.html": (usecase_overall_svg, 1380, 920, "bw_usecase_overall_rot.png", True),
}

print(f"Generating high-resolution black-and-white diagrams using {edge_path}...")
for fname, (svg_code, w, h, out_png_name, do_rotate) in diagrams_dict.items():
    html_file = os.path.join(output_dir, fname)
    png_base = os.path.join(output_dir, fname.replace(".html", ".png"))
    final_out = os.path.join(output_dir, out_png_name)
    
    full_html = wrap_bw_html(svg_code, w, h)
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(full_html)
    
    # Run Edge headless screenshot at generous window size
    cmd = [
        edge_path,
        "--headless",
        "--disable-gpu",
        f"--screenshot={png_base}",
        f"--window-size={w+60},{h+60}",
        f"file:///{html_file.replace(os.sep, '/')}"
    ]
    subprocess.run(cmd, check=True)
    
    if do_rotate:
        im = Image.open(png_base)
        im_rot = im.rotate(90, expand=True)
        im_rot.save(final_out)
        # Also mirror to base name if needed
        if final_out != png_base:
            im_rot.save(png_base)
        print(f"Generated & Rotated 90 deg: {final_out} ({im_rot.size[0]}x{im_rot.size[1]})")
    else:
        print(f"Generated: {final_out}")

# Also ensure er_diagram_v2_rot.png points to bw_er_diagram_rot.png for complete backward compatibility
er_target = os.path.join(output_dir, "er_diagram_v2_rot.png")
er_source = os.path.join(output_dir, "bw_er_diagram_rot.png")
if os.path.exists(er_source):
    im_er = Image.open(er_source)
    im_er.save(er_target)

print("All diagrams generated, sharpened, and rotated 90 degrees for 1-diagram-per-page full visibility!")
