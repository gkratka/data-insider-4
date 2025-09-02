import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import { sendMessage, getChatHistory, startNewSession } from '../chatService'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

describe('chatService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('sendMessage', () => {
    it('sends message successfully', async () => {
      const mockResponse = {
        data: {
          id: 'msg-123',
          content: 'Here is your analysis...',
          role: 'assistant',
          timestamp: '2025-01-15T10:00:00Z',
        }
      }

      mockedAxios.post.mockResolvedValueOnce(mockResponse)

      const result = await sendMessage('Show me sales trends', 'session-123')

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/chat/message', {
        message: 'Show me sales trends',
        session_id: 'session-123',
      })

      expect(result).toEqual(mockResponse.data)
    })

    it('handles message send error', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('Send failed'))

      await expect(sendMessage('test message', 'session-123')).rejects.toThrow('Send failed')
    })
  })

  describe('getChatHistory', () => {
    it('fetches chat history successfully', async () => {
      const mockHistory = [
        { id: '1', content: 'Hello', role: 'user', timestamp: '2025-01-15T10:00:00Z' },
        { id: '2', content: 'Hi there!', role: 'assistant', timestamp: '2025-01-15T10:01:00Z' },
      ]

      mockedAxios.get.mockResolvedValueOnce({ data: mockHistory })

      const result = await getChatHistory('session-123')

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/chat/history/session-123')
      expect(result).toEqual(mockHistory)
    })

    it('handles history fetch error', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('History fetch failed'))

      await expect(getChatHistory('session-123')).rejects.toThrow('History fetch failed')
    })
  })

  describe('startNewSession', () => {
    it('starts new session successfully', async () => {
      const mockSession = {
        data: {
          id: 'session-456',
          created_at: '2025-01-15T10:00:00Z',
        }
      }

      mockedAxios.post.mockResolvedValueOnce(mockSession)

      const result = await startNewSession()

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/chat/sessions/new')
      expect(result).toEqual(mockSession.data)
    })

    it('handles session creation error', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('Session creation failed'))

      await expect(startNewSession()).rejects.toThrow('Session creation failed')
    })
  })
})