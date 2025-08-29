import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import UploadSection from '../UploadSection'

// Mock the useToast hook
vi.mock('@/hooks/use-toast', async () => {
  return {
    useToast: () => ({
      toast: vi.fn(),
    }),
  }
})

// Mock the file service
vi.mock('@/services/fileService', async () => {
  return {
    uploadFile: vi.fn().mockResolvedValue({
      id: 'test-file-id',
      filename: 'test.csv',
      file_type: 'csv',
      file_size: 1024,
      upload_date: new Date().toISOString(),
    }),
    getFiles: vi.fn().mockResolvedValue([]),
    deleteFile: vi.fn().mockResolvedValue({}),
    getFilePreview: vi.fn().mockResolvedValue({
      headers: [],
      rows: [],
      total_rows: 0,
    }),
  }
})

describe('UploadSection', () => {
  it('renders upload area correctly', () => {
    render(<UploadSection />)
    
    expect(screen.getByText('Upload Your Data Files')).toBeInTheDocument()
    expect(screen.getByText(/Drop files here or click to browse/)).toBeInTheDocument()
  })

  it('displays supported file formats', () => {
    render(<UploadSection />)
    
    expect(screen.getByText(/Supported formats: CSV, Excel, JSON, Parquet/)).toBeInTheDocument()
  })

  it('shows file size limit', () => {
    render(<UploadSection />)
    
    expect(screen.getByText(/Maximum file size: 500MB/)).toBeInTheDocument()
  })

  it('handles drag and drop events', () => {
    render(<UploadSection />)
    
    const dropzone = screen.getByText(/Drop files here or click to browse/).closest('div')
    
    // Test drag enter
    fireEvent.dragEnter(dropzone!)
    expect(dropzone).toHaveClass('border-blue-500')

    // Test drag leave
    fireEvent.dragLeave(dropzone!)
    expect(dropzone).not.toHaveClass('border-blue-500')
  })

  it('validates file types', () => {
    const mockToast = vi.fn()
    vi.mocked(require('@/hooks/use-toast').useToast).mockReturnValue({
      toast: mockToast,
    })

    render(<UploadSection />)
    
    const dropzone = screen.getByText(/Drop files here or click to browse/).closest('div')
    
    // Create a mock file with unsupported type
    const unsupportedFile = new File(['test'], 'test.txt', { type: 'text/plain' })
    
    fireEvent.drop(dropzone!, {
      dataTransfer: { files: [unsupportedFile] }
    })

    expect(mockToast).toHaveBeenCalledWith({
      title: 'Invalid file type',
      description: expect.stringContaining('Please upload'),
      variant: 'destructive',
    })
  })
})