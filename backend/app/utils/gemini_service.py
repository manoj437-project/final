import json
import re
import time
import random
import logging
from typing import List, Dict, Any, Optional

try:
    from google import genai as google_genai
    from google.genai.errors import ServerError, ClientError
except ImportError:
    google_genai = None
    ServerError = Exception
    ClientError = Exception

from app.config import settings

logger = logging.getLogger(__name__)

# List of Gemini models to try in order of preference (latest → stable fallbacks)
GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
]


def call_gemini_with_fallback(
    prompt: str,
    models: Optional[List[str]] = None,
    max_retries_per_model: int = 2,
    base_delay: float = 1.0
) -> str:
    """
    Calls Google Gemini with automatic failover across multiple model versions
    and exponential backoff on transient errors (503 Service Unavailable, 429 Rate Limit).
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("Gemini API key is not configured")

    if google_genai is None:
        raise ImportError("google.genai SDK is not installed")

    client = google_genai.Client(api_key=settings.GEMINI_API_KEY)
    model_list = models or GEMINI_MODELS
    last_exception = None

    for model_name in model_list:
        for attempt in range(max_retries_per_model):
            try:
                logger.info(f"Invoking Gemini model '{model_name}' (attempt {attempt + 1})...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    logger.info(f"Gemini model '{model_name}' succeeded.")
                    return response.text.strip()
                raise ValueError(f"Empty response from model '{model_name}'")

            except Exception as e:
                last_exception = e
                err_msg = str(e)
                logger.warning(
                    f"Gemini model '{model_name}' attempt {attempt + 1} failed: {type(e).__name__} - {err_msg[:120]}"
                )

                # Check if error is transient (503 Unavailable / 429 Quota / Overloaded)
                is_transient = any(
                    code in err_msg
                    for code in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "overloaded", "high demand"]
                )

                if is_transient and attempt + 1 < max_retries_per_model:
                    backoff = base_delay * (2 ** attempt) + random.uniform(0.1, 0.5)
                    time.sleep(backoff)
                    continue

                # Move on to the next candidate model
                break

    raise last_exception or RuntimeError("All Gemini candidate models failed.")


def extract_clean_json(text: str) -> Any:
    """
    Robustly extracts JSON from LLM output, stripping code fences and
    ignoring conversational preamble or postscript.
    """
    if not text:
        raise ValueError("Cannot extract JSON from empty text")

    # Remove markdown code blocks
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"^```\s*$", "", cleaned, flags=re.MULTILINE).strip()

    # Find boundaries of first array or object
    start_arr = cleaned.find("[")
    start_obj = cleaned.find("{")

    if start_arr == -1 and start_obj == -1:
        raise ValueError("No JSON array or object found in response")

    if start_arr != -1 and (start_obj == -1 or start_arr < start_obj):
        start = start_arr
        end = cleaned.rfind("]")
    else:
        start = start_obj
        end = cleaned.rfind("}")

    if end == -1 or end <= start:
        json_str = cleaned[start:]
    else:
        json_str = cleaned[start:end + 1]

    # Remove trailing commas before closing brackets/braces (common LLM error)
    json_str = re.sub(r",\s*([\]}])", r"\1", json_str)

    return json.loads(json_str)


# ═══════════════════════════════════════════════════════════════
#  CURATED TOPIC-SPECIFIC FALLBACK QUESTION BANK
# ═══════════════════════════════════════════════════════════════

TOPIC_QUESTION_BANK: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
    "tcp protocol": {
        "MCQ": [
            {
                "q": "What mechanism does the TCP protocol use to establish a reliable connection?",
                "a": "Three-way handshake",
                "options": ["Three-way handshake", "Two-way handshake", "Four-way handshake", "Sliding window exchange"]
            },
            {
                "q": "Which field in the TCP header ensures packets are reassembled in the correct order at the destination?",
                "a": "Sequence Number",
                "options": ["Sequence Number", "Acknowledgment Number", "Checksum", "Window Size"]
            },
            {
                "q": "What is the primary function of TCP flow control?",
                "a": "Prevent the sender from overwhelming the receiver buffer",
                "options": [
                    "Prevent the sender from overwhelming the receiver buffer",
                    "Prevent network congestion on intermediate routers",
                    "Encrypt data packets during transmission",
                    "Select the shortest routing path"
                ]
            },
            {
                "q": "Which TCP flag is set when a host wants to gracefully terminate an existing connection?",
                "a": "FIN",
                "options": ["FIN", "SYN", "RST", "ACK"]
            },
            {
                "q": "What is the size of the standard base TCP header without options?",
                "a": "20 bytes",
                "options": ["20 bytes", "16 bytes", "24 bytes", "32 bytes"]
            }
        ],
        "TF": [
            {
                "q": "TCP is a connectionless and unreliable transport layer protocol.",
                "a": "False",
                "options": ["True", "False"]
            },
            {
                "q": "TCP uses checksums to detect corrupted data segments during transmission.",
                "a": "True",
                "options": ["True", "False"]
            },
            {
                "q": "The TCP sliding window mechanism allows multiple segments to be in flight without immediate acknowledgment.",
                "a": "True",
                "options": ["True", "False"]
            }
        ],
        "FILL": [
            {
                "q": "The process of closing a standard TCP connection uses a ______-way handshake.",
                "a": "four"
            },
            {
                "q": "In TCP congestion control, the phase following Slow Start is called Congestion ______.",
                "a": "Avoidance"
            }
        ]
    },
    "computer networks": {
        "MCQ": [
            {
                "q": "At which layer of the OSI model does the IP protocol operate?",
                "a": "Network Layer",
                "options": ["Network Layer", "Transport Layer", "Data Link Layer", "Application Layer"]
            },
            {
                "q": "Which protocol is used to automatically assign IP addresses to hosts on a network?",
                "a": "DHCP",
                "options": ["DHCP", "DNS", "ARP", "ICMP"]
            },
            {
                "q": "What is the primary purpose of the Address Resolution Protocol (ARP)?",
                "a": "Map an IP address to a MAC address",
                "options": [
                    "Map an IP address to a MAC address",
                    "Map a domain name to an IP address",
                    "Route packets across subnets",
                    "Encrypt transport layer data"
                ]
            }
        ],
        "TF": [
            {
                "q": "UDP provides guaranteed packet delivery and ordered sequencing.",
                "a": "False",
                "options": ["True", "False"]
            },
            {
                "q": "A router operates primarily at the Network Layer (Layer 3) of the OSI model.",
                "a": "True",
                "options": ["True", "False"]
            }
        ],
        "FILL": [
            {
                "q": "The maximum transmission unit default for standard Ethernet frames is ______ bytes.",
                "a": "1500"
            }
        ]
    },
    "blackbox testing": {
        "MCQ": [
            {
                "q": "What is the primary characteristic of Black Box Testing?",
                "a": "Testing system functionality without knowledge of internal code structure",
                "options": [
                    "Testing system functionality without knowledge of internal code structure",
                    "Examining source code lines and control flow paths",
                    "Testing compilers and runtime interpreters",
                    "Validating database schema migration scripts"
                ]
            },
            {
                "q": "Which technique divides the input domain into classes where all values are expected to be processed similarly?",
                "a": "Equivalence Partitioning",
                "options": ["Equivalence Partitioning", "Boundary Value Analysis", "Path Testing", "Mutation Testing"]
            },
            {
                "q": "Boundary Value Analysis primarily focuses on testing input values at:",
                "a": "The edges and extreme limits of input ranges",
                "options": [
                    "The edges and extreme limits of input ranges",
                    "Random values in the middle of partitions",
                    "Internal variable state transitions",
                    "Database foreign key boundaries"
                ]
            }
        ],
        "TF": [
            {
                "q": "Black box test cases can be derived directly from requirement specifications before code is written.",
                "a": "True",
                "options": ["True", "False"]
            },
            {
                "q": "Code coverage metrics like statement coverage are directly measured using black box testing.",
                "a": "False",
                "options": ["True", "False"]
            }
        ],
        "FILL": [
            {
                "q": "In Black Box Testing, BVA stands for Boundary ______ Analysis.",
                "a": "Value"
            }
        ]
    },
    "software engineering": {
        "MCQ": [
            {
                "q": "Which software development life cycle model is most suitable when requirements are well-defined and unlikely to change?",
                "a": "Waterfall Model",
                "options": ["Waterfall Model", "Agile Scrum", "Spiral Model", "Prototyping"]
            },
            {
                "q": "In software architecture, what does high cohesion and low coupling promote?",
                "a": "Maintainability and modularity",
                "options": ["Maintainability and modularity", "Increased memory footprint", "Tighter inter-component dependencies", "Slower execution speeds"]
            }
        ],
        "TF": [
            {
                "q": "Refactoring refers to altering the external behavior of software while keeping internal structure constant.",
                "a": "False",
                "options": ["True", "False"]
            },
            {
                "q": "Regression testing ensures that recent code changes have not adversely affected existing features.",
                "a": "True",
                "options": ["True", "False"]
            }
        ],
        "FILL": [
            {
                "q": "In Agile methodology, the time-boxed iterative development cycle is known as a ______.",
                "a": "sprint"
            }
        ]
    }
}


def generate_fallback_topic_quiz(
    topic: str,
    subject: str,
    mcq_count: int = 3,
    tf_count: int = 2,
    fill_count: int = 1
) -> List[Dict[str, Any]]:
    """
    Generates high quality topic-specific questions even when all external AI APIs are offline.
    Matches curated topic banks first; otherwise generates contextually relevant questions.
    """
    t_clean = topic.strip().lower()
    s_clean = subject.strip().lower()

    # Match exact or partial topic
    bank = None
    for key in TOPIC_QUESTION_BANK:
        if key in t_clean or t_clean in key:
            bank = TOPIC_QUESTION_BANK[key]
            break

    if not bank:
        for key in TOPIC_QUESTION_BANK:
            if key in s_clean or s_clean in key:
                bank = TOPIC_QUESTION_BANK[key]
                break

    questions: List[Dict[str, Any]] = []

    if bank:
        # Pull requested counts from bank with random sampling
        avail_mcq = list(bank.get("MCQ", []))
        random.shuffle(avail_mcq)
        for item in avail_mcq[:mcq_count]:
            questions.append({"type": "MCQ", "q": item["q"], "a": item["a"], "options": item["options"]})

        avail_tf = list(bank.get("TF", []))
        random.shuffle(avail_tf)
        for item in avail_tf[:tf_count]:
            questions.append({"type": "TF", "q": item["q"], "a": item["a"], "options": ["True", "False"]})

        avail_fill = list(bank.get("FILL", []))
        random.shuffle(avail_fill)
        for item in avail_fill[:fill_count]:
            questions.append({"type": "FILL", "q": item["q"], "a": item["a"]})

    # If we need more questions or no bank match, generate contextual questions
    curr_mcq = sum(1 for q in questions if q["type"] == "MCQ")
    curr_tf = sum(1 for q in questions if q["type"] == "TF")
    curr_fill = sum(1 for q in questions if q["type"] == "FILL")

    topic_title = topic.strip()
    subj_title = subject.strip() if subject.strip() else "Computer Science"

    # Contextual MCQ generator
    mcq_templates = [
        (
            f"What is the core objective of studying '{topic_title}' in {subj_title}?",
            f"Mastering foundational principles and practical applications of {topic_title}",
            [
                f"Mastering foundational principles and practical applications of {topic_title}",
                f"Replacing all existing {subj_title} paradigms completely",
                f"Automating hardware-level silicon compilation",
                f"None of the above"
            ]
        ),
        (
            f"Which of the following best represents a standard application of '{topic_title}'?",
            f"Solving domain-specific problems within {subj_title}",
            [
                f"Solving domain-specific problems within {subj_title}",
                "Managing unformatted disk sectors manually",
                "Translating analog telephone audio streams",
                "Overclocking motherboard processor clock rates"
            ]
        ),
        (
            f"When evaluating performance in '{topic_title}', what is typically a key factor?",
            "Correctness, efficiency, and adherence to specifications",
            [
                "Correctness, efficiency, and adherence to specifications",
                "Only the physical size of source code files",
                "Random variable initialization speed",
                "Ignoring edge cases and error conditions"
            ]
        )
    ]

    for i in range(curr_mcq, mcq_count):
        tpl = mcq_templates[i % len(mcq_templates)]
        questions.append({"type": "MCQ", "q": tpl[0], "a": tpl[1], "options": tpl[2]})

    # Contextual TF generator
    tf_templates = [
        (f"In {subj_title}, '{topic_title}' plays a fundamental role in modern system design.", "True"),
        (f"The principles of '{topic_title}' cannot be applied in real-world software or engineering scenarios.", "False"),
        (f"Understanding requirements and boundary conditions is essential when implementing '{topic_title}'.", "True")
    ]

    for i in range(curr_tf, tf_count):
        tpl = tf_templates[i % len(tf_templates)]
        questions.append({"type": "TF", "q": tpl[0], "a": tpl[1], "options": ["True", "False"]})

    # Contextual Fill generator
    fill_templates = [
        (f"The study of '{topic_title}' is an integral component of the ______ curriculum.", subj_title),
        (f"A rigorous implementation of '{topic_title}' requires careful verification of ______ conditions.", "boundary")
    ]

    for i in range(curr_fill, fill_count):
        tpl = fill_templates[i % len(fill_templates)]
        questions.append({"type": "FILL", "q": tpl[0], "a": tpl[1]})

    return questions
