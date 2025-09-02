/**
 * Secure file upload component with drag-and-drop functionality
 * Integrates with file validation service for comprehensive security
 */

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, AlertTriangle, CheckCircle, FileText, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { fileValidationService, FileValidationResult } from '@/services/fileValidationService';
import { cn } from '@/lib/utils';

export interface UploadedFile {
  id: string;
  file: File;
  validation: FileValidationResult;
  uploadProgress: number;
  status: 'validating' | 'valid' | 'invalid' | 'uploading' | 'uploaded' | 'error';
  errorMessage?: string;
  backendFileId?: string;
}

interface FileUploadProps {
  onFilesChange?: (files: UploadedFile[]) => void;
  onUploadComplete?: (files: UploadedFile[]) => void;
  maxFiles?: number;
  disabled?: boolean;
  className?: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFilesChange,
  onUploadComplete,
  maxFiles = 10,
  disabled = false,
  className
}) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isValidating, setIsValidating] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[], rejectedFiles: any[]) => {
    if (disabled) return;

    setIsValidating(true);

    // Handle rejected files
    const rejectedFileErrors = rejectedFiles.map(({ file, errors }) => ({
      id: `rejected-${Date.now()}-${Math.random()}`,
      file,
      validation: {
        isValid: false,
        errors: errors.map((e: any) => e.message),
        warnings: []
      },
      uploadProgress: 0,
      status: 'invalid' as const,
      errorMessage: errors.map((e: any) => e.message).join(', ')
    }));

    // Process accepted files
    const newFiles: UploadedFile[] = [];

    for (const file of acceptedFiles) {
      const fileId = `file-${Date.now()}-${Math.random()}`;
      
      // Add file with validating status
      const uploadedFile: UploadedFile = {
        id: fileId,
        file,
        validation: { isValid: false, errors: [], warnings: [] },
        uploadProgress: 0,
        status: 'validating'
      };

      newFiles.push(uploadedFile);

      // Validate file asynchronously
      try {
        const validation = await fileValidationService.validateFile(file);
        
        // Update file with validation results
        const updatedFile: UploadedFile = {
          ...uploadedFile,
          validation,
          status: validation.isValid ? 'valid' : 'invalid',
          errorMessage: validation.errors.join(', ')
        };

        newFiles[newFiles.findIndex(f => f.id === fileId)] = updatedFile;
      } catch (error) {
        // Update file with error status
        const errorFile: UploadedFile = {
          ...uploadedFile,
          validation: {
            isValid: false,
            errors: [`Validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
            warnings: []
          },
          status: 'error',
          errorMessage: `Validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`
        };

        newFiles[newFiles.findIndex(f => f.id === fileId)] = errorFile;
      }
    }

    // Combine all files (accepted + rejected)
    const allNewFiles = [...newFiles, ...rejectedFileErrors];
    
    // Respect max files limit
    const updatedFiles = [...files, ...allNewFiles].slice(0, maxFiles);
    
    setFiles(updatedFiles);
    setIsValidating(false);
    onFilesChange?.(updatedFiles);
  }, [files, onFilesChange, maxFiles, disabled]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    disabled,
    maxFiles,
    maxSize: 500 * 1024 * 1024, // 500MB
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/json': ['.json'],
      'text/plain': ['.txt'],
      'application/vnd.apache.parquet': ['.parquet']
    },
    multiple: maxFiles > 1
  });

  const removeFile = useCallback((fileId: string) => {
    const updatedFiles = files.filter(f => f.id !== fileId);
    setFiles(updatedFiles);
    onFilesChange?.(updatedFiles);
  }, [files, onFilesChange]);

  const uploadToBackend = useCallback(async (uploadedFile: UploadedFile) => {
    try {
      // Set uploading status
      setFiles(prev => prev.map(f => 
        f.id === uploadedFile.id ? { ...f, status: 'uploading' as const, uploadProgress: 0 } : f
      ));

      // Import the upload service
      const { fileUploadService } = await import('@/services/fileUploadService');

      // Upload with progress tracking
      const result = await fileUploadService.uploadFileWithProgress(
        uploadedFile.file,
        (progress) => {
          setFiles(prev => prev.map(f => 
            f.id === uploadedFile.id ? { ...f, uploadProgress: progress } : f
          ));
        }
      );

      // Mark as uploaded with backend response
      setFiles(prev => prev.map(f => 
        f.id === uploadedFile.id ? { 
          ...f, 
          status: 'uploaded' as const, 
          uploadProgress: 100,
          backendFileId: result.file_id 
        } : f
      ));

      return result;
    } catch (error) {
      // Mark as error
      setFiles(prev => prev.map(f => 
        f.id === uploadedFile.id ? { 
          ...f, 
          status: 'error' as const, 
          errorMessage: error instanceof Error ? error.message : 'Upload failed'
        } : f
      ));
      throw error;
    }
  }, []);

  const uploadValidFiles = useCallback(async () => {
    const validFiles = files.filter(f => f.status === 'valid');
    
    // Upload files one by one to avoid overwhelming the server
    const uploadResults = [];
    for (const file of validFiles) {
      try {
        const result = await uploadToBackend(file);
        uploadResults.push({ file, result });
      } catch (error) {
        console.error(`Failed to upload ${file.file.name}:`, error);
      }
    }
    
    // Call completion callback with successfully uploaded files
    const uploadedFiles = files.filter(f => f.status === 'uploaded');
    onUploadComplete?.(uploadedFiles);
  }, [files, uploadToBackend, onUploadComplete]);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'validating':
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
      case 'valid':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'invalid':
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'uploading':
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
      case 'uploaded':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      default:
        return <FileText className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: UploadedFile['status']) => {
    switch (status) {
      case 'validating':
        return <Badge variant="secondary">Validating</Badge>;
      case 'valid':
        return <Badge variant="default" className="bg-green-500">Valid</Badge>;
      case 'invalid':
      case 'error':
        return <Badge variant="destructive">Invalid</Badge>;
      case 'uploading':
        return <Badge variant="secondary">Uploading</Badge>;
      case 'uploaded':
        return <Badge variant="default" className="bg-green-500">Uploaded</Badge>;
      default:
        return null;
    }
  };

  const validFilesCount = files.filter(f => f.status === 'valid').length;
  const hasValidFiles = validFilesCount > 0;

  return (
    <div className={cn("w-full max-w-4xl mx-auto space-y-6", className)}>
      {/* Drop Zone */}
      <Card className="border-dashed border-2 hover:border-primary/50 transition-colors">
        <CardContent className="p-8">
          <div
            {...getRootProps()}
            data-testid="dropzone"
            className={cn(
              "cursor-pointer text-center space-y-4 transition-colors",
              isDragActive && "text-primary",
              disabled && "cursor-not-allowed opacity-50"
            )}
          >
            <input {...getInputProps()} />
            
            <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              {isValidating ? (
                <Loader2 className="w-6 h-6 animate-spin text-primary" />
              ) : (
                <Upload className="w-6 h-6 text-primary" />
              )}
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">
                {isDragActive ? 'Drop files here' : 'Upload your data files'}
              </h3>
              <p className="text-muted-foreground text-sm mb-4">
                Drag and drop your CSV, Excel, JSON, or Parquet files here, or click to browse
              </p>
              <p className="text-xs text-muted-foreground">
                Maximum file size: 500MB • Maximum {maxFiles} files • Supported formats: CSV, XLS, XLSX, JSON, TXT, Parquet
              </p>
            </div>

            {!disabled && (
              <Button variant="outline" className="mt-4">
                Choose Files
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* File List */}
      {files.length > 0 && (
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                Uploaded Files ({files.length})
              </h3>
              {hasValidFiles && (
                <Button onClick={uploadValidFiles} className="ml-auto">
                  Upload Valid Files ({validFilesCount})
                </Button>
              )}
            </div>

            <div className="space-y-4">
              {files.map((uploadedFile) => (
                <div key={uploadedFile.id} data-testid="uploaded-file" className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3 flex-1">
                      {getStatusIcon(uploadedFile.status)}
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{uploadedFile.file.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {formatFileSize(uploadedFile.file.size)} • {uploadedFile.file.type || 'Unknown type'}
                        </p>
                      </div>
                      {getStatusBadge(uploadedFile.status)}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(uploadedFile.id)}
                      className="ml-2"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>

                  {/* Upload Progress */}
                  {uploadedFile.status === 'uploading' && (
                    <div className="mt-3">
                      <Progress value={uploadedFile.uploadProgress} className="w-full" />
                      <p className="text-xs text-muted-foreground mt-1">
                        Uploading... {uploadedFile.uploadProgress}%
                      </p>
                    </div>
                  )}

                  {/* Validation Results */}
                  {(uploadedFile.validation.errors.length > 0 || uploadedFile.validation.warnings.length > 0) && (
                    <div className="mt-3 space-y-2">
                      {uploadedFile.validation.errors.map((error, index) => (
                        <Alert key={`error-${index}`} variant="destructive">
                          <AlertTriangle className="h-4 w-4" />
                          <AlertDescription className="text-sm">{error}</AlertDescription>
                        </Alert>
                      ))}
                      {uploadedFile.validation.warnings.map((warning, index) => (
                        <Alert key={`warning-${index}`}>
                          <AlertTriangle className="h-4 w-4" />
                          <AlertDescription className="text-sm">{warning}</AlertDescription>
                        </Alert>
                      ))}
                    </div>
                  )}

                  {/* File Info */}
                  {uploadedFile.validation.fileInfo && uploadedFile.status === 'valid' && (
                    <div className="mt-3 text-xs text-muted-foreground">
                      File validated successfully • Extension: {uploadedFile.validation.fileInfo.extension} • Type: {uploadedFile.validation.fileInfo.type}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default FileUpload;