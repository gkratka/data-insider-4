import { useState } from "react";
import { Send, Mic } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Message {
  id: number;
  sender: 'user' | 'ai';
  content: string;
  timestamp: string;
}

const ChatInterface = () => {
  const [message, setMessage] = useState("");
  
  // Sample conversation as specified by the user
  const [messages] = useState<Message[]>([
    {
      id: 1,
      sender: 'user',
      content: 'provide a summary analysis of the data',
      timestamp: '2 min ago'
    },
    {
      id: 2,
      sender: 'ai',
      content: 'what analysis do you need?',
      timestamp: '2 min ago'
    },
    {
      id: 3,
      sender: 'user',
      content: 'I need to know the sales by quarter',
      timestamp: '1 min ago'
    },
    {
      id: 4,
      sender: 'ai',
      content: 'here you go: Q1 = $1000, Q2 = $2000, Q3 = $3000, Q4 = $4000',
      timestamp: '1 min ago'
    }
  ]);

  const handleSend = () => {
    if (message.trim()) {
      // In a real app, this would add the message to the conversation
      setMessage("");
    }
  };

  return (
    <div className="bg-chat text-chat-foreground">
      <div className="max-w-4xl mx-auto">
        <div className="border-t border-chat-border">
          {/* Chat Messages */}
          <ScrollArea className="h-96 p-4">
            <div className="space-y-4">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <Card
                    className={`max-w-xs md:max-w-md p-3 ${
                      msg.sender === 'user'
                        ? 'bg-chat-user-bg text-chat-user-fg border-chat-user-bg'
                        : 'bg-chat-ai-bg text-chat-ai-fg border-chat-border'
                    }`}
                  >
                    <p className="text-sm">{msg.content}</p>
                    <p className="text-xs opacity-70 mt-1">{msg.timestamp}</p>
                  </Card>
                </div>
              ))}
            </div>
          </ScrollArea>
          
          {/* Chat Input */}
          <div className="p-4 border-t border-chat-border">
            <div className="flex gap-2">
              <Input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask Gemini"
                className="flex-1 bg-chat-input-bg border-chat-border text-chat-foreground placeholder:text-chat-foreground/60"
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              />
              <Button
                onClick={handleSend}
                size="icon"
                className="bg-chat-user-bg hover:bg-chat-user-bg/80 text-chat-user-fg"
              >
                <Send className="w-4 h-4" />
              </Button>
              <Button
                size="icon"
                variant="ghost"
                className="text-chat-foreground hover:bg-chat-border/50"
              >
                <Mic className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-xs text-chat-foreground/60 mt-2 text-center">
              Gemini can make mistakes, so double-check it
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;