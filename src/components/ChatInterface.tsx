import { useState, useEffect, useRef, useCallback } from "react";
import { Send, Mic, Loader2, FileText, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { toast } from "sonner";
import { chatService } from "@/services/chatService";
import { sessionService } from "@/services/sessionService";
import { useApi, useApiMutation } from "@/hooks/useApi";
import { ChatMessage } from "@/types/api";

interface StreamingMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  isStreaming?: boolean;
  metadata?: {
    fileReferences?: string[];
    queryType?: string;
    executionTime?: number;
  };
}

interface ChatInterfaceProps {
  uploadedFiles?: Array<{ id: string; name: string }>;
}

const ChatInterface = ({ uploadedFiles = [] }: ChatInterfaceProps) => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<StreamingMessage[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Get current session
  const { data: session, refetch: refetchSession } = useApi(() => sessionService.getCurrentSession());

  // Load chat history
  const { data: chatHistory, refetch: refetchHistory } = useApi(
    () => session ? chatService.getChatHistory(session.sessionId) : Promise.resolve([]),
    [session?.sessionId]
  );

  // Send message mutation
  const { mutate: sendMessage, isLoading: isSending } = useApiMutation(chatService.sendMessage);

  // Convert API messages to display format
  useEffect(() => {
    if (chatHistory) {
      const displayMessages: StreamingMessage[] = chatHistory.map(msg => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        timestamp: new Date(msg.timestamp).toLocaleTimeString(),
        metadata: msg.metadata
      }));
      setMessages(displayMessages);
    }
  }, [chatHistory]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const formatTimestamp = (date: Date = new Date()) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleStreamMessage = useCallback((request: { message: string; sessionId: string; fileIds?: string[] }) => {
    const messageId = Math.random().toString(36).substr(2, 9);
    const userMessage: StreamingMessage = {
      id: `user-${messageId}`,
      role: 'user',
      content: request.message,
      timestamp: formatTimestamp()
    };

    const assistantMessage: StreamingMessage = {
      id: `assistant-${messageId}`,
      role: 'assistant',
      content: '',
      timestamp: formatTimestamp(),
      isStreaming: true
    };

    // Add user message and empty assistant message
    setMessages(prev => [...prev, userMessage, assistantMessage]);
    setStreamingMessageId(`assistant-${messageId}`);

    // Stream the response
    chatService.streamMessage(
      request,
      (chunk: string) => {
        // Update streaming message with new chunk
        setMessages(prev => prev.map(msg => 
          msg.id === `assistant-${messageId}` 
            ? { ...msg, content: msg.content + chunk }
            : msg
        ));
      },
      (completeMessage: ChatMessage) => {
        // Finalize the message
        setMessages(prev => prev.map(msg => 
          msg.id === `assistant-${messageId}` 
            ? { 
                ...msg, 
                content: completeMessage.content,
                isStreaming: false,
                metadata: completeMessage.metadata
              }
            : msg
        ));
        setStreamingMessageId(null);
        refetchHistory(); // Refresh history from server
      },
      (error: string) => {
        // Handle streaming error
        setMessages(prev => prev.map(msg => 
          msg.id === `assistant-${messageId}` 
            ? { 
                ...msg, 
                content: `Error: ${error}`,
                isStreaming: false
              }
            : msg
        ));
        setStreamingMessageId(null);
        toast.error('Failed to get response');
      }
    );
  }, [refetchHistory]);

  const handleSend = async () => {
    if (!message.trim() || isSending || !session) {
      return;
    }

    const messageText = message;
    setMessage("");

    try {
      // Get file IDs from uploaded files
      const fileIds = uploadedFiles.map(file => file.id);
      
      // Use streaming for real-time response
      handleStreamMessage({
        message: messageText,
        sessionId: session.sessionId,
        fileIds: fileIds.length > 0 ? fileIds : undefined
      });

    } catch (error) {
      toast.error('Failed to send message');
      console.error('Send message error:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleVoiceInput = async () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error('Speech recognition not supported in this browser');
      return;
    }

    if (isListening) {
      setIsListening(false);
      return;
    }

    try {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      
      recognition.onstart = () => setIsListening(true);
      recognition.onend = () => setIsListening(false);
      
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setMessage(transcript);
      };
      
      recognition.onerror = (event: any) => {
        toast.error(`Speech recognition error: ${event.error}`);
        setIsListening(false);
      };
      
      recognition.start();
    } catch (error) {
      toast.error('Failed to start voice input');
      setIsListening(false);
    }
  };

  return (
    <div className="bg-chat text-chat-foreground">
      <div className="max-w-4xl mx-auto">
        <div className="border-t border-chat-border">
          {/* File Context */}
          {uploadedFiles.length > 0 && (
            <div className="p-4 border-b border-chat-border">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-4 h-4" />
                <span className="text-sm font-medium">Context Files:</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {uploadedFiles.map((file) => (
                  <Badge key={file.id} variant="secondary" className="text-xs">
                    {file.name}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Chat Messages */}
          <ScrollArea className="h-96 p-4" ref={scrollAreaRef}>
            <div className="space-y-4">
              {messages.length === 0 && !session && (
                <div className="text-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">Loading session...</p>
                </div>
              )}
              
              {messages.length === 0 && session && (
                <div className="text-center py-8">
                  <p className="text-sm text-muted-foreground">
                    Start a conversation by asking about your data
                  </p>
                </div>
              )}

              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <Card
                    className={`max-w-xs md:max-w-md p-3 ${
                      msg.role === 'user'
                        ? 'bg-chat-user-bg text-chat-user-fg border-chat-user-bg'
                        : 'bg-chat-ai-bg text-chat-ai-fg border-chat-border'
                    }`}
                  >
                    <div className="space-y-2">
                      {msg.isStreaming ? (
                        <div className="flex items-center gap-2">
                          <Loader2 className="w-3 h-3 animate-spin" />
                          <span className="text-xs opacity-70">Thinking...</span>
                        </div>
                      ) : null}
                      
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      
                      {msg.metadata?.fileReferences && msg.metadata.fileReferences.length > 0 && (
                        <div className="mt-2 space-y-1">
                          <p className="text-xs opacity-70">Referenced files:</p>
                          <div className="flex flex-wrap gap-1">
                            {msg.metadata.fileReferences.map((fileId, idx) => (
                              <Badge key={idx} variant="outline" className="text-xs">
                                File {fileId.substring(0, 8)}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {msg.metadata?.executionTime && (
                        <p className="text-xs opacity-70">
                          Executed in {msg.metadata.executionTime}ms
                        </p>
                      )}
                    </div>
                    
                    <p className="text-xs opacity-70 mt-2">{msg.timestamp}</p>
                  </Card>
                </div>
              ))}
              
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>
          
          {/* Chat Input */}
          <div className="p-4 border-t border-chat-border">
            {!session && (
              <Alert className="mb-4">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Unable to connect to session. Please refresh the page.
                </AlertDescription>
              </Alert>
            )}
            
            <div className="flex gap-2">
              <Input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask about your data..."
                className="flex-1 bg-chat-input-bg border-chat-border text-chat-foreground placeholder:text-chat-foreground/60"
                onKeyPress={handleKeyPress}
                disabled={isSending || streamingMessageId !== null || !session}
              />
              <Button
                onClick={handleSend}
                size="icon"
                className="bg-chat-user-bg hover:bg-chat-user-bg/80 text-chat-user-fg"
                disabled={!message.trim() || isSending || streamingMessageId !== null || !session}
              >
                {isSending || streamingMessageId ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
              <Button
                onClick={toggleVoiceInput}
                size="icon"
                variant="ghost"
                className={`text-chat-foreground hover:bg-chat-border/50 ${
                  isListening ? 'bg-red-100 text-red-600' : ''
                }`}
                disabled={isSending || streamingMessageId !== null}
              >
                <Mic className={`w-4 h-4 ${isListening ? 'animate-pulse' : ''}`} />
              </Button>
            </div>
            <p className="text-xs text-chat-foreground/60 mt-2 text-center">
              AI can make mistakes, so double-check responses
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;