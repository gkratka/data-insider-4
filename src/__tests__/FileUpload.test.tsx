/**
 * Tests for FileUpload component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileUpload, UploadedFile } from '../components/FileUpload';

// Mock the file validation service
vi.mock('../services/fileValidationService', () => ({
  fileValidationService: {
    validateFile: vi.fn().mockResolvedValue({
      isValid: true,
      errors: [],
      warnings: [],
      fileInfo: {
        name: 'test.csv',
        size: 1024,
        type: 'text/csv',
        extension: '.csv'
      }
    })
  }
}));

// Mock the file upload service
vi.mock('../services/fileUploadService', () => ({
  fileUploadService: {
    uploadFileWithProgress: vi.fn().mockResolvedValue({
      filename: 'test.csv',
      size: 1024,
      content_type: 'text/csv',
      file_id: 'test-file-id',
      message: 'Upload successful'
    })
  }
}));

// Helper to create mock files
const createMockFile = (name: string, size: number, type: string): File => {
  const file = new File(['test content'], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
};

describe('FileUpload Component', () => {
  const mockOnFilesChange = vi.fn();
  const mockOnUploadComplete = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders upload zone correctly', () => {
    render(<FileUpload />);

    expect(screen.getByText('Upload your data files')).toBeInTheDocument();
    expect(screen.getByText(/Drag and drop your CSV, Excel, JSON/)).toBeInTheDocument();
    expect(screen.getByText('Choose Files')).toBeInTheDocument();
  });

  it('shows correct file size and format restrictions', () => {
    render(<FileUpload />);

    expect(screen.getByText(/Maximum file size: 500MB/)).toBeInTheDocument();
    expect(screen.getByText(/Supported formats: CSV, XLS, XLSX, JSON, TXT, Parquet/)).toBeInTheDocument();
  });

  it('accepts valid file types', async () => {
    const user = userEvent.setup();
    render(<FileUpload onFilesChange={mockOnFilesChange} />);

    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const csvFile = createMockFile('test.csv', 1024, 'text/csv');

    await user.upload(fileInput, csvFile);

    await waitFor(() => {
      expect(mockOnFilesChange).toHaveBeenCalled();
    });
  });

  it('displays uploaded files with correct information', async () => {
    const user = userEvent.setup();
    render(<FileUpload onFilesChange={mockOnFilesChange} />);

    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const csvFile = createMockFile('test.csv', 1024, 'text/csv');

    await user.upload(fileInput, csvFile);

    await waitFor(() => {
      expect(screen.getByText('test.csv')).toBeInTheDocument();
      expect(screen.getByText('1 KB • text/csv')).toBeInTheDocument();
    });
  });

  it('shows validation status for files', async () => {
    const user = userEvent.setup();
    render(<FileUpload onFilesChange={mockOnFilesChange} />);

    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const csvFile = createMockFile('test.csv', 1024, 'text/csv');

    await user.upload(fileInput, csvFile);

    await waitFor(() => {
      expect(screen.getByText('Valid')).toBeInTheDocument();
    });
  });

  it('allows removing files', async () => {
    const user = userEvent.setup();
    render(<FileUpload onFilesChange={mockOnFilesChange} />);

    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const csvFile = createMockFile('test.csv', 1024, 'text/csv');

    await user.upload(fileInput, csvFile);

    await waitFor(() => {
      expect(screen.getByText('test.csv')).toBeInTheDocument();
    });

    // Find and click the remove button
    const removeButton = screen.getByRole('button', { name: /remove/i });
    await user.click(removeButton);

    await waitFor(() => {
      expect(screen.queryByText('test.csv')).not.toBeInTheDocument();
    });
  });

  it('shows upload button when valid files are present', async () => {
    const user = userEvent.setup();
    render(<FileUpload onFilesChange={mockOnFilesChange} />);

    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const csvFile = createMockFile('test.csv', 1024, 'text/csv');

    await user.upload(fileInput, csvFile);

    await waitFor(() => {
      expect(screen.getByText('Upload Valid Files (1)')).toBeInTheDocument();
    });
  });

  it('respects maxFiles limit', async () => {
    const user = userEvent.setup();
    render(<FileUpload maxFiles={2} onFilesChange={mockOnFilesChange} />);

    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const files = [
      createMockFile('test1.csv', 1024, 'text/csv'),
      createMockFile('test2.csv', 1024, 'text/csv'),
      createMockFile('test3.csv', 1024, 'text/csv'),
    ];

    await user.upload(fileInput, files);

    await waitFor(() => {
      const fileElements = screen.getAllByText(/test\d\.csv/);
      expect(fileElements).toHaveLength(2);
    });
  });

  it('handles upload errors gracefully', async () => {
    // Mock upload service to throw an error
    const { fileUploadService } = await import('../services/fileUploadService');
    vi.mocked(fileUploadService.uploadFileWithProgress).mockRejectedValueOnce(
      new Error('Upload failed')
    );

    const user = userEvent.setup();
    render(<FileUpload onFilesChange={mockOnFilesChange} />);

    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const csvFile = createMockFile('test.csv', 1024, 'text/csv');

    await user.upload(fileInput, csvFile);

    // Wait for validation to complete
    await waitFor(() => {
      expect(screen.getByText('Upload Valid Files (1)')).toBeInTheDocument();
    });

    // Click upload button
    const uploadButton = screen.getByText('Upload Valid Files (1)');
    await user.click(uploadButton);

    // Should show error state
    await waitFor(() => {
      expect(screen.queryByText('Valid')).not.toBeInTheDocument();
    });
  });

  it('shows upload progress during file upload', async () => {
    const user = userEvent.setup();
    render(<FileUpload onFilesChange={mockOnFilesChange} />);

    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const csvFile = createMockFile('test.csv', 1024, 'text/csv');

    await user.upload(fileInput, csvFile);

    await waitFor(() => {
      expect(screen.getByText('Upload Valid Files (1)')).toBeInTheDocument();
    });

    const uploadButton = screen.getByText('Upload Valid Files (1)');
    await user.click(uploadButton);

    // Should show uploading state
    await waitFor(() => {
      expect(screen.getByText('Uploading')).toBeInTheDocument();
    });
  });

  it('calls onUploadComplete when uploads finish', async () => {
    const user = userEvent.setup();
    render(<FileUpload onUploadComplete={mockOnUploadComplete} />);

    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const csvFile = createMockFile('test.csv', 1024, 'text/csv');

    await user.upload(fileInput, csvFile);

    await waitFor(() => {
      expect(screen.getByText('Upload Valid Files (1)')).toBeInTheDocument();
    });

    const uploadButton = screen.getByText('Upload Valid Files (1)');
    await user.click(uploadButton);

    await waitFor(() => {
      expect(mockOnUploadComplete).toHaveBeenCalled();
    });
  });

  it('can be disabled', () => {
    render(<FileUpload disabled={true} />);

    const chooseButton = screen.getByText('Choose Files');
    expect(chooseButton.closest('div')).toHaveClass('cursor-not-allowed');
  });

  it('shows file count in header when files are uploaded', async () => {
    const user = userEvent.setup();
    render(<FileUpload />);

    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const csvFile = createMockFile('test.csv', 1024, 'text/csv');

    await user.upload(fileInput, csvFile);

    await waitFor(() => {
      expect(screen.getByText('Uploaded Files (1)')).toBeInTheDocument();
    });
  });

  it('displays validation errors for invalid files', async () => {
    // Mock validation service to return errors
    const { fileValidationService } = await import('../services/fileValidationService');
    vi.mocked(fileValidationService.validateFile).mockResolvedValueOnce({
      isValid: false,
      errors: ['File type not allowed'],
      warnings: [],
      fileInfo: {
        name: 'test.exe',
        size: 1024,
        type: 'application/octet-stream',
        extension: '.exe'
      }
    });

    const user = userEvent.setup();
    render(<FileUpload />);

    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const invalidFile = createMockFile('test.exe', 1024, 'application/octet-stream');

    await user.upload(fileInput, invalidFile);

    await waitFor(() => {
      expect(screen.getByText('File type not allowed')).toBeInTheDocument();
      expect(screen.getByText('Invalid')).toBeInTheDocument();
    });
  });

  it('displays validation warnings', async () => {
    // Mock validation service to return warnings
    const { fileValidationService } = await import('../services/fileValidationService');
    vi.mocked(fileValidationService.validateFile).mockResolvedValueOnce({
      isValid: true,
      errors: [],
      warnings: ['File extension and MIME type may not match'],
      fileInfo: {
        name: 'test.csv',
        size: 1024,
        type: 'application/json',
        extension: '.csv'
      }
    });

    const user = userEvent.setup();
    render(<FileUpload />);

    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const csvFile = createMockFile('test.csv', 1024, 'application/json');

    await user.upload(fileInput, csvFile);

    await waitFor(() => {
      expect(screen.getByText('File extension and MIME type may not match')).toBeInTheDocument();
    });
  });
});