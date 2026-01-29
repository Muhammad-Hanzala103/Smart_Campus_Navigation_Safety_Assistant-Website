import random
import json
from datetime import datetime

class CampusChatbot:
    """
    Intelligent Assistant for the Smart Campus System.
    Uses a Mock RAG (Retrieval-Augmented Generation) approach to answer queries.
    """
    
    def __init__(self):
        # Knowledge Base (Mock Dictionary)
        # In a production system, this would be vector embeddings in a database.
        self.knowledge_base = {
            "transport": [
                {
                    "keywords": ["bus", "shuttle", "transport", "schedule", "timing"],
                    "answer": "Shuttles run every 15 minutes from the Main Gate to the Academic Block between 8:00 AM and 5:00 PM. You can track them live on the Dashboard.",
                    "source": "Transport Department"
                },
                {
                    "keywords": ["driver", "contact", "transport office"],
                    "answer": "The Transport Office can be reached at Ext. 404 or transport@university.edu.",
                    "source": "Directory"
                }
            ],
            "academic": [
                {
                    "keywords": ["exam", "datesheet", "schedule", "midterm", "final"],
                    "answer": "The Final Exams for Fall 2024 are scheduled from Jan 15th to Jan 30th. Please check your personalized datesheet in the Faculty Portal.",
                    "source": "Controller of Exams"
                },
                {
                    "keywords": ["library", "book", "issue", "return"],
                    "answer": "The Central Library is open 24/7 during exam weeks. Normal hours are 8 AM - 8 PM. You can borrow up to 5 books at a time.",
                    "source": "Library Handbook"
                }
            ],
            "general": [
                {
                    "keywords": ["wifi", "internet", "password", "network"],
                    "answer": "The student WiFi is 'Uni-Connect'. Use your CMS ID and password to login.",
                    "source": "IT Services"
                },
                {
                    "keywords": ["cafe", "food", "lunch"],
                    "answer": "The Main Cafeteria serves lunch from 12:00 PM to 2:30 PM. The Coffee Shop is open until 10 PM.",
                    "source": "Admin Services"
                }
            ]
        }
        
        # Fallback responses for unknown queries
        self.abstractions = [
            "I'm not sure about that, but I can help you with Transport, Exams, or General queries.",
            "That's outside my current knowledge base. Would you like me to open a ticket for the Help Desk?",
            "I apologize, I didn't catch that. Could you try rephrasing your question?"
        ]

    def get_response(self, user_query):
        """
        Process the user query and return the best match answer.
        """
        query = user_query.lower()
        best_match = None
        max_score = 0
        
        # 1. Simple Keyword Matching (Mock Semantic Search)
        for category, items in self.knowledge_base.items():
            for item in items:
                score = 0
                for keyword in item['keywords']:
                    if keyword in query:
                        score += 1
                
                if score > max_score:
                    max_score = score
                    best_match = item
        
        # 2. Return Result
        if best_match and max_score > 0:
            return {
                "reply": best_match['answer'],
                "source": best_match['source'],
                "confidence": "High" if max_score > 1 else "Medium"
            }
        
        # 3. Fallback
        return {
            "reply": random.choice(self.abstractions),
            "source": "AI Assistant",
            "confidence": "Low"
        }

# Global Instance
chatbot = CampusChatbot()
