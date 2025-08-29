import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ChatInterface from '../ChatInterface'

// Mock the chat service
vi.mock('@/services/chatService', async () => {
  return {
    sendMessage: vi.fn().mockResolvedValue({
      id: 'response-1',
      content: 'Test response',
      role: 'assistant',
      timestamp: new Date().toISOString(),
    }),
    getChatHistory: vi.fn().mockResolvedValue([]),
    startNewSession: vi.fn().mockResolvedValue({
      id: 'test-session',
      created_at: new Date().toISOString(),
    }),
  }
})

// Mock the session service
vi.mock('@/services/sessionService', async () => {
  return {
    getCurrentSession: vi.fn().mockResolvedValue({
      id: 'test-session',
      created_at: new Date().toISOString(),
    }),
    createSession: vi.fn().mockResolvedValue({
      id: 'test-session',
      created_at: new Date().toISOString(),
    }),
  }
})

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  )
}

describe('ChatInterface', () => {
  it('renders chat interface correctly', () => {
    renderWithQueryClient(<ChatInterface />)
    
    expect(screen.getByPlaceholderText(/Ask me anything about your data/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument()
  })

  it('displays initial welcome message', () => {
    renderWithQueryClient(<ChatInterface />)
    
    expect(screen.getByText(/Hello! I'm your data analysis assistant/)).toBeInTheDocument()
  })

  it('handles message input', () => {
    renderWithQueryClient(<ChatInterface />)
    
    const input = screen.getByPlaceholderText(/Ask me anything about your data/)
    fireEvent.change(input, { target: { value: 'Test message' } })
    
    expect(input).toHaveValue('Test message')
  })

  it('sends message on form submit', async () => {
    const mockSendMessage = vi.mocked(require('@/services/chatService').sendMessage)
    
    renderWithQueryClient(<ChatInterface />)
    
    const input = screen.getByPlaceholderText(/Ask me anything about your data/)
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    fireEvent.change(input, { target: { value: 'Test question' } })
    fireEvent.click(sendButton)
    
    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalledWith('Test question', expect.any(String))
    })
  })

  it('clears input after sending message', async () => {
    renderWithQueryClient(<ChatInterface />)
    
    const input = screen.getByPlaceholderText(/Ask me anything about your data/)
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    fireEvent.change(input, { target: { value: 'Test question' } })
    fireEvent.click(sendButton)
    
    await waitFor(() => {
      expect(input).toHaveValue('')
    })
  })

  it('displays loading state while sending message', async () => {
    const mockSendMessage = vi.mocked(require('@/services/chatService').sendMessage)
    mockSendMessage.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
    
    renderWithQueryClient(<ChatInterface />)
    
    const input = screen.getByPlaceholderText(/Ask me anything about your data/)
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    fireEvent.change(input, { target: { value: 'Test question' } })
    fireEvent.click(sendButton)
    
    expect(sendButton).toBeDisabled()
  })
})