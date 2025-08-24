import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import { uploadFile, getFiles, deleteFile, getFilePreview } from '../fileService'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

describe('fileService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('uploadFile', () => {
    it('uploads file successfully', async () => {
      const mockFile = new File(['test content'], 'test.csv', { type: 'text/csv' })
      const mockResponse = {
        data: {
          id: 'file-123',
          filename: 'test.csv',
          file_type: 'csv',
          file_size: 12,
          upload_date: '2025-01-15T10:00:00Z',
        }
      }

      mockedAxios.post.mockResolvedValueOnce(mockResponse)

      const result = await uploadFile(mockFile)

      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/files/upload',
        expect.any(FormData),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'multipart/form-data',
          }),
          onUploadProgress: expect.any(Function),
        })
      )

      expect(result).toEqual(mockResponse.data)
    })

    it('handles upload error', async () => {
      const mockFile = new File(['test content'], 'test.csv', { type: 'text/csv' })
      
      mockedAxios.post.mockRejectedValueOnce(new Error('Upload failed'))

      await expect(uploadFile(mockFile)).rejects.toThrow('Upload failed')
    })
  })

  describe('getFiles', () => {
    it('fetches files successfully', async () => {
      const mockFiles = [
        { id: '1', filename: 'file1.csv', file_type: 'csv' },
        { id: '2', filename: 'file2.xlsx', file_type: 'excel' },
      ]

      mockedAxios.get.mockResolvedValueOnce({ data: mockFiles })

      const result = await getFiles()

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/files')
      expect(result).toEqual(mockFiles)
    })

    it('handles fetch error', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('Fetch failed'))

      await expect(getFiles()).rejects.toThrow('Fetch failed')
    })
  })

  describe('deleteFile', () => {
    it('deletes file successfully', async () => {
      mockedAxios.delete.mockResolvedValueOnce({ data: { success: true } })

      await deleteFile('file-123')

      expect(mockedAxios.delete).toHaveBeenCalledWith('/api/files/file-123')
    })

    it('handles delete error', async () => {
      mockedAxios.delete.mockRejectedValueOnce(new Error('Delete failed'))

      await expect(deleteFile('file-123')).rejects.toThrow('Delete failed')
    })
  })

  describe('getFilePreview', () => {
    it('fetches file preview successfully', async () => {
      const mockPreview = {
        headers: ['col1', 'col2', 'col3'],
        rows: [
          ['val1', 'val2', 'val3'],
          ['val4', 'val5', 'val6'],
        ],
        total_rows: 100,
      }

      mockedAxios.get.mockResolvedValueOnce({ data: mockPreview })

      const result = await getFilePreview('file-123')

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/files/file-123/preview')
      expect(result).toEqual(mockPreview)
    })

    it('handles preview error', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('Preview failed'))

      await expect(getFilePreview('file-123')).rejects.toThrow('Preview failed')
    })
  })
})