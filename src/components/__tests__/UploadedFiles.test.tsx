import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import UploadedFiles from '../UploadedFiles'

const mockFiles = [
  {
    id: '1',
    filename: 'sales_data.csv',
    file_type: 'csv',
    file_size: 1024000,
    upload_date: '2025-01-15T10:30:00Z',
    row_count: 1500,
    column_count: 8,
  },
  {
    id: '2',
    filename: 'customer_data.xlsx',
    file_type: 'excel',
    file_size: 2048000,
    upload_date: '2025-01-15T11:00:00Z',
    row_count: 2000,
    column_count: 12,
  },
]

describe('UploadedFiles', () => {
  it('renders uploaded files list', () => {
    render(<UploadedFiles files={mockFiles} />)
    
    expect(screen.getByText('Uploaded Files')).toBeInTheDocument()
    expect(screen.getByText('sales_data.csv')).toBeInTheDocument()
    expect(screen.getByText('customer_data.xlsx')).toBeInTheDocument()
  })

  it('displays file metadata correctly', () => {
    render(<UploadedFiles files={mockFiles} />)
    
    // Check file sizes
    expect(screen.getByText('1.0 MB')).toBeInTheDocument()
    expect(screen.getByText('2.0 MB')).toBeInTheDocument()
    
    // Check row/column counts
    expect(screen.getByText('1,500 rows, 8 columns')).toBeInTheDocument()
    expect(screen.getByText('2,000 rows, 12 columns')).toBeInTheDocument()
  })

  it('shows empty state when no files', () => {
    render(<UploadedFiles files={[]} />)
    
    expect(screen.getByText('No files uploaded yet')).toBeInTheDocument()
    expect(screen.getByText(/Upload some data files to get started/)).toBeInTheDocument()
  })

  it('displays correct file type icons', () => {
    render(<UploadedFiles files={mockFiles} />)
    
    // Both files should have file icons
    const fileIcons = screen.getAllByTestId('file-icon')
    expect(fileIcons).toHaveLength(2)
  })

  it('calls onFileDelete when delete button clicked', () => {
    const mockOnDelete = vi.fn()
    render(<UploadedFiles files={mockFiles} onFileDelete={mockOnDelete} />)
    
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
    fireEvent.click(deleteButtons[0])
    
    expect(mockOnDelete).toHaveBeenCalledWith('1')
  })

  it('calls onFilePreview when preview button clicked', () => {
    const mockOnPreview = vi.fn()
    render(<UploadedFiles files={mockFiles} onFilePreview={mockOnPreview} />)
    
    const previewButtons = screen.getAllByRole('button', { name: /preview/i })
    fireEvent.click(previewButtons[0])
    
    expect(mockOnPreview).toHaveBeenCalledWith('1')
  })

  it('formats upload dates correctly', () => {
    render(<UploadedFiles files={mockFiles} />)
    
    // Should show relative time format
    expect(screen.getByText(/Uploaded/)).toBeInTheDocument()
  })
})