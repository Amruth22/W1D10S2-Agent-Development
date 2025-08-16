"""
Conversation Memory Management using LangChain
"""

from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage
from langchain.schema.messages import HumanMessage, AIMessage
from config import CONVERSATION_MEMORY_KEY, MAX_TOKEN_LIMIT
from typing import List, Dict, Any


class ResearchAgentMemory:
    """
    Enhanced conversation memory for the research agent using LangChain.
    Maintains context and conversation history for better research continuity.
    """
    
    def __init__(self, k: int = 10):
        """
        Initialize conversation memory
        
        Args:
            k: Number of recent conversation turns to remember
        """
        self.memory = ConversationBufferWindowMemory(
            k=k,
            return_messages=True,
            memory_key=CONVERSATION_MEMORY_KEY,
            max_token_limit=MAX_TOKEN_LIMIT
        )
        
        # Track research topics for context
        self.research_topics = []
        self.session_summary = ""
    
    def add_user_message(self, message: str):
        """Add a user message to memory"""
        self.memory.chat_memory.add_user_message(message)
        
        # Extract potential research topics
        self._extract_research_topics(message)
    
    def add_ai_message(self, message: str):
        """Add an AI response to memory"""
        self.memory.chat_memory.add_ai_message(message)
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """Get the current conversation history"""
        return self.memory.chat_memory.messages
    
    def get_memory_variables(self) -> Dict[str, Any]:
        """Get memory variables for the agent"""
        memory_vars = self.memory.load_memory_variables({})
        
        # Add research context
        memory_vars["research_topics"] = self.research_topics
        memory_vars["session_summary"] = self.session_summary
        
        return memory_vars
    
    def get_formatted_history(self) -> str:
        """Get conversation history formatted for display"""
        messages = self.get_conversation_history()
        if not messages:
            return "No conversation history yet."
        
        formatted = "Conversation History:\n" + "="*50 + "\n"
        
        for i, message in enumerate(messages, 1):
            if isinstance(message, HumanMessage):
                role = "Human"
                content = message.content
            elif isinstance(message, AIMessage):
                role = "Assistant"
                content = message.content
            else:
                role = f"{message.type.title()}"
                content = message.content
            
            # Truncate long messages for display
            display_content = content[:200] + "..." if len(content) > 200 else content
            formatted += f"{i}. {role}: {display_content}\n\n"
        
        return formatted
    
    def get_research_context(self) -> str:
        """Get research context for the agent"""
        context_parts = []
        
        # Recent conversation context
        recent_messages = self.get_conversation_history()[-4:]  # Last 4 messages
        if recent_messages:
            context_parts.append("Recent conversation:")
            for msg in recent_messages:
                role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
                content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                context_parts.append(f"- {role}: {content}")
        
        # Research topics context
        if self.research_topics:
            context_parts.append(f"\nOngoing research topics: {', '.join(self.research_topics[-5:])}")
        
        # Session summary
        if self.session_summary:
            context_parts.append(f"\nSession summary: {self.session_summary}")
        
        return "\n".join(context_parts) if context_parts else "No previous context."
    
    def clear_memory(self):
        """Clear all conversation history and research context"""
        self.memory.clear()
        self.research_topics = []
        self.session_summary = ""
    
    def update_session_summary(self, summary: str):
        """Update the session summary with key research findings"""
        self.session_summary = summary
    
    def _extract_research_topics(self, message: str):
        """Extract potential research topics from user messages"""
        # Simple keyword extraction for research topics
        research_keywords = [
            "research", "analyze", "study", "investigate", "examine",
            "explore", "report", "trends", "statistics", "data"
        ]
        
        message_lower = message.lower()
        
        # Look for research-related phrases
        for keyword in research_keywords:
            if keyword in message_lower:
                # Extract the main topic (simplified approach)
                words = message.split()
                for i, word in enumerate(words):
                    if word.lower() == keyword and i + 1 < len(words):
                        # Take the next few words as potential topic
                        topic = " ".join(words[i+1:i+4])
                        topic = topic.replace("?", "").replace(".", "").strip()
                        if len(topic) > 3 and topic not in self.research_topics:
                            self.research_topics.append(topic)
                        break
        
        # Keep only recent topics (last 10)
        self.research_topics = self.research_topics[-10:]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics for debugging/monitoring"""
        messages = self.get_conversation_history()
        
        return {
            "total_messages": len(messages),
            "human_messages": len([m for m in messages if isinstance(m, HumanMessage)]),
            "ai_messages": len([m for m in messages if isinstance(m, AIMessage)]),
            "research_topics_count": len(self.research_topics),
            "has_session_summary": bool(self.session_summary),
            "memory_key": CONVERSATION_MEMORY_KEY
        }