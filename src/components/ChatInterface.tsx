import { useState, useEffect, useRef, useCallback } from "react";
import { Send, MessageSquare, FileText, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { toast } from "sonner";
import { chatService } from "@/services/chatService";
import { useApiMutation } from "@/hooks/useApi";
import { ChatMessage } from "@/types/api";

interface ChatInterfaceProps {
  uploadedFiles?: Array<{ id: string; name: string }>;
  messages?: ChatMessage[];
  onMessagesChange?: (messages: ChatMessage[]) => void;
}

const ChatInterface = ({ uploadedFiles = [], messages = [], onMessagesChange }: ChatInterfaceProps) => {
  const [message, setMessage] = useState("");
  const [showWelcome, setShowWelcome] = useState(false);
  const [sessionId] = useState(() => `session-${Math.random().toString(36).substr(2, 9)}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);


  // Send message mutation using ChatService
  const { mutate: sendMessage, isLoading } = useApiMutation(chatService.sendMessage);

  // Show welcome message when files are uploaded
  useEffect(() => {
    if (uploadedFiles.length > 0 && !showWelcome && messages.length === 0) {
      setShowWelcome(true);
      // Add welcome message as a chat message from the assistant
      const welcomeMessage: ChatMessage = {
        id: 'welcome-' + Date.now(),
        role: 'assistant',
        content: 'Welcome! You can now ask questions about your data. Try asking about patterns, statistics, or specific insights.',
        timestamp: new Date().toISOString(),
        sessionId
      };
      onMessagesChange?.([welcomeMessage]);
    }
  }, [uploadedFiles.length, showWelcome, sessionId, messages.length, onMessagesChange]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!message.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: message.trim(),
      timestamp: new Date().toISOString(),
      sessionId
    };

    onMessagesChange?.([...messages, userMessage]);
    setMessage("");

    try {
      const response = await sendMessage({
        message: userMessage.content,
        sessionId,
        fileIds: uploadedFiles.map(f => f.id)
      });

      const assistantMessage: ChatMessage = {
        id: response.id,
        role: 'assistant',
        content: response.content,
        timestamp: response.timestamp,
        sessionId: response.sessionId
      };

      onMessagesChange?.([...messages, userMessage, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request.',
        timestamp: new Date().toISOString(),
        sessionId
      };
      onMessagesChange?.([...messages, userMessage, errorMessage]);
      toast.error('Failed to send message');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {(!uploadedFiles || uploadedFiles.length === 0) ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <MessageSquare className="w-12 h-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground text-center">
              Chat interface will be available after uploading data
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {/* File Context Display */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-sm">
                <FileText className="w-4 h-4" />
                Context Files
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="flex flex-wrap gap-2">
                {uploadedFiles.map((file) => (
                  <Badge key={file.id} variant="secondary">
                    {file.name}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Chat Messages */}
          <Card>
            <ScrollArea className="h-[calc(100vh-400px)] p-4">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                  <MessageSquare className="w-8 h-8 mb-2" />
                  <p>Start a conversation about your data...</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          msg.role === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {formatTimestamp(msg.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-muted px-4 py-2 rounded-lg flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <p className="text-sm text-muted-foreground">AI is thinking...</p>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </ScrollArea>
          </Card>

          {/* Message Input */}
          <Card>
            <CardContent className="p-4">
              <div className="flex gap-2">
                <Input
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Ask a question about your data..."
                  onKeyPress={handleKeyPress}
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button
                  onClick={handleSend}
                  disabled={!message.trim() || isLoading}
                  size="icon"
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default ChatInterface;