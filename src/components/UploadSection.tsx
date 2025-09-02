import { Upload, FileText, AlertCircle, CheckCircle2, X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { toast } from "sonner";
import { fileService } from "@/services/fileService";
import { sessionService } from "@/services/sessionService";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  error?: string;
}

const UploadSection = () => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const validateFile = (file: File): string | null => {
    const maxSize = 500 * 1024 * 1024; // 500MB
    const supportedTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/json',
      'application/x-parquet'
    ];
    
    if (file.size > maxSize) {
      return `File size (${formatFileSize(file.size)}) exceeds the 500MB limit`;
    }
    
    if (!supportedTypes.includes(file.type) && !file.name.endsWith('.parquet')) {
      return `Unsupported file type. Please upload CSV, Excel, JSON, or Parquet files`;
    }
    
    return null;
  };

  const uploadFile = async (file: File): Promise<void> => {
    const fileId = Math.random().toString(36).substr(2, 9);
    const uploadedFile: UploadedFile = {
      id: fileId,
      name: file.name,
      size: file.size,
      progress: 0,
      status: 'uploading'
    };
    
    setUploadedFiles(prev => [...prev, uploadedFile]);
    
    try {
      // Listen for upload progress events
      const handleProgress = (event: CustomEvent) => {
        if (event.detail.filename === file.name) {
          setUploadedFiles(prev => 
            prev.map(f => 
              f.id === fileId ? { ...f, progress: event.detail.progress } : f
            )
          );
        }
      };
      
      window.addEventListener('fileUploadProgress', handleProgress as EventListener);
      
      // Use fileService for actual upload
      const response = await fileService.uploadFile({
        file,
        sessionId: sessionService.getCurrentSessionId() || undefined
      });
      
      // Update with server response
      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === fileId 
            ? { ...f, id: response.fileId, status: 'completed', progress: 100 } 
            : f
        )
      );
      
      window.removeEventListener('fileUploadProgress', handleProgress as EventListener);
      toast.success(`${file.name} uploaded successfully`);
      
    } catch (error) {
      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === fileId 
            ? { ...f, status: 'error', error: error instanceof Error ? error.message : 'Upload failed' } 
            : f
        )
      );
      toast.error(`Failed to upload ${file.name}`);
    }
  };

  const onDrop = useCallback(async (acceptedFiles: File[], rejectedFiles: any[]) => {
    setIsUploading(true);
    
    // Handle rejected files
    rejectedFiles.forEach(({ file, errors }) => {
      errors.forEach((error: any) => {
        toast.error(`${file.name}: ${error.message}`);
      });
    });
    
    // Validate and upload accepted files
    for (const file of acceptedFiles) {
      const validation = validateFile(file);
      if (validation) {
        toast.error(validation);
        continue;
      }
      
      await uploadFile(file);
    }
    
    setIsUploading(false);
  }, []);

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/json': ['.json'],
      'application/x-parquet': ['.parquet']
    },
    maxSize: 500 * 1024 * 1024, // 500MB
    disabled: isUploading
  });

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] px-4">
      <div className="max-w-4xl mx-auto text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-5xl md:text-6xl font-bold text-foreground">
            Give me data and I will give you insights
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Upload your files and start analyzing with AI-powered insights
          </p>
        </div>
        
        {/* Drag and Drop Zone */}
        <div className="max-w-2xl mx-auto">
          <div
            {...getRootProps()}
            className={`
              relative border-2 border-dashed rounded-lg p-8 transition-all duration-200 cursor-pointer
              ${isDragActive && !isDragReject ? 'border-primary bg-primary/5' : ''}
              ${isDragReject ? 'border-destructive bg-destructive/5' : ''}
              ${!isDragActive ? 'border-muted-foreground/25 hover:border-primary hover:bg-primary/5' : ''}
              ${isUploading ? 'pointer-events-none opacity-50' : ''}
            `}
          >
            <input {...getInputProps()} />
            <div className="flex flex-col items-center gap-4">
              <Upload className={`w-12 h-12 ${isDragActive ? 'text-primary' : 'text-muted-foreground'}`} />
              <div className="space-y-2">
                <p className="text-lg font-medium">
                  {isDragActive 
                    ? isDragReject 
                      ? 'Invalid file type' 
                      : 'Drop your files here'
                    : 'Drag & drop files here, or click to browse'
                  }
                </p>
                <p className="text-sm text-muted-foreground">
                  Supports CSV, Excel, JSON, and Parquet files up to 500MB
                </p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Upload Progress */}
        {uploadedFiles.length > 0 && (
          <div className="max-w-2xl mx-auto space-y-3">
            <h3 className="text-lg font-medium text-left">Uploaded Files</h3>
            {uploadedFiles.map((file) => (
              <div key={file.id} className="border rounded-lg p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileText className="w-4 h-4" />
                    <span className="font-medium text-sm">{file.name}</span>
                    <span className="text-xs text-muted-foreground">
                      {formatFileSize(file.size)}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    {file.status === 'completed' && (
                      <Badge variant="default" className="bg-green-100 text-green-800">
                        <CheckCircle2 className="w-3 h-3 mr-1" />
                        Complete
                      </Badge>
                    )}
                    {file.status === 'error' && (
                      <Badge variant="destructive">
                        <AlertCircle className="w-3 h-3 mr-1" />
                        Error
                      </Badge>
                    )}
                    {file.status === 'uploading' && (
                      <Badge variant="secondary">
                        <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                        Uploading
                      </Badge>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(file.id)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                
                {file.status === 'uploading' && (
                  <Progress value={file.progress} className="w-full" />
                )}
                
                {file.error && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{file.error}</AlertDescription>
                  </Alert>
                )}
              </div>
            ))}
          </div>
        )}
        
        <div className="flex flex-col sm:flex-row gap-4 max-w-2xl mx-auto">
          <Input 
            placeholder="Ask me anything about your data..."
            className="h-12 flex-1"
          />
        </div>
      </div>
    </div>
  );
};

export default UploadSection;