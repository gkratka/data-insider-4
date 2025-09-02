import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, Download, Trash2, Eye, Calendar, HardDrive } from 'lucide-react';
import { UploadedFile } from '@/components/FileUpload';

interface FilesTabProps {
  files: UploadedFile[];
  onDeleteFile?: (fileId: string) => void;
  onPreviewFile?: (fileId: string) => void;
  onDownloadFile?: (fileId: string) => void;
}

const FilesTab: React.FC<FilesTabProps> = ({
  files,
  onDeleteFile,
  onPreviewFile,
  onDownloadFile
}) => {
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploaded':
        return 'bg-green-500 text-white';
      case 'valid':
        return 'bg-blue-500 text-white';
      case 'uploading':
        return 'bg-yellow-500 text-white';
      case 'invalid':
      case 'error':
        return 'bg-red-500 text-white';
      case 'validating':
        return 'bg-gray-500 text-white';
      default:
        return 'bg-gray-400 text-white';
    }
  };

  const getStatusText = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploaded':
        return 'Uploaded';
      case 'valid':
        return 'Valid';
      case 'uploading':
        return 'Uploading';
      case 'invalid':
        return 'Invalid';
      case 'error':
        return 'Error';
      case 'validating':
        return 'Validating';
      default:
        return 'Unknown';
    }
  };

  if (files.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">No Files Uploaded</h3>
          <p className="text-muted-foreground">
            Upload some files to see them listed here.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">Uploaded Files</h2>
        <p className="text-muted-foreground">
          Manage your uploaded data files and access their information.
        </p>
      </div>

      <div className="grid gap-4">
        {files.map((file) => (
          <Card key={file.id} className="transition-shadow hover:shadow-md">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <FileText className="w-8 h-8 text-blue-600" />
                  <div>
                    <CardTitle className="text-lg">{file.file.name}</CardTitle>
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground mt-1">
                      <span className="flex items-center space-x-1">
                        <HardDrive className="w-4 h-4" />
                        <span>{formatFileSize(file.file.size)}</span>
                      </span>
                      <span>{file.file.type || 'Unknown type'}</span>
                      <span className="flex items-center space-x-1">
                        <Calendar className="w-4 h-4" />
                        <span>{new Date(file.file.lastModified).toLocaleDateString()}</span>
                      </span>
                    </div>
                  </div>
                </div>
                <Badge className={getStatusColor(file.status)}>
                  {getStatusText(file.status)}
                </Badge>
              </div>
            </CardHeader>
            
            <CardContent>
              {/* File Info */}
              {file.validation.fileInfo && (
                <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-sm mb-2">File Details</h4>
                  <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                    <div>Extension: {file.validation.fileInfo.extension}</div>
                    <div>Type: {file.validation.fileInfo.type}</div>
                    {file.backendFileId && (
                      <div className="col-span-2">ID: {file.backendFileId}</div>
                    )}
                  </div>
                </div>
              )}

              {/* Validation Errors/Warnings */}
              {file.validation.errors.length > 0 && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <h4 className="font-medium text-sm text-red-800 mb-2">Errors</h4>
                  <ul className="text-xs text-red-700 space-y-1">
                    {file.validation.errors.map((error, index) => (
                      <li key={index}>• {error}</li>
                    ))}
                  </ul>
                </div>
              )}

              {file.validation.warnings.length > 0 && (
                <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <h4 className="font-medium text-sm text-yellow-800 mb-2">Warnings</h4>
                  <ul className="text-xs text-yellow-700 space-y-1">
                    {file.validation.warnings.map((warning, index) => (
                      <li key={index}>• {warning}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Error Message */}
              {file.errorMessage && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-xs text-red-700">{file.errorMessage}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center space-x-2">
                {file.status === 'uploaded' && onPreviewFile && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onPreviewFile(file.backendFileId || file.id)}
                    className="flex items-center space-x-1"
                  >
                    <Eye className="w-4 h-4" />
                    <span>Preview</span>
                  </Button>
                )}

                {file.status === 'uploaded' && onDownloadFile && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onDownloadFile(file.backendFileId || file.id)}
                    className="flex items-center space-x-1"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download</span>
                  </Button>
                )}

                {onDeleteFile && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onDeleteFile(file.id)}
                    className="flex items-center space-x-1 text-red-600 hover:text-red-700 hover:border-red-300"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Delete</span>
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default FilesTab;