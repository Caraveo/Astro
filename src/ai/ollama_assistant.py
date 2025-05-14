import requests
import json
import os
import threading
import queue
import time
from typing import Dict, List, Optional

class OllamaAssistant:
    def __init__(self, model: str = "llama2"):
        self.base_url = "http://localhost:11434"
        self.model = model
        self.conversation_history: List[Dict] = []
        self.response_queue = queue.Queue()
        self.is_processing = False
        
        # Ensure Ollama is running
        self._check_ollama_status()
    
    def _check_ollama_status(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code != 200:
                raise Exception("Ollama server is not responding properly")
        except requests.exceptions.ConnectionError:
            raise Exception("Ollama server is not running. Please start Ollama first.")
    
    def _ensure_model(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            models = response.json()['models']
            if not any(model['name'] == self.model for model in models):
                print(f"Downloading {self.model} model...")
                requests.post(f"{self.base_url}/api/pull", json={'name': self.model})
        except Exception as e:
            print(f"Error ensuring model: {e}")
    
    def process_command(self, command: str) -> str:
        """Process a voice command and return a response."""
        self.is_processing = True
        
        try:
            # Add command to conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': command
            })
            
            # Prepare the prompt
            prompt = self._prepare_prompt(command)
            
            # Send request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result['response']
                
                # Add response to conversation history
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': response_text
                })
                
                return response_text
            else:
                return "I apologize, but I'm having trouble processing your request right now."
        
        except Exception as e:
            print(f"Error processing command: {e}")
            return "I encountered an error while processing your request."
        
        finally:
            self.is_processing = False
    
    def _prepare_prompt(self, command: str) -> str:
        """Prepare the prompt for Ollama with conversation context."""
        context = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in self.conversation_history[-5:]  # Last 5 messages for context
        ])
        
        return f"""Previous conversation:
{context}

User: {command}

Assistant:"""
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
    
    def get_status(self) -> Dict:
        """Get the current status of the assistant."""
        return {
            'is_processing': self.is_processing,
            'model': self.model,
            'conversation_length': len(self.conversation_history)
        }

class VoiceCommandProcessor:
    def __init__(self, assistant: OllamaAssistant):
        self.assistant = assistant
        self.command_queue = queue.Queue()
        self.processing_thread = threading.Thread(target=self._process_commands)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def add_command(self, command: str):
        """Add a command to the processing queue."""
        self.command_queue.put(command)
    
    def _process_commands(self):
        """Process commands from the queue."""
        while True:
            try:
                command = self.command_queue.get()
                response = self.assistant.process_command(command)
                # Handle response (e.g., text-to-speech, display, etc.)
                print(f"Assistant: {response}")
            except Exception as e:
                print(f"Error processing command: {e}")
            finally:
                self.command_queue.task_done()
            time.sleep(0.1)  # Prevent CPU overuse

if __name__ == '__main__':
    # Example usage
    assistant = OllamaAssistant()
    processor = VoiceCommandProcessor(assistant)
    
    # Test command
    processor.add_command("What's the weather like today?") 